#!/usr/bin/env python3
"""
简单测试增强版审计日志组件功能
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

async def test_enhanced_audit_logs():
    """测试增强版审计日志功能"""
    print("🧪 开始测试增强版审计日志组件功能...")
    
    try:
        from app.services.audit_service_enhanced import AuditServiceEnhanced, AuditEventType, AuditSeverity, AuditStatus
        
        # 初始化审计服务
        audit_service = AuditServiceEnhanced()
        
        # 测试1: 健康检查
        print("\n📋 测试1: 健康检查")
        health = await audit_service.health_check()
        print(f"✅ 健康检查: {health}")
        
        # 测试2: 记录审计事件
        print("\n📋 测试2: 记录审计事件")
        
        await audit_service.log_audit_event(
            event_type=AuditEventType.USER_LOGIN,
            user_id="user001",
            action="登录系统",
            resource_type="system",
            resource_id="login_system",
            details={"method": "email", "ip": "192.168.1.100", "user_name": "张三", "user_role": "管理员"},
            severity=AuditSeverity.LOW,
            status=AuditStatus.SUCCESS,
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        print("✅ 成功记录审计事件")
        
        # 测试3: 查询审计日志
        print("\n📋 测试3: 查询审计日志")
        
        logs = await audit_service.get_audit_logs(
            user_id=None,
            event_type=None,
            severity=None,
            status=None,
            start_date=None,
            end_date=None,
            limit=10,
            offset=0
        )
        
        print(f"✅ 查询到 {len(logs)} 条日志记录")
        
        # 测试4: 统计功能
        print("\n📋 测试4: 统计功能")
        
        stats = await audit_service.get_audit_statistics(
            start_date=None,
            end_date=None
        )
        
        print(f"✅ 统计信息:")
        print(f"   - 总日志数: {stats.get('total_logs', 0)}")
        print(f"   - 成功操作: {stats.get('success_count', 0)}")
        print(f"   - 失败操作: {stats.get('failed_count', 0)}")
        
        print("\n🎉 增强版审计日志组件功能测试完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🚀 启动增强版审计日志组件测试...")
    
    success = await test_enhanced_audit_logs()
    
    if success:
        print("\n✅ 所有测试通过！增强版审计日志组件已准备就绪。")
    else:
        print("\n❌ 测试失败，请检查错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
