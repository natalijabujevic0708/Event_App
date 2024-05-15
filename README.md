# Marketing Event Management Application

This application is designed to create marketing events in HubSpot and store event details in DynamoDB. It allows users to input event information, such as event name, type, start and end dates, organizer, and description, through a user-friendly interface. The application utilizes Flask for the backend, allowing for easy integration with the HubSpot API and DynamoDB.

## Summary

This project was inspired by questions found on the HubSpot Community forums ([Question 1](https://community.hubspot.com/t5/APIs-Integrations/Marketing-Events-API-Search-Returns-No-Results/m-p/519352), [Question 2](https://community.hubspot.com/t5/APIs-Integrations/Marketing-events-api-get-list-of-events-with-full-details/m-p/866596)). The goal was to create an application that could interact with the HubSpot Marketing Events API to create marketing events. Additionally, the application stores event details in DynamoDB, providing an option to retrieve all created events with full details.

## Technologies Used

- **Flask**: Flask is a micro web framework for Python used to build web applications. It provides tools, libraries, and patterns to create web applications quickly and easily.
- **AWS DynamoDB**: DynamoDB is a fully managed NoSQL database service provided by AWS. It offers low-latency performance at any scale and is designed to handle large amounts of traffic.
- **HubSpot API**: The HubSpot API allows developers to integrate their applications with HubSpot's marketing, sales, and service software. It provides access to a wide range of HubSpot features, including marketing events.
- **Python Requests Library**: The Requests library is used to send HTTP requests easily in Python. It is used to interact with the HubSpot API to create and retrieve marketing events.
- **Boto3**: Boto3 is the AWS SDK for Python. It allows Python developers to write software that makes use of services like Amazon S3 and DynamoDB. In this project, Boto3 is used to interact with DynamoDB to store and retrieve event data.

## Overview of app.py

The `app.py` file contains the main Flask application code. Here's a summary of its functionality:

- **OAuth Authentication**: Handles user authentication using OAuth 2.0. Users are redirected to HubSpot's authentication page, where they can authorize the application to access their HubSpot account.
<img width="943" alt="image" src="https://github.com/natalijabujevic0708/Event_App/assets/67863074/57da8893-8813-4e27-834c-6b64631f3ea8">
<img width="1899" alt="image" src="https://github.com/natalijabujevic0708/Event_App/assets/67863074/1e8b6ff7-54de-44e1-acd7-4df2abc97346">

- **Event Form**: Renders a form where users can input event details, such as name, type, dates, organizer, and description.
  <img width="1897" alt="image" src="https://github.com/natalijabujevic0708/Event_App/assets/67863074/6b915c22-d9df-4a0b-97f6-ff4181458a61">

- **Adding Events**: Handles the submission of event data from the form. The data is then sent to the HubSpot API to create the event. Additionally, the event details are stored in DynamoDB.
  
https://github.com/natalijabujevic0708/Event_App/assets/67863074/248f1024-a0e5-4258-bc2e-d6906dd116d8


- **Listing Events**: Retrieves events from DynamoDB based on the selected event type and displays them on a webpage.
  
https://github.com/natalijabujevic0708/Event_App/assets/67863074/94606448-937f-440f-97b6-1035887b73eb

## db_operations.py

The `db_operations.py` file contains functions for interacting with DynamoDB. These functions include retrieving tokens, checking token validity, generating tokens, storing tokens, retrieving events by event type, and adding events to DynamoDB.

## Setup Instructions

To set up and run the application locally, follow these steps:

1. Clone the repository to your local machine.
2. Install the required dependencies by running `pip install -r requirements.txt`.
3. Set up environment variables for the HubSpot and AWS credentials in a `.env` file.
4. Run the Flask application using `python app.py`.
5. Access the application through your web browser at `http://localhost:5000`.

## Additional Notes

- Make sure to configure the necessary environment variables for authentication and database access.
- Ensure that your HubSpot account has the required permissions to access the Marketing Events API.

