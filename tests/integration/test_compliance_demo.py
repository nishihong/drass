#!/usr/bin/env python3
"""
Test script for ComplianceDemoService
"""

import asyncio
import json
import sys
import os

# Add the services directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

from app.services.compliance_demo_service import compliance_demo_service


async def test_compliance_demo_service():
    """Test the ComplianceDemoService functionality"""
    
    print("🧪 Testing ComplianceDemoService...")
    print("=" * 50)
    
    # Test 1: Get demo templates
    print("\n1. Testing demo templates...")
    try:
        templates = await compliance_demo_service.get_demo_data_templates()
        print(f"✅ Found {len(templates)} demo templates:")
        for name, template in templates.items():
            print(f"   - {name}: {template['name']} ({template['data_type'].value})")
    except Exception as e:
        print(f"❌ Error getting templates: {e}")
    
    # Test 2: Get compliance rules
    print("\n2. Testing compliance rules...")
    try:
        rules = await compliance_demo_service.get_compliance_rules()
        print(f"✅ Found {len(rules)} compliance rules:")
        for rule in rules[:3]:  # Show first 3 rules
            print(f"   - {rule.rule_id}: {rule.name} ({rule.standard})")
        if len(rules) > 3:
            print(f"   ... and {len(rules) - 3} more rules")
    except Exception as e:
        print(f"❌ Error getting rules: {e}")
    
    # Test 3: Test data classification
    print("\n3. Testing data classification...")
    try:
        test_data = {
            "name": "张三",
            "id_number": "110101199001011234",
            "phone": "13800138000",
            "email": "zhangsan@example.com"
        }
        
        result = await compliance_demo_service.process_demo_data(test_data)
        
        print(f"✅ Analysis completed:")
        print(f"   - Analysis ID: {result.analysis_id}")
        print(f"   - Data Type: {result.data_classification.data_type.value}")
        print(f"   - Sensitivity: {result.data_classification.sensitivity_level.value}")
        print(f"   - Contains PII: {result.data_classification.contains_pii}")
        print(f"   - Overall Risk: {result.risk_assessment.overall_risk.value}")
        print(f"   - Risk Score: {result.risk_assessment.risk_score}")
        print(f"   - Compliance Status: {result.risk_assessment.compliance_status.value}")
        print(f"   - Issues Found: {len(result.risk_assessment.issues)}")
        print(f"   - Recommendations: {len(result.recommendations)}")
        print(f"   - Processing Time: {result.processing_time_ms}ms")
        
        if result.risk_assessment.issues:
            print(f"\n   Issues found:")
            for issue in result.risk_assessment.issues:
                print(f"   - {issue.description} (Severity: {issue.severity.value})")
        
        if result.recommendations:
            print(f"\n   Recommendations:")
            for i, rec in enumerate(result.recommendations[:3], 1):
                print(f"   {i}. {rec}")
            if len(result.recommendations) > 3:
                print(f"   ... and {len(result.recommendations) - 3} more recommendations")
                
    except Exception as e:
        print(f"❌ Error in data analysis: {e}")
    
    # Test 4: Test with template data
    print("\n4. Testing with template data...")
    try:
        result = await compliance_demo_service.process_demo_data(
            data={},  # Empty data
            compliance_rules=None
        )
        result.template_name = "personal_info"  # Use template
        
        print(f"✅ Template analysis completed:")
        print(f"   - Data Type: {result.data_classification.data_type.value}")
        print(f"   - Risk Score: {result.risk_assessment.risk_score}")
        print(f"   - Processing Time: {result.processing_time_ms}ms")
        
    except Exception as e:
        print(f"❌ Error in template analysis: {e}")
    
    # Test 5: Test specific rule
    print("\n5. Testing specific rule...")
    try:
        rule = await compliance_demo_service.get_rule_by_id("gdpr_001")
        if rule:
            print(f"✅ Found rule: {rule.name}")
            print(f"   - Description: {rule.description}")
            print(f"   - Standard: {rule.standard}")
            print(f"   - Severity: {rule.severity.value}")
        else:
            print("❌ Rule not found")
    except Exception as e:
        print(f"❌ Error getting specific rule: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 ComplianceDemoService testing completed!")


async def test_api_endpoints():
    """Test the API endpoints"""
    
    print("\n🌐 Testing API endpoints...")
    print("=" * 50)
    
    import httpx
    
    base_url = "http://localhost:8888/api/v1/compliance-demo"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            print("\n1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check passed: {health_data['status']}")
                print(f"   - Templates available: {health_data['templates_available']}")
                print(f"   - Rules available: {health_data['rules_available']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
            
            # Test templates endpoint
            print("\n2. Testing templates endpoint...")
            response = await client.get(f"{base_url}/templates")
            if response.status_code == 200:
                templates = response.json()
                print(f"✅ Found {len(templates)} templates via API")
                for template in templates[:2]:
                    print(f"   - {template['template_name']}: {template['name']}")
            else:
                print(f"❌ Templates endpoint failed: {response.status_code}")
            
            # Test rules endpoint
            print("\n3. Testing rules endpoint...")
            response = await client.get(f"{base_url}/rules")
            if response.status_code == 200:
                rules = response.json()
                print(f"✅ Found {len(rules)} rules via API")
                for rule in rules[:2]:
                    print(f"   - {rule['rule_id']}: {rule['name']} ({rule['standard']})")
            else:
                print(f"❌ Rules endpoint failed: {response.status_code}")
            
            # Test analysis endpoint
            print("\n4. Testing analysis endpoint...")
            test_data = {
                "data": {
                    "name": "李四",
                    "email": "lisi@example.com",
                    "account_balance": 10000.00
                }
            }
            response = await client.post(f"{base_url}/analyze", json=test_data)
            if response.status_code == 200:
                analysis = response.json()
                print(f"✅ Analysis completed via API")
                print(f"   - Analysis ID: {analysis['analysis_id']}")
                print(f"   - Data Type: {analysis['data_classification']['data_type']}")
                print(f"   - Risk Score: {analysis['risk_assessment']['risk_score']}")
                print(f"   - Processing Time: {analysis['processing_time_ms']}ms")
            else:
                print(f"❌ Analysis endpoint failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Cannot connect to API server. Make sure the server is running on port 8888")
    except Exception as e:
        print(f"❌ Error testing API endpoints: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting ComplianceDemoService Tests")
    print("=" * 60)
    
    # Test service directly
    await test_compliance_demo_service()
    
    # Test API endpoints
    await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✨ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
