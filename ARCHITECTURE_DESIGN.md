# 项目架构设计

## 📁 **新的项目目录结构**

基于 Domain-Driven Design (DDD) 原则，我们将项目重构为以下结构：

```
backend/app/
├── __init__.py
├── main.py
├── core/                          # 核心配置和基础设施
│   ├── __init__.py
│   ├── config.py                 # 应用配置
│   ├── db.py                     # PostgreSQL 数据库连接
│   ├── security.py               # 安全相关
│   └── influxdb.py               # InfluxDB 连接配置
├── domains/                       # 业务域划分
│   ├── __init__.py
│   ├── auth/                     # 认证域
│   │   ├── __init__.py
│   │   ├── models.py             # 认证相关模型
│   │   ├── services.py           # 认证业务逻辑
│   │   ├── repositories.py       # 认证数据访问
│   │   └── schemas.py            # 认证相关Schema
│   ├── products/                 # 商品域
│   │   ├── __init__.py
│   │   ├── models.py             # 商品模型
│   │   ├── services.py           # 商品业务逻辑
│   │   ├── repositories.py       # 商品数据访问
│   │   └── schemas.py            # 商品相关Schema
│   ├── analytics/                # 分析域
│   │   ├── __init__.py
│   │   ├── models.py             # 分析数据模型
│   │   ├── services.py           # 分析业务逻辑
│   │   ├── repositories.py       # InfluxDB数据访问
│   │   └── schemas.py            # 分析相关Schema
│   ├── orders/                   # 订单域
│   │   ├── __init__.py
│   │   ├── models.py             # 订单模型
│   │   ├── services.py           # 订单业务逻辑
│   │   ├── repositories.py       # 订单数据访问
│   │   └── schemas.py            # 订单相关Schema
│   └── campaigns/                # 广告活动域
│       ├── __init__.py
│       ├── models.py             # 广告模型
│       ├── services.py           # 广告业务逻辑
│       ├── repositories.py       # 广告数据访问
│       └── schemas.py            # 广告相关Schema
├── integrations/                  # 外部集成
│   ├── __init__.py
│   ├── yandex/                   # Yandex API集成
│   │   ├── __init__.py
│   │   ├── market_api.py         # Market Partner API
│   │   ├── direct_api.py         # Direct API
│   │   ├── metrica_api.py        # Metrica API
│   │   └── base_client.py        # 基础API客户端
│   └── influxdb/                 # InfluxDB集成
│       ├── __init__.py
│       ├── client.py             # InfluxDB客户端
│       ├── models.py             # 时序数据模型
│       └── queries.py            # 查询封装
├── api/                          # API层
│   ├── __init__.py
│   ├── main.py                   # API路由主入口
│   ├── deps.py                   # 依赖注入
│   └── routes/                   # 路由定义
│       ├── __init__.py
│       ├── auth.py               # 认证路由
│       ├── products.py           # 商品路由
│       ├── analytics.py          # 分析路由
│       ├── orders.py             # 订单路由
│       ├── campaigns.py          # 广告路由
│       └── health.py             # 健康检查
├── tasks/                        # 后台任务
│   ├── __init__.py
│   ├── celery_app.py             # Celery配置
│   ├── data_collection.py        # 数据采集任务
│   └── analytics.py              # 分析任务
├── utils/                        # 工具函数
│   ├── __init__.py
│   ├── logging.py                # 日志配置
│   ├── exceptions.py             # 自定义异常
│   └── helpers.py                # 辅助函数
├── alembic/                      # 数据库迁移
│   └── ... (保持现有结构)
└── tests/                        # 测试
    ├── __init__.py
    ├── conftest.py
    ├── unit/                     # 单元测试
    │   ├── __init__.py
    │   ├── test_auth.py
    │   ├── test_products.py
    │   ├── test_analytics.py
    │   └── test_orders.py
    ├── integration/               # 集成测试
    │   ├── __init__.py
    │   ├── test_yandex_api.py
    │   └── test_influxdb.py
    └── e2e/                       # 端到端测试
        ├── __init__.py
        └── test_api.py
```

## 🏗️ **架构层次说明**

### 1. **Core Layer (核心层)**

- 基础设施配置
- 数据库连接
- 安全配置
- 日志配置

### 2. **Domain Layer (业务域层)**

- **Models**: 业务实体和值对象
- **Services**: 业务逻辑和用例
- **Repositories**: 数据访问抽象
- **Schemas**: 数据传输对象

### 3. **Integration Layer (集成层)**

- 外部API集成
- 第三方服务集成
- 数据源适配器

### 4. **API Layer (API层)**

- REST API路由
- 请求/响应处理
- 依赖注入

### 5. **Tasks Layer (任务层)**

- 后台任务
- 定时任务
- 异步处理

## 🔧 **技术栈扩展**

### 新增依赖

```python
# requirements.txt 新增
influxdb-client==1.38.0          # InfluxDB客户端
celery==5.3.4                    # 任务队列
redis==5.0.1                      # Celery broker
pandas==2.1.4                     # 数据分析
numpy==1.24.3                     # 数值计算
matplotlib==3.8.2                 # 图表生成
```

### Docker 服务扩展

```yaml
# docker-compose.yml 新增服务
services:
  influxdb:
    image: influxdb:2.7
    container_name: yandexbot-influxdb
    restart: unless-stopped
    ports:
      - "8086:8086"
    environment:
      - DOCKER_INFLUXDB_INIT_MODE=setup
      - DOCKER_INFLUXDB_INIT_USERNAME=admin
      - DOCKER_INFLUXDB_INIT_PASSWORD=changethis
      - DOCKER_INFLUXDB_INIT_ORG=yandexbot
      - DOCKER_INFLUXDB_INIT_BUCKET=sales_metrics
      - DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=yandexbot-token
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2
    networks:
      - default

  redis:
    image: redis:7-alpine
    container_name: yandexbot-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/var/lib/redis
    networks:
      - default

  celery-worker:
    build:
      context: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    depends_on:
      - db
      - redis
      - influxdb
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    volumes:
      - ./backend:/app
    networks:
      - default

volumes:
  influxdb-data:
  influxdb-config:
  redis-data:
```

## 📋 **实施计划**

### 第一阶段：基础架构搭建

1. 创建新的目录结构
2. 迁移现有代码到新结构
3. 更新Docker配置
4. 配置InfluxDB和Redis

### 第二阶段：核心功能实现

1. 实现InfluxDB集成
2. 创建数据模型
3. 实现Yandex API集成
4. 开发数据采集任务

### 第三阶段：业务逻辑开发

1. 实现各domain的业务逻辑
2. 开发API接口
3. 实现数据分析和可视化

### 第四阶段：测试和优化

1. 编写单元测试
2. 集成测试
3. 性能优化
4. 文档完善

## 🎯 **下一步行动**

1. **立即开始**: 创建新的目录结构
2. **更新Docker**: 添加InfluxDB和Redis服务
3. **配置InfluxDB**: 设置数据库和连接
4. **迁移代码**: 将现有代码重构到新架构

这个架构设计遵循了DDD原则，具有良好的可维护性和扩展性，能够支持我们复杂的电商数据分析需求。
