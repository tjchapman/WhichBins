#!/usr/bin/env python
import os
import sys
import json
import logging
import requests
import pendulum
from dotenv import load_dotenv
from waste_collection import select_council

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s\t%(levelname)s\t%(funcName)s\t%(message)s')

def send_telegram(message: str, bot_token: str, chat_id: str):
    send_text = 'https://api.telegram.org/bot' + str(bot_token) + '/sendMessage?chat_id=' + str(chat_id) + \
        '&parse_mode=HTML&text=' + str(message)
    response = requests.get(send_text)
    logger.info('GOT %s', response)

    return {
        'statusCode': 200,
        'body': json.dumps(str(message))
    }

def collect_bins(council: str, postcode: str, date_to_check: str, address:str=None,property: int=None):
    council_function = select_council(council=council)
    try:
        if address or property:
            waste_collection = council_function(postcode=postcode, address=address, property=property)
        else:
            raise ValueError('Please supply an address or postcode')
    
        bin_days = waste_collection.fetch()
        print(bin_days)


        arr = []
        for i in bin_days:
            arr.append({i['t']: i['date']})

        bin_dict= {k:v for e in arr for (k,v) in e.items()}
        bins_due = [bin for bin, day in bin_dict.items() if day == date_to_check]
        bins_due_fmtd =  " & ".join(str(element) for element in bins_due)

        if bins_due:
            message = f'Bins for tomorrow: {bins_due_fmtd}'
        else:
            sorted_bins= dict(sorted(bin_dict.items(), key=lambda item: item[1]))
            message = f'Uh oh change of plans... this is the latest bin schedule: {sorted_bins}'

        logger.info('GOT %s', message)
        return message
    
    except Exception as e:
        message= f'Error fetching bin status: {str(e)}'
        logger.info('GOT ERROR %s', message)
        return message


def main():
    COUNCIL = os.environ['COUNCIL']
    POSTCODE = os.environ['POSTCODE']
    PROPERTY = os.environ['PROPERTY']
    ADDRESS = os.environ['ADDRESS']

    BOT_TOKEN = os.environ['TELEGRAM_API_KEY']

    today = pendulum.now("Europe/London")
    tomorrow_fmted = today.add(days=1).to_date_string()
    logger.debug('GOT tomorrow= %s', tomorrow_fmted)

    message =collect_bins(council=COUNCIL, postcode=POSTCODE, date_to_check=tomorrow_fmted, address=ADDRESS, property=PROPERTY)
    logger.debug(message)

    with open('chat_id.json', 'r') as file:
              chat_ids =  json.load(file)

    for chat_id in chat_ids["details"]:
        chat_id = chat_id['id']
        send_telegram(message=message, bot_token=BOT_TOKEN, chat_id=chat_id)

    return 


def handler(event, context):
    main()  

  
if __name__ == '__main__':
    sys.exit(main())