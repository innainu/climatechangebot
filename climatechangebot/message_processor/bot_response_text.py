"""
    Some generic text that the bot will return

"""

help_button_title = (
    u"Sorry I'm too busy worrying about climate change \U0001f30e, "
    u"I missed what you were saying. If you need help worrying about"
    u" climate change too, click HELP below!"
)

help_postback_text = [
    (
        u"I'm still learning, but what I can do now is: \n \u2022 Search for an article "
        u"when you type something like 'show me articles about fish'. I can also search on keywords "
        u"like if you type 'ice caps' \n"
    ),
    (
        u"\u2022 Have a simple conversation with you; for example ask me: 'what is my name?' \n"
        u"\u2022 I can give you the latest scoop on climate change, just type 'trending' or 'latest' \n"
        u"That's all folks! \U0001f389"
    )
]


# Welcome messages for when a user starts chatting with climatechangebot
#   the first welcome_message is a template
#   the rest of the welcome_messages are plain text
welcome_messages_new_user = [
    {
        "type": "template",
        "payload": {
            "template_type": "generic",
            "elements": [
                {
                    "title": "Welcome to the climatechangebot thread!",
                    "item_url": "https://www.facebook.com/climatechangebot/",
                    "image_url": "https://scontent-lga3-1.xx.fbcdn.net/t31.0-8/13422214_852984424805822_3203580027459777074_o.jpg",
                    "subtitle": "Stay informed about climate change so that we can make a difference!",
                }
            ]
        }
    },
    (
        u"Hey there! You can search for an article "
        u"when you type something like 'show me articles about fish'"
    ),
    u"I also like having simple conversations for example ask me: 'what is my name?'",
    u"I hope you enjoying chatting with me about climate change!"
]

# If we've seen this user before, the welcome message should reference their name
welcome_back = "Welcome back %s!"
