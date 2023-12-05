import json
import datetime
import requests
import yaml
import logging, logging.config
import uuid
from pykafka import KafkaClient
import time
import connexion
from connexion import NoContent
# Your functions here

MAX_EVENTS = 10
EVENT_FILE = './events.json'

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

max_retries = app_config["connection"]["max_retries"]
sleep_time = app_config["connection"]["sleep_time"]
retry_count = 0

while retry_count < max_retries: 
    try:
        logger.info(f'Trying to reconnect to Kafka. Retry count: {retry_count}')
        client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
        TOPIC = client.topics[str.encode(app_config["events"]["topic"])]
        producer = TOPIC.get_sync_producer()
        logger.info("Connected!")
        break
    except:
        logger.error("Connection failed. Retrying ...")
        time.sleep(sleep_time)
        retry_count += 1

def clock_in(body):
    """
    Receives clock-in post request and produces a message in Kafka producer stream.
    """
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    event = "clock in"
    logger.info(f"Received event {event} request with a trace id of {trace_id}")
    headers = { "content-type": "application/json"}
    # response = requests.post(app_config['eventstore1']['url'], json=body, headers=headers)
    # client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    # producer = TOPIC.get_sync_producer()
    msg = { "type": "clock_in",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event {event} response {trace_id} with status 201")
    return NoContent, 201

def clock_out(body):
    """
    Receives clock-out post request and produces a message in Kafka producer stream.
    """
    trace_id = str(uuid.uuid4())
    body['trace_id'] = trace_id
    event = "clock out"
    logger.info(f"Received event {event} request with a trace id of {trace_id}")
    headers = { "content-type": "application/json"}
    # response = requests.post(app_config['eventstore2']['url'], json=body, headers=headers)
    # if response.status_code == 201:
    #     print(response)
    # client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    # topic = client.topics[str.encode(app_config["events"]["topic"])]
    # producer = TOPIC.get_sync_producer()
    msg = { "type": "clock_out",
            "datetime" : datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    logger.info(f"Returned event {event} response {trace_id} with status 201")
    return NoContent, 201

def log_events(body, data_str):
    with open(EVENT_FILE, 'r') as f:
        que = json.loads(f.read())
    current_datetime = datetime.datetime.now()
    curr_datetime_str = current_datetime.strftime(f"%Y-%m-%d %H:%M:%S")
    data_obj = {
        "received_timestamp": curr_datetime_str,
        "request_data": data_str
    }
    que.insert(0, data_obj)
    if len(que) > MAX_EVENTS:
        que.pop()
    #can also use que[:10] to just load top ten entries to the file
    with open(EVENT_FILE, 'w') as f:
        json_obj = json.dumps(que, indent=4)
        f.write(json_obj)

def get_health():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    app.run(port=8080)
    

    