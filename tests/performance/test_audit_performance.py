#!/usr/bin/env python3
"""
Enhanced Audit Logs Performance Test
Tests the performance and functionality of the enhanced audit logging system
"""

import asyncio
import time
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import audit service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

from app.services.audit_service_enhanced import audit_service_enhanced, AuditEventType, AuditSeverity, AuditStatus


class AuditLogsPerformanceTest:
    """Performance test for enhanced audit logging system"""
    
    def __init__(self):
        self.test_results = {}
    
    async def setup_test_data(self, count: int = 1000):
        """Setup test data for performance testing"""
        logger.info(f"Setting up {count} test audit log entries...")
        
        start_time = time.time()
        
        for i in range(count):
            await audit_service_enhanced.log_audit_event(
                event_type=AuditEventType.API_ACCESS,
                user_id=f"test_user_{i % 10}",
                details={"test_id": i, "operation": "performance_test"},
                request_id=f"req_{i}",
                resource_type="test_resource",
                resource_id=f"resource_{i}",
                action="test_action",
                severity=AuditSeverity.MEDIUM,
                status=AuditStatus.SUCCESS,
                ip_address="127.0.0.1",
                user_agent="PerformanceTest/1.0",
                session_id=f"session_{i}",
                outcome="completed",
                metadata={"test": True, "iteration": i}
            )
            
            if (i + 1) % 100 == 0:
                logger.info(f"Created {i + 1} test entries...")
        
        end_time = time.time()
        setup_time = end_time - start_time
        
        self.test_results["setup"] = {
            "entries_created": count,
            "setup_time_seconds": setup_time,
            "entries_per_second": count / setup_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Setup completed: {count} entries in {setup_time:.2f} seconds")
    
    async def test_query_performance(self):
        """Test query performance with different filters"""
        logger.info("Testing query performance...")
        
        test_cases = [
            {"name": "no_filters", "params": {"limit": 100}},
            {"name": "user_filter", "params": {"user_id": "test_user_1", "limit": 100}},
            {"name": "event_type_filter", "params": {"event_type": AuditEventType.API_ACCESS, "limit": 100}},
            {"name": "severity_filter", "params": {"severity": AuditSeverity.MEDIUM, "limit": 100}},
            {"name": "status_filter", "params": {"status": AuditStatus.SUCCESS, "limit": 100}}
        ]
        
        query_results = {}
        
        for test_case in test_cases:
            logger.info(f"Testing query: {test_case['name']}")
            
            times = []
            for _ in range(5):
                start_time = time.time()
                logs = await audit_service_enhanced.get_audit_logs(**test_case["params"])
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            
            query_results[test_case["name"]] = {
                "average_time_seconds": avg_time,
                "result_count": len(logs),
                "queries_per_second": 1 / avg_time
            }
            
            logger.info(f"Query {test_case['name']}: {avg_time:.4f}s avg, {len(logs)} results")
        
        self.test_results["query_performance"] = query_results
    
    async def test_health_check(self):
        """Test health check functionality"""
        logger.info("Testing health check...")
        
        start_time = time.time()
        health_status = await audit_service_enhanced.health_check()
        end_time = time.time()
        
        self.test_results["health_check"] = {
            "response_time_seconds": end_time - start_time,
            "status": health_status.get("status"),
            "database_connected": health_status.get("database_connected"),
            "total_logs": health_status.get("total_logs"),
            "storage_type": health_status.get("storage_type")
        }
        
        logger.info(f"Health check: {health_status.get('status')} in {end_time - start_time:.4f}s")
    
    async def run_all_tests(self, test_data_count: int = 1000):
        """Run all performance tests"""
        logger.info("Starting enhanced audit logs performance tests...")
        
        try:
            await self.setup_test_data(test_data_count)
            await self.test_query_performance()
            await self.test_health_check()
            
            # Save results
            with open("audit_logs_performance_test_results.json", "w") as f:
                json.dump(self.test_results, f, indent=2, default=str)
            
            logger.info("Performance tests completed successfully!")
            logger.info("Results saved to: audit_logs_performance_test_results.json")
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            raise


async def main():
    """Main test function"""
    test = AuditLogsPerformanceTest()
    await test.run_all_tests(test_data_count=1000)


if __name__ == "__main__":
    asyncio.run(main())
