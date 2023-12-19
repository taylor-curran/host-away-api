import requests
from dotenv import load_dotenv
import os
import pandas as pd


def get_access_token(client_id, client_secret):
    url = "https://api.hostaway.com/v1/accessTokens"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "general",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Error obtaining access token:", response.text)
        return None


def make_api_call(api_endpoint, access_token):
    url = f"https://api.hostaway.com/v1/{api_endpoint}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response


load_dotenv()

# Get values from .env file
client_id = os.getenv("HOSTAWAY_CLIENT_ID")
client_secret = os.getenv("HOSTAWAY_CLIENT_SECRET")

# Obtaining the access token
token = get_access_token(client_id, client_secret)

if token:
    # Replace 'listings/12345' with your actual endpoint
    api_endpoint = "listings"
    response = make_api_call(api_endpoint, token)
    print(response.text)
    rjs = response.json()
    df = pd.DataFrame(rjs)
    breakpoint()
    print("Status code:", response.status_code)
else:
    print("Failed to obtain access token.")
