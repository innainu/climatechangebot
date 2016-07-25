
# climatechangebot

Vagrant and ansible playbook taken from:
https://github.com/paste/fvang


## To run app:

```
$ vagrant provision
$ ngrok http -host-header=rewrite 192.168.33.11:80
$ python app.py
```
Visit the page on localhost or using ngrok. Add testing webhook to Facebook webhooks.

## Connect to db example:

Tutorial: https://api.mongodb.com/python/current/tutorial.html

```
from pymongo import MongoClient
client = MongoClient()
client.database_names()
mongo = client.app
mongo.db.users.find_one()
```

### DigitalOcean Release Notes

- Create a Droplet
- Set up non-root user: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-14-04
- Other settings: https://www.digitalocean.com/community/tutorials/additional-recommended-steps-for-new-ubuntu-14-04-servers and https://www.digitalocean.com/community/tutorials/how-to-protect-an-nginx-server-with-fail2ban-on-ubuntu-14-04
- Clone the repository into home directory
- Install Ansible
    - `ansible/install.sh`
- Copy config to remote
    - `scp local.cfg user@remote:climatechangebot/climatechangebot`
- Create SSL: https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04
- Run Ansible Playbook
    - `sudo ansible-playbook -c local ansible/prod.yml`
- `python -m textblob.download_corpora`
- Run nosetests
- Logs
    - `tail -f /var/log/gunicorn/gunicorn-error.log`

## To do:

1. Continuous rive improvement
2. Email notification about errors on prod
3. Code refactor
4. Install better mongo Ansible role: https://galaxy.ansible.com/greendayonfire/mongodb/
