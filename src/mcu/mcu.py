"""Module to implement a flask web server with the custom commands defined in the
'external' directory"""
import json
import logging
import os
import sys
from dotenv import load_dotenv

from flask import Flask, make_response, request

from .models.command import Command
from .config import SERIAL_CONNECTIONS, TCP_CONNECTIONS, report_error
from mcu import config

logging.getLogger("werkzeug").disabled = True  # disable flask logger

# load the environment variables from .env
load_dotenv()

HOST = os.getenv('HOST')
PORT = os.getenv('PORT')

if HOST is None or PORT is None:
    logging.fatal("Please set the HOST and PORT environment variables")
    sys.exit(1)

# create Flask app instance
app = Flask(__name__)

# Load the command class instances
COMMANDS = Command.load_commands()

@app.route('/api', methods=["GET", "POST"])
def api():
    """Main entry point for the MCU api requests"""

    data_json = json.loads(request.data)
    keys = data_json.keys()

    logging.info("Incoming %s: %s", request.method, data_json)

    if request.method == "GET":
        return make_response(json.dumps({'': 'BAD REQUEST'}), 400)

    if request.method == "POST":
        for command in COMMANDS:
            if command.keyword in keys:
                if command.running:
                    return make_response(json.dumps({command.keyword: 'BUSY'}), 503)

                args = data_json[command.keyword]  # get the value for the key

                command.execute(args)
                return make_response(json.dumps({command.keyword: 'RECEIVED'}), 200)

    return make_response(json.dumps({'': 'BAD_COMMAND'}), 400)


def main():
    """Main entrypoint and setup method for the flask app"""

    # initialize the connections
    for value in TCP_CONNECTIONS:
        value.start()

    for value in SERIAL_CONNECTIONS:
        value.start()

    config.clear_errors()  # clear the errors

    app.run(host=HOST, port=PORT)
