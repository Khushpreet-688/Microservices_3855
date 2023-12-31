import connexion
from connexion import NoContent
import json
import datetime
import requests
import yaml
import logging, logging.config
import uuid
from pykafka import KafkaClient
from flask_cors import CORS, cross_origin

import os
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

def get_clock_in_reading(index):
    """ Get Clock in reading in history """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info(f"Retrieving Clock in reading at index {index}")
    i = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "clock_in":
                if i == index:
                    return msg, 200
                else:
                    i += 1
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
        return { "message": "Not Found" }, 404
    except:
        logger.error(f"Could not find clock in event at index {index}")
        return { "message": "Not Found" }, 404


def get_clock_out_reading(index):
    """ Get Clock out reading in history """
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]
    
    # messages at the beginning of the message queue.
    # To prevent the for loop from blocking, we set the timeout to
    # 100ms. There is a risk that this loop never stops if the
    # index is large and messages are constantly being received!

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
    consumer_timeout_ms=1000)
    logger.info(f"Retrieving Clock out reading at index {index}")
    i = 0
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg["type"] == "clock_out":
                if i == index:
                    return msg, 200
                else:
                    i += 1
            # Find the event at the index you want and
            # return code 200
            # i.e., return event, 200
        return { "message": "Not Found" }, 404
    except:
        logger.error(f"Could not find clock out event at index {index}")
        return { "message": "Not Found" }, 404

def get_health():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/audit_log", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8110)
