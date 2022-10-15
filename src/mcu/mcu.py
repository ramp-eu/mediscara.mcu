"""Module to implement a flask web server with the custom commands defined in the
'external' directory"""
import json
import logging
import os
import sys
from typing import List
from dotenv import dotenv_values

from flask import Flask, make_response, request


from .models.user_defined import Service, load
from .config import SERIAL_CONNECTIONS, TCP_CONNECTIONS, clear_errors

logging.getLogger("werkzeug").disabled = True  # disable flask logger

# load the environment variables from .env
config = dotenv_values()

HOST = config["HOST"]
PORT = config["PORT"]


if HOST is None or PORT is None:
    logging.fatal("Please set the HOST and PORT environment variables")
    sys.exit(1)

# create Flask app instance
app = Flask(__name__)

# Load the command class instances
COMMANDS, SERVICES = load()


@app.route("/api", methods=["GET", "POST"])
def api():
    """Main entry point for the MCU api requests"""

    data_json = json.loads(request.data)
    keys = data_json.keys()  # type: List[str]

    if len(keys) != 1:
        error_msg = "Multiple commands got called"
        logging.error(error_msg)
        Service.update_attribute("error", info=error_msg)
        return make_response(json.dumps({"": "BAD REQUEST"}), 400)

    key = list(keys)[0]

    logging.info("Incoming %s: %s", request.method, data_json)

    if request.method == "GET":
        return make_response(json.dumps({"": "BAD REQUEST"}), 400)

    if request.method == "POST":
        for command in COMMANDS:
            matched = False

            if isinstance(command.keywords, str):
                if command.keywords == key:
                    matched = True

            # check if any of the command keywords are in the keys
            elif any(key in command.keywords for key in keys):
                matched = True

            # if a match is found run the command
            if matched:

                if command.running:
                    return make_response(json.dumps({key: "BUSY"}), 503)

                args = data_json[key]  # get the value for the key

                command.execute(args, keyword=key)
                return make_response(json.dumps({key: "RECEIVED"}), 200)

    return make_response(json.dumps({"": "BAD_COMMAND"}), 400)


def main():
    """Main entrypoint and setup method for the flask app"""

    # initialize the connections
    for value in TCP_CONNECTIONS:
        value.start()

    for value in SERIAL_CONNECTIONS:
        value.start()

    clear_errors()  # clear the errors

    app.run(host=HOST, port=PORT)
