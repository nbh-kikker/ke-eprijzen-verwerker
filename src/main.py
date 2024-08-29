import os
import sys
import json
import yaml
import requests
import hashlib
from time import sleep
from datetime import datetime

import logging
import logging.config

from apscheduler.schedulers.blocking import BlockingScheduler

from resources.generation import Generation
from resources.prices import Prices

os.environ['TZ'] = 'Europe/Amsterdam'

dir_path = os.path.dirname(os.path.realpath(__file__))
log_folder = os.path.join(dir_path, 'logging')
config_folder = os.path.join(dir_path, 'config')

os.makedirs(log_folder, exist_ok=True)

logging.config.fileConfig(os.path.join(config_folder, 'logging.conf'))

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

config_filename = ""

match PY_ENV:
    case 'dev':
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        config_filename = "development.yml"
    case 'acc':
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        config_filename = "acceptance.yml"
    case 'prod':
        logger = logging.getLogger()
        logger.setLevel(logging.ERROR)
        config_filename = "production.yml"
    case _:
        pass

def check_file(file:str = "")->bool:
    if os.path.exists(file):
        return True
    return False

try:
    config_file = os.path.join(config_folder, config_filename)
    if not check_file(file=config_file):
        raise Exception('Config file not found')
except Exception as e:
    log.critical(e, exc_info=True)
    sys.exit()

config = {}
try:
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
except Exception as e:
    log.critical(e, exc_info=True)
    sys.exit()

ip = config["API"]["ip"]
port = config["API"]["port"]

def proces_leveranciers():
    password = get_password(password=config["login"]["password"], salt=config["login"]["salt"])
    bearer_key = get_bearer_key(password=password)

    if bearer_key is None:
        log.error('No bearer key!!, is there a connection?')
        return False

    vandaag_ts = datetime.now()
    vandaag = vandaag_ts.strftime("%Y-%m-%d")

def proces_prices():
    password = get_password(password=config["login"]["password"], salt=config["login"]["salt"])
    bearer_key = get_bearer_key(password=password)

    now = datetime.now()
    cur_hour = int(now.strftime("%H"))

    if bearer_key is None:
        log.error('No bearer key!!, is there a connection?')
        return False

    countries = get_countries(bearer_key=bearer_key)

    # GENERATORS
    try:
        if (solar_wind := Generation.get_wind_and_solar_forecast(entsoe_key=config["entsoe"]["key"], country_code="NL")):

            for g in Generation.generators:
                for sw in solar_wind[g]:
                    Generation.set_generation(bearer_key=bearer_key, ip=ip , port=port, fromdate=sw['fromdate'], fromtime=sw['fromtime'], kind=sw['kind'], mw=sw['mw'], country_code="NL")

    except Exception as e:
        log.critical(e, exc_info=True)

    # PRICING
    for leverancier in Prices.gas_leveranciers:
        try:
            if(gas_prices := Prices.process_gas(leverancier=leverancier)):
                if(gas_prices := Prices.prepare_gas(data=gas_prices)):
                    for price in gas_prices:
                        Prices.set_price(bearer_key=bearer_key, ip=ip , port=port, fromdate=price['fromdate'], fromtime=price['fromtime'], kind=price['kind'], price=price['price'])
            price = None
        except Exception as e:
            log.critical(e, exc_info=True)

    try:
        for country in countries['data']:
            if (power_prices := Prices.process_electra(entsoe_key=config["entsoe"]["key"], country_code=country['country_id'])):
                for price in power_prices:
                    Prices.set_price(bearer_key=bearer_key, ip=ip , port=port, fromdate=price['fromdate'], fromtime=price['fromtime'], kind=price['kind'], price=price['price'], country_code=country['country_id'])

            if cur_hour == 14:
                if country['country_id']=="NL":
                    power_prices = Prices.process_electra_fallback(leverancier="Nordpool")
                    if power_prices:
                        for price in power_prices:
                            Prices.set_price(bearer_key=bearer_key, ip=ip , port=port, fromdate=price['fromdate'], fromtime=price['fromtime'], kind=price['kind'], price=price['price'], country_code=country['country_id'])

            if cur_hour >= 16:
            # if power_prices and power_prices is not None and len(power_prices) < 36 and country['country_id']=="NL":
                if country['country_id']=="NL":
                    for leverancier in Prices.electra_leveranciers:
                        power_prices = Prices.process_electra_fallback(leverancier=leverancier)
                        if power_prices:
                            for price in power_prices:
                                Prices.set_price(bearer_key=bearer_key, ip=ip , port=port, fromdate=price['fromdate'], fromtime=price['fromtime'], kind=price['kind'], price=price['price'], country_code=country['country_id'])

            price = None
            sleep(2)
    except Exception as e:
        log.critical(e, exc_info=True)


def get_password(password:str="", salt:str="")->str:
    try:
        if password is None or salt is None:
            raise Exception('Geen wachtwoord of salt?')

        # Adding salt at the last of the password
        salted_password = password+salt
        # Encoding the password
        hashed_password = hashlib.md5(salted_password.encode())

        return hashed_password.hexdigest()
    except Exception as e:
        log.critical(e, exc_info=True)
        return ""

def get_bearer_key(password:str=""):
    try:
        payload = json.dumps({"email": config["login"]["email"], "password": password})
        reqUrl = f"http://{ip}:{port}/energy/api/v1.0/login"
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json"
        }
        response = requests.request("POST", reqUrl, data=payload,  headers=headersList, timeout=2)
        if response.status_code == 200:
            mjson = response.json()
            return mjson['access_token']
        return None
    except Exception as e:
        log.critical(e, exc_info=True)
        return None

def get_countries(bearer_key:str="")->dict:
    try:
        reqUrl = f"http://{ip}:{port}/energy/api/v1.0/countries"
        headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_key}"
        }
        response = requests.request("GET", reqUrl,  headers=headersList, timeout=2)
        if response.status_code == 200:
            return response.json()

        return {}
    except Exception as e:
        log.critical(e, exc_info=True)
        return {}

if __name__ == "__main__":
    # verwerk direct bij opstart op dev en acc
    if PY_ENV != 'prod':
        # proces_leveranciers()
        proces_prices()
    else:
        # daarna start uur interval
        scheduler = BlockingScheduler()
        scheduler.add_job(proces_prices, trigger='cron', hour='5, 6, 7, 12, 13, 14, 15, 16, 17, 20, 22', minute='50', timezone='Europe/Amsterdam')
        # scheduler.add_job(proces_leveranciers, trigger='cron', hour='4', timezone='Europe/Amsterdam')
        scheduler.start()
