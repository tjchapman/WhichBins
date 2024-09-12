from waste_collection import Source
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    ADDRESS = None
    PROPERTY = None
    POSTCODE = None

    POSTCODE = os.getenv('POSTCODE')
    PROPERTY = os.getenv('PROPERTY')
    ADDRESS = os.getenv('ADDRESS')
    
    if ADDRESS or PROPERTY:
         waste_collection = Source(postcode=POSTCODE, address=ADDRESS, property=PROPERTY)
    else:
        raise ValueError('Please supply an address or postcode')
   
    bin_days = waste_collection.fetch()

    print(bin_days)


