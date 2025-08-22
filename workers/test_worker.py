"""Test script for the worker system."""

import sys
import os
import time
import asyncio
from typing import Dict, Any

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from workers.celery_app import celery_app
from workers.tasks.scoring import score_submission_task
from workers.tasks.file_processing import process_image_task
from workers.tasks.email import send_welcome_email_task
from workers.tasks.analytics import process_user_analytics_task
from workers.tasks.health import health_check_task


def test_scoring_task():
    """Test scoring task."""
    print("Testing scoring task...")
    
    # Create test data
    test_data = {
        "user_id": "test_user_123",
        "task_type": "writing_task_2",
        "text": "This is a test essay for IELTS writing task 2. It contains multiple sentences to test the scoring system.",
        "prompt": "Some people believe that technology has made our lives easier, while others think it has made them more complicated. Discuss both views and give your opinion.",
        "word_count": 45
    }
    
    # Submit task
    result = score_submission_task.delay(test_data)
    
    print(f"Task submitted with ID: {result.id}")
    print(f"Task status: {result.status}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"Task completed: {task_result}")
    except Exception as e:
        print(f"Task failed or timed out: {e}")
    
    return result


def test_file_processing_task():
    """Test file processing task."""
    print("\nTesting file processing task...")
    
    # Create test data
    test_data = {
        "file_path": "/tmp/test_image.jpg",
        "file_type": "image",
        "user_id": "test_user_123",
        "processing_options": {
            "ocr_engine": "mock",
            "language": "en"
        }
    }
    
    # Submit task
    result = process_image_task.delay(test_data)
    
    print(f"Task submitted with ID: {result.id}")
    print(f"Task status: {result.status}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"Task completed: {task_result}")
    except Exception as e:
        print(f"Task failed or timed out: {e}")
    
    return result


def test_email_task():
    """Test email task."""
    print("\nTesting email task...")
    
    # Create test data
    test_data = {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "user_name": "Test User",
        "template_data": {
            "welcome_message": "Welcome to IELTS AI Practice Platform!",
            "next_steps": ["Complete your profile", "Take a practice test", "Join a study group"]
        }
    }
    
    # Submit task
    result = send_welcome_email_task.delay(test_data)
    
    print(f"Task submitted with ID: {result.id}")
    print(f"Task status: {result.status}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"Task completed: {task_result}")
    except Exception as e:
        print(f"Task failed or timed out: {e}")
    
    return result


def test_analytics_task():
    """Test analytics task."""
    print("\nTesting analytics task...")
    
    # Create test data
    test_data = {
        "user_id": "test_user_123",
        "date_range": "7d"
    }
    
    # Submit task
    result = process_user_analytics_task.delay(test_data)
    
    print(f"Task submitted with ID: {result.id}")
    print(f"Task status: {result.status}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"Task completed: {task_result}")
    except Exception as e:
        print(f"Task failed or timed out: {e}")
    
    return result


def test_health_check_task():
    """Test health check task."""
    print("\nTesting health check task...")
    
    # Submit task
    result = health_check_task.delay()
    
    print(f"Task submitted with ID: {result.id}")
    print(f"Task status: {result.status}")
    
    # Wait for result
    try:
        task_result = result.get(timeout=30)
        print(f"Task completed: {task_result}")
    except Exception as e:
        print(f"Task failed or timed out: {e}")
    
    return result


def main():
    """Run all worker tests."""
    print("Starting Worker System Tests")
    print("=" * 50)
    
    # Test each task type
    try:
        test_scoring_task()
        time.sleep(2)
        
        test_file_processing_task()
        time.sleep(2)
        
        test_email_task()
        time.sleep(2)
        
        test_analytics_task()
        time.sleep(2)
        
        test_health_check_task()
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
