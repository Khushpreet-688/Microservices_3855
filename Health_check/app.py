import connexion
from connexion import NoContent, FlaskApp
import json
import datetime
import requests
import yaml
import logging, logging.config
from apscheduler.schedulers.background import BackgroundScheduler


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

def get_health_status():
    logger.info('Request has started')
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            statuses = json.load(f)
        # logger.debug(f'Contents of python dict {statuses}')
        logger.info(f'Request has completed')
    except FileNotFoundError:
        logger.error('Health statuses of services do not exist')
        return 'Health statuses of services do not exist', 404
    
    return statuses, 200

def check_health():
    logger.info('Start Periodic Health Check of services')
    current_datetime = datetime.datetime.now()
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            health = json.load(f)
    except FileNotFoundError:
        #use the default values for the stats 
        health = {
            'receiver': 'Down',
            'storage': 'Down',
            'processing': 'Down',
            'audit_log': 'Down',
            # 'last_updated': current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            'last_updated': '2023-10-17T11:15:00.001Z'
        }
        with open(app_config['datastore']['filename'], 'w') as f:
            json.dump(health, f, indent=4)
    # update the service with current date and time
    services = ['receiver', 'storage', 'processing', 'audit_log']
    for service in services:
        res = requests.get(f"{app_config['eventstore']['url']}/{service}/health", timeout=4)
        logger.info(f'Status received from the {service}')
        if res.status_code == 200:
            health[service] = 'Running'
        else:
            health[service] = 'Down'
        logger.info(f'Status recorded')
    
    health['last_updated'] = current_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    logger.debug(f'Updated status values: {health}')
    #write them to json
    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(health, f, indent=4)
    
    logger.info('Finished Periodic health check')

def init_scheduler():
    sched=BackgroundScheduler(daemon=True)
    sched.add_job(check_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/health_check", strict_validation=True, validate_responses=True)
if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)


        