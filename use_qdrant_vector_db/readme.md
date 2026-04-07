# Qdrant 向量数据库使用示例

本项目包含多个 Python 示例，演示如何使用 Qdrant 向量数据库进行集合管理、数据操作和高级查询。

## 安装依赖

```bash
pip install 'qdrant-client[fastembed]'
```

## docker启动
```bash
docker run -d \
-p 6333:6333 \
-p 6334:6334 \
-v ~/qdrant_data:/qdrant/storage \
--name qdrant \
qdrant/qdrant


Web UI 地址：http://localhost:6333/dashboard
```


## 文件说明

### 1. collection_crud.py - 集合管理示例
演示集合的增删改查操作：
- 创建集合
- 获取集合信息
- 列出所有集合
- 更新集合配置
- 删除集合
- 检查集合是否存在

```bash
python collection_crud.py
```

### 2. data_crud.py - 数据增删改查示例
演示数据点的基本操作：
- 插入数据点（带向量和载荷）
- 获取单个数据点
- 相似度搜索
- 带过滤条件的搜索
- 更新数据载荷
- 删除载荷字段
- 删除数据点
- 分页获取数据
- 统计数据点数量

```bash
python data_crud.py
```

### 3. multimodal_collection.py - 多模态集合示例
演示多模态数据的存储和检索：
- 创建多模态集合（文本/图像/音频向量）
- 插入单模态数据（纯文本/纯图像/纯音频）
- 插入多模态融合数据
- 按模态类型搜索（文本搜索/图像搜索/音频搜索）
- 按模态类型过滤

```bash
python multimodal_collection.py
```

### 4. advanced_features.py - 高级功能示例
演示高级查询功能：
- 指定字段 Schema（文本/关键字/整数/浮点数）
- 全文模糊搜索（词级别匹配）
- 子串模糊搜索（客户端过滤）
- 精确匹配搜索
- 多值匹配搜索
- 范围查询（价格/评分区间）
- 组合搜索（向量相似度 + 过滤条件）

```bash
python advanced_features.py
```

## 快速开始

1. 启动 Qdrant 服务器（Docker）：
```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. 运行示例：
```bash
# 集合管理
python collection_crud.py

# 数据操作
python data_crud.py

# 多模态集合
python multimodal_collection.py

# 高级功能
python advanced_features.py
```

## 核心概念

### 集合（Collection）
集合是存储向量和相关数据的容器，类似于关系数据库中的表。

### 数据点（Point）
数据点是集合中的基本单元，包含：
- **ID**：唯一标识符（整数或 UUID）
- **Vector**：向量数据
- **Payload**：附加信息（JSON 格式）

### 向量搜索
Qdrant 支持多种距离度量方式：
- **Cosine**：余弦相似度（默认，适合文本）
- **Euclidean**：欧几里得距离
- **Dot**：点积

### 过滤条件
支持多种过滤方式：
- `MatchValue`：精确匹配
- `MatchText`：全文搜索（词级别）
- `MatchAny`：多值匹配
- `Range`：范围查询

## 注意事项

1. **ID 格式**：Qdrant 要求 ID 必须是无符号整数或 UUID，不能使用自定义字符串如 `"text_001"`

2. **全文搜索**：`MatchText` 使用词级别匹配，搜索 "手机" 不会匹配 "智能手机"。如需子串匹配，请使用客户端过滤

3. **API 版本**：本项目使用新版 Qdrant 客户端 API（`query_points` 替代 `search`）

## 参考链接

- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [Qdrant Python 客户端](https://github.com/qdrant/qdrant-client)
