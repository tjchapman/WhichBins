import json
import logging
import requests
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

'''
Borrowed from: https://github.com/robbrad/UKBinCollectionData/blob/master/uk_bin_collection/uk_bin_collection/councils/SomersetCouncil.py
'''
class Source():
    '''
    If using Somerset, set UPRN as property 
    '''
    def __init__(self, postcode=None, property=None, address=None):
        self._postcode = postcode
        self._property = property
        self._address = address

    def fetch(self):
        headers = {
            "User-Ageny": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        requests.packages.urllib3.disable_warnings()
        with requests.Session() as s:
                # Set Headers
                s.headers = headers

                # Get the first page - This is the Search for property by Post Code page
                resource = s.get(
                    "https://iweb.itouchvision.com/portal/f?p=customer:BIN_DAYS:::NO:RP:UID:625C791B4D9301137723E9095361401AE8C03934"
                )
                # Create a BeautifulSoup object from the page's HTML
                soup = BeautifulSoup(resource.text, "html.parser")

                # The page contains a number of values that must be passed into subsequent requests - extract them here
                payload = {
                    i["name"]: i.get("value", "") for i in soup.select("input[name]")
                }
                payload2 = {
                    i["data-for"]: i.get("value", "")
                    for i in soup.select("input[data-for]")
                }
                payload_salt = soup.select_one('input[id="pSalt"]').get("value")
                payload_protected = soup.select_one('input[id="pPageItemsProtected"]').get(
                    "value"
                )

                # Add the PostCode and 'SEARCH' to the payload
                payload["p_request"] = "SEARCH"
                payload["P153_POST_CODE"] = self._postcode

                # Manipulate the lists and build the JSON that must be submitted in further requests - some data is nested
                merged_list = {**payload, **payload2}
                new_list = []
                other_list = {}
                for key in merged_list.keys():
                    temp_list = {}
                    val = merged_list[key]
                    if key in [
                        "P153_UPRN",
                        "P153_TEMP",
                        "P153_SYSDATE",
                        "P0_LANGUAGE",
                        "P153_POST_CODE",
                    ]:
                        temp_list = {"n": key, "v": val}
                        new_list.append(temp_list)
                    elif key in [
                        "p_flow_id",
                        "p_flow_step_id",
                        "p_instance",
                        "p_page_submission_id",
                        "p_request",
                        "p_reload_on_submit",
                    ]:
                        other_list[key] = val
                    else:
                        temp_list = {"n": key, "v": "", "ck": val}
                        new_list.append(temp_list)

                json_builder = {
                    "pageItems": {
                        "itemsToSubmit": new_list,
                        "protected": payload_protected,
                        "rowVersion": "",
                        "formRegionChecksums": [],
                    },
                    "salt": payload_salt,
                }
                json_object = json.dumps(json_builder, separators=(",", ":"))
                other_list["p_json"] = json_object

                # Set Referrer header
                s.headers.update(
                    {
                        "referer": "https://iweb.itouchvision.com/portal/f?p=customer:BIN_DAYS:::NO:RP:UID:625C791B4D9301137723E9095361401AE8C03934"
                    }
                )

                # Generate POST including all the JSON we just built
                s.post(
                    "https://iweb.itouchvision.com/portal/wwv_flow.accept", data=other_list
                )

                # The second page on the portal would normally allow you to select your property from a dropdown list of
                # those that are at the postcode entered on the previous page
                # The required cookies are stored within the session so re-use the session to keep them
                resource = s.get(
                    "https://iweb.itouchvision.com/portal/itouchvision/r/customer/bin_days"
                )

                # Create a BeautifulSoup object from the page's HTML
                soup = BeautifulSoup(resource.text, "html.parser")

                # The page contains a number of values that must be passed into subsequent requests - extract them here
                payload = {
                    i["name"]: i.get("value", "") for i in soup.select("input[name]")
                }
                payload2 = {
                    i["data-for"]: i.get("value", "")
                    for i in soup.select("input[data-for]")
                }
                payload_salt = soup.select_one('input[id="pSalt"]').get("value")
                payload_protected = soup.select_one('input[id="pPageItemsProtected"]').get(
                    "value"
                )

                # Add the UPRN and 'SUBMIT' to the payload
                payload["p_request"] = "SUBMIT"
                payload["P153_UPRN"] = self._property

                # Manipulate the lists and build the JSON that must be submitted in further requests - some data is nested
                merged_list = {**payload, **payload2}
                new_list = []
                other_list = {}
                for key in merged_list.keys():
                    temp_list = {}
                    val = merged_list[key]
                    if key in ["P153_UPRN", "P153_TEMP", "P153_SYSDATE", "P0_LANGUAGE"]:
                        temp_list = {"n": key, "v": val}
                        new_list.append(temp_list)
                    elif key in ["P153_ZABY"]:
                        temp_list = {"n": key, "v": "1", "ck": val}
                        new_list.append(temp_list)
                    elif key in ["P153_POST_CODE"]:
                        temp_list = {"n": key, "v": self._postcode, "ck": val}
                        new_list.append(temp_list)
                    elif key in [
                        "p_flow_id",
                        "p_flow_step_id",
                        "p_instance",
                        "p_page_submission_id",
                        "p_request",
                        "p_reload_on_submit",
                    ]:
                        other_list[key] = val
                    else:
                        temp_list = {"n": key, "v": "", "ck": val}
                        new_list.append(temp_list)

                json_builder = {
                    "pageItems": {
                        "itemsToSubmit": new_list,
                        "protected": payload_protected,
                        "rowVersion": "",
                        "formRegionChecksums": [],
                    },
                    "salt": payload_salt,
                }

                json_object = json.dumps(json_builder, separators=(",", ":"))
                other_list["p_json"] = json_object

                # Generate POST including all the JSON we just built
                s.post(
                    "https://iweb.itouchvision.com/portal/wwv_flow.accept", data=other_list
                )

                # The third and final page on the portal shows the detail of the waste collection services
                # The required cookies are stored within the session so re-use the session to keep them
                resource = s.get(
                    "https://iweb.itouchvision.com/portal/itouchvision/r/customer/bin_days"
                )

                # Create a BeautifulSoup object from the page's HTML
                soup = BeautifulSoup(resource.text, "html.parser")
                data = []

                # Loop through the items on the page and build a JSON object for ingestion
                for item in soup.select(".t-MediaList-item"):
                    for value in item.select(".t-MediaList-body"):
                        dict_data = {
                            "t": value.select("span")[1].get_text(strip=True).title(),
                            "date": datetime.strptime(
                                value.select(".t-MediaList-desc")[0].get_text(strip=True),
                                "%A, %d %B, %Y",
                            ).strftime("%Y-%m-%d"),
                        }
                        data.append(dict_data)

                return data













