#!/usr/bin/env python
from flask import Flask

app = Flask(__name__)

app.config.from_object('config.DevelopmentConfig')
app.config.from_pyfile('local.cfg')


@app.route("/")
def index():
    return "Hello world from Climatechangebot!"

# @app.route("/webhook", methods = ['GET', 'POST'])
# def hello():
#     if request.method == 'GET':
#         if (request.args.get("hub.verify_token") == "<token you define during"\
#                 "the verification phase>"):
#                 return request.args.get("hub.challenge")
#     if request.method == 'POST':
#         output = request.json
#         event = output['entry'][0]['messaging']
#         for x in event:
#             if (x.get('message') and x['message'].get('text')):
#                 message = x['message']['text']
#                 recipient_id = x['sender']['id']
#                 bot.send_text_message(recipient_id, message)
#             else:
#                 pass
#         return "success"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
