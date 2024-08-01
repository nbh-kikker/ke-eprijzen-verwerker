import os
from datetime import datetime, timedelta

from resources.api_general import get_timestamp
import requests

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class EasyEnergy_API:

    def __init__(self) -> None:
        pass

    def get_data(self, startdate:str = "", enddate:str = "", kind:int = 1)->list:
        try:
            if(api_data := self.__get_api_data(startdate=startdate, enddate=enddate, kind=kind)):
                if (data := self.__process_api_data(data=api_data, kind=kind, UTC=True)):
                    return data

            raise KeyError()
        except KeyError as e:
            log.warning(f"We did not get data from EnergyZero api : {e}")
            return []
        except Exception as e:
            log.error(e, exc_info=True)
            return []

    def __get_api_data(self, startdate:str = "", enddate:str = "", kind:int = 1)->dict:
        try:
            if startdate == "":
                yesterday_ts = datetime.now() + timedelta(days=-1)
                startdate = yesterday_ts.strftime("%Y-%m-%d")
            if enddate == "":
                tomorrow_ts = datetime.now() + timedelta(days=+1)
                enddate = tomorrow_ts.strftime("%Y-%m-%d")
            url = ""
            if kind == 1: #stroom
                pass
                # zeer afwijkende getallen
                # url = f"https://mijn.easyenergy.com/nl/api/tariff/getlebatariffs?startTimestamp={startdate}T22%3A00%3A00.000Z&endTimestamp={enddate}T22%3A00%3A00.000Z&grouping=&includeVat=false"
            if kind == 2: #gas
                url = f"https://mijn.easyenergy.com/nl/api/tariff/getlebatariffs?startTimestamp={startdate}T22%3A00%3A00.000Z&endTimestamp={enddate}T22%3A00%3A00.000Z&grouping=&includeVat=false"
            if url == "":
                return {}

            response = requests.get(url)

            if response.status_code == 200:
                return response.json()

            raise KeyError(f"Response code {response.status_code}")
        except KeyError as e:
            log.warning(f"We did not get data from Easy Energy api : {e}")
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def __process_api_data(self, data:dict = {}, kind:int = 1, UTC:bool = False)->list:
        try:
            kind_str = ""
            if kind == 1:
                kind_str = 'e'
            if kind == 2:
                kind_str = 'g'

            prices = []
            for d in data:
                price = {}
                efrom = get_timestamp(time_stamp=d['Timestamp'],UTC=UTC)
                price['fromdate'] = efrom['datum']
                price['fromtime'] = efrom['tijd']
                price['price'] = d['TariffUsage']
                price['kind'] = kind_str

                prices.append(price)

            if prices:
                return prices

            raise KeyError('No data?')
        except KeyError as e:
            log.warning(f"We did not get data from EnergyZero api in process_api_data : {e}")
            return []

if __name__ == "__main__":
    EZ = EasyEnergy_API()
    print('Gas prijzen')
    print(EZ.get_data(kind=2))
    print('Electra prijzen')
    print(EZ.get_data(kind=1))
