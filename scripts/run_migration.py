#!/usr/bin/env python3
"""
运行数据库迁移
"""

import sys
import os
import asyncio

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'services', 'main-app'))

def run_migration():
    """运行数据库迁移"""
    try:
        from app.database.migration_manager import create_migration_manager
        
        print("🔄 开始数据库迁移...")
        
        migration_manager = create_migration_manager()
        
        # 获取待应用的迁移
        pending_migrations = migration_manager.get_pending_migrations()
        print(f"📋 发现 {len(pending_migrations)} 个待应用的迁移")
        
        # 应用迁移
        for migration in pending_migrations:
            print(f"🔄 应用迁移: {migration['id']} - {migration['name']}")
            success = migration_manager.apply_migration(migration['id'])
            if success:
                print(f"✅ 迁移 {migration['id']} 应用成功")
            else:
                print(f"❌ 迁移 {migration['id']} 应用失败")
        
        print("✅ 数据库迁移完成")
        
    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
