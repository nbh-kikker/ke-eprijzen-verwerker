import os
from datetime import datetime, timedelta

import requests

from resources.api_general import get_timestamp

import logging
# https://reversed.notion.site/Marktprijzen-API-89ce600a88ac4abe8c2ad89d3167a83e
PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class FrankEnergie_API:
    def __init__(self) -> None:
        pass

    def get_data(self, startdate:str = "", enddate:str = "", kind:int = 1)->list:
        try:
            if(api_data := self.__get_api_data(startdate=startdate, enddate=enddate, kind=kind)):
                if (data := self.__process_api_data(data=api_data, kind=kind, UTC=True)):
                    return data

            raise KeyError('No Data?')
        except KeyError as e:
            log.warning(f"We did not get data from FrankEnergie api : {e}")
            return []
        except Exception as e:
            log.warning(e, exc_info=True)
            return []

    def __get_api_data(self, startdate:str = "", enddate:str = "", kind:int = 1)->dict:
        try:
            # kind => stroom = 1, gas = 2
            now = datetime.now()
            if startdate == "":
                startdate = now.strftime("%Y-%m-%d")
            if enddate == "":
                tomorrow_ts = now + timedelta(days=+1)
                enddate = tomorrow_ts.strftime("%Y-%m-%d")

            query = {
                        "query": """
                            query MarketPrices($startDate: Date!, $endDate: Date!) {
                                marketPricesElectricity(startDate: $startDate, endDate: $endDate) {
                                    from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                                }
                                marketPricesGas(startDate: $startDate, endDate: $endDate) {
                                    from till marketPrice marketPriceTax sourcingMarkupPrice energyTaxPrice
                                }
                            }
                        """,
                        "variables": {"startDate": str(startdate), "endDate": str(enddate)}
                    }

            response = requests.post('https://frank-graphql-prod.graphcdn.app', json=query)
            return response.json()

        except KeyError as e:
            log.warning(f"We did not get data from FrankEnergie api : {e}")
            return {}
        except Exception as e:
            log.warning(e, exc_info=True)
            return {}

    def __process_api_data(self, data:dict = {}, kind:int = 1, UTC:bool = False)->list:
        try:
            api_data = {}
            str_kind = ""
            if kind == 1:
                str_kind = 'e'
                api_data = data['data']['marketPricesElectricity']
            if kind == 2:
                str_kind = 'g'
                api_data = data['data']['marketPricesGas']

            prices = []
            for d in api_data:
                price = {}
                efrom = get_timestamp(time_stamp=d['from'],UTC=UTC)
                price['fromdate'] = efrom['datum']
                price['fromtime'] = efrom['tijd']
                price['price'] = d['marketPrice']
                price['kind'] = str_kind
                prices.append(price)

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
    FE = FrankEnergie_API()
    print('Electra prijzen')
    print(FE.get_data(kind=1))
    print('Gas prijzen')
    print(FE.get_data(kind=2))
