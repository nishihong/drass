#!/usr/bin/env python3
"""
端到端集成测试套件
测试数据合规分析系统的完整功能流程
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List
import tempfile

# 测试配置
API_BASE_URL = "http://localhost:8888"
FRONTEND_URL = "http://localhost:5173"
TEST_TIMEOUT = 180
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class E2ETestSuite:
    """端到端测试套件"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.start_time = time.time()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_check(self) -> bool:
        """测试系统健康检查"""
        try:
            async with self.session.get(
                f"{API_BASE_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("系统健康检查", True, f"状态: {data.get('status', 'unknown')}")
                    return True
                else:
                    self.log_test("系统健康检查", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("系统健康检查", False, str(e))
            return False
    
    async def test_user_authentication(self) -> bool:
        """测试用户认证流程"""
        try:
            # 测试登录
            login_data = {
                "username": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/api/v1/auth/login",
                data=login_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    if self.auth_token:
                        self.log_test("用户认证", True, "登录成功，获取到访问令牌")
                        return True
                    else:
                        self.log_test("用户认证", False, "登录成功但未获取到访问令牌")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("用户认证", False, f"登录失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("用户认证", False, str(e))
            return False
    
    async def test_document_upload(self) -> bool:
        """测试文档上传功能"""
        if not self.auth_token:
            self.log_test("文档上传", False, "缺少认证令牌")
            return False
        
        try:
            # 创建测试文档
            test_content = """
            数据保护政策测试文档
            
            1. 个人信息保护
            - 所有个人信息必须加密存储
            - 访问需要多因素认证
            - 数据保留期限为90天
            
            2. 合规要求
            - 遵守GDPR规定
            - 定期进行安全审计
            - 数据泄露通知机制
            
            3. 技术措施
            - 端到端加密
            - 访问日志记录
            - 定期备份
            """
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                temp_file = f.name
            
            try:
                # 上传文档
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                
                with open(temp_file, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename='test_policy.txt', content_type='text/plain')
                    
                    async with self.session.post(
                        f"{API_BASE_URL}/api/v1/documents/upload",
                        data=data,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            self.log_test("文档上传", True, f"文档ID: {result.get('id', 'unknown')}")
                            return True
                        else:
                            error_text = await response.text()
                            self.log_test("文档上传", False, f"上传失败: {response.status} - {error_text}")
                            return False
            finally:
                # 清理临时文件
                os.unlink(temp_file)
                
        except Exception as e:
            self.log_test("文档上传", False, str(e))
            return False
    
    async def test_document_list(self) -> bool:
        """测试文档列表功能"""
        if not self.auth_token:
            self.log_test("文档列表", False, "缺少认证令牌")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            async with self.session.get(
                f"{API_BASE_URL}/api/v1/documents/",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    doc_count = len(data) if isinstance(data, list) else 0
                    self.log_test("文档列表", True, f"获取到 {doc_count} 个文档")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("文档列表", False, f"获取失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("文档列表", False, str(e))
            return False
    
    async def test_compliance_analysis(self) -> bool:
        """测试合规分析功能"""
        if not self.auth_token:
            self.log_test("合规分析", False, "缺少认证令牌")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 测试合规分析API
            analysis_data = {
                "message": "请分析我们的数据保护政策是否符合GDPR要求",
                "use_rag": True,
                "max_tokens": 1024
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/api/v1/test/chat",
                json=analysis_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    response_text = data.get("response", "")
                    if response_text and len(response_text) > 50:
                        self.log_test("合规分析", True, f"分析完成，响应长度: {len(response_text)} 字符")
                        return True
                    else:
                        self.log_test("合规分析", False, "响应内容过短或为空")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("合规分析", False, f"分析失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("合规分析", False, str(e))
            return False
    
    async def test_audit_logs(self) -> bool:
        """测试审计日志功能"""
        if not self.auth_token:
            self.log_test("审计日志", False, "缺少认证令牌")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 测试审计日志健康检查
            async with self.session.get(
                f"{API_BASE_URL}/api/v1/audit-enhanced/health",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")
                    if status == "healthy":
                        self.log_test("审计日志", True, "审计服务健康状态正常")
                        return True
                    else:
                        self.log_test("审计日志", False, f"审计服务状态异常: {status}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("审计日志", False, f"健康检查失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("审计日志", False, str(e))
            return False
    
    async def test_compliance_demo(self) -> bool:
        """测试合规演示功能"""
        if not self.auth_token:
            self.log_test("合规演示", False, "缺少认证令牌")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 测试合规演示API
            demo_data = {
                "data": {
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "phone": "13800138000",
                    "id_card": "110101199001011234"
                }
            }
            
            async with self.session.post(
                f"{API_BASE_URL}/api/v1/compliance-demo/analyze",
                json=demo_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "risk_assessment" in data and "data_classification" in data:
                        self.log_test("合规演示", True, "合规分析演示功能正常")
                        return True
                    else:
                        self.log_test("合规演示", False, "响应格式不正确")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("合规演示", False, f"演示失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("合规演示", False, str(e))
            return False
    
    async def test_monitoring_system(self) -> bool:
        """测试监控系统功能"""
        if not self.auth_token:
            self.log_test("监控系统", False, "缺少认证令牌")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # 测试监控系统健康检查
            async with self.session.get(
                f"{API_BASE_URL}/api/v1/monitoring/health",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")
                    if status == "healthy":
                        self.log_test("监控系统", True, "监控系统健康状态正常")
                        return True
                    else:
                        self.log_test("监控系统", False, f"监控系统状态异常: {status}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("监控系统", False, f"健康检查失败: {response.status} - {error_text}")
                    return False
        except Exception as e:
            self.log_test("监控系统", False, str(e))
            return False
    
    async def test_performance_metrics(self) -> bool:
        """测试性能指标"""
        try:
            # 测试响应时间
            start_time = time.time()
            
            async with self.session.get(
                f"{API_BASE_URL}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # 转换为毫秒
                
                if response.status == 200 and response_time < 1000:  # 1秒内响应
                    self.log_test("性能指标", True, f"响应时间: {response_time:.2f}ms")
                    return True
                else:
                    self.log_test("性能指标", False, f"响应时间过长: {response_time:.2f}ms")
                    return False
        except Exception as e:
            self.log_test("性能指标", False, str(e))
            return False
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("="*60)
        print("数据合规分析系统 - 端到端集成测试")
        print(f"API地址: {API_BASE_URL}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 定义测试用例
        test_cases = [
            ("系统健康检查", self.test_health_check),
            ("用户认证", self.test_user_authentication),
            ("文档上传", self.test_document_upload),
            ("文档列表", self.test_document_list),
            ("合规分析", self.test_compliance_analysis),
            ("审计日志", self.test_audit_logs),
            ("合规演示", self.test_compliance_demo),
            ("监控系统", self.test_monitoring_system),
            ("性能指标", self.test_performance_metrics),
        ]
        
        # 运行测试
        for test_name, test_func in test_cases:
            try:
                await test_func()
            except Exception as e:
                self.log_test(test_name, False, f"测试异常: {str(e)}")
        
        # 生成测试报告
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        end_time = time.time()
        total_time = end_time - self.start_time
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round(success_rate, 2),
                "total_time": round(total_time, 2)
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # 打印总结
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {success_rate:.1f}%")
        print(f"总耗时: {total_time:.2f}秒")
        
        if failed_tests == 0:
            print("\n🎉 所有测试通过！系统功能正常。")
        else:
            print(f"\n⚠️ {failed_tests} 个测试失败，需要检查相关功能。")
        
        return report

async def main():
    """主函数"""
    async with E2ETestSuite() as test_suite:
        report = await test_suite.run_all_tests()
        
        # 保存测试报告
        report_file = f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存到: {report_file}")
        
        # 返回退出码
        return 0 if report["summary"]["failed_tests"] == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
