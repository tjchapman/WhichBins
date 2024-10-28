import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from councils import wokingham
from councils import somerset


logger = logging.getLogger(__name__)

def select_council(council):
    if council.lower() =='wokingham':
        return wokingham.Source
    
    elif council.lower() =='somerset':
        return somerset.Source
    
    else:
        raise ValueError("Please enter valid council name") 