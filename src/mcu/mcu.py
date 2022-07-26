"""Module to implement a flask web server with the custom commands defined in the
'external' directory"""
import json
import logging

from flask import Flask, make_response, request

from .models.command import Command
from .connectors.tcp import TCPServer

logging.getLogger("werkzeug").disabled = True  # disable flask logger

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
        return make_response(json.dumps({'job_select': 'OK'}), 200)

    if request.method == "POST":
        for command in COMMANDS:
            if command.keyword in keys:
                if command.running:
                    return make_response(json.dumps({command.keyword: 'BUSY'}), 503)

                command.execute()
                return make_response(json.dumps({command.keyword: 'RECEIVED'}), 200)

    return make_response(json.dumps({'': 'BAD_COMMAND'}), 400)

def tcp_connection_made(peer: str):
    """Gets called when a new tcp connection is made"""
    logging.info("TCP Connection to: %s", peer)

def tcp_connection_lost():
    """Gets called when an existing tcp connection is lost"""
    logging.info("TCP Connection lost")

def tcp_received(msg: str):
    """Gets called when a tcp message is received"""
    logging.info("TCP Message: %s", msg)

# Start the TCP Server
TCPServer(connection_made_callback=tcp_connection_made,
          connection_lost_callback=tcp_connection_lost,
          data_received_callback=tcp_received,
          ).start()
