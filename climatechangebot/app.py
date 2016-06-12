#!/usr/bin/env python
from flask import Flask, request
from flask import jsonify

import requests

app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
app.config.from_pyfile("local.cfg")


FB_MESSAGING_URL = (
    "https://graph.facebook.com"
    "/v{0}/me/messages?access_token={1}"
).format(app.config['FB_API_VERSION'], app.config['FB_ACCESS_TOKEN'])

# @app.route("/")
# def index():
#     return "Hello world from Climatechangebot!"


@app.route("/webhook/" + app.config['FB_WEBHOOK_URL'], methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == app.config['FB_VERIFY_TOKEN']):
            return request.args.get("hub.challenge")
        else:
            not_found()

    if request.method == 'POST':
        messages = request.json

        print(messages)
        for entry in messages['entry']:
            for m in entry['messaging']:
                if m.get('message') and m['message'].get('text'):
                    message = m['message']['text']
                    recipient_id = m['sender']['id']

                    # Send back the text message
                    payload = {
                        'recipient': {
                            'id': recipient_id
                        },
                        'message': {
                            'text': message
                        }
                    }

                    status = requests.post(FB_MESSAGING_URL,
                                           headers={"Content-Type": "application/json"},
                                           json=payload)

                    return success(status.status_code)
                else:
                    pass

        return success(200)


@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)

    return resp


def success(status=200):
    return jsonify(response={'success': True}, status=status, mimetype="application/json")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
