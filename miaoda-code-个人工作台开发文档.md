# 个人工作台（Personal Workbench）开发文档

> 版本：v1.0  
> 最后更新：2026-09-07  
> 文档状态：初稿

---

## 目录

1. [项目概述](#1-项目概述)
2. [技术栈选型](#2-技术栈选型)
3. [系统架构设计](#3-系统架构设计)
4. [数据库设计](#4-数据库设计)
5. [API 接口设计](#5-api-接口设计)
6. [后端模块设计](#6-后端模块设计)
7. [前端模块设计](#7-前端模块设计)
8. [项目目录结构](#8-项目目录结构)
9. [部署方案](#9-部署方案)
10. [开发规范](#10-开发规范)
11. [开发计划与里程碑](#11-开发计划与里程碑)
12. [安全设计](#12-安全设计)
13. [附录](#13-附录)

---

## 1. 项目概述

### 1.1 项目背景

个人工作台是一款面向个人用户的知识管理与内容创作平台，核心目标是帮助用户高效管理笔记、创作并发布文章，实现个人知识资产的沉淀与分享。

### 1.2 核心功能

| 模块 | 功能描述 |
|------|----------|
| **用户系统** | 注册、登录、个人信息管理、头像上传 |
| **笔记管理** | 创建、编辑、删除、分类、标签、搜索笔记 |
| **文章发布** | 文章撰写、Markdown 编辑器、草稿箱、发布/下架、文章列表 |
| **分类标签** | 笔记/文章的分类与标签管理 |
| **搜索功能** | 全文检索笔记与文章内容 |
| **数据统计** | 笔记数量、文章阅读量、创作趋势等个人数据看板 |

### 1.3 非功能性需求

- **性能**：接口平均响应时间 < 200ms，支持 100 并发用户
- **可用性**：系统可用性 ≥ 99.5%
- **安全性**：JWT 认证、密码加密存储、接口权限校验
- **可扩展性**：模块化设计，支持后续功能扩展（如待办、日历等）

---

## 2. 技术栈选型

### 2.1 前端技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Vue 3 | 3.4+ | 前端框架 | Composition API、响应式性能优异、生态成熟 |
| Vite | 5.x | 构建工具 | 极速冷启动、HMR 热更新、原生 ESM 支持 |
| TypeScript | 5.x | 类型系统 | 类型安全、提升可维护性 |
| Pinia | 2.x | 状态管理 | Vue 官方推荐、轻量、TypeScript 友好 |
| Vue Router | 4.x | 路由管理 | 官方路由、支持动态路由与导航守卫 |
| Element Plus | 2.x | UI 组件库 | 组件丰富、文档完善、适配 Vue 3 |
| Axios | 1.x | HTTP 客户端 | 拦截器、请求取消、统一错误处理 |
| md-editor-v3 | 最新 | Markdown 编辑器 | 支持实时预览、工具栏、图片上传 |
| ECharts | 5.x | 数据可视化 | 个人数据看板图表渲染 |

### 2.2 后端技术栈

| 技术 | 版本 | 用途 | 选型理由 |
|------|------|------|----------|
| Python | 3.11+ | 运行环境 | 异步支持完善、生态丰富 |
| FastAPI | 0.110+ | Web 框架 | 高性能异步、自动生成 OpenAPI 文档、Pydantic 校验 |
| Uvicorn | 0.27+ | ASGI 服务器 | 异步高性能、生产可用 |
| SQLAlchemy | 2.0+ | ORM（MySQL） | 异步支持（asyncio）、功能强大 |
| aiomysql | 最新 | MySQL 异步驱动 | 配合 SQLAlchemy 异步使用 |
| Motor | 3.x | MongoDB 异步驱动 | 官方异步驱动、性能优异 |
| redis-py | 5.x | Redis 客户端 | 支持异步（asyncio）、连接池 |
| Pydantic | 2.x | 数据校验 | FastAPI 原生集成、类型安全 |
| python-jose | 最新 | JWT 认证 | JWT 编解码 |
| passlib | 最新 | 密码加密 | bcrypt 哈希算法 |
| python-multipart | 最新 | 文件上传支持 | FastAPI 文件上传依赖 |

### 2.3 数据存储选型

| 数据库 | 用途 | 选型理由 |
|--------|------|----------|
| **MySQL 8.0** | 用户、笔记元数据、文章元数据、分类标签等结构化数据 | 关系型数据、事务支持、查询灵活 |
| **MongoDB 7.0** | 笔记正文、文章正文等大文本/富文本内容 | 文档型存储、适合大文本、Schema 灵活 |
| **Redis 7.x** | 会话缓存、热点数据缓存、限流计数 | 高性能内存数据库、支持多种数据结构 |

> **设计原则**：元数据（标题、时间、分类、作者等）存 MySQL，正文内容存 MongoDB，通过 `content_id` 关联；热点数据与 Token 黑名单存 Redis。

### 2.4 运维与部署

| 技术 | 用途 |
|------|------|
| Docker | 容器化部署 |
| Docker Compose | 多服务编排 |
| Nginx | 反向代理、静态资源服务、HTTPS |
| Gunicorn + Uvicorn Workers | 生产环境 WSGI/ASGI 服务器 |

---

## 3. 系统架构设计

### 3.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   PC 浏览器   │  │  移动端浏览器 │  │   后续扩展    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘      │
└─────────┼─────────────────┼─────────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                          │
│         （静态资源 / HTTPS 终止 / 负载均衡 / Gzip）          │
└───────────────────────────┬─────────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────────────┐   ┌───────────────────────────────┐
│    前端静态资源        │   │       FastAPI 后端服务         │
│  (Vue3 + Vite 构建)   │   │   (Uvicorn / Gunicorn)        │
└───────────────────────┘   └───────────┬───────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
          ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐
          │   MySQL 8.0     │ │   MongoDB 7.0   │ │   Redis 7.x   │
          │  (结构化元数据)  │ │  (正文内容存储)  │ │ (缓存/会话/限流)│
          └─────────────────┘ └─────────────────┘ └───────────────┘
```

### 3.2 架构分层

```
┌──────────────────────────────────────────────┐
│              API 层（Router）                 │
│    接收请求 → 参数校验 → 调用 Service         │
├──────────────────────────────────────────────┤
│            业务逻辑层（Service）              │
│    核心业务处理 → 事务控制 → 数据组装         │
├──────────────────────────────────────────────┤
│            数据访问层（DAO/Repository）       │
│    MySQL CRUD / MongoDB 操作 / Redis 操作     │
├──────────────────────────────────────────────┤
│              模型层（Model/Schema）           │
│    SQLAlchemy Model / Pydantic Schema        │
└──────────────────────────────────────────────┘
```

### 3.3 数据流说明

**笔记创建流程**：
1. 前端提交笔记（标题 + 正文 + 分类 + 标签）
2. 后端先将正文写入 MongoDB，获得 `content_id`
3. 将元数据（标题、content_id、分类、标签、用户ID、时间）写入 MySQL
4. 清除 Redis 中该用户的笔记列表缓存
5. 返回创建结果

**笔记查询流程**：
1. 查询笔记列表 → 先查 Redis 缓存，未命中则查 MySQL，结果回写 Redis
2. 查询笔记详情 → MySQL 取元数据 + MongoDB 取正文，合并返回

---

## 4. 数据库设计

### 4.1 MySQL 数据库设计

#### 4.1.1 用户表（users）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希（bcrypt） |
| nickname | VARCHAR(50) | DEFAULT '' | 昵称 |
| avatar | VARCHAR(255) | DEFAULT '' | 头像URL |
| bio | VARCHAR(500) | DEFAULT '' | 个人简介 |
| status | TINYINT | DEFAULT 1 | 状态：0-禁用，1-正常 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) DEFAULT '',
    avatar VARCHAR(255) DEFAULT '',
    bio VARCHAR(500) DEFAULT '',
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.2 笔记表（notes）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 笔记ID |
| user_id | BIGINT | NOT NULL, INDEX | 所属用户ID |
| title | VARCHAR(200) | NOT NULL | 笔记标题 |
| content_id | VARCHAR(50) | NOT NULL, INDEX | MongoDB正文ID |
| category_id | BIGINT | NULL, INDEX | 分类ID |
| is_pinned | TINYINT | DEFAULT 0 | 是否置顶：0-否，1-是 |
| status | TINYINT | DEFAULT 1 | 状态：0-删除，1-正常 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

```sql
CREATE TABLE notes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_id VARCHAR(50) NOT NULL,
    category_id BIGINT NULL,
    is_pinned TINYINT DEFAULT 0,
    status TINYINT DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.3 文章表（articles）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 文章ID |
| user_id | BIGINT | NOT NULL, INDEX | 作者用户ID |
| title | VARCHAR(200) | NOT NULL | 文章标题 |
| summary | VARCHAR(500) | DEFAULT '' | 文章摘要 |
| content_id | VARCHAR(50) | NOT NULL, INDEX | MongoDB正文ID |
| cover_image | VARCHAR(255) | DEFAULT '' | 封面图URL |
| category_id | BIGINT | NULL, INDEX | 分类ID |
| view_count | INT | DEFAULT 0 | 阅读量 |
| like_count | INT | DEFAULT 0 | 点赞数 |
| status | TINYINT | DEFAULT 0 | 状态：0-草稿，1-已发布，2-已下架 |
| published_at | DATETIME | NULL | 发布时间 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE | 更新时间 |

```sql
CREATE TABLE articles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    summary VARCHAR(500) DEFAULT '',
    content_id VARCHAR(50) NOT NULL,
    cover_image VARCHAR(255) DEFAULT '',
    category_id BIGINT NULL,
    view_count INT DEFAULT 0,
    like_count INT DEFAULT 0,
    status TINYINT DEFAULT 0,
    published_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id),
    INDEX idx_status (status),
    INDEX idx_user_status (user_id, status),
    INDEX idx_published_at (published_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.4 分类表（categories）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 分类ID |
| user_id | BIGINT | NOT NULL, INDEX | 所属用户ID |
| name | VARCHAR(50) | NOT NULL | 分类名称 |
| type | TINYINT | NOT NULL | 类型：1-笔记分类，2-文章分类 |
| sort_order | INT | DEFAULT 0 | 排序权重 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

```sql
CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    type TINYINT NOT NULL,
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_type_name (user_id, type, name),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.5 标签表（tags）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 标签ID |
| user_id | BIGINT | NOT NULL, INDEX | 所属用户ID |
| name | VARCHAR(30) | NOT NULL | 标签名称 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

```sql
CREATE TABLE tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    name VARCHAR(30) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_tag (user_id, name),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.6 笔记-标签关联表（note_tags）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 主键ID |
| note_id | BIGINT | NOT NULL | 笔记ID |
| tag_id | BIGINT | NOT NULL | 标签ID |

```sql
CREATE TABLE note_tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    note_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    UNIQUE KEY uk_note_tag (note_id, tag_id),
    INDEX idx_note_id (note_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

#### 4.1.7 文章-标签关联表（article_tags）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 主键ID |
| article_id | BIGINT | NOT NULL | 文章ID |
| tag_id | BIGINT | NOT NULL | 标签ID |

```sql
CREATE TABLE article_tags (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    article_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    UNIQUE KEY uk_article_tag (article_id, tag_id),
    INDEX idx_article_id (article_id),
    INDEX idx_tag_id (tag_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

### 4.2 MongoDB 数据库设计

#### 4.2.1 笔记内容集合（note_contents）

```json
{
  "_id": "ObjectId('650...')",
  "note_id": 1001,
  "user_id": 1,
  "content": "# 笔记标题\n\n这是笔记的 Markdown 正文内容...",
  "content_html": "<h1>笔记标题</h1><p>这是笔记的正文内容...</p>",
  "word_count": 520,
  "version": 1,
  "created_at": "2026-09-07T10:00:00Z",
  "updated_at": "2026-09-07T10:30:00Z"
}
```

**索引设计**：
- `{ note_id: 1 }` — 单字段索引，按笔记ID查询
- `{ user_id: 1 }` — 单字段索引，按用户查询
- `{ content: "text" }` — 全文索引，支持内容搜索

#### 4.2.2 文章内容集合（article_contents）

```json
{
  "_id": "ObjectId('651...')",
  "article_id": 2001,
  "user_id": 1,
  "content": "# 文章标题\n\n这是文章的 Markdown 正文内容...",
  "content_html": "<h1>文章标题</h1><p>这是文章的正文内容...</p>",
  "word_count": 1200,
  "reading_time": 5,
  "version": 1,
  "created_at": "2026-09-07T10:00:00Z",
  "updated_at": "2026-09-07T10:30:00Z"
}
```

**索引设计**：
- `{ article_id: 1 }` — 单字段索引
- `{ user_id: 1 }` — 单字段索引
- `{ content: "text" }` — 全文索引

### 4.3 Redis 数据设计

| Key 模式 | 数据类型 | TTL | 用途 |
|----------|----------|-----|------|
| `user:token:{user_id}` | String | 7天 | 存储当前有效JWT（支持单设备登录/踢人） |
| `token:blacklist:{jti}` | String | 与Token过期时间一致 | Token黑名单（登出/修改密码时使用） |
| `cache:notes:list:{user_id}:{page}:{size}` | String(JSON) | 5分钟 | 笔记列表缓存 |
| `cache:articles:list:{user_id}:{page}:{size}` | String(JSON) | 5分钟 | 文章列表缓存 |
| `cache:article:detail:{article_id}` | String(JSON) | 10分钟 | 文章详情缓存 |
| `cache:user:profile:{user_id}` | String(JSON) | 30分钟 | 用户信息缓存 |
| `rate:limit:{ip}:{api_path}` | String(计数器) | 1分钟 | 接口限流计数 |
| `stat:article:view:{article_id}` | Hash | 永久 | 文章阅读量实时计数（定时回写MySQL） |

---

## 5. API 接口设计

### 5.1 接口规范

- **基础路径**：`/api/v1`
- **认证方式**：Bearer Token（JWT），Header 中 `Authorization: Bearer <token>`
- **响应格式**：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

- **分页参数**：`page`（默认1）、`page_size`（默认10，最大100）
- **分页响应**：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 10,
    "total_pages": 10
  }
}
```

### 5.2 认证接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 用户注册 | 否 |
| POST | `/api/v1/auth/login` | 用户登录 | 否 |
| POST | `/api/v1/auth/logout` | 用户登出 | 是 |
| POST | `/api/v1/auth/refresh` | 刷新Token | 是 |
| GET | `/api/v1/auth/me` | 获取当前用户信息 | 是 |

#### 注册请求体

```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "Abc123456",
  "nickname": "张三"
}
```

#### 登录响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

### 5.3 用户接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| PUT | `/api/v1/users/profile` | 更新个人信息 | 是 |
| PUT | `/api/v1/users/password` | 修改密码 | 是 |
| POST | `/api/v1/users/avatar` | 上传头像 | 是 |

### 5.4 笔记接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/notes` | 获取笔记列表（支持分类、标签、关键词筛选） | 是 |
| GET | `/api/v1/notes/{note_id}` | 获取笔记详情 | 是 |
| POST | `/api/v1/notes` | 创建笔记 | 是 |
| PUT | `/api/v1/notes/{note_id}` | 更新笔记 | 是 |
| DELETE | `/api/v1/notes/{note_id}` | 删除笔记（软删除） | 是 |
| PATCH | `/api/v1/notes/{note_id}/pin` | 置顶/取消置顶 | 是 |
| GET | `/api/v1/notes/search` | 全文搜索笔记 | 是 |

#### 创建笔记请求体

```json
{
  "title": "学习笔记 - FastAPI入门",
  "content": "# FastAPI 入门\n\nFastAPI 是一个现代、高性能的 Web 框架...",
  "category_id": 1,
  "tags": ["Python", "FastAPI", "后端"],
  "is_pinned": false
}
```

#### 笔记详情响应

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1001,
    "title": "学习笔记 - FastAPI入门",
    "content": "# FastAPI 入门\n\nFastAPI 是一个现代、高性能的 Web 框架...",
    "content_html": "<h1>FastAPI 入门</h1><p>FastAPI 是一个现代、高性能的 Web 框架...</p>",
    "category": {
      "id": 1,
      "name": "技术学习"
    },
    "tags": [
      {"id": 1, "name": "Python"},
      {"id": 2, "name": "FastAPI"}
    ],
    "is_pinned": false,
    "word_count": 350,
    "created_at": "2026-09-07T10:00:00",
    "updated_at": "2026-09-07T10:30:00"
  }
}
```

### 5.5 文章接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/articles` | 获取文章列表（公开，仅已发布） | 否 |
| GET | `/api/v1/articles/mine` | 获取我的文章列表（含草稿） | 是 |
| GET | `/api/v1/articles/{article_id}` | 获取文章详情 | 否（公开文章） |
| POST | `/api/v1/articles` | 创建文章（草稿） | 是 |
| PUT | `/api/v1/articles/{article_id}` | 更新文章 | 是 |
| DELETE | `/api/v1/articles/{article_id}` | 删除文章 | 是 |
| POST | `/api/v1/articles/{article_id}/publish` | 发布文章 | 是 |
| POST | `/api/v1/articles/{article_id}/unpublish` | 下架文章 | 是 |
| POST | `/api/v1/articles/{article_id}/like` | 点赞/取消点赞 | 是 |
| GET | `/api/v1/articles/search` | 全文搜索文章 | 否 |

#### 创建文章请求体

```json
{
  "title": "深入理解 Python 异步编程",
  "summary": "本文详细介绍了 Python 异步编程的原理与实践...",
  "content": "# 深入理解 Python 异步编程\n\n## 什么是异步编程...",
  "cover_image": "https://example.com/cover.jpg",
  "category_id": 2,
  "tags": ["Python", "异步", "编程"]
}
```

### 5.6 分类接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/categories?type=1` | 获取分类列表（type:1笔记,2文章） | 是 |
| POST | `/api/v1/categories` | 创建分类 | 是 |
| PUT | `/api/v1/categories/{id}` | 更新分类 | 是 |
| DELETE | `/api/v1/categories/{id}` | 删除分类 | 是 |

### 5.7 标签接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/tags` | 获取我的标签列表 | 是 |
| POST | `/api/v1/tags` | 创建标签 | 是 |
| DELETE | `/api/v1/tags/{id}` | 删除标签 | 是 |

### 5.8 统计接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/v1/stats/overview` | 获取概览统计（笔记数、文章数、总字数等） | 是 |
| GET | `/api/v1/stats/trend?days=30` | 获取创作趋势（近N天每日创建数） | 是 |

### 5.9 文件上传接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/v1/upload/image` | 上传图片（笔记/文章插图） | 是 |

---

## 6. 后端模块设计

### 6.1 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   ├── config.py                # 配置管理（环境变量）
│   ├── database/
│   │   ├── __init__.py
│   │   ├── mysql.py             # MySQL 异步连接
│   │   ├── mongodb.py           # MongoDB 异步连接
│   │   └── redis.py             # Redis 异步连接
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # 用户模型
│   │   ├── note.py              # 笔记模型
│   │   ├── article.py           # 文章模型
│   │   ├── category.py          # 分类模型
│   │   └── tag.py               # 标签模型
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py              # 用户 Pydantic 模型
│   │   ├── note.py              # 笔记 Pydantic 模型
│   │   ├── article.py           # 文章 Pydantic 模型
│   │   ├── category.py          # 分类 Pydantic 模型
│   │   ├── tag.py               # 标签 Pydantic 模型
│   │   └── common.py            # 通用响应模型
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # 依赖注入（认证、分页等）
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py          # 认证路由
│   │       ├── users.py         # 用户路由
│   │       ├── notes.py         # 笔记路由
│   │       ├── articles.py      # 文章路由
│   │       ├── categories.py    # 分类路由
│   │       ├── tags.py          # 标签路由
│   │       ├── stats.py         # 统计路由
│   │       └── upload.py        # 文件上传路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # 认证业务逻辑
│   │   ├── user_service.py      # 用户业务逻辑
│   │   ├── note_service.py      # 笔记业务逻辑
│   │   ├── article_service.py   # 文章业务逻辑
│   │   ├── category_service.py  # 分类业务逻辑
│   │   ├── tag_service.py       # 标签业务逻辑
│   │   └── stats_service.py     # 统计业务逻辑
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py          # JWT、密码加密
│   │   ├── cache.py             # Redis 缓存装饰器
│   │   ├── exceptions.py        # 自定义异常
│   │   ├── middleware.py        # 中间件（CORS、日志、限流）
│   │   └── response.py          # 统一响应封装
│   └── utils/
│       ├── __init__.py
│       ├── markdown.py          # Markdown 转 HTML
│       ├── file_handler.py      # 文件上传处理
│       └── logger.py            # 日志配置
├── alembic/                     # 数据库迁移
│   ├── versions/
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_notes.py
│   └── test_articles.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── alembic.ini
```

### 6.2 核心模块说明

#### 6.2.1 配置管理（config.py）

使用 `pydantic-settings` 从环境变量读取配置：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 应用
    APP_NAME: str = "Personal Workbench"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "workbench"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "workbench"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1天
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    class Config:
        env_file = ".env"
```

#### 6.2.2 认证与安全（core/security.py）

- 密码使用 `passlib` + `bcrypt` 哈希
- JWT 使用 `python-jose` 编解码
- Token 包含 `user_id`、`username`、`jti`（唯一标识，用于黑名单）
- 登录时将 Token 存入 Redis，支持单设备登录控制

#### 6.2.3 缓存机制（core/cache.py）

实现缓存装饰器，支持：
- 自动缓存函数返回值到 Redis
- 支持自定义 Key 模板和 TTL
- 数据变更时主动清除相关缓存

#### 6.2.4 统一异常处理（core/exceptions.py）

```python
class APIException(Exception):
    def __init__(self, code: int, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code

# 常用异常
class NotFoundException(APIException):
    def __init__(self, message="资源不存在"):
        super().__init__(404, message, 404)

class UnauthorizedException(APIException):
    def __init__(self, message="未授权"):
        super().__init__(401, message, 401)

class ForbiddenException(APIException):
    def __init__(self, message="无权限"):
        super().__init__(403, message, 403)
```

### 6.3 关键业务流程

#### 6.3.1 笔记创建流程（Service 层伪代码）

```python
async def create_note(user_id: int, data: NoteCreate) -> NoteDetail:
    # 1. Markdown 转 HTML
    content_html = markdown_to_html(data.content)
    word_count = count_words(data.content)

    # 2. 写入 MongoDB
    content_doc = await mongo_db.note_contents.insert_one({
        "user_id": user_id,
        "content": data.content,
        "content_html": content_html,
        "word_count": word_count,
        "version": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    content_id = str(content_doc.inserted_id)

    # 3. 写入 MySQL（事务）
    async with mysql_session() as session:
        async with session.begin():
            note = Note(
                user_id=user_id,
                title=data.title,
                content_id=content_id,
                category_id=data.category_id,
                is_pinned=data.is_pinned
            )
            session.add(note)
            await session.flush()

            # 4. 处理标签（查找或创建）
            if data.tags:
                tag_ids = await tag_service.get_or_create_tags(session, user_id, data.tags)
                for tag_id in tag_ids:
                    session.add(NoteTag(note_id=note.id, tag_id=tag_id))

    # 5. 清除缓存
    await cache.invalidate_pattern(f"cache:notes:list:{user_id}:*")

    # 6. 返回详情
    return await get_note_detail(note.id, user_id)
```

#### 6.3.2 文章发布流程

```python
async def publish_article(article_id: int, user_id: int) -> ArticleDetail:
    # 1. 校验文章归属与状态
    article = await get_article_by_id(article_id)
    if article.user_id != user_id:
        raise ForbiddenException("无权操作此文章")
    if article.status != 0:  # 非草稿
        raise APIException(400, "仅草稿状态可发布")

    # 2. 更新状态
    article.status = 1
    article.published_at = datetime.utcnow()
    await mysql_session.commit()

    # 3. 清除缓存
    await cache.invalidate_pattern(f"cache:articles:*")

    return await get_article_detail(article_id)
```

---

## 7. 前端模块设计

### 7.1 项目结构

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── main.ts                  # 应用入口
│   ├── App.vue                  # 根组件
│   ├── router/
│   │   └── index.ts             # 路由配置
│   ├── stores/
│   │   ├── index.ts             # Pinia 入口
│   │   ├── user.ts              # 用户状态
│   │   └── app.ts               # 应用全局状态
│   ├── api/
│   │   ├── request.ts           # Axios 封装（拦截器）
│   │   ├── auth.ts              # 认证接口
│   │   ├── note.ts              # 笔记接口
│   │   ├── article.ts           # 文章接口
│   │   ├── category.ts          # 分类接口
│   │   ├── tag.ts               # 标签接口
│   │   └── stats.ts             # 统计接口
│   ├── views/
│   │   ├── login/
│   │   │   └── Login.vue        # 登录页
│   │   ├── register/
│   │   │   └── Register.vue     # 注册页
│   │   ├── layout/
│   │   │   └── Layout.vue       # 主布局（侧边栏+顶栏）
│   │   ├── dashboard/
│   │   │   └── Dashboard.vue    # 工作台首页/数据看板
│   │   ├── notes/
│   │   │   ├── NoteList.vue     # 笔记列表
│   │   │   ├── NoteDetail.vue   # 笔记详情
│   │   │   └── NoteEditor.vue   # 笔记编辑器
│   │   ├── articles/
│   │   │   ├── ArticleList.vue  # 文章列表（我的）
│   │   │   ├── ArticleDetail.vue# 文章详情
│   │   │   ├── ArticleEditor.vue# 文章编辑器
│   │   │   └── ArticlePublic.vue# 公开文章浏览
│   │   ├── categories/
│   │   │   └── CategoryManage.vue # 分类管理
│   │   ├── tags/
│   │   │   └── TagManage.vue    # 标签管理
│   │   └── profile/
│   │       └── Profile.vue      # 个人设置
│   ├── components/
│   │   ├── MarkdownEditor.vue   # Markdown 编辑器封装
│   │   ├── MarkdownPreview.vue  # Markdown 预览
│   │   ├── PageHeader.vue       # 页面头部
│   │   ├── Pagination.vue       # 分页组件
│   │   ├── TagSelector.vue      # 标签选择器
│   │   └── EmptyState.vue       # 空状态组件
│   ├── composables/
│   │   ├── useAuth.ts           # 认证逻辑
│   │   ├── usePagination.ts     # 分页逻辑
│   │   └── useDebounce.ts       # 防抖
│   ├── utils/
│   │   ├── auth.ts              # Token 存储
│   │   ├── format.ts            # 格式化工具
│   │   └── constants.ts         # 常量定义
│   ├── types/
│   │   ├── api.ts               # API 类型定义
│   │   ├── note.ts              # 笔记类型
│   │   ├── article.ts           # 文章类型
│   │   └── user.ts              # 用户类型
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── index.scss       # 全局样式
│   │   │   └── variables.scss   # SCSS 变量
│   │   └── images/
│   └── env.d.ts
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
└── .env.example
```

### 7.2 路由设计

```typescript
const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: Dashboard, meta: { title: '工作台' } },
      { path: 'notes', component: NoteList, meta: { title: '笔记管理' } },
      { path: 'notes/new', component: NoteEditor, meta: { title: '新建笔记' } },
      { path: 'notes/:id', component: NoteDetail, meta: { title: '笔记详情' } },
      { path: 'notes/:id/edit', component: NoteEditor, meta: { title: '编辑笔记' } },
      { path: 'articles', component: ArticleList, meta: { title: '文章管理' } },
      { path: 'articles/new', component: ArticleEditor, meta: { title: '新建文章' } },
      { path: 'articles/:id/edit', component: ArticleEditor, meta: { title: '编辑文章' } },
      { path: 'categories', component: CategoryManage, meta: { title: '分类管理' } },
      { path: 'tags', component: TagManage, meta: { title: '标签管理' } },
      { path: 'profile', component: Profile, meta: { title: '个人设置' } },
    ]
  },
  // 公开文章浏览
  { path: '/p/articles', component: ArticlePublic, meta: { public: true } },
  { path: '/p/articles/:id', component: ArticleDetail, meta: { public: true } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
]
```

### 7.3 页面功能说明

| 页面 | 功能描述 |
|------|----------|
| **登录/注册** | 表单校验、密码强度提示、登录状态保持 |
| **工作台首页** | 数据概览卡片（笔记数、文章数、总字数）、近期创作列表、创作趋势图（ECharts）、快捷入口 |
| **笔记列表** | 分类筛选、标签筛选、关键词搜索、置顶标记、分页、新建/编辑/删除操作 |
| **笔记编辑器** | Markdown 实时预览、自动保存草稿、标签选择、分类选择、图片上传 |
| **笔记详情** | 正文渲染、元信息展示、编辑/删除/置顶操作 |
| **文章列表** | 状态筛选（草稿/已发布/已下架）、阅读量/点赞数展示、发布/下架操作 |
| **文章编辑器** | Markdown 编辑、摘要编辑、封面上传、预览、保存草稿/发布 |
| **文章详情（公开）** | 正文渲染、阅读量统计、点赞、作者信息 |
| **分类管理** | 笔记分类/文章分类切换、增删改、排序 |
| **标签管理** | 标签列表、使用次数、删除 |
| **个人设置** | 基本信息编辑、头像上传、密码修改 |

### 7.4 Axios 封装要点

```typescript
// request.ts
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15000
})

// 请求拦截器：自动添加 Token
request.interceptors.request.use(config => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误处理
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      if (res.code === 401) {
        // Token 过期，跳转登录
        router.push('/login')
      }
      return Promise.reject(new Error(res.message))
    }
    return res.data
  },
  error => {
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)
```

---

## 8. 项目目录结构

### 8.1 完整项目根目录

```
personal-workbench/
├── backend/                    # 后端服务（FastAPI）
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # 前端应用（Vue 3）
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
├── deploy/                     # 部署相关
│   ├── docker-compose.yml      # 完整编排（MySQL+MongoDB+Redis+后端+前端+Nginx）
│   ├── nginx/
│   │   └── default.conf        # Nginx 配置
│   └── init/
│       ├── init.sql            # MySQL 初始化脚本
│       └── init-mongo.js       # MongoDB 初始化脚本
├── docs/                       # 项目文档
│   ├── api.md                  # API 详细文档（由 FastAPI 自动生成亦可）
│   ├── deployment.md           # 部署手册
│   └── changelog.md            # 变更日志
├── .gitignore
├── README.md
└── docker-compose.yml          # 根目录快捷编排（指向 deploy/）
```

---

## 9. 部署方案

### 9.1 Docker Compose 编排

```yaml
# deploy/docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: workbench-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: workbench
      MYSQL_USER: workbench
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  mongodb:
    image: mongo:7.0
    container_name: workbench-mongo
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  redis:
    image: redis:7-alpine
    container_name: workbench-redis
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD} --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  backend:
    build: ../backend
    container_name: workbench-backend
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
      mongodb:
        condition: service_started
      redis:
        condition: service_started
    environment:
      MYSQL_HOST: mysql
      MONGODB_URL: mongodb://admin:${MONGO_PASSWORD}@mongodb:27017/workbench?authSource=admin
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    volumes:
      - upload_data:/app/uploads

  frontend:
    build: ../frontend
    container_name: workbench-frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf

volumes:
  mysql_data:
  mongo_data:
  redis_data:
  upload_data:
```

### 9.2 Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;

    # 前端静态资源
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
        client_max_body_size 20m;
    }

    # 上传文件静态访问
    location /uploads/ {
        proxy_pass http://backend:8000/uploads/;
    }

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1024;
}
```

### 9.3 后端 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

RUN mkdir -p uploads

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
```

### 9.4 前端 Dockerfile

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 9.5 部署步骤

1. **环境准备**：安装 Docker 和 Docker Compose
2. **配置环境变量**：复制 `.env.example` 为 `.env`，修改密码等敏感配置
3. **启动服务**：`docker-compose up -d --build`
4. **初始化数据库**：首次启动自动执行 `init.sql` 创建表结构
5. **验证部署**：访问 `http://localhost`，API 文档访问 `http://localhost/api/v1/docs`
6. **HTTPS 配置（可选）**：使用 Certbot 申请证书，修改 Nginx 配置

---

## 10. 开发规范

### 10.1 后端开发规范

#### 10.1.1 代码风格

- 遵循 **PEP 8** 规范
- 使用 **Black** 格式化代码（line-length=100）
- 使用 **isort** 排序导入
- 使用 **flake8** 进行代码检查
- 类型注解全覆盖（函数参数和返回值）

#### 10.1.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/文件 | 小写+下划线 | `note_service.py` |
| 类 | 大驼峰 | `NoteService` |
| 函数/方法 | 小写+下划线 | `create_note()` |
| 变量 | 小写+下划线 | `note_id` |
| 常量 | 全大写+下划线 | `MAX_RETRY_COUNT` |
| 数据库表 | 小写+下划线（复数） | `note_tags` |
| 数据库字段 | 小写+下划线 | `created_at` |

#### 10.1.3 Git 提交规范

```
<type>(<scope>): <subject>

type:
  feat:     新功能
  fix:      修复bug
  docs:     文档变更
  style:    代码格式（不影响功能）
  refactor: 重构
  perf:     性能优化
  test:     测试相关
  chore:    构建/工具/依赖变更

示例：
  feat(notes): 新增笔记置顶功能
  fix(auth): 修复Token刷新失败问题
```

### 10.2 前端开发规范

#### 10.2.1 代码风格

- 使用 **ESLint + Prettier** 统一代码风格
- Vue 组件使用 `<script setup lang="ts">` 语法
- 组件名使用大驼峰（`NoteEditor.vue`）
- Props 必须定义类型和默认值
- 优先使用 Composition API

#### 10.2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 组件文件 | 大驼峰 | `NoteEditor.vue` |
| 普通文件 | 小写+短横线 | `request.ts` |
| 组件名 | 大驼峰 | `NoteEditor` |
| 函数 | 小驼峰 | `fetchNoteList()` |
| 变量/常量 | 小驼峰 / 全大写 | `noteList`, `MAX_SIZE` |
| CSS 类名 | BEM 或短横线 | `.note-list`, `.note-list__item` |

#### 10.2.3 组件设计原则

- 单一职责：一个组件只做一件事
- Props 向下传递，Events 向上传递
- 通用组件放入 `components/`，页面组件放入 `views/`
- 复杂逻辑抽离到 `composables/`

### 10.3 API 设计规范

- RESTful 风格，资源用名词复数
- 使用标准 HTTP 方法：GET（查询）、POST（创建）、PUT（全量更新）、PATCH（部分更新）、DELETE（删除）
- 版本化：`/api/v1/`
- 统一响应格式：`{ code, message, data }`
- 错误码规范：
  - 200：成功
  - 400：请求参数错误
  - 401：未认证
  - 403：无权限
  - 404：资源不存在
  - 409：资源冲突
  - 500：服务器内部错误

---

## 11. 开发计划与里程碑

### 11.1 阶段划分

| 阶段 | 周期 | 目标 | 交付物 |
|------|------|------|--------|
| **Phase 1：基础搭建** | 第1周 | 项目初始化、基础设施搭建 | 前后端项目骨架、数据库初始化、Docker环境、CI/CD基础 |
| **Phase 2：用户系统** | 第2周 | 认证与用户管理 | 注册/登录/登出、JWT认证、个人信息管理、头像上传 |
| **Phase 3：笔记模块** | 第3-4周 | 笔记核心功能 | 笔记CRUD、分类标签、Markdown编辑器、搜索、置顶 |
| **Phase 4：文章模块** | 第5-6周 | 文章发布功能 | 文章CRUD、草稿箱、发布/下架、阅读量、点赞、公开浏览 |
| **Phase 5：数据看板** | 第7周 | 统计与可视化 | 概览统计、创作趋势图、ECharts集成 |
| **Phase 6：优化上线** | 第8周 | 性能优化与部署 | 缓存优化、安全加固、Docker部署、文档完善 |

### 11.2 Phase 1 详细任务

- [ ] 后端：FastAPI 项目初始化、配置管理、数据库连接
- [ ] 后端：MySQL 表结构设计与 Alembic 迁移
- [ ] 后端：MongoDB 集合与索引初始化
- [ ] 后端：Redis 连接与缓存工具类
- [ ] 后端：统一响应格式、异常处理、中间件
- [ ] 前端：Vue 3 + Vite + TypeScript 项目初始化
- [ ] 前端：路由、Pinia、Axios 封装
- [ ] 前端：Element Plus 集成、全局样式
- [ ] 前端：主布局（侧边栏+顶栏）
- [ ] 部署：Docker Compose 编排、Nginx 配置

### 11.3 验收标准

- 所有接口通过 FastAPI 自动文档可测试
- 前端页面在 Chrome / Edge / Firefox 最新版正常显示
- 接口响应时间 P95 < 500ms
- 核心功能单元测试覆盖率 ≥ 70%
- Docker Compose 一键启动成功

---

## 12. 安全设计

### 12.1 认证与授权

- **JWT 认证**：Access Token（1天）+ Refresh Token（7天）双 Token 机制
- **密码安全**：bcrypt 哈希（cost factor = 12），禁止明文存储
- **Token 黑名单**：登出/修改密码时将 jti 加入 Redis 黑名单
- **接口权限**：所有写操作校验资源归属，防止越权访问

### 12.2 输入校验

- 所有接口参数通过 Pydantic 模型校验
- SQL 注入防护：使用 SQLAlchemy ORM 参数化查询
- XSS 防护：Markdown 渲染时过滤危险 HTML 标签（使用 `bleach` 库）
- 文件上传：校验文件类型（白名单）、大小限制、重命名存储

### 12.3 接口安全

- **限流**：基于 IP + 接口路径的 Redis 计数器限流（登录接口 5次/分钟）
- **CORS**：配置允许的域名白名单
- **敏感信息脱敏**：响应中不返回 password_hash 等字段
- **HTTPS**：生产环境强制 HTTPS

### 12.4 数据安全

- 数据库定期备份（MySQL mysqldump + MongoDB mongodump）
- 上传文件存储路径不可直接执行
- 日志中不记录敏感信息（密码、Token）

---

## 13. 附录

### 13.1 环境变量配置模板（.env.example）

```bash
# 应用
DEBUG=true
SECRET_KEY=change-this-to-a-random-secret-key-in-production

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=workbench

# MongoDB
MONGODB_URL=mongodb://localhost:27017/workbench

# Redis
REDIS_URL=redis://localhost:6379/0

# 文件上传
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760
```

### 13.2 前端环境变量（.env.example）

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=个人工作台
```

### 13.3 后端依赖清单（requirements.txt）

```
fastapi==0.110.0
uvicorn[standard]==0.27.1
gunicorn==21.2.0
sqlalchemy[asyncio]==2.0.27
aiomysql==0.2.0
motor==3.3.2
redis==5.0.1
pydantic==2.6.1
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
alembic==1.13.1
markdown==3.5.2
bleach==6.1.0
pytest==8.0.0
pytest-asyncio==0.23.4
httpx==0.26.0
```

### 13.4 前端依赖清单（package.json 核心依赖）

```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "element-plus": "^2.5.0",
    "axios": "^1.6.0",
    "md-editor-v3": "^4.0.0",
    "echarts": "^5.5.0",
    "dayjs": "^1.11.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "sass": "^1.70.0",
    "eslint": "^8.56.0",
    "prettier": "^3.2.0"
  }
}
```

### 13.5 快速启动命令

```bash
# 1. 克隆项目
git clone <repo-url>
cd personal-workbench

# 2. 配置环境变量
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# 编辑 .env 文件，填入实际配置

# 3. Docker 一键启动
cd deploy
docker-compose up -d --build

# 4. 访问
# 前端: http://localhost
# API文档: http://localhost/api/v1/docs
```

### 13.6 本地开发启动

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端（新开终端）
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

---

> **文档结束**  
> 如有疑问或需要调整，请及时更新本文档并记录变更日志。
