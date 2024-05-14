import boto3
import os
import requests
from datetime import datetime

# Configuration in the HubSpot App
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
HUBSPOT_ACCOUNT_ID = os.environ.get('HUBSPOT_ACCOUNT_ID')
SCOPES = 'crm.objects.marketing_events.read%20crm.objects.marketing_events.write'
REDIRECT_URI = 'http://localhost:5000/oauth-callback'  # Redirect URI configured in your HubSpot app


# Required to connect to AWS Dynamo DB
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
TOKEN_TABLE = os.environ.get('TOKEN_TABLE') # Your created table in DynamoDB for storing tokens
EVENT_TABLE = os.environ.get('EVENT_TABLE')  # Your created table in DynamoDB for storing events

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-1',
                        aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Retrieve tokens from DynamoDB
def retrieve_tokens(user_email):
    try:
        response = dynamodb.get_item(TableName=TOKEN_TABLE, Key={'UserEmail': {'S': user_email}})
        item = response.get('Item')
        if item:
            tokens = {
                'access_token': item['AccessToken']['S'],
                'refresh_token': item['RefreshToken']['S'],
                'expires_in': item['ExpiresIn']['S']
            }
            return tokens
    except Exception as e:
        raise ValueError(f"Error retrieving tokens: {str(e)}")
    
def is_token_valid(tokens):
    try:
        # Extract the expiration time of a token
        expiration_time = float(tokens['expires_in'])
        #Get time now and turn it into seconds
        current_time = datetime.now()
        current_time_seconds = current_time.timestamp()

        # Check if the current time is before expiration time
        return current_time < expiration_time
    except Exception as e:
        raise ValueError(f"Error checking token validity: {str(e)}")

# Requests for tokens
def generate_tokens(token_proof, user_email):
    try:
        response = requests.post('https://api.hubapi.com/oauth/v1/token', data=token_proof)
        tokens = response.json()
        store_tokens(user_email, tokens)
    except Exception as e:
        raise ValueError(f"Error generating tokens: {str(e)}")
    
# Storing token data in DynamoDB
def store_tokens(user_email, tokens):
     # Get the current time
    current_time = datetime.now()
    current_time_seconds = current_time.timestamp()

    # Calculate the expiration time by adding expires_in_seconds to the current time
    try:
        expiration_time = current_time_seconds + float(tokens['expires_in'])

        response = dynamodb.put_item(
            TableName=TOKEN_TABLE,
            Item={
                'UserEmail': {'S': user_email},
                'AccessToken': {'S': tokens['access_token']},
                'RefreshToken': {'S': tokens['refresh_token']},
                'ExpiresIn': {'S': str(expiration_time) }
            })
    except Exception as e:
        raise ValueError(f"Error storing tokens: {str(e)}")


# Get events by the selected type
def get_items_by_event_type(table_name, event_type):
    try:
        response = dynamodb.query(
            TableName=EVENT_TABLE,
            IndexName='EventTypeIndex', 
            KeyConditionExpression='eventType = :val',
            ExpressionAttributeValues={
                ':val': {'S': event_type}
            }
        )
        
        items = response.get('Items', [])
        return items
    except Exception as e:
        raise ValueError(f"Error retrieving items by event type: {str(e)}")


# Add the event to DynamoDB
def add_event_db_hub(event_name, event_type, start_datetime, end_datetime, event_organizer, event_description, event_id):
    response = dynamodb.put_item(
        TableName=EVENT_TABLE,
        Item={
            'eventID': {'S': event_id},
            'eventName': {'S': event_name},
            'eventType': {'S': event_type},
            'startDateTime': {'S': start_datetime},
            'endDateTime': {'S': end_datetime},
            'eventOrganizer': {'S': event_organizer},
            'eventDescription': {'S': event_description}
        }
    )
    
    return response