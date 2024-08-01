import os
from datetime import datetime, timedelta

import requests

from resources.api_general import get_timestamp

import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class NordPool_API:
    def __init__(self) -> None:
        pass

    def get_data(self, startdate:str = "", enddate:str = "", kind:int = 1)->list:
        try:
            if(api_data := self.__get_api_data(startdate=startdate)):
                if (data := self.__process_api_data(data=api_data, kind=kind, UTC=False)):
                    return data

            raise KeyError('No Data?')
        except KeyError as e:
            log.warning(f"We did not get data from NordPool api : {e}")
            return []
        except Exception as e:
            log.warning(e, exc_info=True)
            return []

    def __get_api_data(self, startdate:str = "")->dict:
        try:
            # kind => stroom = 1, gas = 2
            now = datetime.now()
            if startdate == "":
                date = now.strftime("%d-%m-%Y")
            else:
                date = startdate

            tomorrow_ts = now + timedelta(days=+1)
            tomorrow = tomorrow_ts.strftime("%d-%m-%Y")

            url = "https://www.nordpoolgroup.com/api/marketdata/page/10"

            current_hour = datetime.now().hour
            if startdate == "" and current_hour >= 14:
                url += "?currency=,,,EUR&endDate=" + tomorrow
            else:
                url += "?currency=,,,EUR&endDate=" + date

            response = requests.get(url)
            return response.json()

        except KeyError as e:
            log.warning(f"We did not get data from NordPool api : {e}")
            return {}
        except Exception as e:
            log.warning(e, exc_info=True)
            return {}

    def __process_api_data(self, data:dict = {}, kind:int = 1, UTC:bool = False)->list:
        try:
            kind_type = 'e'
            if kind == 1:
                kind_type = 'e'
            if kind == 2:
                kind_type = 'g'

            prices = []
            previous_timestamp = None
            price_data = []

            for row in data["data"]["Rows"]:
                localrow = list(filter(lambda col: col["Name"] == "NL", row["Columns"]))
                localrow = localrow[0] if localrow else None  # Get the first item

                if localrow and localrow["IsValid"]:
                    cost = float(localrow["Value"].replace(" ", "").replace(",", "."))
                    dateTimeStamp = row["StartTime"]
                    timestamp = datetime.strptime(dateTimeStamp, "%Y-%m-%dT%H:%M:%S")
                    efrom = get_timestamp(time_stamp=timestamp, UTC=UTC)
                    # Check if the time is 00:00:00 and if it's the same date as the previous row
                    if previous_timestamp and timestamp.strftime('%H:%M:%S') == "00:00:00" and timestamp.strftime('%Y-%m-%d') == previous_timestamp.strftime('%Y-%m-%d'):
                        continue  # Skip this iteration and move to the next row

                    cost_per_kwh = cost / 1000  # Convert the cost to cost per kWh
                    previous_timestamp = timestamp  # Update the previous timestamp

                    # Prepare the data to be inserted into the database
                    prices.append({
                        "fromdate": efrom['datum'],
                        "fromtime": efrom['tijd'],
                        "price": cost_per_kwh,
                        "kind": kind_type
                    })

            if prices:
                return prices

            raise KeyError('No data?')
        except KeyError as e:
            log.warning(f"{e} {data['data']}", exc_info=True)
            return []
        except Exception as e:
            log.warning(e, exc_info=True)
            return []


if __name__ == "__main__":
    NP = NordPool_API()
    print('Electra prijzen')
    print(NP.get_data(kind=1))
