import connexion
from connexion import NoContent
import json
import datetime
# Your functions here

from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker
from base import Base
from clock_in import ClockIn
from clock_out import ClockOut

import mysql.connector
import pymysql 
import yaml
import logging, logging.config

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import os
import time

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

MAX_EVENTS = 10
EVENT_FILE = './events.json'
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# get password from env variable defined in docker file
db_pass = os.environ.get(app_config["datastore"]["password"])
# DB_ENGINE = create_engine("sqlite:///records.sqlite")
DB_ENGINE = create_engine(f'mysql+pymysql://{app_config["datastore"]["user"]}:{app_config["datastore"]["password"]}@{app_config["datastore"]["hostname"]}:{app_config["datastore"]["port"]}/{app_config["datastore"]["db"]}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f'Connecting to DB. Hostname: {app_config["datastore"]["hostname"]}, Port: {app_config["datastore"]["port"]}')

def clock_in(body):
    """ Receives a clock in reading """

    session = DB_SESSION()
    event = 'Clock in'


    bp = ClockIn(body['trace_id'],
                       body['emp_num'],
                       body['emp_name'],
                       body['store_code'],
                       body['timestamp'],
                       body['num_hours_scheduled'],
                       body['late_arrival'])

    session.add(bp)

    session.commit()
    session.close()
    logger.debug(f'Stored event {event} request with the trace id of {body["trace_id"]}')
    return NoContent, 201


def clock_out(body):
    """ Receives a clock out reading """

    session = DB_SESSION()
    event = "Clock out"
    
    bp = ClockOut(body['trace_id'],
                       body['emp_num'],
                       body['emp_name'],
                       body['store_code'],
                       body['timestamp'],
                       body['num_hours_worked'],
                       body['overtime_hours'])

    session.add(bp)

    session.commit()
    session.close()
    logger.debug(f'Stored event {event} request with the trace id of {body["trace_id"]}')
    return NoContent, 201

def get_clock_in_readings(start_timestamp, end_timestamp):
    """
    Gets new clock in readings after the timestamp
    """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    readings = session.query(ClockIn).filter(and_(ClockIn.date_created >= start_timestamp_datetime, ClockIn.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info(f"Query for Clock in readings after {start_timestamp} returns {len(results_list)} results")
    return results_list, 200

def get_clock_out_readings(start_timestamp, end_timestamp):
    """
    Gets new clock out readings after the timestamp
    """
    session = DB_SESSION()
    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    readings = session.query(ClockOut).filter(and_(ClockOut.date_created >= start_timestamp_datetime, ClockOut.date_created < end_timestamp_datetime))
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    session.close()
    logger.info(f"Query for Clock out readings after {start_timestamp} returns {len(results_list)} results")
    return results_list, 200

def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
    app_config["events"]["port"])
    
    max_retries = app_config["connection"]["max_retries"]
    sleep_time = app_config["connection"]["sleep_time"]
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f'Trying to reconnect to Kafka. Retry count: {retry_count}')
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            break
        except:
            logger.error("Connection failed. Retrying ...")
            time.sleep(sleep_time)
            retry_count += 1

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
    reset_offset_on_start=False,
    auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        if msg["type"] == "clock_in": # Change this to your event type
            # Store the event1 (i.e., the payload) to the DB
            clock_in(payload)
            logger.info("Clock in event stored successfully")
        elif msg["type"] == "clock_out": # Change this to your event type
            # Store the event2 (i.e., the payload) to the DB
            clock_out(payload)
            logger.info("Clock out event stored successfully")
        # Commit the new message as being read
        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
    