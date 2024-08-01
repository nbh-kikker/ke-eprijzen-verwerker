from resources.api_nordpool import NordPool_API
from resources.api_frankenergie import FrankEnergie_API
from resources.api_easyenergy import EasyEnergy_API
from resources.api_energyzero import EnergieZero_API
from resources.api_entsoe import Entsoe_API

NP = NordPool_API()
print('Electra prijzen Nordpool')
print(NP.get_data(kind=1))

FE = FrankEnergie_API()
print('Electra prijzen FrankEnergie')
print(FE.get_data(kind=1))

EE = EasyEnergy_API()
print('Gas prijzen EasyEnergy')
print(EE.get_data(kind=2))
print('Electra prijzen EasyEnergy')
print(EE.get_data(kind=1))

EZ = EnergieZero_API()
print('Gas prijzen  EnergieZero')
print(EZ.get_data(kind=2))
print('Electra prijzen  EnergieZero')
print(EZ.get_data(kind=1))

EN = Entsoe_API()
print(EN.get_wind_and_solar_forecast(entsoe_key="57dc91c6-03ed-433a-a6cd-a6bcc0edbdcd"))
