from email.mime.image import MIMEImage
import os

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """Existing initialization code..."""
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.image_dir = os.path.join(os.path.dirname(__file__), 'images')  # Add this line
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=True
        )

    def send_notification(self, recipient_email, template_name, template_data, subject, header_image_name=None):
        try:
            # Create the root message
            message = MIMEMultipart('related')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email

            # Create the multipart/alternative child container
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)

            # Render and attach HTML
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            html_part = MIMEText(html_content, 'html')
            msg_alternative.attach(html_part)

            # Attach the image if provided
            if header_image_name:
                image_path = os.path.join(self.image_dir, header_image_name)
                if os.path.exists(image_path):
                    with open(image_path, 'rb') as img:
                        img_data = img.read()
                    image = MIMEImage(img_data)
                    image.add_header('Content-ID', '<header_image>')
                    message.attach(image)
                else:
                    print(f"Warning: Image file not found at {image_path}")

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
