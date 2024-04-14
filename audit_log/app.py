import time
from datetime import datetime 
import json
import connexion
from connexion import NoContent
from flask import Flask, request, jsonify
from os import path
import os
# from models_mysql import TrafficFlow, IncidentReport, Base
# import db_mysql 
import yaml
import logging
import logging.config
from sqlalchemy import and_
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware

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

def get_traffic_reading(index):
    """ Get BP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving Traffic at index %d" % index)

    try:
        indx = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'TrafficFlow':
                if indx == index:
                    return msg, 200
                else:
                    indx +=1
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find Traffic at index %d" % index)
    return {"message": "Not Found"}, 404


def get_incident_reading(index):
    """ Get BP Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Here we reset the offset on start so that we retrieve
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving BP at index %d" % index)

    try:
        indx = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            logger.info("Message: %s" % msg)
            if msg['type'] == 'reportIncident':
                if indx == index:
                    return msg, 200
                else:
                    indx +=1
            # incident_number = int(msg['IncidentNumber'])
            # if incident_number == index:
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find BP at index %d" % index)
    return {"message": "Not Found"}, 404



app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    app.add_middleware(CORSMiddleware,position=MiddlewarePosition.BEFORE_EXCEPTION,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_api("trafficreport.yaml", base_path="/audit", strict_validation=True, validate_responses=True)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8110)


