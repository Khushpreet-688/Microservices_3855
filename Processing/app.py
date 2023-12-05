import connexion
from connexion import NoContent, FlaskApp
import json
import datetime
import requests
import yaml
import logging, logging.config
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
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

def get_stats():
    """
    Get endpoint function. Retrieves stats entries for the JSON file.
    """
    logger.info('Request has started')
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)
        logger.debug(f'Contents of python dict {stats}')
        logger.info(f'Request has completed')
    except FileNotFoundError:
        logger.error('Statistics do not exist')
        return 'Statistics do not exist', 404
    return stats, 200

def populate_stats():
    """
    Function run periodically to calculate stats and update the JSON file
    """
    logger.info('Start Periodic Processing')
    current_datetime = datetime.datetime.now()
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        #use the default values for the stats 
        stats = {
            'num_clock_ins': 0,
            'num_clock_outs': 0,
            'avg_num_hours_worked': 8,
            'max_late_arrival': 0,
            # 'last_updated': current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            'last_updated': '2023-10-17T11:15:00.001Z'
        }
        with open(app_config['datastore']['filename'], 'w') as f:
            json.dump(stats, f, indent=4)

    current_timestamp = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    get_response_clock_in = requests.get(f"{app_config['eventstore']['url']}/reporting/clock-in", params={'start_timestamp': stats['last_updated'], 'end_timestamp': current_timestamp})
    get_response_clock_out = requests.get(f"{app_config['eventstore']['url']}/reporting/clock-out", params={'start_timestamp': stats['last_updated'], 'end_timestamp': current_timestamp})
    
    if get_response_clock_out.status_code == 200 and get_response_clock_out.status_code == 200:
        clock_in_events = get_response_clock_in.json()
        clock_out_events = get_response_clock_out.json()
        logger.info(f'Number of events received {len(clock_in_events) + len(clock_out_events)}')

        #Calculate updated statistics
        stats['num_clock_ins'] += len(clock_in_events)
        stats['num_clock_outs'] += len(clock_out_events)
        hours = stats['avg_num_hours_worked']
        for i in clock_out_events:
            hours += i['num_hours_worked']
            
        stats['avg_num_hours_worked'] = round(hours/(len(clock_out_events) + 1), 2)
        late_arrivals = [stats['max_late_arrival']]
        for i in clock_in_events:
            late_arrivals.append(i['late_arrival'])
        stats['max_late_arrival'] = max(late_arrivals)
        stats['last_updated'] = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        logger.debug(f'Updated statistics values: {stats}')
    else:
        logger.error("Failed to get any events from storage")
    #write them to json
    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(stats, f, indent=4)
    logger.info('Period processing has ended')

def get_health():
    return 200

def init_scheduler():
    sched=BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml", base_path="/processing", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, use_reloader=False)