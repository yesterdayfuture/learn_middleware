"""
文档操作路由模块

提供文档的创建、读取、更新、删除等 CRUD 功能。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

from config import get_es_client
from models import DocumentCreate, DocumentUpdate, DocumentResponse

router = APIRouter()

@router.post("", response_model=DocumentResponse)
def create_document(doc: DocumentCreate):
    """
    创建文档

    向指定索引中插入一个文档。如果提供了文档ID，则使用该ID；
    否则 Elasticsearch 会自动生成一个唯一的文档ID。

    Args:
        doc: DocumentCreate 模型，包含索引名、文档ID和文档内容

    Returns:
        DocumentResponse: 包含操作结果的响应模型

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=doc.index):
        raise HTTPException(status_code=404, detail=f"Index '{doc.index}' not found")

    if doc.id:
        result = es.index(index=doc.index, id=doc.id, body=doc.body)
    else:
        result = es.index(index=doc.index, body=doc.body)

    return DocumentResponse(
        id=result["_id"],
        index=result["_index"],
        result=result["result"],
        message="Document created successfully"
    )

@router.get("/{index_name}")
def list_documents(
    index_name: str,
    from_: int = Query(0, alias="from", description="Offset for pagination"),
    size: int = Query(10, description="Number of results to return")
):
    """
    获取索引下的所有文档

    返回指定索引中的所有文档列表，支持分页。

    Args:
        index_name: 索引名称
        from_: 分页起始位置（偏移量）
        size: 返回文档数量

    Returns:
        包含文档总数和文档列表的字典

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    result = es.search(
        index=index_name,
        body={
            "query": {"match_all": {}},
            "from": from_,
            "size": size
        }
    )

    hits = result["hits"]["hits"]
    total = result["hits"]["total"]["value"]

    return {
        "total": total,
        "index": index_name,
        "documents": [
            {
                "id": hit["_id"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in hits
        ]
    }

@router.get("/{index_name}/{doc_id}")
def get_document(index_name: str, doc_id: str):
    """
    获取文档

    根据文档ID从指定索引中检索文档内容。

    Args:
        index_name: 文档所在的索引名称
        doc_id: 文档的唯一标识符

    Returns:
        包含文档ID、索引名和文档内容的字典

    Raises:
        HTTPException: 如果索引或文档不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    try:
        result = es.get(index=index_name, id=doc_id)
        return {
            "id": result["_id"],
            "index": result["_index"],
            "body": result["_source"]
        }
    except Exception:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")

@router.put("", response_model=DocumentResponse)
def update_document(doc: DocumentUpdate):
    """
    更新文档

    对指定索引中的文档进行部分更新，只更新提供的字段。

    Args:
        doc: DocumentUpdate 模型，包含索引名、文档ID和要更新的字段

    Returns:
        DocumentResponse: 包含操作结果的响应模型

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=doc.index):
        raise HTTPException(status_code=404, detail=f"Index '{doc.index}' not found")

    result = es.update(index=doc.index, id=doc.id, body={"doc": doc.body})
    return DocumentResponse(
        id=doc.id,
        index=doc.index,
        result=result["result"],
        message="Document updated successfully"
    )

@router.delete("/{index_name}/{doc_id}", response_model=DocumentResponse)
def delete_document(index_name: str, doc_id: str):
    """
    删除文档

    从指定索引中删除指定的文档。

    Args:
        index_name: 文档所在的索引名称
        doc_id: 文档的唯一标识符

    Returns:
        DocumentResponse: 包含操作结果的响应模型

    Raises:
        HTTPException: 如果索引或文档不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=index_name):
        raise HTTPException(status_code=404, detail=f"Index '{index_name}' not found")

    try:
        result = es.delete(index=index_name, id=doc_id)
        return DocumentResponse(
            id=doc_id,
            index=index_name,
            result=result["result"],
            message="Document deleted successfully"
        )
    except Exception:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found")