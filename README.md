
# climatechangebot

Vagrant and ansible playbook taken from:
https://github.com/paste/fvang


## To run app:

```
$ vagrant provision
$ ngrok http -host-header=rewrite 192.168.33.11:80
$ python app.py
```

## Connect to db:

Tutorial: https://api.mongodb.com/python/current/tutorial.html

```
from pymongo import MongoClient
client = MongoClient()
client.database_names()
mongo = client.app
mongo.db.users.find_one()
```

## To do:

1. Write tests for User() and for DB read-writes
2. Build more RiveScripts
3. Push to prod
4. Consider installing better mongo Ansible role: https://galaxy.ansible.com/greendayonfire/mongodb/