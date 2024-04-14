import time
from datetime import datetime 
import json
import connexion
from connexion import NoContent
from flask import Flask, request, jsonify
from os import path
import os
from models_mysql import TrafficFlow, IncidentReport, Base
import db_mysql 
import yaml
import logging
import logging.config
from sqlalchemy import and_
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())


with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

#session = db_mysql.make_session()
def log_to_db(session, body, type):
    if type not in ("traffic", "incident"):
        raise  ValueError("Invalid event type: {}".format(type))
    
    if type == "traffic":
        new_event = TrafficFlow(
            trace_id=body["trace_id"],
            traffic_id=body["traffic_id"],
            intersection_id=body["intersectionId"],
            dateRecorded=body["dateRecorded"],
            vehicle_count=body["vehicleCount"]
        )
    else:
        new_event = IncidentReport(
            trace_id=body["trace_id"],
            accident_id=body["accident_id"],
            camera_id=body["cameraId"],
            timestamp=body["timestamp"],
            incidentType=body["incidentType"]
        )
    
    session.add(new_event)
    session.commit()
    session.close()

# def write_data(type, req):
#     if not path.isfile(EVENT_FILE):
#         with open(EVENT_FILE, "w") as file:
#             file.write('[]')

#     file_content = []
#     if path.isfile(EVENT_FILE):
#         with open(EVENT_FILE, "r") as read_file:
#             try:
#                 file_content = json.load(read_file)
#             except json.JSONDecodeError:
#                 print("Error decoding JSON. Initializing with an empty list.")
#                 file_content = []

#     request_key = f"num_{type.lower()}"
#     recent_key = f"recent_{type.lower()}"

#     file_content_dict = dict(file_content)

#     file_content_dict.setdefault(request_key, 0)
#     file_content_dict.setdefault(recent_key, [])

#     file_content_dict[request_key] += 1
#     # file_content_dict[recent_key].append(req)
#     file_content_dict[recent_key].insert(0, req)
#     file_content_dict[recent_key] = file_content_dict[recent_key][:MAX_EVENTS]
    
#     with open(EVENT_FILE, "w") as write_file:
#         json.dump(file_content_dict, write_file, indent='\t')



#def recordTrafficFlow(body):
#    session = db_mysql.make_session()
#    log_to_db(session, body,"traffic")
#    logger.debug(f"Recieved event traffic request with a trace id of {body['trace_id']})")
#    return NoContent, 201


#def reportIncident(body):
#    session = db_mysql.make_session()
#    log_to_db(session, body,"incident")
#    logger.debug(f"Recieved event accident request with a trace id of {body['trace_id']})")
#    return NoContent, 201


def get_traffic_report(start_timestamp, end_timestamp):
    session = db_mysql.make_session()
    start_timestamp_dt = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_dt = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    results = session.query(TrafficFlow).filter(
        and_(TrafficFlow.date_created >= start_timestamp_dt,TrafficFlow.date_created < end_timestamp_dt))
    
    result_list = []
    for result in results:
       result_list.append(result.to_dict())

    session.close()
    logger.info("Query for Traffic report after %s returns %d results" % (start_timestamp, len(result_list)))

    return result_list, 200

def get_incident_report(start_timestamp, end_timestamp):
    session = db_mysql.make_session()
    start_timestamp_dt = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S.%f")
    end_timestamp_dt = datetime.strptime(end_timestamp, "%Y-%m-%d %H:%M:%S.%f")

    results = session.query(IncidentReport).filter(
    and_(IncidentReport.date_created >= start_timestamp_dt,IncidentReport.date_created < end_timestamp_dt))
    
    result_list = []
    for result in results:
       result_list.append(result.to_dict())

    session.close()
    logger.info("Query for Incident report after %s returns %d results" % (start_timestamp, len(result_list)))

    return result_list, 200

database_name = app_config['datastore']['database']
port = app_config['datastore']['port']
username = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname =app_config['datastore']['hostname']

logger.info(f"Connecting to {database_name}. Hostname:{hostname}, Port:{port}")



def connect_to_kafka():
    """ Connect to Kafka and return the client and topic """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    return client, topic


def process_messages():
    """ Process event messages """
    connected = False
    while not connected:
        try:
            client, topic = connect_to_kafka()
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                                 reset_offset_on_start=False,
                                                 auto_offset_reset=OffsetType.LATEST)
            connected = True
#    hostname = "%s:%d" % (app_config["events"]["hostname"], 
#    app_config["events"]["port"])
#    client = KafkaClient(hosts=hostname)
#    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consume on a consumer group, that only reads new messages 
    # (uncommitted messages) when the service re-starts (i.e., it doesn't 
    # read all the old messages from the history in the message queue).
#    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
#    reset_offset_on_start=False,
#    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info("Message: %s" % msg)

                payload = msg["payload"]
        
                if msg["type"] == "TrafficFlow": # Change this to your event type
                    new_event = TrafficFlow(
                    trace_id=payload["trace_id"],
                    traffic_id=payload["traffic_id"],
                    intersection_id=payload["intersectionId"],
                    dateRecorded=payload["dateRecorded"],
                    vehicle_count=payload["vehicleCount"]
                )
                    session = db_mysql.make_session()
                    session.add(new_event)
                    session.commit()
                    session.close()
           
        # Store the event1 (i.e., the payload) to the DB
                elif msg["type"] == "reportIncident": # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
                    new_event = IncidentReport(
                    trace_id=payload["trace_id"],
                    accident_id=payload["accident_id"],
                    camera_id=payload["cameraId"],
                    timestamp=payload["timestamp"],
                    incidentType=payload["incidentType"]
                )
                    session = db_mysql.make_session()
                    session.add(new_event)
                    session.commit()
                    session.close()

        # Commit the new message as being read
                consumer.commit_offsets()

        except Exception as e:
            logger.error(f"Error connecting to Kafka: {e}")
            logger.info("Retrying connection...")



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("trafficreport.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(host="0.0.0.0", port=8090)

