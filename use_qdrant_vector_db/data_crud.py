"""
Qdrant 数据管理示例
包含数据的增删改查操作
"""

import uuid
from typing import List, Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    Range,
    ScoredPoint,
)


class DataManager:
    """数据管理器"""

    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        初始化连接
        :param host: Qdrant服务器地址
        :param port: Qdrant服务器端口
        """
        self.client = QdrantClient(host=host, port=port)
        print(f"✅ 已连接到 Qdrant 服务器: {host}:{port}")

    def create_collection_if_not_exists(
        self,
        collection_name: str,
        vector_size: int = 4,
    ):
        """如果集合不存在则创建"""
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            print(f"✅ 集合 '{collection_name}' 创建成功")
        except Exception:
            print(f"ℹ️ 集合 '{collection_name}' 已存在")

    def insert_points(
        self,
        collection_name: str,
        vectors: List[List[float]],
        payloads: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        插入数据点
        :param collection_name: 集合名称
        :param vectors: 向量列表
        :param payloads: 载荷数据列表（可选）
        :param ids: 自定义ID列表（可选，默认自动生成UUID）
        :return: 插入的ID列表
        """
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(len(vectors))]

        if payloads is None:
            payloads = [{} for _ in range(len(vectors))]

        points = [
            PointStruct(id=id_, vector=vector, payload=payload)
            for id_, vector, payload in zip(ids, vectors, payloads)
        ]

        try:
            self.client.upsert(collection_name=collection_name, points=points)
            print(f"✅ 成功插入 {len(points)} 条数据")
            return ids
        except Exception as e:
            print(f"❌ 插入数据失败: {e}")
            return []

    def get_point(
        self, collection_name: str, point_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取单个数据点
        :param collection_name: 集合名称
        :param point_id: 数据点ID
        :return: 数据点信息
        """
        try:
            points = self.client.retrieve(
                collection_name=collection_name, ids=[point_id], with_payload=True, with_vectors=True
            )
            if points:
                point = points[0]
                result = {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload,
                }
                print(f"✅ 成功获取数据点: {point_id}")
                return result
            return None
        except Exception as e:
            print(f"❌ 获取数据点失败: {e}")
            return None

    def search_similar(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
        query_filter: Optional[Filter] = None,
    ) -> List[Any]:
        """
        相似度搜索
        :param collection_name: 集合名称
        :param query_vector: 查询向量
        :param limit: 返回结果数量
        :param score_threshold: 分数阈值
        :param query_filter: 过滤条件
        :return: 相似度搜索结果
        """
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter,
                with_payload=True,
            )
            print(f"✅ 搜索完成，找到 {len(results.points)} 个相似结果")
            return results.points
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return []

    def update_payload(
        self,
        collection_name: str,
        point_id: str,
        payload: Dict[str, Any],
    ) -> bool:
        """
        更新数据点载荷
        :param collection_name: 集合名称
        :param point_id: 数据点ID
        :param payload: 新的载荷数据
        :return: 是否更新成功
        """
        try:
            self.client.set_payload(
                collection_name=collection_name,
                payload=payload,
                points=[point_id],
            )
            print(f"✅ 成功更新数据点 {point_id} 的载荷")
            return True
        except Exception as e:
            print(f"❌ 更新载荷失败: {e}")
            return False

    def delete_payload_keys(
        self,
        collection_name: str,
        point_id: str,
        keys: List[str],
    ) -> bool:
        """
        删除数据点载荷中的指定字段
        :param collection_name: 集合名称
        :param point_id: 数据点ID
        :param keys: 要删除的字段名列表
        :return: 是否删除成功
        """
        try:
            self.client.delete_payload(
                collection_name=collection_name,
                keys=keys,
                points=[point_id],
            )
            print(f"✅ 成功删除数据点 {point_id} 的字段: {keys}")
            return True
        except Exception as e:
            print(f"❌ 删除载荷字段失败: {e}")
            return False

    def delete_points(
        self,
        collection_name: str,
        point_ids: List[str],
    ) -> bool:
        """
        删除数据点
        :param collection_name: 集合名称
        :param point_ids: 要删除的数据点ID列表
        :return: 是否删除成功
        """
        try:
            self.client.delete(
                collection_name=collection_name,
                points_selector=point_ids,
            )
            print(f"✅ 成功删除 {len(point_ids)} 个数据点")
            return True
        except Exception as e:
            print(f"❌ 删除数据点失败: {e}")
            return False

    def scroll_points(
        self,
        collection_name: str,
        limit: int = 10,
        offset: Optional[str] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> tuple:
        """
        分页获取数据点
        :param collection_name: 集合名称
        :param limit: 每页数量
        :param offset: 偏移量（上一页最后一个点的ID）
        :param with_payload: 是否包含载荷
        :param with_vectors: 是否包含向量
        :return: (数据点列表, 下一页偏移量)
        """
        try:
            points, next_offset = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            print(f"✅ 成功获取 {len(points)} 个数据点")
            return points, next_offset
        except Exception as e:
            print(f"❌ 获取数据点失败: {e}")
            return [], None

    def count_points(
        self,
        collection_name: str,
        query_filter: Optional[Filter] = None,
    ) -> int:
        """
        统计数据点数量
        :param collection_name: 集合名称
        :param query_filter: 过滤条件
        :return: 数据点数量
        """
        try:
            count = self.client.count(
                collection_name=collection_name, count_filter=query_filter
            )
            print(f"✅ 集合 '{collection_name}' 共有 {count.count} 个数据点")
            return count.count
        except Exception as e:
            print(f"❌ 统计数据点失败: {e}")
            return 0

    def close(self):
        """关闭连接"""
        self.client.close()
        print("✅ 已关闭 Qdrant 连接")


def demo_data_crud():
    """数据CRUD演示"""
    print("=" * 60)
    print("Qdrant 数据管理示例")
    print("=" * 60)

    # 初始化管理器
    manager = DataManager(host="localhost", port=6333)
    collection_name = "demo_data_collection"

    # 创建集合
    print("\n📋 步骤1: 创建集合")
    manager.create_collection_if_not_exists(collection_name, vector_size=4)

    # 插入数据
    print("\n📋 步骤2: 插入数据")
    vectors = [
        [0.1, 0.2, 0.3, 0.4],
        [0.2, 0.3, 0.4, 0.5],
        [0.3, 0.4, 0.5, 0.6],
        [0.9, 0.8, 0.7, 0.6],
        [0.8, 0.7, 0.6, 0.5],
    ]
    payloads = [
        {"name": "产品A", "category": "电子产品", "price": 100},
        {"name": "产品B", "category": "电子产品", "price": 200},
        {"name": "产品C", "category": "服装", "price": 50},
        {"name": "产品D", "category": "食品", "price": 30},
        {"name": "产品E", "category": "食品", "price": 40},
    ]
    ids = manager.insert_points(collection_name, vectors, payloads)

    # 统计数据
    print("\n📋 步骤3: 统计数据点")
    manager.count_points(collection_name)

    # 获取单个数据点
    print("\n📋 步骤4: 获取单个数据点")
    if ids:
        point = manager.get_point(collection_name, ids[0])
        if point:
            print(f"   ID: {point['id']}")
            print(f"   Payload: {point['payload']}")

    # 相似度搜索
    print("\n📋 步骤5: 相似度搜索")
    query_vector = [0.15, 0.25, 0.35, 0.45]
    results = manager.search_similar(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3,
    )
    for i, result in enumerate(results, 1):
        print(f"   {i}. ID: {result.id}, Score: {result.score:.4f}, Payload: {result.payload}")

    # 带过滤条件的搜索
    print("\n📋 步骤6: 带过滤条件的搜索（category = 电子产品）")
    query_filter = Filter(
        must=[FieldCondition(key="category", match=MatchValue(value="电子产品"))]
    )
    results = manager.search_similar(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=3,
        query_filter=query_filter,
    )
    for i, result in enumerate(results, 1):
        print(f"   {i}. ID: {result.id}, Score: {result.score:.4f}, Payload: {result.payload}")

    # 更新载荷
    print("\n📋 步骤7: 更新数据点载荷")
    if ids:
        manager.update_payload(
            collection_name=collection_name,
            point_id=ids[0],
            payload={"name": "产品A-更新版", "discount": 0.9},
        )
        # 查看更新后的数据
        point = manager.get_point(collection_name, ids[0])
        if point:
            print(f"   更新后 Payload: {point['payload']}")

    # 删除载荷字段
    print("\n📋 步骤8: 删除载荷字段")
    if ids:
        manager.delete_payload_keys(
            collection_name=collection_name,
            point_id=ids[0],
            keys=["discount"],
        )
        point = manager.get_point(collection_name, ids[0])
        if point:
            print(f"   删除后 Payload: {point['payload']}")

    # 分页获取数据
    print("\n📋 步骤9: 分页获取数据")
    points, next_offset = manager.scroll_points(
        collection_name=collection_name, limit=3, with_payload=True
    )
    for point in points:
        print(f"   ID: {point.id}, Payload: {point.payload}")

    # 删除数据点
    # print("\n📋 步骤10: 删除数据点")
    # if len(ids) > 0:
    #     manager.delete_points(collection_name, [ids[0]])
    #     manager.count_points(collection_name)

    # # 清理：删除集合
    # print("\n📋 步骤11: 清理集合")
    # try:
    #     manager.client.delete_collection(collection_name)
    #     print(f"✅ 集合 '{collection_name}' 已删除")
    # except Exception as e:
    #     print(f"❌ 删除集合失败: {e}")

    # 关闭连接
    manager.close()

    print("\n" + "=" * 60)
    print("数据管理示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_data_crud()
