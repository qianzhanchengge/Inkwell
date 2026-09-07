# 个人工作台（Personal Workbench）

个人知识管理与内容创作平台 —— 高效管理笔记、创作并发布文章，实现个人知识资产的沉淀与分享。

## 核心功能

- 用户系统（注册 / 登录 / 个人信息 / 头像上传）
- 笔记管理（创建 / 编辑 / 分类 / 标签 / 全文搜索 / 置顶）
- 文章发布（Markdown 编辑器 / 草稿箱 / 发布与下架 / 阅读量与点赞）
- 分类与标签管理
- 个人数据看板（笔记数 / 阅读量 / 创作趋势）

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + TypeScript + Pinia + Vue Router + Element Plus + md-editor-v3 + ECharts |
| 后端 | Python + FastAPI + SQLAlchemy 2.0（异步）+ Motor + redis-py + Pydantic v2 + JWT |
| 存储 | MySQL 8.0（元数据）+ MongoDB 7.0（正文）+ Redis 7（缓存 / 会话 / 限流） |
| 部署 | Docker + Docker Compose + Nginx + Gunicorn/Uvicorn |

## 目录结构

```
.
├── backend/            # FastAPI 后端服务
├── frontend/           # Vue 3 前端应用
├── deploy/             # Docker Compose 编排、Nginx、初始化脚本
├── docs/               # 项目文档
├── miaoda-code-个人工作台开发文档.md   # 开发文档
├── docker-compose.yml  # 根目录快捷编排（指向 deploy/）
└── README.md
```

## 快速开始

### 本地开发 —— 后端（使用虚拟环境）

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API 文档：http://localhost:8000/docs
```

### 本地开发 —— 前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### Docker 一键启动

```bash
cd deploy
docker-compose up -d --build
# 前端 http://localhost  |  API 文档 http://localhost/api/v1/docs
```

> 详细设计请阅读《miaoda-code-个人工作台开发文档.md》。
