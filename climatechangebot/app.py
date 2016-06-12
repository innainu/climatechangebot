#!/usr/bin/env python
from flask import Flask, request

app = Flask(__name__)

app.config.from_object("config.DevelopmentConfig")
app.config.from_pyfile("local.cfg")


@app.route("/")
def index():
    return "Hello world from Climatechangebot!"


@app.route("/webhook/" + app.config['FB_WEBHOOK_URL'], methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        if (request.args.get("hub.verify_token") == app.config['FB_VERIFY_TOKEN']):
            return request.args.get("hub.challenge")

    # if request.method == 'POST':
    #     output = request.json
    #     event = output['entry'][0]['messaging']
    #     for x in event:
    #         if (x.get('message') and x['message'].get('text')):
    #             message = x['message']['text']
    #             recipient_id = x['sender']['id']
    #             bot.send_text_message(recipient_id, message)
    #         else:
    #             pass
    #     return "success"
    return 'success'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
