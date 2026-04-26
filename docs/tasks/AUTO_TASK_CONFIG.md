# 自动任务执行配置 · Drass

> 适用：Claude Code CLI · 项目自动化任务驱动开发  
> 主任务列表：`docs/tasks/TASK_LIST_LANGCHAIN.md`  
> 更新时间：2026-04-26

---

## 一、激活 / 停止

```
激活：/auto · /task · /continue · /next
      继续执行任务 · 自动执行 · 开始自动化

停止：/stop · /halt · 停止 · 任意明确的人工指令
```

---

## 二、执行流程

```
① 读取任务列表，找首个 PENDING / IN_PROGRESS 任务
② 状态 → IN_PROGRESS
③ 分析需求，定位相关文件，制定实现方案
④ 编写/修改代码
⑤ 运行测试（pytest / npm test），确认通过
⑥ git add <具体文件> && git commit -m "type(scope): 描述"
⑦ 状态 → COMPLETED，记录耗时 + commit hash
⑧ 执行 /init 刷新 context
⑨ 重复 ①，列表清空后停止
```

---

## 三、任务状态与优先级

| 状态 | 含义 | 执行行为 |
|------|------|---------|
| `IN_PROGRESS` | 执行中（中断续接） | **优先执行** |
| `PENDING` | 待执行 | 按文件顺序执行 |
| `BLOCKED` | 需人工介入 | 记录原因，跳过，继续下一个 |
| `COMPLETED` | 已完成 | 跳过 |
| `CANCELLED` | 已取消 | 跳过 |

---

## 四、权限边界

**自动执行（无需确认）**
- 文件读写（src / tests / docs）
- `git add <files>` · `git commit`
- `pip install` · `npm install`
- 测试运行 · 本地构建

**必须用户确认**
- `git push` · 任何部署脚本
- 删除超过 100 行的文件
- 修改 `package.json` / `requirements.txt` 依赖版本
- 修改 `docker-compose.yml` · CI/CD 配置

**只读保护**
- `.env`（生产环境） · `.git/config` · `~/.ssh/*`

---

## 五、错误处理

| 错误类型 | 策略 |
|---------|------|
| 编译 / 语法错误 | 修复后重试，连续失败 → `BLOCKED` |
| 测试失败 | 最多重试 3 次，仍失败 → `BLOCKED` |
| 缺失依赖 | 自动安装后继续 |
| Git 冲突 | 尝试合并，无法解决 → `BLOCKED` |
| 网络超时 | 指数退避，最多重试 5 次 |

---

## 六、提交规范

格式：`type(scope): 简述`

| type | 场景 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（不改功能） |
| `test` | 测试相关 |
| `docs` | 文档变更 |
| `chore` | 构建/脚本/依赖 |

示例：`feat(rag): 添加多路召回重排序支持`

---

## 七、质量检查（提交前必过）

- `pytest services/main-app/` 通过
- `npm run lint` 通过（前端任务）
- 无 `print()` / `console.log` 残留在非测试文件
- 新功能必须有对应测试用例

---

## 八、Context 刷新时机

每完成 1 个任务、遇到 `BLOCKED`、或连续执行超过 3 个任务后，执行 `/init`。

---

## 九、输出格式

```
▶ [TASK-001] 任务名称  PENDING → IN_PROGRESS

✅ [TASK-001] 任务名称  COMPLETED
   耗时 8m · 修改 3 文件 · 提交 a1b2c3d

❌ [TASK-002] 任务名称  BLOCKED
   原因: pytest 失败 3 次 · 跳至 TASK-003
```

---

## 十、任务列表查找路径

1. `docs/tasks/TASK_LIST_LANGCHAIN.md`（主列表，优先）
2. `docs/tasks/*TASK*.md`
3. 根目录 `*TASK*.md`

---

## 十一、日志

写入路径：`logs/auto_task_YYYY-MM-DD.log`  
记录：任务 ID · 起止时间 · commit hash · 错误原因
