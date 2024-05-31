# Class Drop Notifier
A Python script that will notify you via email when a specific class from your wishlist is open. It periodically checks the course status every 5 minutes until it becomes open. \
Note: Due to cookie expiration and 2FA, the script needs to be restarted and authenticated after 12 hours, so the process is only _semi_-automated

## Installation
* Clone the repository

```git clone https://github.com/Junqor/FresnoState-ClassDropNotifier.git```

* (Optional) [Setup a virtual environment](https://docs.python.org/3/library/venv.html)

* Install requirements

```pip install -r requirements.txt```

## Customization
Make sure you add your sign-in information as well as your email credentials before running so that it works correctly. Change the [course target](https://github.com/Junqor/FresnoState-ClassDropNotifier/blame/347002cadc82e6475745a25b756c93d579f9e44b/main.py#L106) based on your needs. You can change how often it checks the course status by modifying the sleep time.
