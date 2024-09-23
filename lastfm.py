# Import basics
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables, so we don't leave tokens in our main program 
load_dotenv()

# Reference the .env and grab the API info we need to make proper calls
LASTFM_API_KEY = os.getenv('LASTFM_API_KEY')
LASTFM_USERNAME = os.getenv('LASTFM_USERNAME')
SLACK_TOKEN = os.getenv('SLACK_TOKEN')

# API endpoints
LASTFM_API_URL = 'http://ws.audioscrobbler.com/2.0/'
SLACK_API_URL = 'https://slack.com/api/users.profile.set'

# What are we listening to?
def get_current_track():
    params = {
        'method': 'user.getrecenttracks',
        'user': LASTFM_USERNAME,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
        'limit': 1
    }
    # Get request, store response
    response = requests.get(LASTFM_API_URL, params=params)
    data = response.json()
    # Parse our song, track, and artist, use the song and artist to set a status
    try:
        track = data['recenttracks']['track'][0]
        artist = track['artist']['#text']
        song = track['name']
        # This is our status! Change this to change what shows up!
        return f"I'm listening to {song} by {artist}!"
    except (KeyError, IndexError):
        return None

# Contact Slack's API, tell them to update our status
def update_slack_status(status_text):
    headers = {
        'Authorization': f'Bearer {SLACK_TOKEN}',
        'Content-Type': 'application/json'
    }
    # Change our status text to what we had on line 37, use the headphones emoji
    data = {
        'profile': {
            'status_text': status_text,
            'status_emoji': ':headphones:'
        }
    }
    response = requests.post(SLACK_API_URL, headers=headers, json=data)
    return response.status_code == 200

def main():
    # Let us know that it's starting
    print("Starting Slack status updater...")
    last_status = ""
    
    while True:
        current_track = get_current_track()
        # Update our status if it's not up to date
        if current_track and current_track != last_status:
            if update_slack_status(current_track):
                print(f"Updated status: {current_track}")
                last_status = current_track
                # If we can't update status:
            else:
                print("Failed to update Slack status")
                # Clear our current status if it doesn't match
        elif not current_track:
            if last_status:
                if update_slack_status(""):
                    print("Cleared Slack status")
                    last_status = ""
                else:
                    # Failure, something's wrong, and it's probably with you! (or me, but I'm not gonna admit that)
                    print("Failed to clear Slack status")
        
        # Wait for 1 minute before checking again
        # I wouldn't change this, you risk being rate-limited or
        # chewed out by Slack/Last.FM.
        time.sleep(60)

if __name__ == "__main__":
    main()