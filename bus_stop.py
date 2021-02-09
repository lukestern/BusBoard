from os import link
from pprint import pprint
import requests
import dotenv

def env(variable_name):
    env_var = dotenv.get_key('.env', variable_name)
    return env_var

TRANSPORT_BASE_URL = "http://transportapi.com/v3/uk/"
POSTCODE_BASE_URL = "https://api.postcodes.io/postcodes/"

APP_ID = env('APP_ID')
APP_KEY = env('APP_KEY')

CREDENTIALS = f"&app_id={APP_ID}&app_key={APP_KEY}"

postcode = "NW51TL"


def validate_postcode(postcode):
    """
    Inputs: postcode.
    Output: boolean
    """
    url = POSTCODE_BASE_URL + postcode + "/validate"
    resp = requests.get(url)
    if resp.json()["status"] == 200 and resp.json()["result"] == True:
        return True
    else:
        return False

def get_location(postcode):
    """
    Inputs: postcode.
    Output: longitude, latitude.
    """
    if validate_postcode(postcode):
        url = POSTCODE_BASE_URL + postcode
        resp = requests.get(url)
        res = resp.json()['result']
        return res["longitude"], res["latitude"]

def get_bus_stops(long, lat):
    """
    Inputs: longitude, latitude.
    Output: dictionary with atcocode and stop name. Keys: code, name
    """
    url = TRANSPORT_BASE_URL + f'places.json?lon={long}&lat={lat}&type=bus_stop' + CREDENTIALS
    resp = requests.get(url)
    two_stops = resp.json()["member"][:2]
    codes = [{"code": code['atcocode'], "name": code['name']} for code in two_stops]
    return codes

def get_buses_from_stop(atcocode):
    """
    Inputs: atcocode
    Output: bus info dictionary
    """
    url = TRANSPORT_BASE_URL + f'bus/stop/{atcocode}/live.json?group=no&nextbuses=yes' + CREDENTIALS
    resp = requests.get(url)
    buses = resp.json()
    return buses

def print_bus_info(bus_info):
    """
    Inputs: dictionary of bus information
    Output: None
    """
    for bus in bus_info:
        print(bus['best_departure_estimate'], bus['line_name'], bus['direction'])


if __name__ == "__main__":
    lon, lat = get_location(postcode)
    bus_stop_list = get_bus_stops(lon, lat)
    for stop in bus_stop_list:
        print(stop['name'])
        buses = get_buses_from_stop(stop['code'])
        buses_inbound = [departure for departure in buses['departures']['all']] 
        print_bus_info(buses_inbound)
