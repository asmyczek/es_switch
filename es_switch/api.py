# -*- coding: utf-8 -*-
 
from datetime import datetime
import requests
import config
import sys


API_BASE = "https://developer.sepush.co.za/business/2.0/"
API_ESCOM_STATUS = "http://loadshedding.eskom.co.za/LoadShedding/GetStatus"
API_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

def _get_hander(request, response_parser=lambda x: x.json(), headers={"token":config.ESPUSH_TOKEN}):
    ''' Get request error decorator '''
    try:
        response = requests.get(request, headers=headers)
    except Exception as e:
        print("Server error.")
        print(f"> {sys.exc_info()}")
        return
    else:
        if response.status_code == requests.codes.ok:
            return response_parser(response)
        else:
            print(f"Response error {response.status_code}.")
            return


'''
ES Push API calls
See API doc https://documenter.getpostman.com/view/1296288/UzQuNk3E#intro for detials
'''
def api_status():
    return _get_hander(f"{API_BASE}status")

def api_search_by_name(area_name):
    return _get_hander(f"{API_BASE}areas_search?text={area_name}")

def api_allowance():
    return _get_hander(f"{API_BASE}api_allowance")

def api_my_status():
    return _get_hander(f"{API_BASE}area?id={config.HOME_AREA_ID}")

def api_current_stage():
    timestamp = int(datetime.now().timestamp() * 1000)
    return _get_hander(f"{API_ESCOM_STATUS}?_={timestamp}", response_parser=lambda x: (int (x.text)) - 1, headers={})


def next_ls_events():
    '''
    Query next load shedding events
    '''
    try:
        events = []
        for event in api_my_status().get("events", []):
            events.append((datetime.strptime(event["start"], API_DATETIME_FORMAT),
                           datetime.strptime(event["end"], API_DATETIME_FORMAT)))
        return events
    except Exception as e:
        print(e)
        return
