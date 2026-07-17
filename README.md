# AI大模型Prompt安全防护系统

基于FastAPI的AI大模型Prompt安全防护系统，提供7层防御架构，保护LLM应用免受Prompt注入、越狱攻击、数据泄露等安全威胁。

## 功能特性

- **7层防御架构**：Gateway层、输入预处理层、系统Prompt保护、模型推理层、输出后校验层、上下文/会话管理、监控审计层
- **Prompt注入防护**：检测并阻止直接指令覆盖、角色扮演诱导、DAN模式等注入攻击
- **越狱防护**：识别暴力、欺诈、恶意代码等危险内容
- **PII脱敏**：自动识别并脱敏手机号、身份证、邮箱、银行卡等敏感信息
- **SQL/XSS注入防护**：检测代码注入攻击
- **混淆检测**：识别Base64、Hex、Unicode编码等混淆方式
- **RAG安全**：文档摄入安全检查、ACL权限过滤
- **Agent安全**：工具调用白名单、参数校验、权限控制
- **多模态支持**：文本、图像、音频安全处理

## 技术栈

- Python 3.10+
- FastAPI 0.115+
- Pydantic 2.8+
- SQLAlchemy 2.0+
- Redis 5.0+
- pytest 8.2+

## 项目结构

```
prompt_safe/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── core/                   # 核心模块
│   │   ├── security_context.py # 安全上下文定义
│   │   ├── database.py         # 数据库连接
│   │   └── redis_client.py     # Redis连接
│   ├── models/                 # SQLAlchemy模型
│   │   ├── __init__.py
│   │   ├── security_events.py
│   │   ├── prompt_versions.py
│   │   ├── tool_registry.py
│   │   ├── users.py
│   │   └── roles.py
│   ├── schemas/                # Pydantic模型
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── input_guard.py
│   │   ├── output_guard.py
│   │   ├── session.py
│   │   ├── rag.py
│   │   ├── agent.py
│   │   └── mm.py
│   ├── services/               # 业务服务
│   │   ├── __init__.py
│   │   ├── input_guard.py     # L2输入预处理
│   │   ├── prompt_engine.py   # L3系统Prompt引擎
│   │   ├── inference_adapter.py # L4模型推理层
│   │   ├── output_guard.py    # L5输出后校验
│   │   ├── session_manager.py # L6会话管理
│   │   ├── audit_logger.py    # L7监控审计
│   │   ├── rag_guard.py       # RAG安全模块
│   │   ├── agent_wrapper.py   # Agent安全包装器
│   │   └── mm_guard.py        # 多模态安全处理器
│   └── api/                    # API路由
│       ├── __init__.py
│       ├── v1/
│       │   ├── __init__.py
│       │   ├── auth.py
│       │   ├── chat.py
│       │   ├── input_guard.py
│       │   ├── output_guard.py
│       │   ├── session.py
│       │   ├── rag.py
│       │   ├── agent.py
│       │   └── mm.py
│       └── dependencies.py     # 依赖注入
├── tests/                      # 测试用例
│   ├── __init__.py
│   ├── test_input_guard.py
│   ├── test_output_guard.py
│   ├── test_prompt_engine.py
│   ├── test_agent_wrapper.py
│   ├── test_rag_guard.py
│   └── conftest.py
├── docs/                       # 设计文档
├── requirements.txt            # 依赖清单
├── .env                        # 环境变量
├── Dockerfile                  # Docker配置
├── docker-compose.yml          # Docker Compose配置
└── README.md                   # 项目说明
```

## 快速开始

### 环境要求

- Python 3.10+
- Redis 6.0+（可选，用于会话管理）

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制并编辑 `.env` 文件：

```bash
cp .env.example .env
```

主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | sqlite+aiosqlite:///./test.db |
| REDIS_URL | Redis连接URL | redis://localhost:6379/0 |
| JWT_SECRET_KEY | JWT密钥 | 自动生成 |
| MAX_INPUT_CHARS | 最大输入字符数 | 8192 |
| MAX_OUTPUT_CHARS | 最大输出字符数 | 16384 |

### 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：http://localhost:8000/docs 查看API文档

### 运行测试

```bash
pytest tests/ -v
```

## API接口

### 认证接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 用户登录 |
| POST | /api/v1/auth/logout | 用户登出 |
| POST | /api/v1/auth/refresh | 刷新令牌 |
| POST | /api/v1/auth/register | 用户注册 |

### 聊天接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/chat | 安全聊天 |
| GET | /api/v1/chat/{session_id} | 获取会话历史 |

### 安全防护接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/input-guard/process | 输入安全检查 |
| POST | /api/v1/output-guard/check | 输出安全检查 |

### 会话管理接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/sessions | 创建会话 |
| GET | /api/v1/sessions | 获取会话列表 |
| GET | /api/v1/sessions/{session_id} | 获取会话详情 |
| DELETE | /api/v1/sessions/{session_id} | 删除会话 |

### RAG安全接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/rag/ingest | 文档摄入安全检查 |
| POST | /api/v1/rag/filter | 检索结果权限过滤 |

### Agent安全接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/agent/execute | 工具调用安全执行 |
| GET | /api/v1/agent/tools | 获取工具列表 |

### 多模态接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/mm/analyze | 多模态内容安全分析 |

## 安全架构

### L1 Gateway层
- IP白名单/黑名单
- 请求速率限制
- 认证授权
- 流量清洗

### L2 输入预处理层
- 输入格式校验
- 长度限制
- 编码规范检查
- 混淆检测（Base64、Hex、Unicode）
- 关键词匹配
- 模式匹配
- 安全分类
- PII脱敏

### L3 系统Prompt保护
- Prompt版本管理
- Prompt哈希校验
- 防篡改机制
- 动态Prompt组装

### L4 模型推理层
- 推理超时控制
- 模型输出长度限制
- 响应内容过滤
- 异常响应处理

### L5 输出后校验层
- 输出规则匹配
- 内容安全审核
- PII脱敏
- 格式化输出
- 免责声明追加

### L6 上下文/会话管理
- 会话隔离
- 上下文安全过滤
- 会话过期管理
- 状态恢复控制

### L7 监控审计层
- 安全事件日志
- 审计追踪
- 异常告警
- 性能监控

## 安全事件分类

| 分类 | 说明 |
|------|------|
| SECURITY | 安全事件（注入攻击、越狱等） |
| INFERENCE | 推理事件（模型调用、响应时间等） |
| SESSION | 会话事件（创建、销毁、超时等） |
| RAG | RAG事件（文档摄入、检索等） |
| AGENT | Agent事件（工具调用、权限检查等） |
| SYSTEM | 系统事件（启动、配置变更等） |

## 风险等级

| 等级 | 说明 | 处理方式 |
|------|------|----------|
| green | 安全 | 允许通过 |
| yellow | 低风险 | 标记并监控 |
| red | 高风险 | 阻止请求 |
| critical | 严重风险 | 阻止并告警 |

## Docker部署

```bash
docker-compose up -d
```

## 许可证

MIT License