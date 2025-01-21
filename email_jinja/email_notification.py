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
        Add a header image to the email message with proper Content-ID
        """
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
            
            # Create image attachment with correct MIME type
            img_type = imghdr.what(None, img_data)
            if img_type is None:
                img_type = 'jpeg'  # Default to JPEG if type cannot be determined
                
            image = MIMEImage(img_data, _subtype=img_type)
            
            # Set Content-ID with angle brackets
            content_id = 'header_image'
            image.add_header('Content-ID', f'<{content_id}>')
            image.add_header('Content-Disposition', 'inline', filename=f'header.{img_type}')
            
            # Attach the image to the message
            message.attach(image)
            
            print(f"Image attached successfully with Content-ID: {content_id}")
            return content_id
            
        except Exception as e:
            print(f"Error adding header image: {str(e)}")
            return None
    
    def send_notification(self, recipient_email, template_name, template_data, subject, header_image_path=None):
        try:
            # Create the root message
            message = MIMEMultipart('related')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            # Create the multipart/alternative child container
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)
            
            # Add header image if provided
            image_cid = None
            if header_image_path and os.path.exists(header_image_path):
                image_cid = self.add_header_image(message, header_image_path)
                if image_cid:
                    template_data['header_image_cid'] = image_cid
                    print(f"Image CID set in template data: {image_cid}")
            
            # Get template and render it
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            
            # Attach HTML part
            html_part = MIMEText(html_content, 'html')
            msg_alternative.attach(html_part)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
                print("Email sent successfully!")
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

# Save this as templates/notification.html
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
            display: block;
            margin: 0 auto 15px auto;
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
    </div>
</body>
</html>
"""

# Usage example
if __name__ == "__main__":
    notifier = EmailNotifier(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        sender_email='your-email@gmail.com',
        sender_password='your-app-specific-password'
    )
    
    template_data = {
        'title': 'Important Update',
        'recipient_name': 'John Doe',
        'message_body': 'Your project status has been updated.',
        'action_required': True,
        'action_details': 'Please review and approve the changes by EOD.',
        'deadline': 'September 15, 2024'
    }
    
    success = notifier.send_notification(
        recipient_email='recipient@example.com',
        template_name='notification.html',
        template_data=template_data,
        subject='Project Status Update',
        header_image_path='path/to/your/header.jpg'  # Make sure this path is correct
    )
