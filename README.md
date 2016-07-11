
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
> from pymongo import MongoClient
> client = MongoClient()
> client.database_names()
> db = client.app
> db.users.find_one()
```

## To do:

1. Consider installing better mongo Ansible role: https://galaxy.ansible.com/greendayonfire/mongodb/
2. Build more RiveScripts
3. Push to prod