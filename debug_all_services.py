#!/usr/bin/env python3
"""Debug script to start all IELTS platform services in debug mode."""

import asyncio
import subprocess
import sys
import os
import signal
import time
from typing import List, Dict
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceManager:
    """Manages multiple services in debug mode."""
    
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.services = {
            'api': {
                'command': ['python', 'main.py'],
                'cwd': 'services/api',
                'port': 8000,
                'env': {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
            },
            'scoring': {
                'command': ['python', 'main.py'],
                'cwd': 'services/scoring',
                'port': 8004,
                'env': {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
            },
            'speech': {
                'command': ['python', 'main.py'],
                'cwd': 'services/speech',
                'port': 8002,
                'env': {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
            },
            'ocr': {
                'command': ['python', 'main.py'],
                'cwd': 'services/ocr',
                'port': 8003,
                'env': {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
            },
            'ai-tutor': {
                'command': ['python', 'main.py'],
                'cwd': 'services/ai-tutor',
                'port': 8005,
                'env': {'DEBUG': 'true', 'LOG_LEVEL': 'DEBUG'}
            }
        }
    
    def start_service(self, service_name: str) -> bool:
        """Start a single service in debug mode."""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
        
        service_config = self.services[service_name]
        
        # Set environment variables
        env = os.environ.copy()
        env.update(service_config['env'])
        env['PYTHONPATH'] = os.path.abspath('.')
        
        try:
            logger.info(f"Starting {service_name} service...")
            process = subprocess.Popen(
                service_config['command'],
                cwd=service_config['cwd'],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.processes[service_name] = process
            logger.info(f"Started {service_name} service (PID: {process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start {service_name} service: {e}")
            return False
    
    def start_all_services(self) -> bool:
        """Start all services in debug mode."""
        logger.info("Starting all IELTS platform services in debug mode...")
        
        success_count = 0
        for service_name in self.services:
            if self.start_service(service_name):
                success_count += 1
                time.sleep(2)  # Give each service time to start
        
        logger.info(f"Started {success_count}/{len(self.services)} services")
        return success_count == len(self.services)
    
    def stop_service(self, service_name: str):
        """Stop a single service."""
        if service_name in self.processes:
            process = self.processes[service_name]
            logger.info(f"Stopping {service_name} service (PID: {process.pid})...")
            
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"Stopped {service_name} service")
            except subprocess.TimeoutExpired:
                logger.warning(f"Force killing {service_name} service")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping {service_name} service: {e}")
            
            del self.processes[service_name]
    
    def stop_all_services(self):
        """Stop all services."""
        logger.info("Stopping all services...")
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)
    
    def get_service_status(self) -> Dict[str, str]:
        """Get status of all services."""
        status = {}
        for service_name, process in self.processes.items():
            if process.poll() is None:
                status[service_name] = "running"
            else:
                status[service_name] = f"stopped (exit code: {process.returncode})"
        return status
    
    def monitor_services(self):
        """Monitor running services and restart if needed."""
        logger.info("Monitoring services...")
        try:
            while True:
                for service_name, process in self.processes.items():
                    if process.poll() is not None:
                        logger.warning(f"{service_name} service stopped unexpectedly")
                        # Restart the service
                        self.stop_service(service_name)
                        time.sleep(1)
                        self.start_service(service_name)
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
    
    def print_logs(self):
        """Print logs from all services."""
        logger.info("Service logs:")
        for service_name, process in self.processes.items():
            if process.stdout:
                logger.info(f"\n=== {service_name.upper()} LOGS ===")
                for line in process.stdout:
                    print(f"[{service_name}] {line.strip()}")


def main():
    """Main function to run the debug environment."""
    manager = ServiceManager()
    
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        manager.stop_all_services()
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all services
        if not manager.start_all_services():
            logger.error("Failed to start all services")
            return 1
        
        # Print service status
        logger.info("Service status:")
        for service_name, status in manager.get_service_status().items():
            logger.info(f"  {service_name}: {status}")
        
        logger.info("\n" + "="*50)
        logger.info("IELTS Platform Debug Environment Started!")
        logger.info("="*50)
        logger.info("Services running:")
        logger.info("  - API Gateway: http://localhost:8000")
        logger.info("  - Scoring Service: http://localhost:8004")
        logger.info("  - Speech Service: http://localhost:8002")
        logger.info("  - OCR Service: http://localhost:8003")
        logger.info("  - AI Tutor Service: http://localhost:8005")
        logger.info("  - Frontend: http://localhost:3000")
        logger.info("\nDebug endpoints:")
        logger.info("  - API Debug Stats: http://localhost:8000/debug/stats")
        logger.info("  - API Docs: http://localhost:8000/docs")
        logger.info("\nPress Ctrl+C to stop all services")
        logger.info("="*50)
        
        # Monitor services
        manager.monitor_services()
        
    except KeyboardInterrupt:
        logger.info("Shutting down debug environment...")
    finally:
        manager.stop_all_services()
        logger.info("Debug environment stopped")


if __name__ == "__main__":
    sys.exit(main())
