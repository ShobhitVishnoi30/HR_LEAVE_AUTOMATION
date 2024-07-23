from document_utils.chat_with_hr import get_reply_normally
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, tool
from typing import Optional, Type
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from config import openai_client,embedding_model_name,pinecone_index
from typing import List
from typing import List, Optional
from datetime import datetime, timedelta

employee_leave_history = [
    {
        "employee_email": "shobhit@gmail.com",
        "leave_type": "Sick Leave",
        "reason": "Flu",
        "start_date": "2023-03-15",
        "end_date": "2023-03-17",
        "start_weekday": "Wednesday",
        "end_weekday": "Friday",
    },
    {
        "employee_email": "shobhit@gmail.com",
        "leave_type": "Earned Leave",
        "reason": "Family Vacation",
        "start_date": "2023-07-10",
        "end_date": "2023-07-20",
        "start_weekday": "Monday",
        "end_weekday": "Thursday",
    },
    {
        "employee_email": "shobhit@gmail.com",
        "leave_type": "Paternity Leave",
        "reason": "Birth of a child",
        "start_date": "2022-11-01",
        "end_date": "2022-11-14",
        "start_weekday": "Tuesday",
        "end_weekday": "Monday",
    },
    {
        "employee_email": "shobhit@gmail.com",
        "leave_type": "Comp Off",
        "reason": "Worked on a weekend project",
        "start_date": "2023-04-22",
        "end_date": "2023-04-22",
        "start_weekday": "Saturday",
        "end_weekday": "Saturday",
    },
    {
        "employee_email": "shobhit@gmail.com",
        "leave_type": "Optional Leave",
        "reason": "Personal Reasons",
        "start_date": "2023-09-05",
        "end_date": "2023-09-07",
        "start_weekday": "Tuesday",
        "end_weekday": "Thursday",
    },
    {
        "employee_email": "harshitgupta@gmail.co",
        "leave_type": "Sick Leave",
        "reason": "Surgery",
        "start_date": "2023-02-01",
        "end_date": "2023-02-10",
        "start_weekday": "Wednesday",
        "end_weekday": "Friday",
    },
    {
        "employee_email": "harshitgupta@gmail.com",
        "leave_type": "Earned Leave",
        "reason": "Travel",
        "start_date": "2023-06-01",
        "end_date": "2023-06-15",
        "start_weekday": "Thursday",
        "end_weekday": "Thursday",
    },
    {
        "employee_email": "harshitgupta@gmail.com",
        "leave_type": "Comp Off",
        "reason": "Worked on a holiday",
        "start_date": "2023-01-02",
        "end_date": "2023-01-02",
        "start_weekday": "Monday",
        "end_weekday": "Monday",
    },
    {
        "employee_email": "debi@gmail.com",
        "leave_type": "Sick Leave",
        "reason": "Dental Procedure",
        "start_date": "2023-04-10",
        "end_date": "2023-04-12",
        "start_weekday": "Monday",
        "end_weekday": "Wednesday",
    },
    {
        "employee_email": "debi@gmail.com",
        "leave_type": "Earned Leave",
        "reason": "Wedding Anniversary",
        "start_date": "2023-08-15",
        "end_date": "2023-08-19",
        "start_weekday": "Tuesday",
        "end_weekday": "Saturday",
    },
    {
        "employee_email": "debi@gmail.com",
        "leave_type": "Paternity Leave",
        "reason": "Birth of a child",
        "start_date": "2021-05-01",
        "end_date": "2021-05-14",
        "start_weekday": "Saturday",
        "end_weekday": "Friday",
    },
]
employee_leave_balance = [
    {
        "employee_email": "shobhit@gmail.com",
        "Earned Leave": 20,
        "Optional Leave": 3,
        "Sick Leave": 10,
        "Special Leave": 2,
        "Comp Off": 3,
    },
    {
        "employee_email": "harshitGupta@gmail.com",
        "Earned Leave": 18,
        "Optional Leave": 4,
        "Sick Leave": 8,
        "Special Leave": 1,
        "Comp Off": 2,
    },
    {
        "employee_email": "debi@gmail.com",
        "Earned Leave": 22,
        "Optional Leave": 6,
        "Sick Leave": 12,
        "Special Leave": 3,
        "Comp Off": 4,
    },
    {
        "employee_email": "kj@gmail.com",
        "Earned Leave": 25,
        "Optional Leave": 7,
        "Sick Leave": 15,
        "Special Leave": 2,
        "Comp Off": 5,
    },
    {
        "employee_email": "hy@gmail.com",
        "Earned Leave": 19,
        "Optional Leave": 5,
        "Sick Leave": 9,
        "Special Leave": 1,
        "Comp Off": 3,
    },
]

class SearchInput(BaseModel):
    emailAddress: str = Field(description="should be a email address")
    typeOfLeave:str=Field(description="Should state type of leave")


class CustomFetcherTool(BaseTool):
    name = "custom_fetcher_tool"
    description = "Fetch all the data for email address and the type of leave"
    args_schema: Type[BaseModel] = SearchInput

    def _run(
        self,
        emailAddress: str,
        typeOfLeave: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""
        employee_leaves=self.fetch_leave_history(emailAddress)
        leavePolicy = self.fetch_leave_policy(typeOfLeave)
        leaveBalance= self.fetch_leave_balance(emailAddress,typeOfLeave)
        # print(data.content)
        return {
            "employee_leaves": employee_leaves,
            "leave_policy": leavePolicy,
            "leave_balance": leaveBalance,
        }

    def fetch_leave_history(self, emailAddress):
        employee_leaves = []
        for leave_entry in employee_leave_history:
            if leave_entry["employee_email"] == emailAddress:
                employee_leaves.append(leave_entry)
        return employee_leaves

    def fetch_leave_balance(self, email_address, type_of_leave):
        employee_leaves_balance = []
        for leave_entry in employee_leave_balance:
            if leave_entry["employee_email"] == email_address:
                employee_leaves_balance.append(leave_entry)

        if not employee_leaves_balance:
            return 0

        print(employee_leaves_balance)
        return employee_leaves_balance[0][type_of_leave]

    def fetch_leave_policy(self, typeOfLeave):
        query = f"""Please provide the details about the {typeOfLeave}"""
        data=get_reply_normally(query, "LEAVES", "openai")
        return data


class SearchInputForLeaveCalculator(BaseModel):
    date_ranges: List[str] = Field(
     description="Should be an array of date ranges in string format"
    )
    leave_balance:str=Field(description="Should be a number with leave balance")
    date_of_the_email: str = Field(description="Should be a date in string format")
    days_notice: str = Field(
        description="Should provide days of which notice is required"
    )
    half_days: List[str] = Field(
        description="Should be an array of date ranges in string format"
    )
    leave_type: str=Field(
        description="Should be the type of the leave"
    )


class CustomLeaveCalculator(BaseTool):
    name = "custom_leave_tool"
    description = "Calculate if there are available leaves or not"
    args_schema: Type[BaseModel] = SearchInputForLeaveCalculator

    def _run(
        self,
        date_ranges: List[str],
        leave_balance:str,
        date_of_the_email: str,
        days_notice:str,
        half_days:List[str],
        leave_type:str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        """Use the tool."""

        total_leave_requested = self.calculate_requested_leave_days(date_ranges,half_days)
        leave_balance_days = self.convert_leave_balance_to_days(leave_balance)

        if total_leave_requested <= leave_balance_days:

            days_difference=self.calculate_days_difference(date_ranges,date_of_the_email)
            if leave_type == "Sick Leave":
                result = {
                    "status": "Approved",
                    "message": "Sick Leave is approved.",
                }
                return result

            if days_difference >= int(days_notice):
                result = {
                    "status": "Approved",
                    "message": f"Sufficient leave balance.Available balance of {leave_balance_days} day(s) fulfills {total_leave_requested} days requests.The leave request was submitted {days_difference} day(s) before the start date, which meets the {days_notice} day(s) notice requirement.",
                }
            else:
                result = {
                    "status": "Rejected",
                    "message": f"The leave request was submitted only {days_difference} day(s) before the start date, which does not meet the {days_notice} day(s) notice requirement.",
                }
            return result

        else:
            result = {
                "status": "Rejected",
                "message": f"Insufficient leave balance. Requested leave of {total_leave_requested} day(s) exceeds the available balance of {leave_balance_days} day(s)."
            }

        return result

    def calculate_requested_leave_days(self, date_ranges: List[str], half_days: List[str]) -> float:
        """Calculate the total number of days requested for leave."""
        total_days = len(date_ranges)
        half_day_count = 0

        # Convert date strings to datetime objects
        date_ranges = [datetime.strptime(date_str, "%d/%m/%Y").date() for date_str in date_ranges]
        half_days = [datetime.strptime(date_str, "%d/%m/%Y").date() for date_str in half_days]

        # Check if any half-day date is present in date_ranges
        for half_day in half_days:
            if half_day in date_ranges:
                half_day_count += 1
                total_days -= 1  # Subtract 1 from total days for the half day

        total_days += half_day_count * 0.5  # Add half-day counts as 0.5 days

        return total_days

    def convert_leave_balance_to_days(self, leave_balance: str) -> int:
        """Convert the leave balance string to the number of days."""
        # Implement the logic to convert the leave balance string to the number of days
        # based on the format and units used in your organization
        return int(leave_balance)

    def calculate_days_difference(self,date_ranges, email_date):
        if not date_ranges:
            return 0

        # Parse the date ranges
        start_date = datetime.strptime(date_ranges[0], "%d/%m/%Y")
        end_date = datetime.strptime(date_ranges[1], "%d/%m/%Y")

        # Parse the email date
        email_date = datetime.strptime(email_date, "%d/%m/%Y")

        # Calculate the difference in days
        if email_date < start_date:
            return (start_date - email_date).days
        elif email_date > end_date:
            return -(email_date - end_date).days
        else:
            return 0


# Instantiate the ReadFileTool
fetcher_tool = CustomFetcherTool()
leave_calculator_tool = CustomLeaveCalculator()


def generate_function_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": ["emailAddress", "typeOfLeave"],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema


def generate_leave_calculator_function_config(tool):
    # Define the function schema based on the tool's args_schema
    function_schema = {
        "name": tool.name.lower().replace(" ", "_"),
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [
                "date_ranges",
                "leave_balance",
                "date_of_the_email",
                "days_notice",
                "leave_type",
            ],
        },
    }

    if tool.args is not None:
        function_schema["parameters"]["properties"] = tool.args

    return function_schema
