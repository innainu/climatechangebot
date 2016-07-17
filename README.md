
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

### DigitalOcean

- Set up non-root user: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-14-04
- Other settings: https://www.digitalocean.com/community/tutorials/additional-recommended-steps-for-new-ubuntu-14-04-servers
- Install Ansible
    - ```ansible/install.sh```
- Copy config to remote
    - ```scp local.cfg user@remote:climatechangebot/climatechangebot```
- Create SSL: https://www.digitalocean.com/community/tutorials/how-to-create-a-self-signed-ssl-certificate-for-nginx-in-ubuntu-16-04
- Run Ansible Playbook
    - ```ansible-playbook -c local ansible/prod.yml```

## To do:

1. Build more RiveScripts
2. Push to production server
3. Refactor code
4. Install better mongo Ansible role: https://galaxy.ansible.com/greendayonfire/mongodb/ and configure with DigitalOcean
