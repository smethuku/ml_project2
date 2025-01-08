# email_notification.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import os

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize the email notifier with SMTP server details
        
        Args:
            smtp_server (str): SMTP server address (e.g., 'smtp.gmail.com')
            smtp_port (int): SMTP port (e.g., 587 for TLS)
            sender_email (str): Sender's email address
            sender_password (str): Sender's email password or app-specific password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # Setup Jinja environment
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )
    
    def send_notification(self, recipient_email, template_name, template_data, subject):
        """
        Send an email notification using a specified template
        
        Args:
            recipient_email (str): Recipient's email address
            template_name (str): Name of the template file (e.g., 'notification.html')
            template_data (dict): Dictionary containing template variables
            subject (str): Email subject line
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Get template and render it with provided data
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Connect to SMTP server and send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

# Example template structure (save as templates/notification.html):
"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #f8f9fa;
            padding: 15px;
            margin-bottom: 20px;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{{ title }}</h2>
        </div>
        
        <div class="content">
            <p>Hello {{ recipient_name }},</p>
            
            <p>{{ message_body }}</p>
            
            {% if action_required %}
            <p><strong>Action Required:</strong> {{ action_details }}</p>
            {% endif %}
            
            {% if deadline %}
            <p><strong>Deadline:</strong> {{ deadline }}</p>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>This is an automated notification. Please do not reply to this email.</p>
            {% if contact_info %}
            <p>For support: {{ contact_info }}</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# Usage example:
if __name__ == "__main__":
    # Initialize the notifier
    notifier = EmailNotifier(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        sender_email='your-email@gmail.com',
        sender_password='your-app-specific-password'
    )
    
    # Example template data
    template_data = {
        'title': 'Important Update',
        'recipient_name': 'John Doe',
        'message_body': 'Your project status has been updated.',
        'action_required': True,
        'action_details': 'Please review and approve the changes by EOD.',
        'deadline': 'September 15, 2024',
        'contact_info': 'support@company.com'
    }
    
    # Send notification
    success = notifier.send_notification(
        recipient_email='recipient@example.com',
        template_name='notification.html',
        template_data=template_data,
        subject='Project Status Update'
    )
    
    if success:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")
