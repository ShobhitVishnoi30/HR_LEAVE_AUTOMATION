# HR Leave Management System

An automated HR leave management system using AI agents to process, analyze, and respond to employee leave requests.

## Table of Contents
- [Overview](#overview)
- [Key Components](#key-components)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Overview

This system leverages AI agents and custom tools to streamline the leave management process. It extracts details from leave request emails, fetches employee leave history and company policies, analyzes requests, makes approval decisions, and drafts response emails.

## Key Components

### AI Agents
- User Proxy Agent
- Leave Application Details Extractor
- Leave Application Details Extractor Critic
- Leave Approver Rejector
- Leave Approver Rejector Reviewer
- Leave Policy Days Requirement
- Email Drafter

### Custom Tools
- CustomFetcherTool: Fetches employee leave history, leave policy, and leave balance
- CustomLeaveCalculator: Calculates available leaves and checks policy compliance

## Features

- Automatic extraction of leave request details from emails
- Integration with Slack for notifications
- Leave balance tracking and policy enforcement
- AI-powered decision making for leave approvals/rejections
- Automated response email drafting

## Installation

1. Clone the repository:

   git clone https://github.com/your-username/hr-leave-management-system.git
  cd hr-leave-management-system

2. Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

3. Install the required dependencies:
pip install -r requirements.txt

4. Set up environment variables:
- Create a `.env` file in the project root directory
- Add the following variables (replace with your actual values):
  ```
  SLACK_TOKEN=your_slack_token
  OPENAI_API_KEY=your_openai_api_key
  PINECONE_API_KEY=your_pinecone_api_key
  PINECONE_ENVIRONMENT=your_pinecone_environment
  ```

5. Configure the database and Pinecone index (if applicable):
- [Add specific instructions for database setup]
- [Add specific instructions for Pinecone index setup]

6. Run the application:
python3 app.py

The application should now be running on `http://localhost:5001`.

## Usage

Once the application is running, it will automatically process incoming leave requests. The system will:

1. Extract details from leave request emails
2. Fetch the employee's leave history and relevant company policies
3. Analyze the leave request based on available balance and policy compliance
4. Make an approval or rejection decision
5. Draft a response email

Administrators can monitor the process through the configured Slack channel.

## API Endpoints

- `/insert_data` (POST): Inserts data from a PDF link into a specified namespace
- `/query` (GET): Allows querying a specific character or persona
- `/slack/event` (POST): Handles Slack events
- `/send_message` (POST): Sends messages to Slack

For detailed API documentation, refer to the Swagger UI available at `http://localhost:5001/apidocs/` when the application is running.

## Contributing

We welcome contributions to the HR Leave Management System! Here are some ways you can contribute:

1. Report bugs or suggest features by opening an issue
2. Improve documentation
3. Submit pull requests with bug fixes or new features

Please read our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

For any questions or support, please contact [your-email@example.com].

