"""
Gets entities from wit.ai

- each entity gets a confidence value from 0 to 1. do something with this?
    "1 is extremely confident. Lower than 0.5 is considered very low confidence."

- can add intents using api:
https://wit.ai/docs/http/20160330#get-intent-via-text-link
"""

from wit import Wit


#gets message text from message_processor
#and sends to wit.ai

#i can't call wit.ai without specifying some "actions"


class ParsedMessage():
    def __init__(self, text, entities, intent):
        self.text = text
        self.entities = entities
        self.intent = intent


class WitParser(object):
    def __init__(self, key, nyt_api):
        #define actions
        self.actions = {}
        self.client = Wit(access_token=key, actions=self.actions)
        self.NYT_API = nyt_api

    def parse_message(self, text):
        entities = []
        mess = self.client.message(text)
        mess_entities = mess['entities']

        if 'intent' in mess_entities:
            intent = (mess['entities']['intent'][0]['value'], mess['entities']['intent'][0]['confidence'])
        else:
            intent = None

        for ent in mess_entities['search_query']:
            entities.append((ent['value'], ent['confidence']))
        message = ParsedMessage(text, entities, intent)
        return message

    def action(self, message, num=1):
        if message.intent[0] == 'search_article' and message.intent[1] > 0.5:
            #take entitiy with highest confidence
            ent = sorted(message.entities, lambda x: x[1], reverse=True)[0]
            response = self.NYT_API.return_article_list(ent, num=num)
        else:
            response = "Cannot compute."
        return response
