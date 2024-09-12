from waste_collection import Source
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    POSTCODE = os.getenv('POSTCODE')
    PROPERTY = os.getenv('PROPERTY')
    
    scraper = Source(property=PROPERTY, postcode=POSTCODE)
    print(scraper.fetch())

