#!/usr/bin/env python
from flask import Flask, request
from flask import jsonify

from bot_interface.bot_interface import NotificationType, RecipientMethod, BotInterface

import requests

app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
app.config.from_pyfile("local.cfg")


FB_MESSAGING_URL = (
    "https://graph.facebook.com"
    "/v{0}/me/messages?access_token={1}"
).format(app.config['FB_API_VERSION'], app.config['FB_ACCESS_TOKEN'])

bot = BotInterface(FB_MESSAGING_URL)

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

        print(messages)
        for entry in messages['entry']:
            for m in entry['messaging']:
                if m.get('message') and m['message'].get('text'):
                    message = m['message']['text']
                    recipient_id = m['sender']['id']

                    response = bot.send_text_message(recipient_id, message,
                                    RecipientMethod.ID.value, NotificationType.REGULAR.value)

                    return success(response.status_code)
                else:
                    pass

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
