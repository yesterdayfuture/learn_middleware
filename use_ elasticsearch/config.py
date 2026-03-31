from elasticsearch import Elasticsearch
from typing import Optional

es_client: Optional[Elasticsearch] = None

def get_es_client() -> Elasticsearch:
    """
    获取 Elasticsearch 客户端单例

    使用全局单例模式确保整个应用生命周期内复用同一个连接，
    避免频繁创建和销毁连接带来的性能开销。

    Returns:
        Elasticsearch: Elasticsearch 客户端实例

    Note:
        默认连接地址: http://localhost:9200
        默认请求超时时间: 30秒
    """
    global es_client
    if es_client is None:
        es_client = Elasticsearch(
            hosts=["http://localhost:9200"],
            verify_certs=False,
            request_timeout=30
        )
    return es_client

def close_es_client():
    """
    关闭 Elasticsearch 客户端连接

    在应用关闭时调用，确保资源正确释放。
    主要在 FastAPI lifespan 事件结束时被调用。
    """
    global es_client
    if es_client is not None:
        es_client.close()
        es_client = None