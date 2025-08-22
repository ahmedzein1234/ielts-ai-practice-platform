"""Email notification tasks for the worker system."""

import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from celery import current_task
import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from workers.celery_app import celery_app
from workers.config import settings

logger = structlog.get_logger()


class EmailService:
    """Email service for sending notifications."""
    
    def __init__(self):
        """Initialize email service."""
        self.template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Initialize email provider
        if settings.email_provider == "sendgrid" and settings.sendgrid_api_key:
            try:
                from sendgrid import SendGridAPIClient
                self.sendgrid_client = SendGridAPIClient(api_key=settings.sendgrid_api_key)
                self.provider = "sendgrid"
            except ImportError:
                logger.warning("SendGrid not available, falling back to SMTP")
                self.provider = "smtp"
        else:
            self.provider = "smtp"
    
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email using the configured provider."""
        try:
            if self.provider == "sendgrid":
                return self._send_via_sendgrid(to_email, subject, html_content, text_content)
            else:
                return self._send_via_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error("Failed to send email", error=str(e), to_email=to_email)
            return False
    
    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email via SendGrid."""
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            from_email = Email(settings.from_email, settings.from_name)
            to_email_obj = To(to_email)
            
            mail = Mail(from_email, to_email_obj, subject, Content("text/html", html_content))
            
            if text_content:
                mail.add_content(Content("text/plain", text_content))
            
            response = self.sendgrid_client.send(mail)
            
            logger.info("Email sent via SendGrid", to_email=to_email, status_code=response.status_code)
            return response.status_code in [200, 201, 202]
            
        except Exception as e:
            logger.error("SendGrid email failed", error=str(e), to_email=to_email)
            return False
    
    def _send_via_smtp(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email via SMTP."""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            if not all([settings.smtp_host, settings.smtp_username, settings.smtp_password]):
                logger.warning("SMTP configuration incomplete, simulating email send")
                return True  # Simulate success for development
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.from_name} <{settings.from_email}>"
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Send email
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_use_tls:
                    server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
            
            logger.info("Email sent via SMTP", to_email=to_email)
            return True
            
        except Exception as e:
            logger.error("SMTP email failed", error=str(e), to_email=to_email)
            return False
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render an email template."""
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error("Failed to render template", template=template_name, error=str(e))
            return f"<h1>Error rendering template: {template_name}</h1>"


# Global email service instance
email_service = EmailService()


@celery_app.task(bind=True, name="workers.tasks.email.send_welcome_email")
def send_welcome_email_task(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send welcome email to new users."""
    start_time = time.time()
    
    try:
        user_email = user_data.get("email")
        user_name = user_data.get("name", "there")
        
        logger.info(
            "Starting welcome email task",
            task_id=self.request.id,
            user_email=user_email
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Sending welcome email", "progress": 10}
        )
        
        # Render email template
        context = {
            "user_name": user_name,
            "welcome_url": f"{settings.api_gateway_url}/welcome",
            "support_email": "support@ielts-ai.com"
        }
        
        html_content = email_service.render_template("welcome.html", context)
        text_content = email_service.render_template("welcome.txt", context)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Email rendered", "progress": 50}
        )
        
        # Send email
        subject = "Welcome to IELTS AI Platform!"
        success = email_service.send_email(user_email, subject, html_content, text_content)
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "user_email": user_email,
            "email_sent": success,
            "processing_time": processing_time,
            "status": "completed" if success else "failed",
            "timestamp": time.time()
        }
        
        if success:
            logger.info(
                "Welcome email sent successfully",
                task_id=self.request.id,
                user_email=user_email
            )
        else:
            logger.error(
                "Welcome email failed",
                task_id=self.request.id,
                user_email=user_email
            )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Welcome email task failed",
            task_id=self.request.id,
            user_email=user_data.get("email"),
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.email.send_scoring_complete")
def send_scoring_complete_task(self, scoring_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send email notification when scoring is complete."""
    start_time = time.time()
    
    try:
        user_email = scoring_data.get("user_email")
        user_name = scoring_data.get("user_name", "there")
        band_score = scoring_data.get("band_score")
        task_type = scoring_data.get("task_type")
        
        logger.info(
            "Starting scoring complete email task",
            task_id=self.request.id,
            user_email=user_email,
            band_score=band_score
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Sending scoring complete email", "progress": 10}
        )
        
        # Render email template
        context = {
            "user_name": user_name,
            "band_score": band_score,
            "task_type": task_type,
            "dashboard_url": f"{settings.api_gateway_url}/dashboard",
            "support_email": "support@ielts-ai.com"
        }
        
        html_content = email_service.render_template("scoring_complete.html", context)
        text_content = email_service.render_template("scoring_complete.txt", context)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Email rendered", "progress": 50}
        )
        
        # Send email
        subject = f"Your IELTS {task_type} score is ready!"
        success = email_service.send_email(user_email, subject, html_content, text_content)
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "user_email": user_email,
            "band_score": band_score,
            "email_sent": success,
            "processing_time": processing_time,
            "status": "completed" if success else "failed",
            "timestamp": time.time()
        }
        
        if success:
            logger.info(
                "Scoring complete email sent successfully",
                task_id=self.request.id,
                user_email=user_email,
                band_score=band_score
            )
        else:
            logger.error(
                "Scoring complete email failed",
                task_id=self.request.id,
                user_email=user_email
            )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Scoring complete email task failed",
            task_id=self.request.id,
            user_email=scoring_data.get("user_email"),
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.email.send_weekly_report")
def send_weekly_report_task(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send weekly progress report to users."""
    start_time = time.time()
    
    try:
        user_email = report_data.get("user_email")
        user_name = report_data.get("user_name", "there")
        weekly_stats = report_data.get("weekly_stats", {})
        
        logger.info(
            "Starting weekly report email task",
            task_id=self.request.id,
            user_email=user_email
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Sending weekly report", "progress": 10}
        )
        
        # Render email template
        context = {
            "user_name": user_name,
            "weekly_stats": weekly_stats,
            "dashboard_url": f"{settings.api_gateway_url}/dashboard",
            "support_email": "support@ielts-ai.com"
        }
        
        html_content = email_service.render_template("weekly_report.html", context)
        text_content = email_service.render_template("weekly_report.txt", context)
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Email rendered", "progress": 50}
        )
        
        # Send email
        subject = "Your IELTS AI Platform Weekly Report"
        success = email_service.send_email(user_email, subject, html_content, text_content)
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "user_email": user_email,
            "email_sent": success,
            "processing_time": processing_time,
            "status": "completed" if success else "failed",
            "timestamp": time.time()
        }
        
        if success:
            logger.info(
                "Weekly report email sent successfully",
                task_id=self.request.id,
                user_email=user_email
            )
        else:
            logger.error(
                "Weekly report email failed",
                task_id=self.request.id,
                user_email=user_email
            )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Weekly report email task failed",
            task_id=self.request.id,
            user_email=report_data.get("user_email"),
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.email.send_batch_emails")
def send_batch_emails_task(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send multiple emails in batch."""
    start_time = time.time()
    
    try:
        emails = batch_data.get("emails", [])
        total_emails = len(emails)
        
        logger.info(
            "Starting batch email task",
            task_id=self.request.id,
            total_emails=total_emails
        )
        
        results = []
        successful = 0
        failed = 0
        
        for i, email_data in enumerate(emails):
            try:
                # Update progress
                progress = int((i / total_emails) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "status": f"Sending email {i+1}/{total_emails}",
                        "progress": progress,
                        "completed": i,
                        "total": total_emails
                    }
                )
                
                # Send individual email
                email_type = email_data.get("type", "generic")
                if email_type == "welcome":
                    result = send_welcome_email_task.apply_async(
                        args=[email_data],
                        queue=settings.email_queue
                    )
                elif email_type == "scoring_complete":
                    result = send_scoring_complete_task.apply_async(
                        args=[email_data],
                        queue=settings.email_queue
                    )
                elif email_type == "weekly_report":
                    result = send_weekly_report_task.apply_async(
                        args=[email_data],
                        queue=settings.email_queue
                    )
                else:
                    # Generic email
                    result = send_generic_email_task.apply_async(
                        args=[email_data],
                        queue=settings.email_queue
                    )
                
                # Wait for result
                email_result = result.get(timeout=60)  # 1 minute timeout
                results.append(email_result)
                successful += 1
                
            except Exception as e:
                logger.error(
                    "Failed to send email in batch",
                    user_email=email_data.get("user_email"),
                    error=str(e)
                )
                failed += 1
                results.append({
                    "user_email": email_data.get("user_email"),
                    "status": "failed",
                    "error": str(e)
                })
        
        processing_time = time.time() - start_time
        
        batch_result = {
            "batch_id": batch_data.get("batch_id"),
            "task_id": self.request.id,
            "total_emails": total_emails,
            "successful": successful,
            "failed": failed,
            "results": results,
            "processing_time": processing_time,
            "status": "completed",
            "timestamp": time.time()
        }
        
        logger.info(
            "Batch email completed",
            task_id=self.request.id,
            successful=successful,
            failed=failed,
            processing_time=processing_time
        )
        
        return batch_result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Batch email failed",
            task_id=self.request.id,
            error=str(e),
            processing_time=processing_time
        )
        raise


@celery_app.task(bind=True, name="workers.tasks.email.send_generic_email")
def send_generic_email_task(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send a generic email with custom content."""
    start_time = time.time()
    
    try:
        user_email = email_data.get("user_email")
        subject = email_data.get("subject")
        html_content = email_data.get("html_content")
        text_content = email_data.get("text_content")
        
        logger.info(
            "Starting generic email task",
            task_id=self.request.id,
            user_email=user_email,
            subject=subject
        )
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Sending generic email", "progress": 10}
        )
        
        # Send email
        success = email_service.send_email(user_email, subject, html_content, text_content)
        
        processing_time = time.time() - start_time
        
        result = {
            "task_id": self.request.id,
            "user_email": user_email,
            "subject": subject,
            "email_sent": success,
            "processing_time": processing_time,
            "status": "completed" if success else "failed",
            "timestamp": time.time()
        }
        
        if success:
            logger.info(
                "Generic email sent successfully",
                task_id=self.request.id,
                user_email=user_email
            )
        else:
            logger.error(
                "Generic email failed",
                task_id=self.request.id,
                user_email=user_email
            )
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(
            "Generic email task failed",
            task_id=self.request.id,
            user_email=email_data.get("user_email"),
            error=str(e),
            processing_time=processing_time
        )
        raise
