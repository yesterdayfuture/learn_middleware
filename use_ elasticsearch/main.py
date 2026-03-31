"""
Elasticsearch FastAPI CRUD API

该模块提供基于 FastAPI 的 Elasticsearch 操作接口，
支持索引管理、文档CRUD、模糊搜索和聚合查询等功能。
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from config import close_es_client
from routers import indices, documents, search

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    close_es_client()

app = FastAPI(
    title="Elasticsearch FastAPI",
    description="Elasticsearch CRUD API with fuzzy search and aggregations",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(indices.router, prefix="/indices", tags=["索引管理"])
app.include_router(documents.router, prefix="/documents", tags=["文档操作"])
app.include_router(search.router, prefix="/search", tags=["搜索查询"])

@app.get("/health", tags=["健康检查"])
def health_check():
    from models import HealthResponse
    from config import get_es_client
    es = get_es_client()
    health = es.cluster.health()
    return HealthResponse(
        status=health["status"],
        cluster_name=health["cluster_name"],
        number_of_nodes=health["number_of_nodes"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)