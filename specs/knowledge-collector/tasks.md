# 任务: Aegis 知识采集增强器

**输入**: 来自 `/specs/knowledge-collector/` 的设计文档
**前置条件**: plan.md(必需)、spec.md(必需)

**测试**: TDD 模式 - 测试在实现前编写

**组织结构**: 任务按用户故事分组，以便每个故事能够独立实施和测试

## 格式: `[ID] [P] [Story] 描述`
- **[P]**: 可以并行运行（不同文件，无依赖关系）
- **[Story]**: 此任务属于哪个用户故事（如 US1、US2...）
- 在描述中包含确切的文件路径

## 阶段 1: 设置（项目初始化）

**目的**: 项目初始化和基础结构

- [X] T001 在 `Athena/Aegis/` 下创建项目结构
- [X] T002 [P] 初始化 Python 项目（setup.py/pyproject.toml）
- [X] T003 [P] 配置依赖（fastapi、uvicorn、sqlalchemy、pyyaml、requests）
- [X] T004 在 `Athena/Aegis/` 下创建 `__init__.py`

---

## 阶段 2: 基础（阻塞前置条件）

**目的**: 在任何用户故事可以实施之前必须完成的核心基础设施

**关键**: 在此阶段完成之前，无法开始任何用户故事工作

- [X] T005 创建 `Athena/Aegis/config.yaml` 配置文件（空模板）
- [X] T006 [P] [US1] 在 `Athena/Aegis/core/config.py` 中实现配置加载模块
- [X] T007 [P] [US1] 在 `Athena/Aegis/core/config.py` 中实现配置验证
- [X] T008 创建 SQLite 数据库模型（处理清单表）
- [X] T009 在 `Athena/Aegis/db/models.py` 中定义 CollectionItem 实体
- [X] T010 在 `Athena/Aegis/db/models.py` 中定义状态枚举

**检查点**: 基础就绪 - 现在可以开始并行实施用户故事

---

## 阶段 3: 用户故事 1 - 配置管理 (优先级: P1)🎯 MVP

**目标**: 实现配置文件的加载、验证和管理功能

**独立测试**: 修改配置文件后，系统能够正确加载并验证配置项

### 用户故事 1 的测试（先编写）⚠️

**注意**: 先编写这些测试确保在实施前它们失败

- [X] T011 [P] [US1] 在 `tests/unit/test_config.py` 中编写配置加载测试
- [X] T012 [P] [US1] 在 `tests/unit/test_config.py` 中编写配置验证测试

### 用户故事 1 的实施

- [X] T013 [US1] 在 `Athena/Aegis/core/config.py` 中实现 YAML 配置加载
- [X] T014 [US1] 在 `Athena/Aegis/core/config.py` 中实现配置验证逻辑
- [X] T015 [US1] 在 `Athena/Aegis/core/config.py` 中实现默认值处理
- [ ] T016 [US1] 在 `Athena/Aegis/api/config.py` 中实现 GET /config 端点

**检查点**: 此时，用户故事 1 应该完全功能化且可独立测试

---

## 阶段 4: 用户故事 2 - 本地文件导入 (优先级: P1)🎯 MVP

**目标**: 扫描指定目录的 Markdown 文件，提取/补全 YAML 元数据

**独立测试**: 导入 100 个文件，元数据正确提取/补全

### 用户故事 2 的测试（先编写）⚠️

- [ ] T017 [P] [US2] 在 `tests/unit/test_yaml.py` 中编写 YAML 解析测试
- [ ] T018 [P] [US2] 在 `tests/unit/test_file_import.py` 中编写文件扫描测试

### 用户故事 2 的实施

- [ ] T019 [US2] 在 `Athena/Aegis/core/yaml.py` 中实现 YAML 解析
- [ ] T020 [US2] 在 `Athena/Aegis/core/yaml.py` 中实现标准字段补全
- [ ] T021 [US2] 在 `Athena/Aegis/core/file_import.py` 中实现目录扫描
- [ ] T022 [US2] 在 `Athena/Aegis/core/file_import.py` 中实现图片链接格式转换
- [ ] T023 [US2] 在 `Athena/Aegis/api/import.py` 中实现 POST /import 端点
- [ ] T024 [US2] 在 `Athena/Aegis/core/file_import.py` 中实现增量检查

**检查点**: 此时，用户故事 2 应该完全功能化且可独立测试

---

## 阶段 5: 用户故事 5 - 增量同步 (优先级: P1)🎯 MVP

**目标**: 增量处理，避免重复采集

**独立测试**: 重复运行，不重复处理已完成条目

### 用户故事 5 的测试（先编写）⚠️

- [ ] T025 [P] [US5] 在 `tests/unit/test_sync.py` 中编写增量检查测试

### 用户故事 5 的实施

- [ ] T026 [US5] 在 `Athena/Aegis/core/collector.py` 中实现状态管理
- [ ] T027 [US5] 在 `Athena/Aegis/core/collector.py` 中实现增量检测逻辑
- [ ] T028 [US5] 在 `Athena/Aegis/core/collector.py` 中实现状态更新
- [ ] T029 [US5] 在 `Athena/Aegis/db/dao.py` 中实现 DAO 层

**检查点**: 用户故事 1、2、5 可以一起测试（配置 + 导入 + 增量）

---

## 阶段 6: 用户故事 3 - B 站视频采集 (优先级: P2)

**目标**: 调用 BiliNote API 生成视频笔记

**独立测试**: 输入 B 站 URL，生成完整 Markdown 笔记

### 用户故事 3 的测试（先编写）⚠️

- [ ] T030 [P] [US3] 在 `tests/integration/test_bilibili.py` 编写 BiliNote API 集成测试

### 用户故事 3 的实施

- [ ] T031 [US3] 在 `Athena/Aegis/core/collector.py` 中实现 BiliNote HTTP 客户端
- [ ] T032 [US3] 在 `Athena/Aegis/core/collector.py` 中实现视频采集逻辑
- [ ] T033 [US3] 在 `Athena/Aegis/core/collector.py` 中实现笔记生成
- [ ] T034 [US3] 在 `Athena/Aegis/api/collector.py` 中实现 POST /collect 端点

**检查点**: 用户故事 3 与 US5 集成测试

---

## 阶段 7: 用户故事 4 - 多平台采集 (优先级: P2)

**目标**: 采集知乎、掘金、CSDN 等平台内容

### 用户故事 4 的实施

- [ ] T035 [P] [US4] 在 `Athena/Aegis/core/platform/` 中创建知乎采集器
- [ ] T036 [P] [US4] 在 `Athena/Aegis/core/platform/` 中创建掘金采集器
- [ ] T037 [P] [US4] 在 `Athena/Aegis/core/platform/` 中创建 CSDN 采集器
- [ ] T038 [US4] 在 `Athena/Aegis/core/collector.py` 中实现平台路由

---

## 阶段 8: 用户故事 6 - 输出目录迁移 (优先级: P2)

**目标**: 移动笔记到新位置并更新路径映射

### 用户故事 6 的实施

- [ ] T039 [US6] 在 `Athena/Aegis/core/migration.py` 中实现目录迁移
- [ ] T040 [US6] 在 `Athena/Aegis/core/migration.py` 中实现路径更新

---

## 阶段 9: 用户故事 7 - 按属性分流 (优先级: P2)

**目标**: 根据配置的内容属性将笔记分流到不同目录

**独立测试**: 根据配置的分流规则，正确将内容路由到目标目录

### 用户故事 7 的测试（先编写）⚠️

- [ ] TXXX [P] [US7] 在 `tests/unit/test_routing.py` 中编写分流规则测试

### 用户故事 7 的实施

- [ ] T041 [P] [US7] 在 `Athena/Aegis/core/routing.py` 中实现分流规则
- [ ] T042 [P] [US7] 在 `Athena/Aegis/core/routing.py` 中实现平台属性识别
- [ ] T043 [US7] 在 `Athena/Aegis/core/routing.py` 中实现路由执行

---

## 阶段 10: 完善与横切关注点

**目的**: 影响多个用户故事的改进

- [ ] T044 [P] 在 `docs/` 中更新配置说明文档
- [ ] T045 代码清理和重构
- [ ] T046 跨所有故事的集成测试
- [ ] T047 在 `tests/unit/` 中添加额外的单元测试（如要求）
- [ ] T048 运行 quickstart.md 验证

---

## 依赖关系与执行顺序

### 阶段依赖关系

- **设置（阶段 1）**: 无依赖关系 - 可立即开始
- **基础（阶段 2）**: 依赖于设置完成 - 阻塞所有用户故事
- **用户故事（阶段 3+）**: 都依赖于基础阶段完成
  - 然后用户故事可以并行进行
  - 或按优先级顺序进行（P1 → P2 → P3）

### 用户故事依赖关系

- **US1（配置管理 P1）**: 基础阶段后即可开始
- **US2（本地导入 P1）**: 依赖于 US1 完成配置加载
- **US5（增量同步 P1）**: 依赖于基础阶段完成
- **US3（B站采集 P2）**: 依赖于 US5（状态管理）
- **US4（多平台 P2）**: 依赖于 US3（可复用）
- **US6（目录迁移 P2）**: 依赖于 US1、US2
- **US7（分流 P2）**: 依赖于 US1、US2

### 每个用户故事内部

- 测试（如包含）必须在实施前编写并失败
- 模型在服务之前
- 服务在端点之前
- 核心实施在集成之前
- 故事完成后才移至下一个优先级

### 并行机会

- 所有标���为 [P] 的设置任务可以并行运行
- 所有标记为 [P] 的基础任务可以并行运行（阶段 2 内）
- 基础阶段完成后，所有用户故事可以并行开始
- 所有标记为 [P] 的测试可以并行运行

---

## 并行示例: 用户故事 1

```bash
# 一起启动用户故事 1 的所有测试：
任务: "在 tests/unit/test_config.py 中编写配置加载测试"
任务: "在 tests/unit/test_config.py 中编写配置验证测试"

# 一起启动用户故事 1 的实现：
任务: "在 Aegis/core/config.py 中实现 YAML 配置加载"
```

---

## 实施策略

### 仅 MVP（US1 + US2 + US5）

1. 完成阶段 1: 设置
2. 完成阶段 2: 基础
3. 完成阶段 3: 用户故事 1（配置管理）
4. 完成阶段 4: 用户故事 2（本地文件导入）
5. 完成阶段 5: 用户故事 5（增量同步）
6. **停止并验证**: 独立测试用户故事 1、2、5
7. 如准备好则部署/演示

### 增量交付

1. 完成设置 + 基础 → 基础就绪
2. 添加 US1 配置管理 → 独立测试 → 部署
3. 添加 US2 本地导入 → 独立测试 → 部署
4. 添加 US5 增量同步 → 独立测试 → 部署
5. 添加 US3 B站采集 → 独立测试 → 部署
6. 其他用户故事...

---

## 任务统计

| 用户故事 | 任务数 | 优先级 |
|----------|--------|--------|
| US1 配置管理 | 6 | P1 |
| US2 本地文件导入 | 8 | P1 |
| US5 增量同步 | 5 | P1 |
| US3 B站视频采集 | 5 | P2 |
| US4 多平台采集 | 4 | P2 |
| US6 输出目录迁移 | 2 | P2 |
| US7 按属性分流 | 3 | P2 |
| 设置/基础 | 10 | - |
| 完善 | 5 | - |
| **总计** | **48** | - |