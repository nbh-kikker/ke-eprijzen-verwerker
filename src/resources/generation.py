

import os
import logging
import json
import requests

from resources.api_entsoe import Entsoe_API

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Generation:
    generators = ['Solar', 'Wind Offshore', 'Wind Onshore']

    @staticmethod
    def get_wind_and_solar_forecast(entsoe_key:str = "", country_code:str="")->dict:
        if country_code is None or country_code == "":
            return {}

        data = None
        try:
            if (data := Entsoe_API().get_wind_and_solar_forecast(entsoe_key=entsoe_key, country_code=country_code)):
                return data

            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    @staticmethod
    def set_generation(bearer_key:str, ip:str, port:str, fromdate:str, fromtime:str, kind:str, mw:int, country_code:str="NL")->bool:
        try:
            payload = json.dumps({"fromdate": fromdate, "fromtime": fromtime, "kind": kind, "mw": mw, "country": country_code})
            reqUrl = f"http://{ip}:{port}/energy/api/v1.0/generation"
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
