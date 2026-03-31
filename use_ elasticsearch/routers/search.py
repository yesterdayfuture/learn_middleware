"""
搜索查询路由模块

提供复杂搜索、模糊搜索、聚合查询和分词分析等功能。
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List

from config import get_es_client
from models import SearchQuery, AggregationQuery, FuzzyQuery

router = APIRouter()

@router.post("")
def search(search_query: SearchQuery):
    """
    复杂搜索查询

    支持传入完整的 Elasticsearch Query DSL 进行复杂的搜索操作，
    如多条件组合、过滤器、排序等。

    Args:
        search_query: SearchQuery 模型，包含索引名、查询DSL和分页参数

    Returns:
        包含搜索结果总数和匹配的文档列表的字典

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=search_query.index):
        raise HTTPException(status_code=404, detail=f"Index '{search_query.index}' not found")

    query_body = {
        "query": search_query.query,
        "from": search_query.from_,
        "size": search_query.size
    }

    result = es.search(
        index=search_query.index,
        body=query_body
    )

    hits = result["hits"]["hits"]
    total = result["hits"]["total"]["value"]

    return {
        "total": total,
        "hits": [
            {
                "id": hit["_id"],
                "index": hit["_index"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in hits
        ]
    }

@router.post("/fuzzy")
def fuzzy_search(fuzzy_query: FuzzyQuery):
    """
    模糊搜索

    对文本字段进行模糊匹配搜索，适用于拼写错误容错场景。
    模糊度可设为 AUTO（自动）、0、1、2，数字越大匹配越宽松。

    Args:
        fuzzy_query: FuzzyQuery 模型，包含索引名、字段名、搜索值和模糊度

    Returns:
        包含搜索结果总数和匹配的文档列表的字典

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=fuzzy_query.index):
        raise HTTPException(status_code=404, detail=f"Index '{fuzzy_query.index}' not found")

    query = {
        "query": {
            "fuzzy": {
                fuzzy_query.field: {
                    "value": fuzzy_query.value,
                    "fuzziness": fuzzy_query.fuzziness
                }
            }
        },
        "from": fuzzy_query.from_,
        "size": fuzzy_query.size
    }

    result = es.search(
        index=fuzzy_query.index,
        body=query
    )

    hits = result["hits"]["hits"]
    total = result["hits"]["total"]["value"]

    return {
        "total": total,
        "hits": [
            {
                "id": hit["_id"],
                "index": hit["_index"],
                "score": hit["_score"],
                "source": hit["_source"]
            }
            for hit in hits
        ]
    }

@router.post("/aggregations")
def aggregations(agg_query: AggregationQuery):
    """
    聚合查询

    支持传入 Elasticsearch Aggregation DSL 进行数据聚合分析，
    如求和、平均值、最大最小值、桶聚合等。

    Args:
        agg_query: AggregationQuery 模型，包含索引名、聚合DSL和返回文档数

    Returns:
        包含文档总数和聚合结果的字典

    Raises:
        HTTPException: 如果索引不存在，返回 404 错误
    """
    es = get_es_client()
    if not es.indices.exists(index=agg_query.index):
        raise HTTPException(status_code=404, detail=f"Index '{agg_query.index}' not found")

    query = {
        "aggs": agg_query.aggs
    }

    result = es.search(
        index=agg_query.index,
        body=query,
        size=agg_query.size
    )

    return {
        "total": result["hits"]["total"]["value"],
        "aggregations": result["aggregations"]
    }

@router.post("/bulk")
def bulk_operations(operations: List[Dict[str, Any]]):
    """
    批量操作

    批量执行多个文档操作（索引或删除），提高大量数据写入的效率。
    每个操作包含 action（index/delete）、index、id（可选）和 body。

    Args:
        operations: 操作列表，每个操作是一个描述动作的字典

    Returns:
        包含执行耗时、是否有错误和各操作结果的字典

    Raises:
        HTTPException: 如果操作列表为空，返回 400 错误
    """
    es = get_es_client()
    if not operations:
        raise HTTPException(status_code=400, detail="No operations provided")

    body = []
    for op in operations:
        action = op.get("action")
        index_name = op.get("index")
        doc_id = op.get("id")
        doc_body = op.get("body")

        if action == "index":
            if doc_id:
                body.append({"index": {"_index": index_name, "_id": doc_id}})
            else:
                body.append({"index": {"_index": index_name}})
            body.append(doc_body)
        elif action == "delete":
            body.append({"delete": {"_index": index_name, "_id": doc_id}})

    result = es.bulk(body=body)
    return {
        "took": result["took"],
        "errors": result["errors"],
        "items": result["items"]
    }

@router.post("/analyze")
def analyze_text(analyze_request: Dict[str, Any]):
    """
    分词分析

    预先查看文本经过分词器处理后的结果，用于调试分词效果。
    支持指定索引或直接指定分词器进行分析。

    Args:
        analyze_request: 分析请求，包含以下字段：
            - index: 可选，索引名称（使用该索引的分词器）
            - text: 要分析的文本（字符串或字符串数组）
            - analyzer: 可选，直接指定分词器名称
            - field: 可选，指定字段（需配合 index 使用）
            - tokenizer: 可选，直接指定分词器
            - filter: 可选，分词过滤器配置

    Returns:
        包含分词结果的字典，包括 tokens 列表

    Example:
        POST /search/analyze
        {
            "index": "my_index",
            "text": "Hello World Elasticsearch"
        }

        或指定分词器：
        {
            "analyzer": "ik_max_word",
            "text": "中华人民共和国万岁"
        }
    """
    es = get_es_client()

    body = {}
    index_name = None

    if "text" in analyze_request:
        body["text"] = analyze_request["text"]

    if "index" in analyze_request:
        index_name = analyze_request["index"]
        if "field" in analyze_request:
            body["field"] = analyze_request["field"]
    else:
        if "analyzer" in analyze_request:
            body["analyzer"] = analyze_request["analyzer"]
        if "tokenizer" in analyze_request:
            body["tokenizer"] = analyze_request["tokenizer"]
        if "filter" in analyze_request:
            body["filter"] = analyze_request["filter"]

    if not body.get("text"):
        raise HTTPException(status_code=400, detail="text field is required")

    if index_name:
        result = es.indices.analyze(index=index_name, body=body)
    else:
        result = es.indices.analyze(body=body)

    return {
        "tokens": result.get("tokens", [])
    }