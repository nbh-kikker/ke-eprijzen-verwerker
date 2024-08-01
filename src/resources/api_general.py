import os
import logging
from dateutil import parser, tz

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

def get_timestamp(time_stamp:str = "", min:bool = False, UTC:bool = True)->dict:
    try:
        if UTC:
            from_zone = tz.gettz('UTC')
            to_zone = tz.gettz('CET')

            d = parser.parse(time_stamp)

            utc = d.replace(tzinfo=from_zone)
            cet = utc.astimezone(to_zone)

            datum = cet.strftime('%Y-%m-%d')  #==> '1975-05-14'

            if min:
                tijd = cet.strftime('%H:%M')  #==> '18:15'
            else:
                tijd = cet.strftime('%H:00')  #==> '18:00'

        else:
            datum = time_stamp.strftime('%Y-%m-%d')  #==> '1975-05-14'

            if min:
                tijd = time_stamp.strftime('%H:%M')  #==> '18:15'
            else:
                tijd = time_stamp.strftime('%H:00')  #==> '18:00'

        return {'datum': datum, 'tijd': tijd}
    except Exception as e:
        log.error(e, exc_info=True)
        return {}
