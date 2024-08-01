
import os
import logging
import json
import requests

from resources.api_energyzero import EnergieZero_API
from resources.api_entsoe import Entsoe_API
from resources.api_frankenergie import FrankEnergie_API
from resources.api_nordpool import NordPool_API
from resources.api_easyenergy import EasyEnergy_API

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Prices:
    gas_leveranciers = ["FrankEnergie", "EnergieZero", "EasyEnergy"]
    electra_leveranciers = ["Nordpool", "EnergieZero", "FrankEnergie"]

    @staticmethod
    def process_gas(leverancier:str="")->list:
        try:
            #stroom = 1, gas = 2
            kind = 2 #gas
            match leverancier:
                case "EasyEnergy":
                    return EasyEnergy_API().get_data(kind=kind) # Gas ophalen bij EasyEnergy
                case "EnergieZero":
                    return EnergieZero_API().get_data(kind=kind) #gas ophalen bij ernergyzero
                case "FrankEnergie":
                    return FrankEnergie_API().get_data(kind=kind) # Gas ophalen bij Frank
                case _:
                    return []
        except Exception as e:
            log.error(e, exc_info=True)
            return []

    @staticmethod
    def prepare_gas(data:dict={})->dict:
        try:
            days = {}
            for d in data:
                if d['fromtime'] == "23:00":
                    days[d['fromdate']] = d["price"]

            for index, key in enumerate(data):
                try:
                    data[index]['price'] = days[data[index]['fromdate']]
                except KeyError:
                    pass

            return data
        except (Exception, KeyError)  as e:
            log.error(e, exc_info=True)
            return {}

    @staticmethod
    def process_electra(entsoe_key:str, country_code:str)->list:
        if country_code == "" or entsoe_key == "":
            return []

        data = None
        try:
            #stroom = 1, gas = 2
            # Electra ophalen bij entsoe
            if (data := Entsoe_API().get_day_ahead_prices_data(entsoe_key=entsoe_key, country_code=country_code)):
                return data

            return []
        except Exception as e:
            log.error(e, exc_info=True)
            return []

    @staticmethod
    def process_electra_fallback(leverancier:str="")->list:
        try:
            kind = 1 #stroom
            match leverancier:
                case "Nordpool":
                    return NordPool_API().get_data(kind=kind) # Electra ophalen bij Nordpool
                case "EnergieZero":
                    return EnergieZero_API().get_data(kind=kind) #Electra ophalen bij ernergyzero
                case "FrankEnergie":
                    return FrankEnergie_API().get_data(kind=kind) # Electra ophalen bij Frank
                case _:
                    return []
        except Exception as e:
            log.error(e, exc_info=True)
            return []

    @staticmethod
    def set_price(bearer_key:str, ip:str , port:str, fromdate:str, fromtime:str, kind:str, price:float, country_code:str="NL")->bool:
        try:
            payload = json.dumps({"fromdate": fromdate, "fromtime": fromtime, "kind": kind, "price": price, "country": country_code})
            reqUrl = f"http://{ip}:{port}/energy/api/v1.0/prices"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_key}"
            }
            response = requests.request("PUT", reqUrl, data=payload, headers=headersList, timeout=2)
            if response.status_code == 201:
                return True

            return False
        except Exception as e:
            log.critical(e, exc_info=True)
            return False
