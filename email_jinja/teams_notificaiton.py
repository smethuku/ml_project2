import requests
import json

def send_teams_notification(webhook_url, subject, message):
    """
    Send a notification to Microsoft Teams channel
    
    Args:
        webhook_url (str): The webhook URL for your Teams channel
        subject (str): Subject/title of the message
        message (str): Content of the message
    """
    teams_message = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": subject,
        "sections": [{
            "activityTitle": subject,
            "text": message
        }]
    }
    
    response = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(teams_message)
    )
    
    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")

# Example usage
webhook_url = "YOUR_WEBHOOK_URL"  # You'll need to replace this with your actual webhook URL
subject = "Test Notification"
message = "This is a test notification message."

send_teams_notification(webhook_url, subject, message)
