import os
import logging
import pendulum
from twilio.rest import Client
from dotenv import load_dotenv

from waste_collection import Source
from twilio_wrapper import Twilio

load_dotenv()
logger = logging.getLogger(__name__)


def main():
    ADDRESS = None
    PROPERTY = None
    POSTCODE = None

    POSTCODE = os.getenv('POSTCODE')
    PROPERTY = os.getenv('PROPERTY')
    ADDRESS = os.getenv('ADDRESS')
    PHONE = os.getenv('PHONE')
    TWILIO_SID = os.getenv('TWILIO_SID')
    TWILIO_AUTH = os.getenv('TWILIO_AUTH')
    FROM_NUMBER = os.getenv('TWILIO_NUMBER')

    twill_client = Client(TWILIO_SID, TWILIO_AUTH)

    assert(len(PHONE)==13) # UK number in correct format

    today = pendulum.now("Europe/London")
    tomorrow_fmted = today.add(days=1).to_date_string()
    
    if ADDRESS or PROPERTY:
         waste_collection = Source(postcode=POSTCODE, address=ADDRESS, property=PROPERTY)
    else:
        raise ValueError('Please supply an address or postcode')
   
    bin_days = waste_collection.fetch()

    arr = []
    for i in bin_days:
        arr.append({i['t']: i['date']})

    bin_dict= {k:v for e in arr for (k,v) in e.items()}
    bins_due = [bin for bin, day in bin_dict.items() if day == tomorrow_fmted]
    bins_due_fmtd =  " & ".join(str(element) for element in bins_due)

    twilio = Twilio(Client=twill_client)
    
    if bins_due:
        message = f'Bins for tomorrow are {bins_due_fmtd}'
    else:
        message = f'Uh oh change of plans... this is the bin schedule: {bin_dict}'
    logger.info(message)

    send_text = twilio.send_sms(from_number=FROM_NUMBER, to_number=PHONE, message=message)

    return send_text



if __name__ == '__main__':
    main()