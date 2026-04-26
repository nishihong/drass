#!/usr/bin/env python3
"""
安全加固功能测试脚本
测试权限控制、数据加密、安全审计、漏洞扫描等功能
"""

import asyncio
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8888"
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class SecurityTestRunner:
    """安全测试运行器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        
    async def run_all_tests(self):
        """运行所有安全测试"""
        print("🔒 开始安全加固功能测试...")
        print("=" * 60)
        
        # 1. 认证测试
        await self.test_authentication()
        
        # 2. 数据加密测试
        await self.test_data_encryption()
        
        # 3. RSA加密测试
        await self.test_rsa_encryption()
        
        # 4. 密码哈希测试
        await self.test_password_hashing()
        
        # 5. 令牌管理测试
        await self.test_token_management()
        
        # 6. 权限检查测试
        await self.test_permission_checking()
        
        # 7. 安全报告测试
        await self.test_security_reporting()
        
        # 8. 漏洞扫描测试
        await self.test_vulnerability_scanning()
        
        # 9. Web应用扫描测试
        await self.test_web_application_scanning()
        
        # 10. 安全测试综合测试
        await self.test_comprehensive_security_tests()
        
        # 生成测试报告
        self.generate_test_report()
    
    async def test_authentication(self):
        """测试认证功能"""
        print("\n🔐 测试认证功能...")
        
        try:
            # 测试登录
            response = self.session.post(
                f"{BASE_URL}/api/v1/auth/login",
                data={
                    "username": TEST_USER["email"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print("✅ 登录成功")
                
                # 设置认证头
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                
                self.test_results.append({
                    "test": "authentication",
                    "status": "passed",
                    "details": "Login successful"
                })
            else:
                print(f"❌ 登录失败: {response.status_code}")
                self.test_results.append({
                    "test": "authentication",
                    "status": "failed",
                    "details": f"Login failed: {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 认证测试异常: {e}")
            self.test_results.append({
                "test": "authentication",
                "status": "error",
                "details": str(e)
            })
    
    async def test_data_encryption(self):
        """测试数据加密功能"""
        print("\n🔒 测试数据加密功能...")
        
        try:
            # 测试加密
            test_data = "This is sensitive data that needs to be encrypted"
            encrypt_response = self.session.post(
                f"{BASE_URL}/api/v1/security/encrypt",
                json={"data": test_data}
            )
            
            if encrypt_response.status_code == 200:
                encrypt_data = encrypt_response.json()
                encrypted_data = encrypt_data["encrypted_data"]
                print("✅ 数据加密成功")
                
                # 测试解密
                decrypt_response = self.session.post(
                    f"{BASE_URL}/api/v1/security/decrypt",
                    json={"encrypted_data": encrypted_data}
                )
                
                if decrypt_response.status_code == 200:
                    decrypt_data = decrypt_response.json()
                    decrypted_data = decrypt_data["decrypted_data"]
                    
                    if decrypted_data == test_data:
                        print("✅ 数据解密成功，数据完整性验证通过")
                        self.test_results.append({
                            "test": "data_encryption",
                            "status": "passed",
                            "details": "Encryption and decryption successful"
                        })
                    else:
                        print("❌ 数据解密后内容不匹配")
                        self.test_results.append({
                            "test": "data_encryption",
                            "status": "failed",
                            "details": "Decrypted data does not match original"
                        })
                else:
                    print(f"❌ 数据解密失败: {decrypt_response.status_code}")
                    self.test_results.append({
                        "test": "data_encryption",
                        "status": "failed",
                        "details": f"Decryption failed: {decrypt_response.status_code}"
                    })
            else:
                print(f"❌ 数据加密失败: {encrypt_response.status_code}")
                self.test_results.append({
                    "test": "data_encryption",
                    "status": "failed",
                    "details": f"Encryption failed: {encrypt_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 数据加密测试异常: {e}")
            self.test_results.append({
                "test": "data_encryption",
                "status": "error",
                "details": str(e)
            })
    
    async def test_rsa_encryption(self):
        """测试RSA加密功能"""
        print("\n🔐 测试RSA加密功能...")
        
        try:
            # 获取公钥
            public_key_response = self.session.get(f"{BASE_URL}/api/v1/security/public-key")
            
            if public_key_response.status_code == 200:
                public_key_data = public_key_response.json()
                print("✅ 获取RSA公钥成功")
                
                # 测试RSA加密
                test_data = "This is data for RSA encryption"
                rsa_encrypt_response = self.session.post(
                    f"{BASE_URL}/api/v1/security/rsa/encrypt",
                    json={"data": test_data}
                )
                
                if rsa_encrypt_response.status_code == 200:
                    rsa_encrypt_data = rsa_encrypt_response.json()
                    rsa_encrypted_data = rsa_encrypt_data["encrypted_data"]
                    print("✅ RSA加密成功")
                    
                    # 测试RSA解密
                    rsa_decrypt_response = self.session.post(
                        f"{BASE_URL}/api/v1/security/rsa/decrypt",
                        json={"encrypted_data": rsa_encrypted_data}
                    )
                    
                    if rsa_decrypt_response.status_code == 200:
                        rsa_decrypt_data = rsa_decrypt_response.json()
                        rsa_decrypted_data = rsa_decrypt_data["decrypted_data"]
                        
                        if rsa_decrypted_data == test_data:
                            print("✅ RSA解密成功，数据完整性验证通过")
                            self.test_results.append({
                                "test": "rsa_encryption",
                                "status": "passed",
                                "details": "RSA encryption and decryption successful"
                            })
                        else:
                            print("❌ RSA解密后内容不匹配")
                            self.test_results.append({
                                "test": "rsa_encryption",
                                "status": "failed",
                                "details": "RSA decrypted data does not match original"
                            })
                    else:
                        print(f"❌ RSA解密失败: {rsa_decrypt_response.status_code}")
                        self.test_results.append({
                            "test": "rsa_encryption",
                            "status": "failed",
                            "details": f"RSA decryption failed: {rsa_decrypt_response.status_code}"
                        })
                else:
                    print(f"❌ RSA加密失败: {rsa_encrypt_response.status_code}")
                    self.test_results.append({
                        "test": "rsa_encryption",
                        "status": "failed",
                        "details": f"RSA encryption failed: {rsa_encrypt_response.status_code}"
                    })
            else:
                print(f"❌ 获取RSA公钥失败: {public_key_response.status_code}")
                self.test_results.append({
                    "test": "rsa_encryption",
                    "status": "failed",
                    "details": f"Failed to get RSA public key: {public_key_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ RSA加密测试异常: {e}")
            self.test_results.append({
                "test": "rsa_encryption",
                "status": "error",
                "details": str(e)
            })
    
    async def test_password_hashing(self):
        """测试密码哈希功能"""
        print("\n🔑 测试密码哈希功能...")
        
        try:
            # 测试密码哈希
            test_password = "testpassword123"
            hash_response = self.session.post(
                f"{BASE_URL}/api/v1/security/password/hash",
                json={"password": test_password}
            )
            
            if hash_response.status_code == 200:
                hash_data = hash_response.json()
                hashed_password = hash_data["hashed_password"]
                salt = hash_data["salt"]
                print("✅ 密码哈希成功")
                
                # 测试密码验证
                verify_response = self.session.post(
                    f"{BASE_URL}/api/v1/security/password/verify",
                    json={
                        "password": test_password,
                        "hashed_password": hashed_password,
                        "salt": salt
                    }
                )
                
                if verify_response.status_code == 200:
                    verify_data = verify_response.json()
                    is_valid = verify_data["is_valid"]
                    
                    if is_valid:
                        print("✅ 密码验证成功")
                        self.test_results.append({
                            "test": "password_hashing",
                            "status": "passed",
                            "details": "Password hashing and verification successful"
                        })
                    else:
                        print("❌ 密码验证失败")
                        self.test_results.append({
                            "test": "password_hashing",
                            "status": "failed",
                            "details": "Password verification failed"
                        })
                else:
                    print(f"❌ 密码验证请求失败: {verify_response.status_code}")
                    self.test_results.append({
                        "test": "password_hashing",
                        "status": "failed",
                        "details": f"Password verification request failed: {verify_response.status_code}"
                    })
            else:
                print(f"❌ 密码哈希失败: {hash_response.status_code}")
                self.test_results.append({
                    "test": "password_hashing",
                    "status": "failed",
                    "details": f"Password hashing failed: {hash_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 密码哈希测试异常: {e}")
            self.test_results.append({
                "test": "password_hashing",
                "status": "error",
                "details": str(e)
            })
    
    async def test_token_management(self):
        """测试令牌管理功能"""
        print("\n🎫 测试令牌管理功能...")
        
        try:
            # 测试生成安全令牌
            generate_response = self.session.post(
                f"{BASE_URL}/api/v1/security/token/generate",
                json={
                    "user_id": "test-user-id",
                    "additional_claims": {"role": "user"}
                }
            )
            
            if generate_response.status_code == 200:
                generate_data = generate_response.json()
                new_token = generate_data["token"]
                token_id = generate_data["token_id"]
                print("✅ 安全令牌生成成功")
                
                # 测试撤销令牌
                revoke_response = self.session.post(
                    f"{BASE_URL}/api/v1/security/token/revoke",
                    json={"token": new_token}
                )
                
                if revoke_response.status_code == 200:
                    revoke_data = revoke_response.json()
                    success = revoke_data["success"]
                    
                    if success:
                        print("✅ 令牌撤销成功")
                        self.test_results.append({
                            "test": "token_management",
                            "status": "passed",
                            "details": "Token generation and revocation successful"
                        })
                    else:
                        print("❌ 令牌撤销失败")
                        self.test_results.append({
                            "test": "token_management",
                            "status": "failed",
                            "details": "Token revocation failed"
                        })
                else:
                    print(f"❌ 令牌撤销请求失败: {revoke_response.status_code}")
                    self.test_results.append({
                        "test": "token_management",
                        "status": "failed",
                        "details": f"Token revocation request failed: {revoke_response.status_code}"
                    })
            else:
                print(f"❌ 安全令牌生成失败: {generate_response.status_code}")
                self.test_results.append({
                    "test": "token_management",
                    "status": "failed",
                    "details": f"Token generation failed: {generate_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 令牌管理测试异常: {e}")
            self.test_results.append({
                "test": "token_management",
                "status": "error",
                "details": str(e)
            })
    
    async def test_permission_checking(self):
        """测试权限检查功能"""
        print("\n🔐 测试权限检查功能...")
        
        try:
            # 测试权限检查
            permission_response = self.session.post(
                f"{BASE_URL}/api/v1/security/permission/check",
                json={
                    "user_id": "test-user-id",
                    "resource": "documents",
                    "action": "read"
                }
            )
            
            if permission_response.status_code == 200:
                permission_data = permission_response.json()
                has_permission = permission_data["has_permission"]
                print(f"✅ 权限检查成功: {has_permission}")
                
                self.test_results.append({
                    "test": "permission_checking",
                    "status": "passed",
                    "details": f"Permission check successful: {has_permission}"
                })
            else:
                print(f"❌ 权限检查失败: {permission_response.status_code}")
                self.test_results.append({
                    "test": "permission_checking",
                    "status": "failed",
                    "details": f"Permission check failed: {permission_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 权限检查测试异常: {e}")
            self.test_results.append({
                "test": "permission_checking",
                "status": "error",
                "details": str(e)
            })
    
    async def test_security_reporting(self):
        """测试安全报告功能"""
        print("\n📊 测试安全报告功能...")
        
        try:
            # 测试生成安全报告
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=7)
            
            report_response = self.session.post(
                f"{BASE_URL}/api/v1/security/report",
                json={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
            
            if report_response.status_code == 200:
                report_data = report_response.json()
                print("✅ 安全报告生成成功")
                print(f"   报告期间: {report_data['report_period']['start_date']} 到 {report_data['report_period']['end_date']}")
                print(f"   总事件数: {report_data['summary']['total_events']}")
                
                self.test_results.append({
                    "test": "security_reporting",
                    "status": "passed",
                    "details": f"Security report generated successfully: {report_data['summary']['total_events']} events"
                })
            else:
                print(f"❌ 安全报告生成失败: {report_response.status_code}")
                self.test_results.append({
                    "test": "security_reporting",
                    "status": "failed",
                    "details": f"Security report generation failed: {report_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 安全报告测试异常: {e}")
            self.test_results.append({
                "test": "security_reporting",
                "status": "error",
                "details": str(e)
            })
    
    async def test_vulnerability_scanning(self):
        """测试漏洞扫描功能"""
        print("\n🔍 测试漏洞扫描功能...")
        
        try:
            # 测试扫描当前项目
            scan_response = self.session.get(f"{BASE_URL}/api/v1/security-testing/scan/current-project")
            
            if scan_response.status_code == 200:
                scan_data = scan_response.json()
                print("✅ 项目漏洞扫描成功")
                print(f"   发现漏洞数: {scan_data['total_vulnerabilities']}")
                print(f"   严重程度分布: {scan_data['severity_summary']}")
                
                self.test_results.append({
                    "test": "vulnerability_scanning",
                    "status": "passed",
                    "details": f"Vulnerability scan completed: {scan_data['total_vulnerabilities']} vulnerabilities found"
                })
            else:
                print(f"❌ 项目漏洞扫描失败: {scan_response.status_code}")
                self.test_results.append({
                    "test": "vulnerability_scanning",
                    "status": "failed",
                    "details": f"Vulnerability scan failed: {scan_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 漏洞扫描测试异常: {e}")
            self.test_results.append({
                "test": "vulnerability_scanning",
                "status": "error",
                "details": str(e)
            })
    
    async def test_web_application_scanning(self):
        """测试Web应用扫描功能"""
        print("\n🌐 测试Web应用扫描功能...")
        
        try:
            # 测试扫描本地应用
            scan_response = self.session.get(f"{BASE_URL}/api/v1/security-testing/scan/local-app")
            
            if scan_response.status_code == 200:
                scan_data = scan_response.json()
                print("✅ Web应用扫描成功")
                print(f"   发现漏洞数: {scan_data['total_vulnerabilities']}")
                print(f"   严重程度分布: {scan_data['severity_summary']}")
                
                self.test_results.append({
                    "test": "web_application_scanning",
                    "status": "passed",
                    "details": f"Web application scan completed: {scan_data['total_vulnerabilities']} vulnerabilities found"
                })
            else:
                print(f"❌ Web应用扫描失败: {scan_response.status_code}")
                self.test_results.append({
                    "test": "web_application_scanning",
                    "status": "failed",
                    "details": f"Web application scan failed: {scan_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Web应用扫描测试异常: {e}")
            self.test_results.append({
                "test": "web_application_scanning",
                "status": "error",
                "details": str(e)
            })
    
    async def test_comprehensive_security_tests(self):
        """测试综合安全测试功能"""
        print("\n🧪 测试综合安全测试功能...")
        
        try:
            # 测试运行综合安全测试
            test_response = self.session.post(
                f"{BASE_URL}/api/v1/security-testing/test",
                json={"test_type": "all"}
            )
            
            if test_response.status_code == 200:
                test_data = test_response.json()
                print("✅ 综合安全测试成功")
                print(f"   测试类型: {test_data['test_type']}")
                print(f"   测试结果: {test_data['results']}")
                
                self.test_results.append({
                    "test": "comprehensive_security_tests",
                    "status": "passed",
                    "details": f"Comprehensive security tests completed: {test_data['test_type']}"
                })
            else:
                print(f"❌ 综合安全测试失败: {test_response.status_code}")
                self.test_results.append({
                    "test": "comprehensive_security_tests",
                    "status": "failed",
                    "details": f"Comprehensive security tests failed: {test_response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ 综合安全测试异常: {e}")
            self.test_results.append({
                "test": "comprehensive_security_tests",
                "status": "error",
                "details": str(e)
            })
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📋 安全加固功能测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "passed"])
        failed_tests = len([r for r in self.test_results if r["status"] == "failed"])
        error_tests = len([r for r in self.test_results if r["status"] == "error"])
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"错误测试: {error_tests}")
        print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n详细结果:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "passed" else "❌" if result["status"] == "failed" else "⚠️"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   详情: {result['details']}")
        
        # 保存测试报告到文件
        report_data = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "error_tests": error_tests,
            "success_rate": (passed_tests/total_tests)*100,
            "results": self.test_results
        }
        
        with open("security_enhancement_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细测试报告已保存到: security_enhancement_test_report.json")
        
        if passed_tests == total_tests:
            print("\n🎉 所有安全加固功能测试通过！")
        else:
            print(f"\n⚠️  有 {failed_tests + error_tests} 个测试失败，请检查相关功能。")


async def main():
    """主函数"""
    runner = SecurityTestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
