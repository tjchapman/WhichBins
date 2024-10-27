import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

API_URL = "https://www.wokingham.gov.uk/rubbish-and-recycling/waste-collection/see-your-new-bin-collection-dates"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "www.wokingham.gov.uk",
    "Origin": "https://www.wokingham.gov.uk",
    "Referer": "https://www.wokingham.gov.uk/rubbish-and-recycling/waste-collection/see-your-new-bin-collection-dates",
}

class Source:
    def __init__(self, postcode=None, property=None, address=None):
        self._postcode = postcode
        self._property = property
        self._address = address
        

    def get_form_id(self, txt: str) -> str:
        soup = BeautifulSoup(txt, "html.parser")
        x = soup.find("input", {"name": "form_build_id"})
        id = x.get("value")
        return id

    def match_address(self, lst: list, addr: str) -> str:
        for item in lst:
            if addr in item.text.replace(",", ""):
                a = item.get("value")
        return a

    def fetch(self):
        s = requests.Session()

        # Load page to generate token needed for  query
        r = s.get(API_URL)
        form_id = self.get_form_id(r.text)

        # Perform postcode search to generate token needed for next query
        self._postcode = str(self._postcode.upper().strip().replace(" ", ""))
        payload = {
            "postcode_search_csv": self._postcode,
            "op": "Find Address",
            "form_build_id": form_id,
            "form_id": "waste_recycling_information",
        }
        r = s.post(
            API_URL,
            headers=HEADERS,
            data=payload,
        )
        form_id = self.get_form_id(r.text)

        # Use address to get an ID if property wasn't supplied. Assumes first match is correct.
        if self._property is None:
            soup = BeautifulSoup(r.text, "html.parser")
            dropdown = soup.find("div", {"class": "form-item__dropdown"})
            addresses = dropdown.find_all("option")
            self._address = self._address.upper()
            self._property = self.match_address(addresses, self._address)
        else:
            self._property = str(self._property)

        # Now get the collection schedule
        payload = {
            "postcode_search_csv": self._postcode,
            "address_options_csv": self._property,
            "op": "Show collection dates",
            "form_build_id": form_id,
            "form_id": "waste_recycling_information",
        }
        r = s.post(
            API_URL,
            headers=HEADERS,
            data=payload,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.find_all("div", {"class": "card--waste"})

        # Extract the collection schedules
        entries = []
        for card in cards:
            # Cope with Garden waste suffixed with (week 1) or (week 2)
            waste_type = " ".join(card.find("h3").text.strip().split()[:2])
            waste_date = card.find("span").text.strip().split()[-1]
            entries.append(
                {
            'date' : str(datetime.strptime(waste_date, "%d/%m/%Y").date()),
            't': waste_type
              }
            )

        return entries

