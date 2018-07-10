# MiningStats - ETH Mining Monitoring

A simple Python 3/Django app for monitoring of Ethereum mining rigs. Currently supports only Claymore miner >= V10.

## Features

* Real-time dashboard of multiple mining rigs
* Tracking of hashrate and temperatures per rig or per graphics card
* Historical charts
* Responsive
* Low requirements (can run on a Raspberry Pi, for example)
* Works offline (no external JS/CSS used)

## Getting Started

### Requirements

You'll need PostgreSQL, Python 3 and pip:

```
sudo apt install postgresql python3 python3-pip
```

### Clone repository and install dependencies 

***note:** you may want to use a [virtualenv](https://virtualenv.pypa.io/en/stable/)*

```
git clone https://github.com/bitmario/mining-stats
cd mining-stats
pip3 install -r requirements.txt
```

### Environment variables to set

* MS_SECRET_KEY *(use a secret and random value such as a UUID)*
* MS_DB_HOST
* MS_DB_PORT
* MS_DB_NAME
* MS_DB_USER
* MS_DB_PASSWORD
* MS_TZ *(optional, defaults to Etc/UTC)*

### Run migrations and create admin user

```
python3 manage.py migrate
python3 manage.py createsuperuser
```

### Schedule data collection

Add a line to your cron (`crontab -e`), e.g.:

```
*/1 * * * *    python3 /home/user/mining-stats/manage.py runcrons >> /home/user/miningstats_cron.log
```

### Run the server

```
python3 manage.py runserver 0.0.0.0:8000
```

You should now be able to access the server at *http://YOUR_IP:8000*, cool!

At this point you should seriously consider setting up [gunicorn and nginx](http://docs.gunicorn.org/en/stable/deploy.html) if this machine is accessible outside a very restricted LAN! Otherwise, you can just run this on boot.

### Configure options and rigs

1. Access the MiningStats server and log in with the superuser account that you created
2. Click the *Admin* link on the page header
3. Select *Site configuration* under *App*
4. Set the desired options and click on *Save*
5. Select *Rigs*, under *App* and click on *Add Rig* in the upper right corner
6. Enter the rig information and save

### Done!

MiningStats will now collect information from your rigs every minute, and provide real-time and historical insights.

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## Authors

* **Mario Falcao** - *Initial work* - [bitmario](https://github.com/bitmario)

See also the list of [contributors](https://github.com/bitmario/mining-stats/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
