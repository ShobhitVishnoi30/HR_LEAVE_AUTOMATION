from history_and_leave_details_fetcher import (
    generate_function_config,
    generate_leave_calculator_function_config,
    fetcher_tool,
    leave_calculator_tool,
)
from autogen.agentchat import (
    AssistantAgent,
    UserProxyAgent,
)

import json


config_list = [
    {
        "model": "gpt-3.5-turbo-0125",
        "api_key": "API_KEY",
    },
]

mistral_config = {
    "cache_seed": None,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 100,
}

mistral_config_with_calculator_function = {
    "cache_seed": None,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 100,
}


user_agent_task = f"""You are excellent instruction follower which follows all the instruction very accurately and never deviates from those
You are helful assistant which is helping to find out key details like employee , type of leave , date of leave , concerned persons , reason of leaves and your stand whether it should be apporved or not.
"""


user_agent_task_1 = f"""You are excellent instruction follower which follows all the instruction very accurately and never deviates from those
You are helful assistant which is helping to fetch the employee leave history and that leave policy details"""


details_analyser_task = f"""
Task: Analyze a leave email and extract the following details:
- Valid leave email
- Employee email address
- Date of Email
- Type of leave (Optional leave, Sick Leave, Earned Leave, Comp off, Paternity Leave)
- Date(s) of leave
- Concerned persons (categorized into To, CC, and BCC)
- Reason for the leave
- List down the dates for which employee wants to take half day leave

Please follow these steps:
1. Analyse if the email is valid leave email or not.
2. Extract the employee's email address from the 'From' field of the email.
3. Date of Email
4. Identify the type of leave by looking for keywords or phrases like 'Sick Leave', 'Earned Leave', 'Comp Off', 'Paternity Leave', or 'Optional Leave' in the email body.
   Never attach any other string other than specifed keywords and phrases.If half day or full day has been attached no need to include those in leave type.
5. Look for any date(s) or date range(s) mentioned in the email body. Extract only the date values or date ranges, without any additional explanation. If a date range is mentioned, list out all the individual dates within that range not just start date and end date.
6. Check if any other individuals are mentioned or included in the email thread.
   - Those in the 'To' field are directly concerned persons.
   - Those in the 'CC' field are indirectly concerned persons, more like to inform them.
   - Those in the 'BCC' field are other concerned persons.
7. Understand the reason for the leave by reading the details provided in the email body.
8.List down the dates for which employee wants to take half day leave.Extract only the date values or date ranges, without any additional explanation.

Please provide your analysis in a structured format, addressing each of the required details one by one.
"""

details_analyser_task_review = f"""

You will be provided with an email requesting leave and an analysis extracting details from that email. Your task is to carefully review the analysis and provide feedback on the following:
If the employee requested leave for a duration (e.g. 1st May to 10th May), have all the individual dates within that duration been accurately listed? Do not accept just the start and end dates, all dates must be present.
Verify that the type of leave (Optional leave, Sick Leave, Earned Leave, Comp off, Paternity Leave) has been identified correctly based on the keywords/phrases used in the email. There are only these given leave types. If you get any other leave type, reject it and ask for a valid leave type.
Check that the employee email address, email date, concerned persons (To/CC/BCC), and reason for leave have been extracted accurately.
Check if the dates for which the employee wants to take half day leave have been listed correctly.
Let me know if any other important details from the email have been missed in the analysis.
Please provide your feedback point-by-point under respective headings. If the analysis is complete and correct, you can simply confirm that. But if there are any issues, please explain them clearly so the analysis can be improved.
"""

user_and_leave_details_fetcher_task = f""" 
You will be provided with key details of an email:
- Employee email address
- Type of leave (Optional leave, Sick leave, Earned Leave, Comp off, Paternity Leave) 
- Date(s) of leave
- Concerned persons (categorized into To, CC, and BCC)
- Reason for the leave

You need to call external functions to fetch the complete history of the employee's previous leaves and also fetch the full details of the current leave type.

You also need to find out the patterns in user's leave if any.I am giving you some example patterns
a. Employee taking frequent leaves before or after holidays/weekends
b. Employee taking leaves around the same time every year (e.g., during a particular season or festival)
c. Employee taking multiple short leaves instead of a single long leave
d. Employee taking leaves immediately after joining or before resigning
e. Employee taking leaves during critical project phases or deadlines
f. Employee taking leaves frequently for the same reason (e.g., recurring medical issues)
g. Employee taking leaves immediately after being denied a leave request
h. Employee taking leaves frequently on Mondays or Fridays
i. Employee taking leaves without providing sufficient notice or reason

Provide the output in the following format:

user_leave_history=[] # Show all items in the list without minimizing
leave_policy="" # Provide the entire leave policy string without truncating
user_leave_pattern=""Provide the patterns if any otherwise mention no pattern founds
"""


leave_approver_rejector_task = """
You will be provided with the following information:

1. User Leave Request Details:
    - User's email address
    - Type of leave (e.g., Sick Leave, Earned Leave, Comp Off, Paternity Leave)
    - Date(s) of requested leave
    - Reason for the leave

2. User's Leave History:
    - A list containing details of all previous leaves taken by the user

3. Leave Policy Details:
    - A string containing the complete leave policy of the organization

Your task is to analyze the user's leave request based on the provided information and determine whether the leave should be approved or not. Follow these steps:

1. Understand the Leave Request:
   - Identify type of leave requested, date(s) of leave, and reason for the leave.

2. Review the Leave Policy:
   - Read through the complete leave policy string provided.
   - Identify the rules, guidelines, and criteria related to the requested leave type.
   - Check for any restrictions or conditions associated with the leave type.

3. Analyze the User's Leave History:
   - Go through the list of the user's previous leave records.
   - Look for patterns, frequent occurrences, or irregularities in the leave history.
   - Check if the user has sufficient leave balance for the requested duration.

4. Make an Initial Decision:
   - Based on the analysis, make an initial decision to approve or reject the leave request.
   - Document the reasons supporting your initial decision.

5. Rethink and Reevaluate:
   - Step back and carefully review all the information and your initial decision.
   - Consider any additional factors or special circumstances.
   - Reevaluate your decision, making necessary adjustments or clarifications.

6. Provide Final Recommendation:
   - Clearly state your final recommendation: "Approve" or "Reject"
   - Provide a detailed reason justifying your recommendation, citing relevant information from the leave request details, leave policy, and leave history.
   - Ensure that your reason addresses any potential concerns or irregularities identified during the analysis.

7. Review and Refine:
   - Carefully review your final recommendation and the provided reason.
   - Refine the language and ensure that the justification is clear, concise, and well-supported.
   - Double-check that you have not missed any critical information or considerations.

Your response should be formatted as follows:

recommendation: "Approve" or "Reject"
reason: "A detailed explanation justifying your recommendation, considering the leave request details, leave history, and leave policy."

Please provide your recommendation and the corresponding reason based on a thorough analysis of the provided information, following the outlined steps.
"""


leave_approver_rejector_review_task = """
You will be provided with the following information:

1. The original task description for analyzing a user's leave request.
2. The user's leave request details, including:
    - User's email address
    - Type of leave requested (e.g., Sick Leave, Earned Leave, Comp Off, Paternity Leave)
    - Date(s) of requested leave
    - Reason for the leave
3. The user's leave history (a list containing details of all previous leaves taken by the user).
4. The organization's leave policy details (a string containing the complete leave policy).
5. The agent's response to the original task, which includes:
    - recommendation: "Approve" or "Reject"
    - reason: "A detailed explanation justifying the recommendation, considering the leave request details, leave history, and leave policy."

Your task is to critically review the agent's response and provide a critique based on the following aspects:

1. Completeness:
   - Did the agent consider all relevant information provided (leave request details, leave history, and leave policy)?
   - Did the agent follow the outlined steps in the task description?
   - Were there any critical pieces of information or considerations that the agent missed or overlooked?

2. Accuracy:
   - Is the agent's interpretation of the leave policy and its rules/guidelines accurate?
   - Are there any factual errors or incorrect assumptions in the agent's analysis?
   - Is the agent's assessment of the user's leave history and patterns accurate?

3. Justification:
   - Is the agent's recommendation ("Approve" or "Reject") well-justified based on the provided information?
   - Does the reason provided by the agent adequately support the recommendation?
   - Are there any gaps or weaknesses in the agent's justification that need to be addressed?

4. Clarity and Conciseness:
   - Is the agent's response clear, well-structured, and easy to understand?
   - Is the language used concise and to the point, without unnecessary verbosity?
   - Are there any ambiguities or confusing statements in the agent's response?

Your review should be structured as follows:

positive_aspects: "A list of positive aspects or strengths in the agent's response."
areas_for_improvement: "A list of areas where the agent's response can be improved, addressing any issues or concerns identified in the critique."

Please provide a thorough and constructive review of the agent's response, highlighting both positive aspects and areas for improvement, based on the criteria outlined above.
"""


leave_policy_days_requirement_task = """
You will be provided with the leave policy for the given leave type.

Task: Retrieve the number of days required for advance notice when applying for leave from the leave policy and provide additional details about other requirements.

Instructions:
1. Based on the provided leave policy, determine and extract the number of days required for advance notice when applying for leave.
2. For the requested leave type and leave policy,  extract other relevant requirements mentioned in the policy, such as:

    a.Who is eligible to apply for this leave type?
    b.What is the maximum number of days that can be taken in one go?
    c.If applying for more days, what are the conditions?
    d.How many days of this leave type are employees entitled to?
    e.Who should be included in the leave application email?
    f.Any other specific requirements mentioned for this leave type.


If this information is not explicitly stated in the policy, respond with "0".

Expected Output: 
{
    "days_notice": "number of days or '0'",
    "other_requirements": "full details of other requirements"
}

"""


email_drafter_task = """
1. Understand the task:
You are an AI assistant asked to draft an email body given specific data and context. Review the provided data thoroughly to ensure you comprehend the body of the email, and any other relevant details about the email to be written.
Provide only body with relevant details required in the body with greetings and closing remarks.
Do not provide other components of the email


2. Analyze the requirements:
Break down the task into its core components. Determine the key elements that should be included in the email, such as:
- Greeting
- Body content (main message, supporting details, calls to action, etc.)
- Closing



Consider the tone, formatting, and structure appropriate for the given context and recipient(s).

3. Make a step-by-step plan:
Devise a systematic approach to composing the email by outlining the steps you will follow, for example:

Step 1: Craft an appropriate greeting for the recipient(s).
Step 2: Write the body content, ensuring that the main message, supporting information, and any required calls to action are clearly conveyed.
Step 3: Compose a suitable closing statement.

4. Execute the plan step-by-step:
Methodically follow the outlined steps to draft the email, ensuring adherence to the provided data and context.

5. Reanalyze the result:
Review the drafted email critically to ensure it meets the requirements, conveys the intended message effectively, and maintains a consistent tone and structure throughout. Make any necessary revisions or enhancements.

Once satisfied with the email draft, you can present the final version for review or send it to the intended recipient(s) as per the original instructions.

Remember, throughout this process, you should continually refer to the provided data and context to ensure the email accurately reflects the necessary information and meets the specified criteria.

"""
user_proxy = UserProxyAgent(
    name="User",
    system_message=user_agent_task,
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "")
    and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,
    human_input_mode="NEVER",
    llm_config=mistral_config,
    description="""You are working as a user proxy and deciding what agent should be selected according to the given input.
""",
)

leave_application_details_extractor = AssistantAgent(
    name="LeaveApplicationDetailsExtractor",
    system_message=details_analyser_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for finding all the details mentioned
""",
)

leave_application_details_extractor_critic = AssistantAgent(
    name="LeaveApplicationDetailsExtractorCritic",
    system_message=details_analyser_task_review,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for finding and suggesting critic to the detail extractor agent
""",
)

leave_approver_rejector = AssistantAgent(
    name="LeaveApproverRejector",
    system_message=leave_approver_rejector_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for analysing the leave request
""",
)

leave_approver_rejector_reviewer = AssistantAgent(
    name="LeaveApproverRejectorReviewer",
    system_message=leave_approver_rejector_review_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for providing the critic and suggestion to the agent
""",
)

leave_policy_days_requirement = AssistantAgent(
    name="LeavePolicyDaysRequirement",
    system_message=leave_policy_days_requirement_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for extracting the requirement
""",
)

email_drafter = AssistantAgent(
    name="EmailDrafter",
    system_message=email_drafter_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for drafting email
""",
)


mistral_config["functions"] = [generate_function_config(fetcher_tool)]
mistral_config_with_calculator_function["functions"] = [
    generate_leave_calculator_function_config(leave_calculator_tool)
]

user_proxy_1 = UserProxyAgent(
    name="User1",
    system_message=user_agent_task_1,
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "")
    and x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config=False,
    human_input_mode="NEVER",
    llm_config=mistral_config,
    description="""You are working as a user proxy and calling the function to fetch details
""",
)

user_proxy_1.register_function(
    function_map={
        fetcher_tool.name: fetcher_tool._run,
    }
)


user_and_leave_details_fetcher = AssistantAgent(
    name="UserAndLeaveDetailsFetcher",
    system_message=user_and_leave_details_fetcher_task,
    llm_config=mistral_config,
    description=f"""You are the agent responsible for fetching the task using function
""",
)


def reflection_message(recipient, messages, sender, config):
    print("Reflecting...", "yellow")
    return f"Reflect and provide critique  and missing points on the following analysis about the leave  \n\n {recipient.chat_messages_for_summary(sender)}"


user_proxy.register_nested_chats(
    [
        {
            "recipient": leave_application_details_extractor_critic,
            "message": reflection_message,
            "summary_method": "last_msg",
            "max_turns": 1,
        }
    ],
    trigger=leave_application_details_extractor,  # condition=my_condition,
)


leave_application_details_extractor_Args = {
    "summary_prompt": """You have been given the conversation between user and leave extractor agent. Provide the output in the given format.
        Leave type should be only these given strings.(Optional leave, Sick Leave, Earned Leave, Comp off, Paternity Leave)
        {
            "valid_leave_email":"True/False",
            "employee_email_address": "string",
            "date_of_the_email":"date of the email in DD/MM/YYYY format",
            "leave_type": "string",
            "leave_dates": ["date or date range in proper DD/MM/YYYY format"],
            "concerned_persons": {
                "to": ["email addresses"],
                "cc": ["email addresses"],
                "bcc": ["email addresses"]
            },
            "leave_reason": "string",
            "half_days":["date or date range in proper DD/MM/YYYY format"]
        }
    
    """
}

user_and_leave_details_fetcher_Args = {
    "summary_prompt": """You have been given the conversation between user 1 and user_and_leave_details_fetcher agent.
        Do not summarise , remove or add any extra details. Provide the full list of employee leaves and policy.
      
        Provide the output in the given format.
     
        {
                "employee_leaves": [
                    {
                        "employee_email": "",
                        "leave_type": "",
                        "reason": "",
                        "start_date": "",
                        "end_date": ""
                    },
                    {
                        "employee_email": "",
                        "leave_type": "",
                        "reason": "",
                        "start_date": "",
                        "end_date": ""
                    },
                    {
                        "employee_email": "",
                        "leave_type": "",
                        "reason": "",
                        "start_date": "",
                        "end_date": ""
                    }

                    ...
                ],
                "leave_policy": "full data of the leave policy"
                "leave_balance": "leave balance of the employee",
                "user_leave_pattern":"employee leave patterns"
        }
        
    
    """
}


class LeaveEmailTask:
    def details_extractor(self, messageInput):

        extracted_info = user_proxy.initiate_chat(
            recipient=leave_application_details_extractor,
            message=messageInput,
            max_turns=2,
            summary_method="reflection_with_llm",
            summary_args=leave_application_details_extractor_Args,
        )

        extracted_info_dict = json.loads(extracted_info.summary)
        user_and_leave_details = None
        leave_policy_days_requirements = None
        if extracted_info_dict["valid_leave_email"] == "False":
            return (
                extracted_info_dict,
                user_and_leave_details,
                leave_policy_days_requirements,
            )

        chat_results = user_proxy.initiate_chats(
            [
                {
                    "sender": user_proxy_1,
                    "recipient": user_and_leave_details_fetcher,
                    "message": "Call the function with required inputs and fetch the details",
                    "max_turns": 2,
                    "carryover": extracted_info.summary,
                    "summary_method": "reflection_with_llm",
                    "summary_args": user_and_leave_details_fetcher_Args,
                },
                {
                    "recipient": leave_policy_days_requirement,
                    "message": "For the requested leave type and given leave policty fetch the requirements of the leave like who can apply , when can someone apply things like this.And Requirements should be only for the requested leave type mentioned",
                    "max_turns": 1,
                    "summary_method": "last_msg",
                },
            ]
        )
        user_and_leave_details = chat_results[0].summary
        leave_policy_days_requirements = chat_results[1].summary
        return (
            extracted_info.summary,
            user_and_leave_details,
            leave_policy_days_requirements,
        )

    def decide_leave_approval_rejector(
        self,
        sender,
        leaveRequestDetails,
        userLeavesDetailsAndPolicyDetails,
        leavePolicyRequirement,
    ):

        leaveRequestDetailsDict = json.loads(leaveRequestDetails)
        userLeavesDetailsAndPolicyDetailsDict = json.loads(
            userLeavesDetailsAndPolicyDetails
        )
        leavePolicyRequirementDict = json.loads(leavePolicyRequirement)

        leave_result = leave_calculator_tool._run(
            leaveRequestDetailsDict["leave_dates"],
            userLeavesDetailsAndPolicyDetailsDict["leave_balance"],
            leaveRequestDetailsDict["date_of_the_email"],
            leavePolicyRequirementDict["days_notice"],
            leaveRequestDetailsDict["half_days"],
            leaveRequestDetailsDict["leave_type"],
        )

        if leave_result["status"] == "Rejected":
            email_draft = f"""
                here is the {leaveRequestDetails} , {userLeavesDetailsAndPolicyDetails} , {leavePolicyRequirement}
                After understanding we have reached to the decision I am attaching the decision

                {leave_result}.

                recipient of the email is : {sender}


                sender of the email is : "HR Department"

                Now you need to keeping in mind all the details and leave result specially draft an email body 
                for replying to leave request email statung the status of the leave request
                
                Do not include subject.We only need body of the email
                Provide the response in proper format.Paragraph and line changes should be proper
                """

            result = user_proxy.initiate_chat(
                recipient=email_drafter,
                message=str(email_draft),
                max_turns=1,
                summary_method="last_msg",
            )

            email = result.summary

            leave_result["email"] = email

        return leave_result
