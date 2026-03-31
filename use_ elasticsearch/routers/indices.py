"""
索引操作路由模块

提供索引的创建、查询、删除等管理功能。
"""

from fastapi import APIRouter, HTTPException
from typing import List

from config import get_es_client
from models import IndexCreate, IndexResponse

router = APIRouter()

@router.post("", response_model=IndexResponse)
def create_index(index: IndexCreate):
    """
    创建新索引

    在 Elasticsearch 中创建一个新的索引，可以指定索引的设置和字段映射。
    支持指定分词器等高级配置。

    Args:
        index: IndexCreate 模型，包含索引名称、设置和映射

    Returns:
        IndexResponse: 包含操作结果的响应模型

    Raises:
        HTTPException: 如果索引已存在，返回 400 错误
    """
    es = get_es_client()
    if es.indices.exists(index=index.name):
        raise HTTPException(status_code=400, detail=f"Index '{index.name}' already exists")

    body = {}
    if index.settings:
        body["settings"] = index.settings
    if index.mappings:
        body["mappings"] = index.mappings

    result = es.indices.create(index=index.name, body=body if body else None)
    return IndexResponse(
        acknowledged=result["acknowledged"],
        index=result["index"],
        message=f"Index '{index.name}' created successfully"
    )

@router.get("", response_model=List[str])
def list_indices():
    """
    列出所有索引

    返回 Elasticsearch 集群中所有索引的名称列表。

    Returns:
        List[str]: 所有索引名称的列表
    """
    es = get_es_client()
    indices = es.indices.get_alias(index="*")
    return list(indices.keys())

@router.get("/{index_name}")
def get_index(index_name: str):
    """
    获取索引详情

    返回指定索引的完整配置信息，包括设置(settings)和映射(mappings)。

    Args:
        index_name: 要查询的索引名称

    Returns:
        包含索引详细信息的字典

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    result = es.indices.get(index=index_name)
    return result[index_name]

@router.delete("/{index_name}", response_model=IndexResponse)
def delete_index(index_name: str):
    """
    删除索引

    删除指定的索引及其所有关联数据。此操作不可逆！

    Args:
        index_name: 要删除的索引名称

    Returns:
        IndexResponse: 包含操作结果的响应模型

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    result = es.indices.delete(index=index_name)
    return IndexResponse(
        acknowledged=result["acknowledged"],
        index=index_name,
        message=f"Index '{index_name}' deleted successfully"
    )