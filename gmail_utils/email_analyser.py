from config import openai_client
import json


def extract_details_from_email(texts, LLM):
    if texts == "":
        return "Unable to extract text"
    # Construct the assistant's response template
    template = """
        You are a helpful assistant specialized in extracting details from text related to leave requests. 
        Your task is to analyze the given text, identify the type of leave 
        (Sick Leave, Earned Leave, Optional Leave, Compensatory Leave, or Special Leave), extract the date(s) of the leave,
        and the reason for the leave. You should follow the provided response format, 
        which is a JSON object with three keys: "type_of_leave", "date", and "reason_of_leave".
        For single-day leave requests, the "date" value should be a single date string in the format "YYYY-MM-DD".
        For multi-day leave requests, the "date" value should be a list of date strings in the format "YYYY-MM-DD", 
        representing the start and end dates (inclusive)

        output:{"type_of_leave":"leave type","date":"date/array of dates","reason_of_leave":"leave reason"}
        """
    response = ""
    # Prepare the conversation messages
    messages = [{"role": "user", "content": str(template) + "text is" + texts}]

    if LLM == "openai":

        res = openai_client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
            temperature=0.7,
            # stream=True,
        )
        response = res.choices[0].message.content

    return response
