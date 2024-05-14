from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from db_operations import get_items_by_event_type, add_event_db_hub, retrieve_tokens, is_token_valid, generate_tokens
import os
import requests
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Configuration in the HubSpot App
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
HUBSPOT_ACCOUNT_ID = os.environ.get('HUBSPOT_ACCOUNT_ID')
SCOPES = 'crm.objects.marketing_events.read%20crm.objects.marketing_events.write'
REDIRECT_URI = 'http://localhost:5000/oauth-callback'  # Redirect URI configured in your HubSpot app

# Error handler for any unhandled exceptions 
@app.errorhandler(Exception)
def handle_error(error):
    response = jsonify({'error': str(error)})
    response.status_code = 500
    return response

# Render the start page for users to input their email
@app.route('/')
def index():
    return render_template('index.html')

# Route for the event form
@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/auth', methods=['POST'])
def auth():
    # Get the email from the form
    user_email = request.form.get('email')

    # Check if token already exists for the user email
    tokens = retrieve_tokens(user_email)

    if tokens:
        # If it exsist check if it valid (not expired)
        if is_token_valid(tokens):
            return render_template('form.html')
        else:
            token_proof = {
                'grant_type': 'refresh_token',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'refresh_token': tokens['refresh_token']
            }
            generate_tokens(token_proof, user_email)
            

    # Token doesn't exist, initiate the OAuth process
    auth_url = (
        'https://app.hubspot.com/oauth/authorize'
        f'?client_id={CLIENT_ID}'
        f'&scope={SCOPES}'
        f'&redirect_uri={REDIRECT_URI}'
    )
    response = redirect(auth_url)
    response.set_cookie('user_email', user_email)
    return response


@app.route('/oauth-callback', methods=['GET'])
def oauth_callback():
    # Handling the request sent by the server'
    auth_code = request.args.get('code')
    user_email = request.cookies.get('user_email')

    if auth_code:
        token_proof = {
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': auth_code
        }
    
        generate_tokens(token_proof, user_email)
        return render_template('form.html')

    else:
        return 'Authorization code not found', 400


# Listing the selected event type
@app.route('/events/<event_type>')
def list_events(event_type):
    events = get_items_by_event_type('Events', event_type)
    return render_template('events.html', events=events, event_type=event_type, page_title="Events")

@app.route('/add_event', methods=['POST'])
def add_event():
    # Generate a random event ID
    event_id = str(uuid.uuid4())
    # Get the info from the form
    event_name = request.form.get('eventName')
    event_type = request.form.get('eventType')
    start_datetime = request.form.get('startDateTime')
    end_datetime = request.form.get('endDateTime')
    event_organizer = request.form.get('eventOrganizer')
    event_description = request.form.get('eventDescription')


    # Parse the start_datetime string into a datetime object
    parsed_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
    parsed_end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')

    # Format the datetime object into ISO8601 format with microseconds for API
    iso_start_datetime = parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    iso_end_datetime = parsed_end_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    url = "https://api.hubapi.com/marketing/v3/marketing-events/events"

    
    # Define the request payload
    payload = {
        "startDateTime": iso_start_datetime,
        "eventOrganizer": event_organizer,
        "eventDescription": event_description,
        "eventName": event_name,
        "eventType": event_type,
        "endDateTime": iso_end_datetime,
        "externalAccountId": HUBSPOT_ACCOUNT_ID,
        "externalEventId": event_id,
    }
    # Retireve the access token
    access_token = retrieve_tokens(request.cookies.get('user_email'))["access_token"]
    # Define the request headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Send the POST request
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Add event to DynamoDB
    add_event_db_hub(event_name, event_type, start_datetime, end_datetime, event_organizer, event_description, event_id)
    
    return redirect(url_for('list_events', event_type=event_type))
   
