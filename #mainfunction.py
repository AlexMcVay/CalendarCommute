# AlexMcVay\CalendarCommute\#mainfunction.py
# DONE: pip install google-api-python-client googlemaps
# TODO: Add error handling for Google Maps API requests
# TODO: Customize the behavior for specific edge cases as needed
# TODO: Adjust the maximum number of events retrieved or modify event filtering criteria if required
# TODO: Uncomment the line to actually create the travel event once testing is complete
# TODO: Add notifications or reminders to notify the user about upcoming events and travel times
# TODO: Generate a summary report of upcoming events with commute times for better planning
# TODO: Add any additional customization or features as required
# TODO: Add error handling for Google Calendar API requests
# TODO: Customize the behavior for specific edge cases as needed
# TODO: Adjust the maximum number of events retrieved or modify event filtering criteria if required
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import googlemaps

# Set up authentication for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'path_to_service_account_file.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# Build the service for Google Calendar API
service = build('calendar', 'v3', credentials=credentials)

# Set up authentication for Google Maps API
google_maps_api_key = YOUR_GOOGLE_MAPS_API_KEY  # TODO: Replace with your actual Google Maps API key
gmaps = googlemaps.Client(key=google_maps_api_key)
home = 'Your home location' # TODO: Replace with actual home location

# Function to calculate commute time between two locations
# TODO: Add error handling for Google Maps API requests
"""
    A function to calculate the commute time between the given origin and destination using the Google Maps API.
    Parameters:
    - origin: the starting location
    - destination: the destination location
    Return:
    - commute_time_minutes: the commute time in minutes
    """
def calculate_commute_time(origin, destination):
    # TODO: Handle errors from the Google Maps API request
    result = gmaps.distance_matrix(origin, destination, mode="driving", departure_time="now")
    commute_time_seconds = result['rows'][0]['elements'][0]['duration']['value']
    commute_time_minutes = commute_time_seconds // 60
    return commute_time_minutes

# Get events from calendar
calendar_id = 'your_calendar_id@group.calendar.google.com'  # TODO: Replace with your calendar ID
now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

try:
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
except Exception as e:
    print(f"Error retrieving events from Google Calendar API: {e}")
    events = []

# Initialize home location
home = "Your home location"  # TODO: Replace with your home location

if not events:
    print('No upcoming events found.')

prior_event = None
prior_location = home  # Initial location is home 

for event in events:
    # Check if it's an all-day event
    if 'dateTime' not in event['start'] or 'dateTime' not in event['end']:
        print("Skipping all-day event:", event['summary'])
        continue

    start = event['start'].get('dateTime')
    end = event['end'].get('dateTime')

    # Handle events with different time zones
    start_time = datetime.fromisoformat(start)
    end_time = datetime.fromisoformat(end)
    if start_time.tzinfo is None or end_time.tzinfo is None:
        print("Skipping event with missing time zone information:", event['summary'])
        continue

    # Get event location
    location = event.get('location')
    # If location is not provided, assume it doesn't change from prior event's location
    # or use home location if prior event's location not available or if there's more than 4 hours between events
    if not location and prior_event:
        prior_end = prior_event['end'].get('dateTime')
        prior_end_time = datetime.fromisoformat(prior_end)
        if (start_time - prior_end_time) < timedelta(hours=4):
            location = prior_location

    # Use home location if no location provided or if it's a link
    if not location or location.startswith('http'):
        location = home

    # Calculate commute time
    origin = "Your current location"  # TODO: Replace with your actual current location
    destination = location
    try:
        commute_time = calculate_commute_time(origin, destination)
        print("Commute time to the event:", commute_time, "minutes")
    except Exception as e:
        print(f"Error calculating commute time: {e}")
        continue

    # Create new event for travel time
    travel_event = {
        'summary': 'Travel to ' + event['summary'],  # Customize the summary of the travel event
        'description': 'Commute time: {} minutes'.format(commute_time),  # Customize the description of the travel event
        'start': {'dateTime': (start_time - timedelta(minutes=commute_time)).isoformat()},
        'end': {'dateTime': start},
        # You can include additional details such as location or reminders as needed
        'location': 'Your travel destination',
        'reminders': {
             'useDefault': False,
             'overrides': [
                 {'method': 'popup', 'minutes': 30},
                 {'method': 'email', 'minutes': 60}
             ]
         }
    }

    # TODO: Uncomment the line below to actually create the travel event
    # service.events().insert(calendarId=calendar_id, body=travel_event).execute()

    prior_event = event
    prior_location = location