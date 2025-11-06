# sophia

基于LLM的通用Agent助手（后端）

场景：

1. （通用）agent助手
1. （定向）地方高校的Agent助手，帮助解答校园问题

## 规划

**技术栈**：

- sentry
- llama-index
- fastapi
- uvicorn
- sqlmodel
- docker
- ... ...

**功能与模块**：

- 基础功能
  - Agent推理（workflow）
  - 模型记忆管理
  - 工具管理
  - RAG
- 数据库
  - 关系数据库与ORM Model脚手架
  - 向量数据库管理
- 数据治理
  - 高校信息收集与数据编排
  - 向量数据管理
- 日志
  - 性能监控与异常追踪
  - log日志（loguru）
- 鲁棒性
  - pytest代码测试
  - 代码风格检测
  - 代码静态分析
- 部署/发布
  - github ci（semantic release）
  - docker（docker compose）
- ... ...
