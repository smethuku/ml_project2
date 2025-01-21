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
            
            img_type = imghdr.what(None, img_data)
            if img_type is None:
                img_type = 'jpeg'
                
            image = MIMEImage(img_data, _subtype=img_type)
            content_id = 'header_image'
            image.add_header('Content-ID', f'<{content_id}>')
            image.add_header('Content-Disposition', 'inline', filename=f'header.{img_type}')
            message.attach(image)
            return content_id
            
        except Exception as e:
            print(f"Error adding header image: {str(e)}")
            return None
    
    def send_notification(self, recipient_email, template_name, template_data, subject, header_image_path=None):
        try:
            message = MIMEMultipart('related')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)
            
            if header_image_path and os.path.exists(header_image_path):
                image_cid = self.add_header_image(message, header_image_path)
                if image_cid:
                    template_data['header_image_cid'] = image_cid
            
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            
            html_part = MIMEText(html_content, 'html')
            msg_alternative.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
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
        .header img {
            width: 300px;
            height: auto;
            display: block;
            margin: 0 auto 15px auto;
        }
        .horizontal-line {
            border-top: 1px solid #ccc;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f5f5f5;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Image -->
        {% if header_image_cid %}
        <div class="header">
            <img src="cid:{{ header_image_cid }}" alt="Header Image">
        </div>
        {% endif %}

        <!-- First Line -->
        <div class="horizontal-line"></div>
        
        <!-- Content Section 1 -->
        <div class="content">
            {{ content_section_1 }}
        </div>

        <!-- Second Line -->
        <div class="horizontal-line"></div>
        
        <!-- Table -->
        <table>
            <thead>
                <tr>
                    <th>Col1</th>
                    <th>Col2</th>
                    <th>Col3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ table_row1.col1 }}</td>
                    <td>{{ table_row1.col2 }}</td>
                    <td>{{ table_row1.col3 }}</td>
                </tr>
                <tr>
                    <td>{{ table_row2.col1 }}</td>
                    <td>{{ table_row2.col2 }}</td>
                    <td>{{ table_row2.col3 }}</td>
                </tr>
            </tbody>
        </table>

        <!-- Final Content -->
        <div class="content">
            {{ final_content }}
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
        'content_section_1': 'This is the content that appears after the first line.',
        'table_row1': {
            'col1': 'Row 1 Col 1',
            'col2': 'Row 1 Col 2',
            'col3': 'Row 1 Col 3'
        },
        'table_row2': {
            'col1': 'Row 2 Col 1',
            'col2': 'Row 2 Col 2',
            'col3': 'Row 2 Col 3'
        },
        'final_content': 'This is the content that appears after the table.'
    }
    
    success = notifier.send_notification(
        recipient_email='recipient@example.com',
        template_name='notification.html',
        template_data=template_data,
        subject='Formatted Email with Table',
        header_image_path='path/to/your/header.jpg'
    )
