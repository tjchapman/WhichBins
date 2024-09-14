import os
import logging
import pendulum
from boto3 import resource, Session
from dotenv import load_dotenv
from send_text import SnsWrapper
from waste_collection import Source

load_dotenv()
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    ADDRESS = None
    PROPERTY = None
    POSTCODE = None

    POSTCODE = os.getenv('POSTCODE')
    PROPERTY = os.getenv('PROPERTY')
    ADDRESS = os.getenv('ADDRESS')
    PHONE = os.getenv('PHONE')
    AWS_KEY = os.getenv('AWS_KEY')
    AWS_SECRET = os.getenv('AWS_SECRET')

    session = Session(aws_access_key_id=AWS_KEY, aws_secret_access_key=AWS_SECRET)
    sns_resource = session.resource('sns', region_name='eu-west-2')

    assert(len(PHONE)==13) # UK number in correct format
    
    today = pendulum.now("Europe/London")
    # today = pendulum.datetime(2024, 9, 17)
    today_fmted = today.to_date_string()
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
    bins_due_fmtd = " & ".join(str(element) for element in bins_due)

    sns_ = SnsWrapper(sns_resource=sns_resource)
    
    if bins_due:
        message = f'Bins for tomorrow are {bins_due_fmtd}'
    else:
        message = f'Uh oh change of plans... this is the bin schedule: {bin_dict}'
    logger.info(message)

    # sns_.publish_text_message(phone_number=PHONE,message=message)

    # return ##TODO: wrap in func