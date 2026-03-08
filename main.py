import smtplib
import csv
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailAutomationTool:
    def __init__(self, sender_email, sender_password):
        """
        Initialize the email automation tool with Gmail credentials
        
        Args:
            sender_email (str): Gmail address
            sender_password (str): Gmail app password
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
    
    def send_bulk_emails(self, recipient_list, subject, body, attachments=None):
        """
        Send bulk emails to multiple recipients
        
        Args:
            recipient_list (list): List of email addresses
            subject (str): Email subject
            body (str): Email body
            attachments (list): Optional list of file paths to attach
        
        Returns:
            dict: Results with sent/failed counts
        """
        sent = 0
        failed = 0
        failed_emails = []
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            print("✓ Successfully connected to Gmail!")
            
            for recipient in recipient_list:
                try:
                    message = MIMEMultipart()
                    message["From"] = self.sender_email
                    message["To"] = recipient
                    message["Subject"] = subject
                    
                    message.attach(MIMEText(body, "html"))
                    
                    # Add attachments if provided
                    if attachments:
                        for attachment in attachments:
                            self._attach_file(message, attachment)
                    
                    server.send_message(message)
                    sent += 1
                    print(f"✓ Email sent to {recipient}")
                    
                except Exception as e:
                    failed += 1
                    failed_emails.append(recipient)
                    print(f"✗ Failed to send to {recipient}: {str(e)}")
            
            server.quit()
            
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return {"error": str(e)}
        
        results = {
            "total_sent": sent,
            "total_failed": failed,
            "failed_emails": failed_emails
        }
        
        return results
    
    def send_from_csv(self, csv_file, subject, body, attachments=None):
        """
        Send emails to recipients from a CSV file
        
        Args:
            csv_file (str): Path to CSV file with email addresses
            subject (str): Email subject
            body (str): Email body
            attachments (list): Optional list of file paths to attach
        
        Returns:
            dict: Results with sent/failed counts
        """
        recipient_list = []
        
        try:
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:
                        recipient_list.append(row[0].strip())
            
            print(f"✓ Loaded {len(recipient_list)} email addresses from {csv_file}")
            return self.send_bulk_emails(recipient_list, subject, body, attachments)
            
        except FileNotFoundError:
            print(f"✗ CSV file not found: {csv_file}")
            return {"error": f"File not found: {csv_file}"}
    
    @staticmethod
    def _attach_file(message, file_path):
        """Attach a file to the email"""
        try:
            with open(file_path, 'rb') as attachment:
                part = MIMEMultipart()
                part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                message.attach(part)
        except FileNotFoundError:
            print(f"✗ Attachment not found: {file_path}")


def main():
    """Main function to demonstrate email automation"""
    
    # Get credentials from environment variables
    sender_email = os.getenv("GMAIL_EMAIL")
    sender_password = os.getenv("GMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        print("✗ Please set GMAIL_EMAIL and GMAIL_PASSWORD in .env file")
        return
    
    # Initialize the tool
    email_tool = EmailAutomationTool(sender_email, sender_password)
    
    # Example 1: Send to single list
    print("\n--- Sending Bulk Emails ---")
    recipients = ["recipient1@gmail.com", "recipient2@gmail.com", "recipient3@gmail.com"]
    subject = "Welcome to Email Automation!"
    body = """
    <h2>Hello,</h2>
    <p>This is an automated email sent using the Email Automation Tool.</p>
    <p>Best regards,</p>
    <p>Your Name</p>
    """
    
    results = email_tool.send_bulk_emails(recipients, subject, body)
    
    print("\n--- Results ---")
    print(f"Total Sent: {results['total_sent']}")
    print(f"Total Failed: {results['total_failed']}")
    if results['failed_emails']:
        print(f"Failed Emails: {', '.join(results['failed_emails'])}")


if __name__ == "__main__":
    main()