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


def fetch_conversation_details(access_token, reservation_id):
    url = f"https://api.hostaway.com/v1/reservations/{reservation_id}/conversations"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        json_response = response.json()
        all_messages = []
        for conversation in json_response['result']:
            num_messages = len(conversation.get('conversationMessages', []))
            print(f"Reservation ID {reservation_id}, Conversation ID {conversation['id']}, Number of messages: {num_messages}")
            for message in conversation.get('conversationMessages', []):
                all_messages.append({
                    'reservation_id': reservation_id,
                    'conversation_id': conversation['id'],
                    'message_id': message['id'],
                    'message': message.get('body', ''),
                    'sent_on': message['date'],
                    'sender': 'host' if message.get('originatedBy') == 'system' else 'guest'
                })
        print(f"Total messages aggregated for reservation {reservation_id}: {len(all_messages)}")
        return all_messages
    else:
        print(f"Error fetching conversations for reservation {reservation_id}:", response.text)
        return []

# 6540242
# 8990233
# 10498794
# 6252458


def create_conversation_dataframes(access_token, reservations):
    reservation_message_dfs = {}
    for reservation in reservations:
        reservation_id = reservation["id"]
        messages = fetch_conversation_details(access_token, reservation_id)
        if messages:
            df = pd.DataFrame(messages)
            reservation_message_dfs[reservation_id] = df
    return reservation_message_dfs


def get_top_5_longest_threads(message_dfs):
    sorted_dfs = sorted(message_dfs.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    return sorted_dfs


if __name__ == "__main__":
    load_dotenv()

    client_id = os.getenv("HOSTAWAY_CLIENT_ID")
    client_secret = os.getenv("HOSTAWAY_CLIENT_SECRET")
    token = get_access_token(client_id, client_secret)

    if token:
        reservations = fetch_reservations(token)
        conversation_dfs = create_conversation_dataframes(token, reservations)
        top_5_threads = get_top_5_longest_threads(conversation_dfs)

        for reservation_id, df in top_5_threads:
            print(f"Reservation ID: {reservation_id}, Number of messages: {len(df)}")
            df.to_csv(f"reservation_{reservation_id}_messages.csv", index=False)
            print(df.head())  # Print the first few messages for preview

# notes: https://chat.openai.com/c/f6dc6b3d-2e06-4f6f-a4e2-7997385d41cf
