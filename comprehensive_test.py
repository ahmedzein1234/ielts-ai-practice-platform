#!/usr/bin/env python3
"""
Comprehensive Testing Script for IELTS AI Platform
Tests all services, endpoints, and frontend functionality
"""
import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


@dataclass
class TestResult:
    service: str
    endpoint: str
    status: str
    response_time: float
    error: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ComprehensiveTester:
    def __init__(self):
        self.base_urls = {
            "api": "http://localhost:8000",
            "ai_tutor": "http://localhost:8001",
            "exam_generator": "http://localhost:8006",
            "web": "http://localhost:3000",
            "scoring": "http://localhost:8005",
            "ocr": "http://localhost:8002",
            "speech": "http://localhost:8003",
            "worker": "http://localhost:8004",
        }
        self.results: List[TestResult] = []

    def test_service_health(self, service: str, url: str) -> TestResult:
        """Test service health endpoint."""
        start_time = time.time()
        try:
            response = requests.get(f"{url}/health", timeout=5)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return TestResult(
                    service=service,
                    endpoint="/health",
                    status="PASS",
                    response_time=response_time,
                    details=response.json(),
                )
            else:
                return TestResult(
                    service=service,
                    endpoint="/health",
                    status="FAIL",
                    response_time=response_time,
                    error=f"HTTP {response.status_code}",
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                service=service,
                endpoint="/health",
                status="ERROR",
                response_time=response_time,
                error=str(e),
            )

    def test_api_endpoints(self) -> List[TestResult]:
        """Test API endpoints."""
        api_url = self.base_urls["api"]
        endpoints = [
            ("/users/", "GET"),
            ("/assessments/", "GET"),
            ("/content/", "GET"),
            ("/learning-paths/", "GET"),
            ("/analytics/", "GET"),
            ("/auth/login", "POST"),
            ("/auth/register", "POST"),
        ]

        results = []
        for endpoint, method in endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{api_url}{endpoint}", timeout=5)
                else:  # POST
                    response = requests.post(
                        f"{api_url}{endpoint}",
                        json={"email": "test@example.com", "password": "test123"},
                        timeout=5,
                    )

                response_time = time.time() - start_time

                if response.status_code in [200, 201]:
                    results.append(
                        TestResult(
                            service="api",
                            endpoint=endpoint,
                            status="PASS",
                            response_time=response_time,
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            service="api",
                            endpoint=endpoint,
                            status="FAIL",
                            response_time=response_time,
                            error=f"HTTP {response.status_code}",
                        )
                    )
            except Exception as e:
                response_time = time.time() - start_time
                results.append(
                    TestResult(
                        service="api",
                        endpoint=endpoint,
                        status="ERROR",
                        response_time=response_time,
                        error=str(e),
                    )
                )

        return results

    def test_exam_generator(self) -> List[TestResult]:
        """Test exam generator endpoints."""
        exam_url = self.base_urls["exam_generator"]
        endpoints = [
            ("/templates", "GET"),
            ("/generate", "POST"),
            ("/submit", "POST"),
            ("/results", "GET"),
        ]

        results = []
        for endpoint, method in endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{exam_url}{endpoint}", timeout=5)
                else:  # POST
                    response = requests.post(
                        f"{exam_url}{endpoint}",
                        json={"test_type": "academic"},
                        timeout=5,
                    )

                response_time = time.time() - start_time

                if response.status_code in [200, 201]:
                    results.append(
                        TestResult(
                            service="exam_generator",
                            endpoint=endpoint,
                            status="PASS",
                            response_time=response_time,
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            service="exam_generator",
                            endpoint=endpoint,
                            status="FAIL",
                            response_time=response_time,
                            error=f"HTTP {response.status_code}",
                        )
                    )
            except Exception as e:
                response_time = time.time() - start_time
                results.append(
                    TestResult(
                        service="exam_generator",
                        endpoint=endpoint,
                        status="ERROR",
                        response_time=response_time,
                        error=str(e),
                    )
                )

        return results

    def test_ai_tutor(self) -> List[TestResult]:
        """Test AI tutor endpoints."""
        tutor_url = self.base_urls["ai_tutor"]
        endpoints = [
            ("/chat", "POST"),
            ("/speech-analysis", "POST"),
            ("/personality", "GET"),
            ("/learning-path", "GET"),
        ]

        results = []
        for endpoint, method in endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = requests.get(f"{tutor_url}{endpoint}", timeout=5)
                else:  # POST
                    response = requests.post(
                        f"{tutor_url}{endpoint}", json={"message": "Hello"}, timeout=5
                    )

                response_time = time.time() - start_time

                if response.status_code in [200, 201]:
                    results.append(
                        TestResult(
                            service="ai_tutor",
                            endpoint=endpoint,
                            status="PASS",
                            response_time=response_time,
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            service="ai_tutor",
                            endpoint=endpoint,
                            status="FAIL",
                            response_time=response_time,
                            error=f"HTTP {response.status_code}",
                        )
                    )
            except Exception as e:
                response_time = time.time() - start_time
                results.append(
                    TestResult(
                        service="ai_tutor",
                        endpoint=endpoint,
                        status="ERROR",
                        response_time=response_time,
                        error=str(e),
                    )
                )

        return results

    def test_frontend_pages(self) -> List[TestResult]:
        """Test frontend pages."""
        web_url = self.base_urls["web"]
        pages = [
            "/",
            "/dashboard",
            "/ai-tutor",
            "/assessments",
            "/content",
            "/learning-paths",
            "/recommendations",
            "/analytics-dashboard",
            "/custom-reports",
            "/speaking",
            "/writing",
            "/listening",
            "/reading",
            "/analytics",
            "/groups",
            "/goals",
            "/settings",
            "/exam-creator",
            "/exam-simulator",
            "/ai-tutor/enhanced",
        ]

        results = []
        for page in pages:
            start_time = time.time()
            try:
                response = requests.get(f"{web_url}{page}", timeout=5)
                response_time = time.time() - start_time

                if response.status_code == 200:
                    results.append(
                        TestResult(
                            service="web",
                            endpoint=page,
                            status="PASS",
                            response_time=response_time,
                        )
                    )
                else:
                    results.append(
                        TestResult(
                            service="web",
                            endpoint=page,
                            status="FAIL",
                            response_time=response_time,
                            error=f"HTTP {response.status_code}",
                        )
                    )
            except Exception as e:
                response_time = time.time() - start_time
                results.append(
                    TestResult(
                        service="web",
                        endpoint=page,
                        status="ERROR",
                        response_time=response_time,
                        error=str(e),
                    )
                )

        return results

    def run_comprehensive_tests(self):
        """Run all comprehensive tests."""
        print("🚀 Starting Comprehensive IELTS Platform Testing")
        print("=" * 60)

        # Test service health
        print("\n📊 Testing Service Health...")
        for service, url in self.base_urls.items():
            result = self.test_service_health(service, url)
            self.results.append(result)
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(
                f"{status_icon} {service}: {result.status} ({result.response_time:.2f}s)"
            )
            if result.error:
                print(f"   Error: {result.error}")

        # Test API endpoints
        print("\n🔌 Testing API Endpoints...")
        api_results = self.test_api_endpoints()
        self.results.extend(api_results)
        for result in api_results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(
                f"{status_icon} {result.endpoint}: {result.status} ({result.response_time:.2f}s)"
            )
            if result.error:
                print(f"   Error: {result.error}")

        # Test exam generator
        print("\n📝 Testing Exam Generator...")
        exam_results = self.test_exam_generator()
        self.results.extend(exam_results)
        for result in exam_results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(
                f"{status_icon} {result.endpoint}: {result.status} ({result.response_time:.2f}s)"
            )
            if result.error:
                print(f"   Error: {result.error}")

        # Test AI tutor
        print("\n🤖 Testing AI Tutor...")
        tutor_results = self.test_ai_tutor()
        self.results.extend(tutor_results)
        for result in tutor_results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(
                f"{status_icon} {result.endpoint}: {result.status} ({result.response_time:.2f}s)"
            )
            if result.error:
                print(f"   Error: {result.error}")

        # Test frontend pages
        print("\n🌐 Testing Frontend Pages...")
        frontend_results = self.test_frontend_pages()
        self.results.extend(frontend_results)
        for result in frontend_results:
            status_icon = "✅" if result.status == "PASS" else "❌"
            print(
                f"{status_icon} {result.endpoint}: {result.status} ({result.response_time:.2f}s)"
            )
            if result.error:
                print(f"   Error: {result.error}")

    def generate_summary_report(self):
        """Generate summary report."""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TESTING SUMMARY REPORT")
        print("=" * 60)

        # Group results by service
        service_results = {}
        for result in self.results:
            if result.service not in service_results:
                service_results[result.service] = []
            service_results[result.service].append(result)

        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "PASS"])
        failed_tests = len([r for r in self.results if r.status == "FAIL"])
        error_tests = len([r for r in self.results if r.status == "ERROR"])

        response_times = [r.response_time for r in self.results if r.response_time > 0]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0

        # Service status summary
        print("\n🏗️  SERVICE STATUS SUMMARY:")
        for service, results in service_results.items():
            passed = len([r for r in results if r.status == "PASS"])
            total = len(results)
            percentage = (passed / total * 100) if total > 0 else 0
            status_icon = (
                "✅" if percentage >= 80 else "⚠️" if percentage >= 50 else "❌"
            )
            print(
                f"{status_icon} {service.upper()}: {passed}/{total} ({percentage:.1f}%)"
            )

        # Performance analysis
        print(f"\n⚡ PERFORMANCE ANALYSIS:")
        print(f"Average Response Time: {avg_response_time:.2f}s")
        print(f"Fastest Response: {min_response_time:.2f}s")
        print(f"Slowest Response: {max_response_time:.2f}s")

        # Critical issues
        critical_issues = [r for r in self.results if r.status == "ERROR"]
        if critical_issues:
            print(f"\n🚨 CRITICAL ISSUES:")
            for issue in critical_issues:
                print(f"❌ {issue.service} - {issue.endpoint}: {issue.error}")
        else:
            print(f"\n🚨 CRITICAL ISSUES:")
            print("✅ No critical issues found!")

        # Recommendations
        failed_tests = [r for r in self.results if r.status == "FAIL"]
        if failed_tests:
            print(f"\n💡 RECOMMENDATIONS:")
            print("⚠️  Areas needing attention:")
            for test in failed_tests:
                print(f"   - {test.service} {test.endpoint}: {test.error}")

    def save_detailed_report(self):
        """Save detailed report to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_report_{timestamp}.json"

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": len([r for r in self.results if r.status == "PASS"]),
                "failed": len([r for r in self.results if r.status == "FAIL"]),
                "errors": len([r for r in self.results if r.status == "ERROR"]),
            },
            "results": [
                {
                    "service": r.service,
                    "endpoint": r.endpoint,
                    "status": r.status,
                    "response_time": r.response_time,
                    "error": r.error,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        with open(filename, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: {filename}")


def main():
    tester = ComprehensiveTester()
    tester.run_comprehensive_tests()
    tester.generate_summary_report()
    tester.save_detailed_report()


if __name__ == "__main__":
    main()
