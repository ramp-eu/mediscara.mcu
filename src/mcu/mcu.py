import json
import logging
from datetime import datetime
import os
from time import sleep
from threading import Thread
from typing import Callable
from urllib import parse

from flask import Flask, make_response, request
from dotenv import load_dotenv
import requests

# import communication

logging.getLogger("werkzeug").disabled = True  # disable flask logger

# create Flask app instance
app = Flask(__name__)

# load the environment variables from .env
load_dotenv()

# get environment variables
API_KEY = os.getenv('API_KEY')
FIWARE_SERVICE = os.getenv('FIWARE_SERVICE')
FIWARE_SERVICEPATH = os.getenv("FIWARE_SERVICEPATH")
MCU_ID = os.getenv('MCU_ID')
IOTA_URL = os.getenv('IOTA_URL')
IOTA_PATH = os.getenv('IOTA_PATH')

JOB_SELECT = 'job_select'
MEASURE_PCB = 'measure_pcb'
MEASURE_LABEL = 'measure_label'

@app.route('/api', methods=["GET", "POST"])
def api():
    """Main entry point for the MCU api requests"""

    data_json = json.loads(request.data)
    keys = data_json.keys()

    logging.info("Incoming %s: %s", request.method, data_json)

    if request.method == "GET":
        return make_response(json.dumps({'job_select': 'OK'}), 200)

    elif request.method == "POST":
        if JOB_SELECT in keys:
            selected_job = data_json[JOB_SELECT]
            return make_response(json.dumps({JOB_SELECT: f'selected: {selected_job} OK'}), 200)

        elif MEASURE_PCB in keys:
            thread_started =  manage_threads(target=measure_pcb)

            if thread_started:
                return make_response(json.dumps({MEASURE_PCB: "RECEIVED"}), 200)

            return make_response(json.dumps({MEASURE_PCB: 'BUSY'}), 200)

        elif MEASURE_LABEL in keys:
            thread_started =  manage_threads(target=measure_label)

            if thread_started:
                return make_response(json.dumps({MEASURE_LABEL: "RECEIVED"}), 200)

            return make_response(json.dumps({MEASURE_LABEL: 'BUSY'}), 200)

        return make_response(json.dumps({'job_select': 'BAD_COMMAND'}), 400)

def manage_threads(target: Callable):
    if hasattr(manage_threads, "current_task"):
        # return false if it is still running
        if isinstance(manage_threads.current_task, Thread) and manage_threads.current_task.is_alive():
            return False

    manage_threads.current_task = Thread(target=target, daemon=True)
    manage_threads.current_task.start()

    return True

manage_threads.current_task = None

def measure_label() -> bool:
    logging.warning("Implement %s correctly", measure_label.__name__)
    sleep(5)
    update_attribute(f'{measure_label.__name__}_info', info="OK")

def measure_pcb() -> bool:
    logging.warning("Implement %s correctly", measure_pcb.__name__)
    sleep(5)
    update_attribute(f'{measure_pcb.__name__}_info', info="OK")

def update_attribute(attribute: str, info: str):
    """Send a post request updating the given attribute"""
    response = requests.post(f'{IOTA_URL}/{IOTA_PATH}',
                             headers={
                                 'fiware-service': FIWARE_SERVICE,
                                 'fiware-servicepath': FIWARE_SERVICEPATH,
                                 'Content-Type': 'application/json',
                             },
                             params={
                                'k': API_KEY,
                                'i': MCU_ID
                             },
                             json={
                                 attribute: info
                             })

    if response.status_code != 200:
        logging.warning(
            "Could not update attribute '%s': (%s) %s",
            attribute,
            response.status_code,
            response.content.decode('utf-8')
            )