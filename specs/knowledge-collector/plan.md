# 实施计划: Aegis 知识采集增强器

**分支**: `###-aegis-knowledge-collector`
**日期**: 2025-05-02
**规范**: [spec.md](spec.md)

## 技术栈推荐

### 推荐方案：复用 BiliNote 技术栈（轻量化）

| 层级 | 推荐技术 | 选择理由 |
|------|----------|----------|
| **后端** | FastAPI（复用 BiliNote） | BiliNote 已有完整后端，直接集成 HTTP API |
| **前端** | React + Vite + Tailwind（精简） | BiliNote 已有，复用组件库，减少维护成本 |
| **数据库** | SQLite + SQLAlchemy | BiliNote 已有，成熟稳定 |
| **桌面端** | Tauri | BiliNote 已规划，前端可直接复用 |
| **AI 集成** | OpenAI 兼容 API（BiliNote GPT 模块） | BiliNote 已有 gpt 模块 |

### 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                      Aegis UI                          │
│                   (极简 Web/Tauri)                     │
├─────────────────────────────────────────────────────────┤
│                      Aegis API                        │
│   (配置管理 / 采集队列 / 状态管理 / 文件导入)          │
├─────────────────────────────────────────────────────────┤
│                    BiliNote API                       │
│  (视频下载 / 字幕转写 / GPT 生成) ← HTTP 调用          │
├─────────────────────────────────────────────────────────┤
│                   SQLite DB                          │
│         (Aegis 处理清单 + BiliNote 数据)              │
└─────────────────────────────────────────────────────────┘
```

### 文件结构

```
Athena/
├── Aegis/                    # 新增：Aegis 应用
│   ├── api/                 # FastAPI 路由
│   │   ├── config.py        # 配置管理
│   │   ├── collector.py    # 采集队列
│   │   └── import.py       # 文件导入
│   ├── db/                 # 数据库模型
│   │   └── models.py       # Aegis 数据模型
│   ├── core/               # 核心逻辑
│   │   ├── collector.py    # 采集器
│   │   └── yaml.py         # YAML 处理
│   ├── cli.py              # CLI 入口
│   └── config.yaml         # 配置文件
│
├── BiliNote/                # 已有：BiliNote 核心
│   ├── backend/            # FastAPI 后端
│   └── BillNote_frontend/ # React 前端
│
└── notes/                  # 笔记输出目录（可配置）
```

### 关键决策

1. **后端整合方式**: Aegis 作为独立服务，与 BiliNote 通过 HTTP API 通信
2. **启动流程**: Aegis 启动时检测 BiliNote 是否运行，如未运行则启动
3. **数据库**: 共用 BiliNote 的 SQLite，通过表前缀区分
4. **前端**: 复用 BiliNote 前端组件，Aegis 页面极致简化

### 依赖项

**Python (Aegis)**:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- python-dotenv
- requests（BiliNote API 调用）
- pyyaml

**前端**:
- 复用 BiliNote 前端依赖

### 性能优化

- **增量处理**: SQLite 事务批量处理
- **AI 调用**: 按需触发，缓存结果
- **文件操作**: 异步 I/O
- **BiliNote 通信**: HTTP 连接复用

### MVP 范围

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 配置管理 | P1 | config.yaml 管理 |
| 本地文件导入 | P1 | 扫描/补充 YAML |
| B 站视频采集 | P2 | 调用 BiliNote API |
| 增量同步 | P1 | SQLite 状态管理 |
| 目录迁移 | P2 | 移动 + 路径更新 |

## 复杂度跟踪

*无违规*

## 章程检查

- [x] TDD 实施流程已定义
- [x] 极简 UI 目标明确
- [x] 成本控制（按需 AI 调用）
- [x] 性能考虑（增量处理）
- [x] CLI 接口（FAPI → Web UI）

**下一步**: 运行 speckit.tasks 创建任务