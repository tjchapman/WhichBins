import os
import json
import logging
import requests
import pendulum
from dotenv import load_dotenv
from waste_collection import Source

load_dotenv()
logger = logging.getLogger(__name__)

def send_telegram(message, bot_token, chat_id):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + \
        '&parse_mode=HTML&text=' + message
    response = requests.get(send_text)
    print(response)

    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def collect_bins(postcode, address=None,property=None):

    today = pendulum.now("Europe/London")
    tomorrow_fmted = today.add(days=1).to_date_string()
    try:
        if address or property:
            waste_collection = Source(postcode=postcode, address=address, property=property)
        else:
            raise ValueError('Please supply an address or postcode')
    
        bin_days = waste_collection.fetch()

        arr = []
        for i in bin_days:
            arr.append({i['t']: i['date']})

        bin_dict= {k:v for e in arr for (k,v) in e.items()}
        bins_due = [bin for bin, day in bin_dict.items() if day == tomorrow_fmted]
        bins_due_fmtd =  " & ".join(str(element) for element in bins_due)

        if bins_due:
            message = f'Bins for tomorrow: {bins_due_fmtd}'
        else:
            message = f'Uh oh change of plans... this is the bin schedule: {bin_dict}'

        return message
    
    except Exception as e:
        message= f'Error fetching bin status: {str(e)}'
        return message


def main():
    POSTCODE = os.getenv('POSTCODE')
    PROPERTY = os.getenv('PROPERTY')
    ADDRESS = os.getenv('ADDRESS')

    BOT_TOKEN = os.environ.get('TELEGRAM_API_KEY')
    BOT_CHAT_ID = os.environ.get('CHAT_ID')

    message=collect_bins(postcode=POSTCODE, address=ADDRESS, property=PROPERTY)
    send_telegram(message=message, bot_token=BOT_TOKEN, chat_id=BOT_CHAT_ID)
    return 

  
if __name__ == '__main__':
    main()