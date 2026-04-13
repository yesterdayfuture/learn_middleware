# Learn Middleware - 中间件学习项目

本项目是一个中间件技术学习集合，包含多个独立子项目，每个子项目演示一种中间件技术的使用方法和最佳实践。

## 项目列表

| 项目名称 | 技术栈 | 功能描述 |
|---------|-------|---------|
| [use_elasticsearch](./use_%20elasticsearch/) | Python, FastAPI, Elasticsearch | 基于 FastAPI 的 Elasticsearch 操作接口，提供索引管理、文档CRUD、模糊搜索和聚合查询等功能 |
| [use_mqtt](./use_mqtt/) | Python, paho-mqtt | MQTT 消息队列学习项目，包含发布者和订阅者的实现示例 |
| [use_qdrant_vector_db](./use_qdrant_vector_db/) | Python, Qdrant | 向量数据库使用示例，包含集合管理、数据增删改查、多模态集合和高级查询功能 |

## 项目详细说明

### 1. use_elasticsearch

**技术栈：** Python 3.10+, FastAPI, Elasticsearch 8.x

**功能特性：**
- 索引管理：创建、查看、删除索引，支持自定义分词器
- 文档操作：创建、读取、更新、删除文档
- 模糊搜索：支持拼写错误容错搜索
- 聚合查询：支持各种聚合分析操作
- 分词分析：预先查看分词结果
- 批量操作：支持批量索引和删除文档

**快速开始：**
```bash
cd use_ elasticsearch
pip install -r requirements.txt
python main.py
```

**API 文档：** 启动后访问 http://localhost:8000/docs

---

### 2. use_mqtt

**技术栈：** Python 3.10+, paho-mqtt

**功能特性：**
- MQTT 基础发布者实现
- MQTT 基础订阅者实现
- 多线程订阅者示例
- 本地 MQTT 安装与配置文档

**快速开始：**
```bash
cd use_mqtt/code
pip install paho-mqtt

# 运行发布者
python pulisher/01_basic_publisher.py

# 运行订阅者
python subscribe/01_basic_subscribe.py
```

---

### 3. use_qdrant_vector_db

**技术栈：** Python 3.10+, Qdrant

**功能特性：**
- 集合管理：创建、查询、更新、删除集合
- 数据操作：插入、查询、更新、删除数据点
- 向量搜索：相似度搜索、带过滤条件的搜索
- 多模态集合：支持文本、图像、音频多种向量
- 高级查询：全文搜索、范围查询、组合搜索

**快速开始：**
```bash
# 启动 Qdrant（Docker）
docker run -p 6333:6333 qdrant/qdrant

# 运行示例
cd use_qdrant_vector_db
python collection_crud.py
python data_crud.py
python multimodal_collection.py
python advanced_features.py
```

**Web UI：** http://localhost:6333/dashboard

---

## 环境要求

- Python 3.10+
- Docker（用于启动中间件服务）
- 各子项目的具体依赖请参考各自的 requirements.txt 或 readme.md

## 目录结构

```
learn_middleware/
├── README.md                      # 本文件
├── .gitignore                     # Git 忽略配置
├── LICENSE                        # 许可证
├── use_elasticsearch/             # Elasticsearch 学习项目
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   ├── routers/
│   └── README.md
├── use_mqtt/                      # MQTT 学习项目
│   ├── code/
│   │   ├── pulisher/
│   │   ├── subscribe/
│   │   └── readme.md
│   └── 本地安装mqtt文档/
└── use_qdrant_vector_db/          # Qdrant 向量数据库学习项目
    ├── collection_crud.py
    ├── data_crud.py
    ├── multimodal_collection.py
    ├── advanced_features.py
    └── readme.md
```

## 贡献指南

欢迎提交 Issue 和 Pull Request 来完善这些学习示例。

## 许可证

MIT License
