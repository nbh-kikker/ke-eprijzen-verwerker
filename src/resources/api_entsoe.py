import os
import json
from datetime import datetime, timedelta

from entsoe import EntsoePandasClient
import pandas as pd

from resources.api_general import get_timestamp

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

class Entsoe_API:
    def __init__(self) -> None:
        pass

    def get_day_ahead_prices_data(self, startdate:str="", enddate:str="", entsoe_key:str='', country_code:str="NL")->list:
        try:
            api_data = None
            data = None

            if entsoe_key is None or entsoe_key == "":
                raise Exception("We don't have a entsoe key")

            if(api_data := self.__get_day_ahead_prices(startdate=startdate, enddate=enddate, entsoe_key=entsoe_key, country_code=country_code)):
                # kind is always 1 = Energy!
                if (data := self.__process_day_ahead_prices_data(data=api_data, kind=1, UTC=False)):
                     return data

            raise KeyError(f"No Data? {api_data} {data} {country_code}")
        except KeyError as e:
            log.warning(f"We did not get data from Entsoe api : {e}")
            return []
        except Exception as e:
            log.warning(e, exc_info=True)
            return []

    def get_wind_and_solar_forecast(self, startdate:str = "", enddate:str = "", entsoe_key:str="", country_code:str = "NL")->dict:
        try:
            api_data = None

            if entsoe_key is None or entsoe_key == "":
                raise Exception("We don't have a entsoe key")

            if(api_data := self.__wind_and_solar_forecast(startdate=startdate, enddate=enddate, entsoe_key=entsoe_key, country_code=country_code)):
                if (solar := self.__process_solar_wind_api_data(data=api_data['Solar'], kind="s", UTC=False)):
                    pass
                if (wind_on := self.__process_solar_wind_api_data(data=api_data['Wind Onshore'], kind="w_on", UTC=False)):
                    pass
                if (wind_off:= self.__process_solar_wind_api_data(data=api_data['Wind Offshore'], kind="w_off", UTC=False)):
                    pass

                return {'Solar':solar, 'Wind Onshore': wind_on, 'Wind Offshore': wind_off}
            raise KeyError(f"No Data? {api_data}")
        except KeyError as e:
            log.warning(f"{e}")
            return {}
        except Exception as e:
            log.warning(e, exc_info=True)
            return {}

    def __wind_and_solar_forecast(self, startdate:str = "", enddate:str = "", entsoe_key:str="", country_code:str = "NL")->dict:
        try:
            if startdate == "":
                yesterday = datetime.now() + timedelta(days=-1)
                startdate = yesterday.strftime("%Y%m%d0001") #yyyyMMddHHmm
            if enddate == "":
                tomorrow = datetime.now() + timedelta(days=+1)
                enddate = tomorrow.strftime("%Y%m%d2359") #yyyyMMddHHmm

            startdate = pd.Timestamp(startdate, tz='Europe/Brussels')
            enddate = pd.Timestamp(enddate, tz='Europe/Brussels')
            client = EntsoePandasClient(api_key=entsoe_key)

            try:
                return client.query_wind_and_solar_forecast(start=startdate,end=enddate, country_code=country_code, psr_type=None).to_dict()
            except (KeyError, Exception) as e:
                log.warning(e, exc_info=True)
                return {}

        except Exception as e:
            log.warning(e, exc_info=True)
            return {}

    def __get_day_ahead_prices(self, startdate:str = "", enddate:str = "", entsoe_key:str="", country_code:str = "NL")->dict:
        try:
            if startdate == "":
                # yesterday = datetime.now() + timedelta(days=-1)
                yesterday = datetime.now()
                startdate = yesterday.strftime("%Y%m%d0001") #yyyyMMddHHmm
            if enddate == "":
                tomorrow = datetime.now() + timedelta(days=+1)
                enddate = tomorrow.strftime("%Y%m%d2359") #yyyyMMddHHmm

            startdate = pd.Timestamp(startdate, tz='Europe/Brussels')
            enddate = pd.Timestamp(enddate, tz='Europe/Brussels')
            client = EntsoePandasClient(api_key=entsoe_key)

            try:
                ts = client.query_day_ahead_prices(start=startdate, end=enddate, country_code=country_code)
                return ts.to_dict()
            except (KeyError, Exception) as e:
                log.warning(f"StartDate:{startdate}, EndDate:{enddate}, Country: {country_code}, {e}", exc_info=True)
                return {}

        except Exception as e:
            log.warning(e, exc_info=True)
            return {}

    def __process_solar_wind_api_data(self, data:dict = {}, kind:str = "", UTC:bool = False)->list:
        try:
            generation = []
            for k,v in data.items():
                forcast = {}
                dt = pd.to_datetime(k)
                efrom = get_timestamp(time_stamp=dt, min=True, UTC=UTC)
                forcast['fromdate'] = efrom['datum']
                forcast['fromtime'] = efrom['tijd']
                forcast['mw'] = int(v)
                forcast['kind'] = kind
                generation.append(forcast)

            if generation:
                return generation
            raise KeyError('No data?')
        except KeyError as e:
            log.warning(f"We did not get data from Entsoe api in process_api_data : {e}")
            return []

    def __process_day_ahead_prices_data(self, data:dict = {}, kind:int = 1, UTC:bool = False)->list:
        try:
            str_kind = ""
            if kind == 1:
                str_kind = 'e'
            if kind == 2:
                str_kind = 'g'

            prices = []
            for k,v in data.items():
                price = {}
                dt = pd.to_datetime(k)
                efrom = get_timestamp(time_stamp=dt,UTC=UTC)
                price['fromdate'] = efrom['datum']
                price['fromtime'] = efrom['tijd']
                price['price'] = float(v/1000)
                price['kind'] = str_kind
                prices.append(price)

            if prices:
                return prices

            raise KeyError('No data?')
        except KeyError as e:
            log.warning(f"We did not get data from Entsoe api in process_api_data : {e}")
            return []

if __name__ == "__main__":
    EN = Entsoe_API()
    print(EN.get_wind_and_solar_forecast(entsoe_key="YOUR_KEY"))
