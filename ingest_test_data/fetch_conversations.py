import requests
import pandas as pd
from dotenv import load_dotenv
import os


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


def fetch_all_conversations(access_token):
    url = "https://api.hostaway.com/v1/conversations?limit=100"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print("Error fetching conversations:", response.text)
        return []


def fetch_full_conversation(access_token, conversation_id):
    url = f"https://api.hostaway.com/v1/conversations/{conversation_id}/messages?limit=100"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["result"]
    else:
        print(
            f"Error fetching full conversation for ID {conversation_id}:", response.text
        )
        return []


def create_conversation_dataframes(access_token, conversations):
    dfs = []
    for conversation in conversations:
        conversation_id = conversation["id"]
        messages = fetch_full_conversation(access_token, conversation_id)
        if messages:
            df = pd.DataFrame(messages)
            dfs.append(df)
    return dfs


if __name__ == "__main__":
    load_dotenv()

    client_id = os.getenv("HOSTAWAY_CLIENT_ID")
    client_secret = os.getenv("HOSTAWAY_CLIENT_SECRET")
    token = get_access_token(client_id, client_secret)

    if token:
        conversations = fetch_all_conversations(token)
        conversation_dfs = create_conversation_dataframes(token, conversations)

        # Example: print or save each DataFrame
        for i, df in enumerate(conversation_dfs, start=1):
            print(f"Conversation {i}:")
            print(df.head())
            # save to CSV
            df.to_csv(f"conversations/conversation_{i}_messages.csv", index=False)
