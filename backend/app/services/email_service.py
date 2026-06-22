import logging
from typing import List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service to handle email notifications"""
    
    def __init__(self):
        # We use dummy settings for local testing, 
        # or configure real SMTP if settings are provided
        self.smtp_server = getattr(settings, "smtp_server", "smtp.example.com")
        self.smtp_port = getattr(settings, "smtp_port", 587)
        self.smtp_user = getattr(settings, "smtp_user", "test@example.com")
        self.smtp_password = getattr(settings, "smtp_password", "password")
        self.sender_email = getattr(settings, "sender_email", "noreply@aivalidator.com")
        
    async def send_analysis_completion_email(self, user_email: str, idea_title: str, overall_score: float):
        """Send an email notifying the user that their analysis is complete"""
        subject = f"Your Analysis for '{idea_title}' is Complete!"
        
        html_content = f"""
        <html>
            <body>
                <h2>Great news!</h2>
                <p>The AI analysis for your business idea <strong>{idea_title}</strong> has been completed.</p>
                <p><strong>Overall Score: {overall_score}/10</strong></p>
                <p>Log in to your dashboard to view the full comprehensive report, including market analysis, financial projections, and actionable recommendations.</p>
                <br/>
                <p>Best regards,</p>
                <p>The AI Business Validator Team</p>
            </body>
        </html>
        """
        
        await self._send_email(user_email, subject, html_content)
        
    async def _send_email(self, to_email: str, subject: str, html_content: str):
        """Internal method to send the email"""
        # Note: In a real production app, we would use aiosmtplib or a service like SendGrid/AWS SES.
        # Here we mock the email sending to avoid blocking or requiring real credentials for the demo.
        logger.info(f"Mock sending email to {to_email}")
        logger.info(f"Subject: {subject}")
        
        # Uncomment below to actually send if credentials are provided:
        '''
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.sender_email
            msg["To"] = to_email
            
            part = MIMEText(html_content, "html")
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())
            logger.info("Email sent successfully!")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
        '''

email_service = EmailService()
