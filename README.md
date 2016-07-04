
# climatechangebot

Vagrant and ansible playbook taken from:
https://github.com/paste/fvang



## To run app:

> vagrant provision
> ngrok http -host-header=rewrite 192.168.33.11:80
> python app.py

Wit.ai:

Intents:
- greeting
- search_articles
- search_photos
- conversational
    - Is climate change real?
    - You bet it is.
- insult