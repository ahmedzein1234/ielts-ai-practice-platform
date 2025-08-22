# IELTS Worker System

The Worker System handles asynchronous task processing for the IELTS AI Practice Platform using Celery and Redis.

## Overview

The worker system processes background jobs for:
- **Scoring**: AI-powered IELTS scoring and feedback generation
- **File Processing**: OCR, audio transcription, and file uploads
- **Email**: Welcome emails, scoring notifications, and weekly reports
- **Analytics**: User and platform analytics processing
- **Health Checks**: Service monitoring and queue depth monitoring

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│   Redis Broker  │───▶│  Celery Workers │
│                 │    │                 │    │                 │
│  - FastAPI      │    │  - Task Queue   │    │  - Scoring      │
│  - WebSocket    │    │  - Results      │    │  - File Proc    │
│  - Auth         │    │  - Cache        │    │  - Email        │
└─────────────────┘    └─────────────────┘    │  - Analytics    │
                                              │  - Health       │
                                              └─────────────────┘
```

## Task Queues

- `scoring`: AI scoring and feedback generation
- `file_processing`: OCR, audio transcription, file uploads
- `email`: Email notifications and reports
- `analytics`: Data analysis and visualization
- `health`: Service monitoring and health checks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r workers/requirements.txt
```

### 2. Start Redis (if not running)

```bash
# On Windows (if using WSL or Docker)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### 3. Start Celery Worker

```bash
# From project root
celery -A workers.celery_app worker --loglevel=info --concurrency=4
```

### 4. Start Celery Beat (for scheduled tasks)

```bash
# From project root
celery -A workers.celery_app beat --loglevel=info
```

### 5. Test the System

```bash
python workers/test_worker.py
```

## Configuration

Environment variables (see `.env.example`):

```bash
# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Service URLs
API_GATEWAY_URL=http://localhost:8000
SPEECH_SERVICE_URL=http://localhost:8002
OCR_SERVICE_URL=http://localhost:8003
SCORING_SERVICE_URL=http://localhost:8005

# Email Configuration
SENDGRID_API_KEY=your_sendgrid_key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# AWS Configuration (for S3)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=ielts-uploads
```

## Task Types

### Scoring Tasks

- `score_submission_task`: Score a single submission
- `score_batch_task`: Score multiple submissions
- `generate_feedback_task`: Generate detailed feedback
- `cleanup_old_results_task`: Clean up old scoring results

### File Processing Tasks

- `process_image_task`: Process images with OCR
- `process_audio_task`: Transcribe audio files
- `upload_to_s3_task`: Upload files to S3
- `cleanup_temp_files_task`: Clean up temporary files
- `process_batch_task`: Process multiple files

### Email Tasks

- `send_welcome_email_task`: Send welcome emails
- `send_scoring_complete_task`: Send scoring notifications
- `send_weekly_report_task`: Send weekly reports
- `send_batch_emails_task`: Send multiple emails
- `send_generic_email_task`: Send generic emails

### Analytics Tasks

- `process_user_analytics_task`: Process user analytics
- `process_platform_analytics_task`: Process platform analytics
- `generate_weekly_report_task`: Generate weekly reports
- `cleanup_old_analytics_task`: Clean up old analytics data

### Health Tasks

- `health_check_task`: Check service health
- `monitor_queue_depth_task`: Monitor queue depths

## Scheduled Tasks

The system includes scheduled tasks via Celery Beat:

- **Daily (2 AM)**: Clean up old scoring results
- **Daily (3 AM)**: Clean up temporary files
- **Daily (4 AM)**: Clean up old analytics data
- **Weekly (Monday 6 AM)**: Generate platform reports
- **Weekly (Monday 8 AM)**: Send weekly reports
- **Hourly**: Health checks

## Monitoring

### Celery Flower (Optional)

Start Celery Flower for web-based monitoring:

```bash
celery -A workers.celery_app flower --port=5555
```

Access at: http://localhost:5555

### Health Checks

Monitor worker health:

```bash
# Check worker status
celery -A workers.celery_app inspect active

# Check queue depths
celery -A workers.celery_app inspect stats

# Check registered tasks
celery -A workers.celery_app inspect registered
```

## Development

### Adding New Tasks

1. Create a new task module in `workers/tasks/`
2. Define your task function with the `@celery_app.task` decorator
3. Add the module to `celery_app.conf.include` in `workers/celery_app.py`
4. Add routing configuration if needed

Example:

```python
# workers/tasks/my_task.py
from workers.celery_app import celery_app

@celery_app.task(bind=True, name="workers.tasks.my_task.process_data")
def process_data_task(self, data):
    # Your task logic here
    return {"status": "completed", "data": data}
```

### Testing Tasks

```python
# Test a specific task
from workers.tasks.my_task import process_data_task

result = process_data_task.delay({"test": "data"})
print(f"Task ID: {result.id}")
print(f"Result: {result.get()}")
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**: Ensure Redis is running and accessible
2. **Task Not Found**: Check that the task module is included in `celery_app.conf.include`
3. **Import Errors**: Ensure all dependencies are installed
4. **Worker Not Starting**: Check logs for configuration errors

### Logs

Worker logs include:
- Task execution details
- Error messages with stack traces
- Performance metrics
- Service health status

### Performance Tuning

- Adjust `--concurrency` based on CPU cores
- Configure `worker_prefetch_multiplier` for task distribution
- Set appropriate `task_time_limit` and `task_soft_time_limit`
- Monitor queue depths and scale workers accordingly

## Security

- All tasks run in isolated worker processes
- Sensitive data is not logged
- API keys and secrets are stored in environment variables
- Task results are stored securely in Redis
- Rate limiting is configured for all task types

## Production Deployment

For production deployment:

1. Use Redis Cluster or AWS ElastiCache
2. Configure multiple worker instances
3. Set up monitoring and alerting
4. Configure proper logging and error tracking
5. Use environment-specific configurations
6. Set up backup and recovery procedures
