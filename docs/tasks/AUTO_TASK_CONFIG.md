# 自动任务执行配置 · Drass

> 适用范围：Claude Code CLI / 项目级任务自动化  
> 任务列表入口：`docs/tasks/TASK_LIST_LANGCHAIN.md`

---

## 一、激活方式

| 方式 | 触发词 / 条件 |
|------|-------------|
| 命令触发 | `/auto` · `/task` · `/continue` · `/next` |
| 自然语言 | `继续执行任务` · `自动执行` · `开始自动化` |
| 文件检测 | 任务列表存在且有 `PENDING` / `IN_PROGRESS` 任务 |
| 紧急停止 | `/stop` · `/halt` · `停止` · 任意明确人工指令 |

---

## 二、执行流程

```
读取任务列表
    ↓
找到首个 PENDING / IN_PROGRESS 任务
    ↓
更新状态 → IN_PROGRESS
    ↓
┌─────────────────────────┐
│ Step 1  任务分析         │  理解需求 · 定位文件 · 制定方案
│ Step 2  代码实现         │  创建/修改文件 · 实现逻辑
│ Step 3  测试验证         │  单元测试 → 集成测试 → 验收标准
│ Step 4  代码提交         │  git add <files> && git commit
│ Step 5  更新任务状态     │  COMPLETED · 记录耗时和 commit hash
└─────────────────────────┘
    ↓
执行 /init 刷新 context
    ↓
继续下一个任务（列表为空时停止）
```

---

## 三、任务状态

| 状态 | 含义 | 自动行为 |
|------|------|---------|
| `PENDING` | 待执行 | 按顺序自动开始 |
| `IN_PROGRESS` | 执行中 | 优先续接 |
| `COMPLETED` | 已完成 | 跳过 |
| `BLOCKED` | 阻塞（需人工介入） | 记录原因，跳至下一个 |
| `CANCELLED` | 已取消 | 跳过 |

**执行优先级**：`IN_PROGRESS` > `PENDING`（按文件顺序）> `BLOCKED`（不自动执行，仅展示）

---

## 四、权限策略

| 操作类型 | 是否自动批准 |
|---------|------------|
| 文件读写（代码实现） | ✅ 自动 |
| `git add` / `git commit` | ✅ 自动 |
| `npm install` / `pip install` | ✅ 自动 |
| 测试运行 / 构建 | ✅ 自动 |
| `git push` / 部署脚本 | ❌ **需用户确认** |
| 修改 CI/CD 配置 | ❌ **需用户确认** |
| 删除超过 100 行的文件 | ❌ **需用户确认** |
| 修改 `package.json` 依赖 | ❌ **需用户确认** |

**只读保护文件**：`.git/config` · `.env`（生产） · `~/.ssh/*`

---

## 五、错误处理

| 错误类型 | 处理策略 |
|---------|---------|
| 编译错误 | 尝试修复，失败后标记 `BLOCKED` |
| 测试失败 | 分析修复，最多重试 3 次 |
| Git 冲突 | 尝试自动合并，无法解决则标记 `BLOCKED` |
| 网络错误 | 指数退避重试，最多 5 次 |
| 缺失依赖 | 自动安装后继续 |

---

## 六、代码质量要求

每个任务提交前必须满足：

- [ ] `ESLint` / `mypy` / `pytest` 通过（按项目类型）
- [ ] 无 `console.log` / `print` 残留在生产路径
- [ ] git commit message 格式：`type(scope): 简述`（约定式提交）
- [ ] 新增功能需有对应测试文件

---

## 七、Context 管理

触发 `/init` 刷新的时机：

- 每完成 1 个任务后
- 遇到 `BLOCKED` 任务时
- 连续执行超过 3 个任务后

---

## 八、输出格式

### 任务开始
```
▶ [TASK-001] 任务名称
  状态: PENDING → IN_PROGRESS
  开始: 2026-04-26 10:00:00
```

### 任务完成
```
✅ [TASK-001] 任务名称 · COMPLETED
   耗时: 12m
   修改: 5 个文件
   提交: a1b2c3d - feat: xxx
```

### 任务阻塞
```
❌ [TASK-002] 任务名称 · BLOCKED
   原因: 测试连续失败 3 次 - TypeError: ...
   操作: 跳至 TASK-003
```

---

## 九、任务列表查找顺序

系统按以下路径依次查找，找到即用：

1. `docs/tasks/TASK_LIST_LANGCHAIN.md`（主列表）
2. `docs/tasks/*TASK*.md`
3. 根目录 `*TASK*.md`

---

## 十、常用命令速查

```bash
/auto                      # 启动自动执行
/task status               # 查看当前任务进度
/task skip TASK-001        # 跳过指定任务
/task retry TASK-001       # 重试指定任务
/stop                      # 停止自动执行
```

---

## 十一、监控日志

执行日志写入：`logs/auto_task_YYYY-MM-DD.log`

记录内容：任务 ID · 开始/结束时间 · commit hash · 错误信息
