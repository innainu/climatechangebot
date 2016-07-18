
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

### DigitalOcean Notes

- Create a Droplet
- Set up non-root user: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-14-04
- Other settings: https://www.digitalocean.com/community/tutorials/additional-recommended-steps-for-new-ubuntu-14-04-servers
- Clone the repository into home directory
- Install Ansible
    - ```ansible/install.sh```
- Copy config to remote
    - ```scp local.cfg user@remote:climatechangebot/climatechangebot```
- Create SSL: https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-14-04
    - https://certbot.eff.org/#ubuntutrusty-nginx
    - Set SSL to renew automatically:
        - `sudo crontab -e`
        - ```0 0 1 * * ./certbot-auto renew --quiet --no-self-upgrade```
- Run Ansible Playbook
    - ```ansible-playbook -c local ansible/prod.yml```
- Run nosetests
- Logs
    - `tail -f /var/log/gunicorn/gunicorn-error.log`
    


## To do:

1. Build RiveScripts
2. Notify about errors on prod
3. Refactor
4. Install better mongo Ansible role: https://galaxy.ansible.com/greendayonfire/mongodb/ and configure with DigitalOcean
