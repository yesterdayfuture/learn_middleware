# Elasticsearch FastAPI CRUD API

基于 FastAPI 的 Elasticsearch 操作接口，提供索引管理、文档CRUD、模糊搜索和聚合查询等功能。

## 功能特性

- 索引管理：创建、查看、删除索引，支持自定义分词器
- 文档操作：创建、读取、更新、删除文档
- 模糊搜索：支持拼写错误容错搜索
- 聚合查询：支持各种聚合分析操作
- 分词分析：预先查看分词结果
- 批量操作：支持批量索引和删除文档

## 项目结构

```
use_ elasticsearch/
├── main.py                 # FastAPI 主应用入口
├── config.py               # Elasticsearch 连接配置
├── models.py               # Pydantic 数据模型
├── requirements.txt        # 项目依赖
├── routers/                # 路由模块
│   ├── __init__.py
│   ├── indices.py          # 索引管理路由
│   ├── documents.py        # 文档操作路由
│   └── search.py           # 搜索查询路由
└── README.md              # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

确保 Elasticsearch 服务运行在 `http://localhost:9200`，然后启动 FastAPI 服务：

```bash
python main.py
```

或使用 uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问 API 文档

服务启动后，可通过以下地址访问交互式 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 文档

### 健康检查

#### GET /health

检查 Elasticsearch 集群健康状态。

```json
{
  "status": "green",
  "cluster_name": "elasticsearch",
  "number_of_nodes": 1
}
```

### 索引管理

#### POST /indices

创建新索引，支持指定分词器。

**请求体：**
```json
{
  "name": "my_index",
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "my_analyzer"
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "timestamp": {"type": "date"}
    }
  }
}
```

**使用 IK 分词器示例：**
```json
{
  "name": "my_index",
  "settings": {
    "analysis": {
      "analyzer": {
        "ik_analyzer": {
          "type": "custom",
          "tokenizer": "ik_max_word"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "ik_analyzer"
      }
    }
  }
}
```
**使用 IK 分词器，且自定义 token filter 示例：**
```json
{
  "name": "my_index3",
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "ik_analyzer": {
          "type": "custom",
          "tokenizer": "ik_max_word"
        "filter": ["ik_length_filter"]           // 3. 应用的token filter
          }
        },
        "filter": {
          "ik_length_filter": {                      // 4. 自定义token filter的名称
            "type": "length",
            "min": 2,                                // 5. 设定最小词长
            "max": 100                               // 6. 设定最大词长（可根据需要调整）
          }
        }
    }
  },
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "ik_analyzer"
      },
      "content": {
        "type": "text",
        "analyzer": "standard"
      },
      "timestamp": {"type": "date"}
    }
  }
}
```

#### GET /indices

列出所有索引。

#### GET /indices/{index_name}

获取指定索引的详细信息。

#### DELETE /indices/{index_name}

删除指定索引。

### 文档操作

#### POST /documents

创建文档。

**请求体：**
```json
{
  "index": "my_index",
  "id": "doc_1",
  "body": {
    "title": "Example Title",
    "content": "This is the content",
    "tags": ["tag1", "tag2"]
  }
}
```

#### GET /documents/{index_name}

获取指定索引下的所有文档（支持分页）。

**查询参数：**
- `from`: 分页起始位置（默认 0）
- `size`: 返回文档数量（默认 10）

**响应示例：**
```json
{
  "total": 100,
  "index": "my_index",
  "documents": [
    {
      "id": "doc_1",
      "score": 1.0,
      "source": {"title": "Example Title", "content": "Content 1"}
    }
  ]
}
```

#### GET /documents/{index_name}/{doc_id}

获取指定文档。

#### PUT /documents

更新文档（部分更新）。

**请求体：**
```json
{
  "index": "my_index",
  "id": "doc_1",
  "body": {
    "title": "Updated Title"
  }
}
```

#### DELETE /documents/{index_name}/{doc_id}

删除指定文档。

### 搜索查询

#### POST /search

复杂搜索查询，支持完整的 Elasticsearch Query DSL。

**请求体：**
```json
{
  "index": "my_index",
  "query": {
    "match": {
      "title": "elasticsearch"
    }
  },
  "from": 0,
  "size": 10
}
```

**响应示例：**
```json
{
  "total": 1,
  "hits": [
    {
      "id": "doc_1",
      "index": "my_index",
      "score": 1.5,
      "source": {
        "title": "Example Title",
        "content": "This is the content"
      }
    }
  ]
}
```

#### POST /search/fuzzy

模糊搜索，适用于拼写错误容错。

**请求体：**
```json
{
  "index": "my_index",
  "field": "title",
  "value": "elasticsearc",
  "fuzziness": "AUTO",
  "from": 0,
  "size": 10
}
```

**fuzziness 可选值：**
- `AUTO`：自动根据词长度选择模糊度
- `0`：精确匹配
- `1`：允许1个字符编辑
- `2`：允许2个字符编辑

#### POST /search/aggregations

聚合查询，支持各种聚合分析。

**请求体：**
```json
{
  "index": "my_index",
  "aggs": {
    "avg_price": {
      "avg": {"field": "price"}
    },
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          {"to": 100},
          {"from": 100, "to": 500},
          {"from": 500}
        ]
      }
    }
  },
  "size": 0
}
```

#### POST /search/bulk

批量执行文档操作。

**请求体：**
```json
[
  {
    "action": "index",
    "index": "my_index",
    "id": "doc_1",
    "body": {"title": "Document 1", "content": "Content 1"}
  },
  {
    "action": "index",
    "index": "my_index",
    "id": "doc_2",
    "body": {"title": "Document 2", "content": "Content 2"}
  },
  {
    "action": "delete",
    "index": "my_index",
    "id": "doc_0"
  }
]
```

#### POST /search/analyze

分词分析，预先查看文本经过分词器处理后的结果。

**使用索引的分词器分析：**
```json
{
  "index": "my_index",
  "text": "中华人民共和国万岁",
  "field": "content"
}
```

**直接指定分词器分析：**
```json
{
  "analyzer": "standard",
  "text": "Hello World Elasticsearch"
}
```

**响应示例：**
```json
{
  "tokens": [
    {"token": "hello", "start_offset": 0, "end_offset": 5, "type": "word", "position": 0},
    {"token": "world", "start_offset": 6, "end_offset": 11, "type": "word", "position": 1},
    {"token": "elasticsearch", "start_offset": 12, "end_offset": 26, "type": "word", "position": 2}
  ]
}
```

## 配置说明

默认配置位于 [config.py](file:///Users/zhangtian/gitProject/learn_middleware/use_%20elasticsearch/config.py)：

- 连接地址：`http://localhost:9200`
- 请求超时：30秒

如需修改配置，可编辑 `config.py` 中的 `Elasticsearch` 初始化参数。

## 依赖说明

- fastapi==0.109.0
- uvicorn==0.27.0
- elasticsearch==8.12.0
- pydantic==2.5.3
- python-multipart==0.0.6