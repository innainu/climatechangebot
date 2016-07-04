#!/usr/bin/env python
from flask import Flask, request
from flask import jsonify

from bot_interface.bot_interface import BotInterface
from message_processor.message_processor import WitParser, MessageProcessor
from nyt_interface.nyt_interface import NytimesApi


app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
app.config.from_pyfile("local.cfg")

bot = BotInterface(app.config['FB_API_VERSION'], app.config['FB_ACCESS_TOKEN'])
nyt_api = NytimesApi(app.config['NYT_KEY'])
wit = WitParser(app.config['WIT_KEY'], bot, nyt_api)
msgproc = MessageProcessor(bot, wit, app.config)


@app.route("/")
def index():
    return success(status=200, message="Hello world from climatechangebot!")


@app.route("/webhook/" + app.config['FB_WEBHOOK_URL'], methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == app.config['FB_VERIFY_TOKEN']):
            return request.args.get("hub.challenge")
        else:
            return not_found(404)

    if request.method == 'POST':
        messages = request.json

        response = msgproc.parse_messages(messages)

        print('Sent a message')
        print(response)

        return success(200)


@app.errorhandler(404)
def not_found(error):
    return jsonify(response={'success': False},
                   status=404,
                   message="Not Found")


def success(status=200, message=''):
    return jsonify(response={'success': True},
                   status=status,
                   mimetype="application/json",
                   message=message)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
