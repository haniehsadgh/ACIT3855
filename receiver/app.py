import time
from datetime import datetime 
import json
import connexion
from connexion import NoContent
from flask import Flask, request, jsonify
import requests
from os import path
import os
import yaml
import logging
import uuid
import logging.config
from pykafka import KafkaClient

MAX_EVENTS = 5
EVENT_FILE = 'events.json'

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


# Initialize KafkaClient on startup
client = None
topic = None

def connect_to_kafka():
    global client, topic
    """ Connect to Kafka and return the client and topic """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
#    return client, topic

# Retry logic for connecting to Kafka
def retry_connect_to_kafka():
    max_retries = 3  # Maximum number of retries
    current_retry = 0
    while current_retry < max_retries:
        try:
            connect_to_kafka()
            logger.info("Connected to Kafka")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Kafka: {e}")
            logger.info(f"Retrying connection to Kafka ({current_retry + 1}/{max_retries})")
            current_retry += 1
            time.sleep(5)  # Wait for a few seconds before retrying
    logger.error("Failed to connect to Kafka after multiple attempts")
    return False

# Initial connection to Kafka
retry_connect_to_kafka()


def generate_trace_id():
    return str(uuid.uuid4())


def recordTrafficFlow(body):
    trace_id = generate_trace_id()
    logger.info(f"Recieved event traffic request with a trace id of {trace_id})")
    

    # msg = {
    #     "msg_data": f"{body['traffic_id']}, aircraft ID: {body['intersectionId']}, recorded {body['dateRecorded']} vehicle count: {body['vehicleCount']}",
    #     "received_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    # }
    body['trace_id'] = trace_id

    #client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    #topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "TrafficFlow", 
            "datetime" : 
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    #req = requests.post(app_config['traffic_condition']['url'], json=body, headers={'Content-Type': 'application/json'})
    # write_data("Traffic Flow", msg)
    # return NoContent, 201
    logger.info(f"Returned event traffic response (Id: {trace_id}) with status 201")
    return NoContent, 201

    

def reportIncident(body):
    trace_id = generate_trace_id()
    logger.info(f"Recieved event {app_config['accident']} request with a trace id of {trace_id})")

    # msg = {
    #     "msg_data": f"Confirmation incident for {body['id']}. Your camera ID: {body['cameraId']}",
    #     "received_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
    # }
    body['trace_id'] = trace_id

    #client = KafkaClient(hosts='acit3855-kafla.eastus2.cloudapp.azure.com:9092')
    #topic = client.topics[str.encode('events')]
    producer = topic.get_sync_producer()
    msg = { "type": "reportIncident", 
            "datetime" : 
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"), 
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
 
    #req = requests.post(app_config['accident']['url'], json=body, headers={'Content-Type': 'application/json'})
    # write_data("Incident report", msg)
    # return NoContent, 201
    logger.info(f"Returned event {app_config['accident']} response (Id: {trace_id}) with status 201")
    return NoContent, 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("trafficreport.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

