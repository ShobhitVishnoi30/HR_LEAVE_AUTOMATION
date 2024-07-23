from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from slackeventsapi import SlackEventAdapter
import os


slack_client = WebClient(
    token="SLACK_TOKEN"
)


def send_slack_message(email: str, message: str) -> None:
    try:
        # Get user ID using email
        user_id = find_user_id_by_email(email)
        if user_id:
            # Call the chat.postMessage method to send a message to the user's channel
            response = slack_client.chat_postMessage(channel=user_id, text=message)
            print("[+] Slack Message sent successfully")
            print(f"[+] Slack Message Response: {response['ok']}\tTS: {response['ts']}")
        else:
            print("[-] User not found for email:", email)
    except SlackApiError as e:
        print(f"[-] Error sending Slack message: {e.response['error']}")


def get_all_users():
    try:
        users = []
        cursor = None

        # Retrieve a list of all channels in the workspace
        channels = slack_client.conversations_list(types="im").get("channels", [])
        channel_map = {channel["user"]: channel["id"] for channel in channels}

        while True:
            response = slack_client.users_list(cursor=cursor)

            if response["ok"]:
                for user in response["members"]:
                    profile = user.get("profile", {})
                    display_name = profile.get("display_name", user["name"])
                    email = profile.get("email", "")
                    channel_id = channel_map.get(user["id"], "")

                    users.append(
                        {
                            "id": user["id"],
                            "name": user["name"],
                            "display_name": display_name,
                            "email": email,
                            "channel_id": channel_id,
                        }
                    )

                cursor = response.get("response_metadata", {}).get("next_cursor")

                if not cursor:
                    break
            else:
                print(f"Error: {response['error']}")
                break

        return users
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        return []


def get_user_profile(user_id):
    try:
        # Fetch user profile using user ID
        response = slack_client.users_info(user=user_id)

        if response["ok"]:
            user = response["user"]
            profile = user.get("profile", {})
            display_name = profile.get("display_name", user["name"])
            email = profile.get("email", "")

            return {
                "id": user_id,
                "name": user["name"],
                "display_name": display_name,
                "email": email,
            }
        else:
            print(f"Error: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        return None


def find_user_id_by_email(email):
    try:
        response = slack_client.users_list()
        if response["ok"]:
            for user in response["members"]:
                profile = user.get("profile", {})
                user_email = profile.get("email", "")
                print("user_email", user_email)
                print("email", email)
                if user_email.lower() == email.lower():
                    return user["id"]
        else:
            print(f"Error: {response['error']}")
            return None
    except SlackApiError as e:
        print(f"Error: {e.response['error']}")
        return None


