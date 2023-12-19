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


def fetch_reservations(access_token):
    url = "https://api.hostaway.com/v1/reservations"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        reservations = json_response["result"]  # Extracting the reservations list
        return reservations
    else:
        print("Error fetching reservations:", response.text)
        return []


def fetch_latest_conversation(access_token, reservation_id):
    url = f"https://api.hostaway.com/v1/reservations/{reservation_id}/conversations"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        conversations = json_response["result"]  # Extract conversations list

        # Filter conversations with a valid 'messageReceivedOn' date
        valid_conversations = [
            conv for conv in conversations if conv.get("messageReceivedOn")
        ]

        # If there are valid conversations, find the most recent date
        if valid_conversations:
            most_recent_date = max(
                conv["messageReceivedOn"] for conv in valid_conversations
            )
            return most_recent_date
        else:
            return None  # Or an appropriate default value
    else:
        print(
            f"Error fetching conversations for reservation {reservation_id}:",
            response.text,
        )
        return None


def create_reservations_dataframe(access_token):
    reservations = fetch_reservations(access_token)
    data = []

    for reservation in reservations:
        reservation_id = reservation["id"]  # Using 'id' as reservation ID
        latest_conversation_date = fetch_latest_conversation(
            access_token, reservation_id
        )
        data.append(
            {
                "reservation_id": reservation_id,
                "latest_conversation_date": latest_conversation_date,
            }
        )

    return pd.DataFrame(data)


if __name__ == "__main__":
    load_dotenv()

    # Get values from .env file
    client_id = os.getenv("HOSTAWAY_CLIENT_ID")
    client_secret = os.getenv("HOSTAWAY_CLIENT_SECRET")

    # Obtaining the access token
    token = get_access_token(client_id, client_secret)

    if token:
        df = create_reservations_dataframe(token)
        df.to_csv("reservations.csv", index=False)
        print(df)
    else:
        print("Failed to obtain access token.")
