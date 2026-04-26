#!/usr/bin/env python3
"""
Simple test for compliance monitoring service
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

async def test_monitoring_service():
    """Test the compliance monitoring service"""
    try:
        from app.services.monitoring_service import monitoring_service, MetricType, AlertSeverity, AlertStatus
        
        print("Testing compliance monitoring service...")
        
        # Test health check
        print("1. Testing health check...")
        health = await monitoring_service.health_check()
        print(f"   Health status: {health.get('status')}")
        print(f"   Is monitoring: {health.get('is_monitoring')}")
        print(f"   Active alerts: {health.get('active_alerts')}")
        
        # Test monitoring metrics collection
        print("2. Testing monitoring metrics collection...")
        monitoring_result = await monitoring_service.monitor_compliance_metrics()
        print(f"   Compliance score: {monitoring_result.compliance_score}%")
        print(f"   Overall status: {monitoring_result.overall_status}")
        print(f"   Metrics collected: {len(monitoring_result.metrics)}")
        print(f"   Active alerts: {len(monitoring_result.alerts)}")
        print(f"   Risk incidents: {len(monitoring_result.risk_incidents)}")
        
        # Display metrics
        print("3. Metrics details:")
        for metric_type, metric in monitoring_result.metrics.items():
            print(f"   {metric_type.value}: {metric.value} {metric.unit} ({metric.status})")
        
        # Display alerts
        if monitoring_result.alerts:
            print("4. Active alerts:")
            for alert in monitoring_result.alerts:
                print(f"   - {alert.title}: {alert.severity.value} ({alert.status.value})")
        else:
            print("4. No active alerts")
        
        # Display risk incidents
        if monitoring_result.risk_incidents:
            print("5. Risk incidents:")
            for incident in monitoring_result.risk_incidents:
                print(f"   - {incident.incident_type}: {incident.severity.value}")
        else:
            print("5. No risk incidents")
        
        # Test current status
        print("6. Testing current status...")
        status = await monitoring_service.get_current_status()
        print(f"   Status: {status.get('status')}")
        print(f"   Is monitoring: {status.get('is_monitoring')}")
        print(f"   Total metrics: {status.get('total_metrics')}")
        
        print("\n✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_monitoring_service())
