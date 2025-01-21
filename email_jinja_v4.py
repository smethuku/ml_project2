# email_notification.py
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
import imghdr

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
    
    def add_header_image(self, message, image_path):
        """
        Add a header image to the email message
        
        Args:
            message (MIMEMultipart): The email message object
            image_path (str): Path to the header image file
        
        Returns:
            str: Content ID for the image to be used in the HTML template
        """
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            
        # Generate a unique content ID for the image
        image_cid = 'header_image'
        
        # Create image attachment
        image = MIMEImage(img_data, _subtype=imghdr.what(None, img_data))
        image.add_header('Content-ID', f'<{image_cid}>')
        image.add_header('Content-Disposition', 'inline')
        
        # Attach the image
        message.attach(image)
        
        return image_cid
    
    def send_notification(self, recipient_email, template_name, template_data, subject, header_image_path=None):
        """
        Send an email notification using a specified template
        
        Args:
            recipient_email (str): Recipient's email address
            template_name (str): Name of the template file (e.g., 'notification.html')
            template_data (dict): Dictionary containing template variables
            subject (str): Email subject line
            header_image_path (str, optional): Path to the header image file
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('related')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            # Create the HTML message part
            message_alternative = MIMEMultipart('alternative')
            message.attach(message_alternative)
            
            # Add header image if provided
            if header_image_path:
                image_cid = self.add_header_image(message, header_image_path)
                template_data['header_image_cid'] = image_cid
            
            # Get template and render it with provided data
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            message_alternative.attach(html_part)
            
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
            text-align: center;
        }
        .header img {
            max-width: 100%;
            height: auto;
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
            {% if header_image_cid %}
            <img src="cid:{{ header_image_cid }}" alt="Header Image">
            {% endif %}
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
        'contact_info': 'support@company.com',
        'header_image_url': 'https://your-domain.com/path/to/header-image.jpg'  # Add your image URL here
    }
    
    # Send notification with header image
    success = notifier.send_notification(
        recipient_email='recipient@example.com',
        template_name='notification.html',
        template_data=template_data,
        subject='Project Status Update',
        header_image_path='path/to/your/header.jpg'  # Add your image path here
    )
    
    if success:
        print("Notification sent successfully!")
    else:
        print("Failed to send notification.")
