from autogenTasks import LeaveEmailTask
from gmail_utils.email_analyser import extract_details_from_email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from simplegmail import Gmail
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import re
import json

from slack_utils import find_user_id_by_email, send_slack_message

# Define the scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


def get_credentials():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, 
    # and is created automatically when the authorization flow completes for the first time.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    return creds


def save_credentials(creds):
    with open("token.pickle", "wb") as token:
        pickle.dump(creds, token)


def get_unread_messages(service, user_id):
    try:
        # Get the list of unread messages
        unread_msgs = (
            service.users().messages().list(userId=user_id, q="is:unread").execute()
        )
        unread_messages = unread_msgs.get("messages", [])
        return unread_messages
    except Exception as e:
        print(f"An error occurred while fetching unread messages: {e}")
        return []


def mark_as_read(service, user_id, message_id):
    try:
        # Mark the message as read
        service.users().messages().modify(
            userId=user_id, id=message_id, body={"removeLabelIds": ["UNREAD"]}
        ).execute()
    except Exception as e:
        print(f"An error occurred while marking message as read: {e}")


def reply_to_messages(service, user_id, messages):
    for message in messages:

        # Get the message details
        msg = service.users().messages().get(userId=user_id, id=message["id"]).execute()
        original_subject = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Subject"
            ),
            "No Subject",
        )

        # Get the sender
        sender = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "From"
            ),
            "Unknown Sender",
        )

        # Get the email date
        email_date = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Date"
            ),
            "Unknown Date",
        )

        # Get the email body (assuming it's in plain text)
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
                    break
            else:
                body = "No plain text body found"
        else:
            body = "No body found"

        # Get the "To" field
        to_list = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "To"
            ),
            None,
        )

        # Get the "CC" field
        cc_list = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Cc"
            ),
            None,
        )

        bcc_list = next(
            (
                header["value"]
                for header in msg["payload"]["headers"]
                if header["name"] == "Bcc"
            ),
            None,
        )

        if cc_list:
            fullMessage = (
                "The email is sent by "
                + sender
                + " on the date "
                + email_date
                + " and the recipients of the emails are : "
                + to_list
                + ". \n I am also attaching persons in CC list is :  "
                + cc_list
                + "\n"
            )
        else:
            fullMessage = (
                "The email is sent by "
                + sender
                + " on the date "
                + email_date
                + " and the recipients of the emails are : "
                + to_list
                + "\n"
            )

        fullMessage = fullMessage + " " + body
        leave_email_task = LeaveEmailTask()
        (
            leaveRequestDetails,
            userLeavesDetailsAndPolicyDetails,
            leavePolicyRequirement,
        ) = leave_email_task.details_extractor(fullMessage)

        if not userLeavesDetailsAndPolicyDetails and not leavePolicyRequirement:
            leave_result = None

        else:
            leave_result = leave_email_task.decide_leave_approval_rejector(
                sender,
                leaveRequestDetails,
                userLeavesDetailsAndPolicyDetails,
                leavePolicyRequirement,
            )


        if not leave_result:
            mark_as_read(service, user_id, message["id"])
            continue

        if leave_result["status"] == "Rejected":

            # Create a reply message
            reply_text = leave_result["email"]
            reply_message = MIMEText(reply_text)

            from_header = next(
                (
                    header
                    for header in msg["payload"]["headers"]
                    if header["name"] == "From"
                ),
                None,
            )
            message_id_header = next(
                (
                    header
                    for header in msg["payload"]["headers"]
                    if header["name"] == "Message-ID"
                ),
                None,
            )
            references_header = next(
                (
                    header
                    for header in msg["payload"]["headers"]
                    if header["name"] == "References"
                ),
                None,
            )

            if from_header:
                sender_email = from_header["value"]
                reply_message["To"] = sender_email
            else:
                print(f"Could not find the 'From' header for message ID: {msg['id']}")

            reply_message["From"] = "YOUR EMAIl"  # Your email

            reply_message["Subject"] = f"Re: {original_subject}"

            if cc_list and len(cc_list) > 0:
                reply_message["Cc"] = cc_list

            if bcc_list and len(bcc_list) > 0:
                reply_message["Bcc"] = bcc_list

            if message_id_header:
                reply_message["In-Reply-To"] = message_id_header[
                    "value"
                ]  # Original message ID

            if references_header:
                reply_message["References"] = references_header[
                    "value"
                ]  # Reference to the original thread
            else:
                reply_message["References"] = message_id_header[
                    "value"
                ]  # Use the Message-ID as the reference

            # Create a message object with the MIME message
            raw_reply = {
                "raw": base64.urlsafe_b64encode(reply_message.as_bytes()).decode()
            }

            # Send the reply
            sent_message = (
                service.users()
                .messages()
                .send(userId=user_id, body=raw_reply)
                .execute()
            )
            print(f'Reply sent. Message ID: {sent_message["id"]}')

        else:

            print(leaveRequestDetails)
            print(userLeavesDetailsAndPolicyDetails)
            print(leavePolicyRequirement)
            print(to_list)
            emails = re.findall(r"[\w\.-]+@[\w\.-]+", to_list)
            print(emails)
            leaveRequestDetailsDict = json.loads(leaveRequestDetails)
            userLeavesDetailsAndPolicyDetailsDict = json.loads(
                userLeavesDetailsAndPolicyDetails
            )

            leavePolicyRequirement = json.loads(leavePolicyRequirement)

            # profileDetails = find_user_id_by_email(
            #     leaveRequestDetailsDict["employee_email_address"]
            # )

            slack_message = f"""
            New Leave Request \n

            Leave submitted by {leaveRequestDetailsDict["employee_email_address"]} \n

            Leave Type  {leaveRequestDetailsDict["leave_type"]} \n

            Leave Dates {leaveRequestDetailsDict["leave_dates"]} \n

            Leave Reason {leaveRequestDetailsDict["leave_reason"]}



            Past Leave Details of Employee

            Leave History : {userLeavesDetailsAndPolicyDetailsDict["employee_leaves"]}

            Leave Balance : {userLeavesDetailsAndPolicyDetailsDict["leave_balance"]}



            leave Policy 

            Leave Policy Requirement : {leavePolicyRequirement["other_requirements"]}

            """
            for email in emails:
                send_slack_message(email, str(slack_message))

        mark_as_read(service, user_id, message["id"])


def load_credentials_and_process():
    creds = get_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "PATH",
                SCOPES,
            )
            creds = flow.run_local_server(port=8080)
        save_credentials(creds)

    gmail_service = build("gmail", "v1", credentials=creds)
    user_id = "me"

    unread_messages = get_unread_messages(gmail_service, user_id)

    if unread_messages:
        print(f"Found {len(unread_messages)} unread messages.")
        reply_to_messages(gmail_service, user_id, unread_messages)
    else:
        print("No unread messages found.")


def run_cron():
    try:
        load_credentials_and_process()
    except Exception as e:
        print("Scheduler Exception", e)
