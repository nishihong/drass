# Claude Code 自动任务执行配置

## 系统配置
这个文件配置了 Claude Code 的自动任务执行行为。当没有明确的用户指令时，Claude Code 会自动检测并执行待处理的任务。
## 核心规则
  1. **自动批准**: 所有需要用户确认的操作，默认视为已批准，直接执行
  2. **Context管理**: 每完成一个任务后，执行 `/init` 刷新context
  3. **连续执行**: 完成当前任务后，自动开始下一个PENDING状态的任务
  4. **错误处理**: 遇到错误时，记录错误信息，标记任务为BLOCKED，继续下一个任务

## 激活条件
以下任一条件满足时，自动任务执行将被激活：
1. 用户输入包含关键词：`/auto`, `/task`, `/continue`, `/next`
2. 检测到 `TASK_LIST*.md` 文件存在且有 PENDING 或 IN_PROGRESS 任务
3. 用户明确说："继续执行任务"、"自动执行"、"开始自动化"
4. 没有其他明确指令时的默认行为

## 自动执行模式
### 启动触发器
```bash
# 自动检测模式
- 每次对话开始时检查任务列表
- 用户输入后无明确指令时检查任务列表
- 完成一个任务后自动继续下一个

# 手动触发模式  
- 用户输入：/auto
- 用户输入：继续执行任务列表
- 用户输入：自动执行下一个任务
```
## 执行流程
  1. 读取 任务列表.md 文件
  2. 找到第一个状态为 PENDING 或 IN_PROGRESS 的任务
  3. 将任务状态更新为 IN_PROGRESS
  4. 执行任务开发工作
  5. 运行测试验证
  6. 提交代码: `git add . && git commit -m "提交信息"`
  7. 更新任务状态为 COMPLETED
  8. 保存 TASK_LIST.md
  9. 输出: "Task X completed. Executing /init to refresh context..."
  10. 等待新的context后继续下一个任务

  ## 任务执行模板
  对于每个任务，按以下步骤执行：

  ### Step 1: 任务分析
  - 理解需求
  - 识别相关文件
  - 制定实现方案

  ### Step 2: 代码实现
  - 创建/修改必要的文件
  - 实现功能逻辑
  - 添加必要的注释

  ### Step 3: 测试验证
  - 运行单元测试
  - 执行集成测试
  - 验证验收标准

  ### Step 4: 代码提交
  ```bash
  git add .
  git commit -m "commit message from task list"
  git push origin current-branch

  Step 5: 更新任务状态

  - 标记当前任务为 COMPLETED
  - 记录完成时间
  - 添加实际完成的工作说明

  特殊指令

  - 跳过任务: 如果任务被标记为 BLOCKED 或 CANCELLED，自动跳过
  - 依赖处理: 如果任务有依赖，等待依赖任务完成
  - 回滚机制: 如果任务失败，自动回滚并标记为 BLOCKED

  输出格式

  每个任务完成后输出：
  ========================================
  ✅ Task [编号]: [任务名称] - COMPLETED
  ⏱️ Time: [耗时]
  📝 Changes: [修改文件数]
  💾 Commit: [commit hash]
  ========================================
  🔄 Executing /init to refresh context...
  ⏳ Starting next task: Task [下一个编号]
  ========================================

### 执行优先级
1. **高优先级**: BLOCKED 状态的任务（需要人工干预）
2. **中优先级**: IN_PROGRESS 状态的任务（继续执行）
3. **低优先级**: PENDING 状态的任务（按顺序执行）

## 任务列表位置
系统会按以下顺序查找任务列表：
1. `./TASK_LIST.md` (当前目录)
2. `./devops/TASK_LIST.md` (DevOps目录)  
3. `./docs/TASK_LIST.md` (文档目录)
4. `./frontend/flutter/TASK_LIST.md` (Flutter目录)
5. 根目录下的任何 `*TASK*.md` 文件
6. `./backend/docs/`目录下的以`*_Tasks*.md`结尾的文件

## 自动执行规则
### 权限假设
- 所有文件操作：✅ 自动批准
- Git 操作（add, commit, push）：✅ 自动批准  
- 包管理（npm install, flutter pub get）：✅ 自动批准
- 测试运行：✅ 自动批准
- 构建操作：✅ 自动批准
- 部署操作：❌ 需要用户确认

### 🌐 English-Only Output Policy (Updated 2025-01-28)
**ALL generated content must be in English to support international team collaboration:**
- ✅ Code comments: Only English comments
- ✅ Documentation: All .md files in English
- ✅ Variable names: English naming conventions
- ✅ Function names: English descriptive names
- ✅ Git commit messages: English only
- ✅ Error messages: English user-facing messages
- ✅ Log output: English logging statements
- ❌ FORBIDDEN: Chinese characters in code or documentation

### 错误处理
```yaml
处理策略:
  - 编译错误: 尝试修复，失败后标记 BLOCKED
  - 测试失败: 分析并修复，重试3次
  - Git 冲突: 自动合并，冲突时标记 BLOCKED
  - 网络错误: 重试5次，间隔递增
  - 依赖错误: 自动安装缺失依赖
```

### Context 管理
```yaml
Context 刷新策略:
  - 每完成一个任务后执行 /init
  - 遇到 BLOCKED 任务时执行 /init  
  - 连续执行超过3个任务后执行 /init
  - 检测到内存使用过高时执行 /init
```

## 输出格式标准
### 任务开始
```
🤖 AUTO-TASK: Starting Task [ID]: [Title]
📋 Status: PENDING → IN_PROGRESS  
⏰ Started: [timestamp]
📍 Branch: [current_branch]
```

### 任务进行中
```
🔄 AUTO-TASK: [Step description]
📝 Modified: [file_path]
✅ Completed: [sub_task]
```

### 任务完成
```
✅ AUTO-TASK: Task [ID] COMPLETED
⏱️ Duration: [time_taken]
📝 Files Modified: [count]
💾 Commit: [hash] - [commit_message]
📋 Status: IN_PROGRESS → COMPLETED
🔄 AUTO-INIT: Refreshing context...
⏳ AUTO-TASK: Next task in 3 seconds...
```

### 任务阻塞
```
❌ AUTO-TASK: Task [ID] BLOCKED
🚫 Error: [error_description]  
📋 Status: IN_PROGRESS → BLOCKED
🔄 AUTO-INIT: Refreshing context...
⏳ AUTO-TASK: Skipping to next available task...
```

## 安全约束
### 文件保护
```yaml
只读文件:
  - .git/config
  - .env files (production)
  - /etc/* (system files)
  - ~/.ssh/* (SSH keys)

需要确认的操作:
  - 删除超过100行的文件
  - 修改 package.json dependencies
  - 执行 deploy/production 脚本
  - 修改 CI/CD 配置文件
```

### 代码质量检查
```yaml
自动检查:
  - ESLint/Flutter Analyze 必须通过
  - 单元测试覆盖率不低于80%
  - 不允许 console.log/debugPrint 在生产代码
  - Git commit 消息符合约定式提交
```

## 监控和日志
### 执行日志
所有自动执行的操作都会记录在 `./logs/auto_task_[date].log`

### 统计信息
```yaml
跟踪指标:
  - 任务完成率
  - 平均执行时间  
  - 错误频率
  - Context 刷新次数
  - 代码提交数量
```

## 紧急停止
用户可以通过以下方式停止自动执行：
- 输入：`/stop` 或 `/halt`
- 输入：`停止自动执行`
- 按 Ctrl+C (如果支持)
- 输入任何明确的人工指令

## 示例激活命令
```bash
# 开始自动执行
/auto
继续执行任务列表
自动执行下一个任务
开始自动化开发流程

# 检查任务状态
/task status
检查任务列表状态
显示当前任务进度

# 手动控制
/task skip [ID]        # 跳过指定任务
/task retry [ID]       # 重试指定任务  
/task priority [ID]    # 提升任务优先级
```

## 集成到 CLAUDE.md
将以下内容添加到项目的 CLAUDE.md 文件中：

```markdown
# 自动任务执行
当检测到任务列表文件 (TASK_LIST.md) 存在且有待处理任务时，Claude Code 会自动进入任务执行模式。

## 触发条件
- 用户输入包含 `/auto`, `/task`, `/continue`  
- 检测到待处理任务
- 没有明确用户指令时的默认行为

## 行为模式
1. 自动读取任务列表
2. 按优先级执行待处理任务
3. 每完成一个任务后刷新 context
4. 自动提交代码并更新任务状态
5. 继续执行下一个任务直到列表为空

详细配置参见 AUTO_TASK_CONFIG.md
```