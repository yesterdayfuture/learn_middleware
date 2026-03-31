from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class IndexCreate(BaseModel):
    """
    创建索引的请求模型

    Attributes:
        name: 索引名称，必须唯一
        settings: 索引配置（如分片数、副本数等）
        mappings: 索引字段映射定义
    """
    name: str = Field(..., description="Index name")
    settings: Optional[Dict[str, Any]] = Field(None, description="Index settings")
    mappings: Optional[Dict[str, Any]] = Field(None, description="Index mappings")

class IndexResponse(BaseModel):
    """
    索引操作的通用响应模型

    Attributes:
        acknowledged: 操作是否成功确认
        index: 索引名称
        message: 操作结果描述信息
    """
    acknowledged: bool
    index: str
    message: str

class DocumentCreate(BaseModel):
    """
    创建文档的请求模型

    Attributes:
        index: 目标索引名称
        id: 文档ID，可选；若不提供则自动生成UUID
        body: 文档内容，字典类型
    """
    index: str = Field(..., description="Index name")
    id: Optional[str] = Field(None, description="Document ID, auto-generated if not provided")
    body: Dict[str, Any] = Field(..., description="Document body")

class DocumentUpdate(BaseModel):
    """
    更新文档的请求模型

    Attributes:
        index: 目标索引名称
        id: 要更新的文档ID
        body: 要更新的字段，字典类型（partial update）
    """
    index: str = Field(..., description="Index name")
    id: str = Field(..., description="Document ID")
    body: Dict[str, Any] = Field(..., description="Document body to update")

class DocumentResponse(BaseModel):
    """
    文档操作的通用响应模型

    Attributes:
        id: 文档ID
        index: 所属索引名称
        result: 操作结果（created, updated, deleted等）
        message: 操作结果描述信息
    """
    id: str
    index: str
    result: str
    message: str

class SearchQuery(BaseModel):
    """
    复杂搜索查询的请求模型

    支持传入完整的 Elasticsearch Query DSL 进行复杂查询。

    Attributes:
        index: 要搜索的索引名称
        query: Elasticsearch 查询DSL，字典类型
        from_: 分页起始位置（偏移量）
        size: 返回文档数量
    """
    index: str = Field(..., description="Index name")
    query: Dict[str, Any] = Field(..., description="Search query DSL")
    from_: int = Field(0, alias="from", description="Offset for pagination")
    size: int = Field(10, description="Number of results to return")

    class Config:
        populate_by_name = True

class AggregationQuery(BaseModel):
    """
    聚合查询的请求模型

    支持传入 Elasticsearch Aggregation DSL 进行数据聚合分析。

    Attributes:
        index: 要聚合的索引名称
        aggs: Elasticsearch 聚合DSL，字典类型
        size: 同时返回的文档数量（设为0则只返回聚合结果）
    """
    index: str = Field(..., description="Index name")
    aggs: Dict[str, Any] = Field(..., description="Aggregation DSL")
    size: int = Field(0, description="Number of results to return (0 for aggregation only)")

class FuzzyQuery(BaseModel):
    """
    模糊查询的请求模型

    用于对文本字段进行模糊匹配搜索，支持自动调整模糊度。

    Attributes:
        index: 要搜索的索引名称
        field: 要搜索的字段名
        value: 搜索关键词
        fuzziness: 模糊度级别（AUTO, 0, 1, 2）
        from_: 分页起始位置
        size: 返回文档数量
    """
    index: str = Field(..., description="Index name")
    field: str = Field(..., description="Field to search")
    value: str = Field(..., description="Value to search for")
    fuzziness: str = Field("AUTO", description="Fuzziness level")
    from_: int = Field(0, alias="from", description="Offset for pagination")
    size: int = Field(10, description="Number of results to return")

    class Config:
        populate_by_name = True

class HealthResponse(BaseModel):
    """
    集群健康检查的响应模型

    Attributes:
        status: 集群健康状态（green, yellow, red）
        cluster_name: 集群名称
        number_of_nodes: 集群中的节点数量
    """
    status: str
    cluster_name: str
    number_of_nodes: int