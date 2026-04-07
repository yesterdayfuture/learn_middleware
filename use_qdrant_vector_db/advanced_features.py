"""
Qdrant 高级功能示例
- 指定字段（Payload Schema）
- 模糊搜索（Full Text Search）
- 范围查询
- 嵌套字段过滤
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
    MatchText,
    MatchAny,
    Range,
    DatetimeRange,
    GeoBoundingBox,
    GeoPoint,
    PayloadSchemaType,
    TextIndexParams,
    TokenizerType,
)


class AdvancedQdrantManager:
    """高级 Qdrant 管理器"""

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        print(f"✅ 已连接到 Qdrant 服务器: {host}:{port}")

    def create_collection_with_schema(
        self,
        collection_name: str,
        vector_size: int = 768,
    ) -> bool:
        """
        创建集合并设置 Payload Schema（字段类型）
        """
        try:
            # 创建集合
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

            # 设置 Payload Schema - 定义字段类型以支持更高效的查询
            # 文本字段 - 支持全文搜索
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="title",
                field_schema=TextIndexParams(
                    type=PayloadSchemaType.TEXT,
                    tokenizer=TokenizerType.WORD,
                    min_token_len=2,
                    max_token_len=20,
                    lowercase=True,
                ),
            )

            # 关键字字段 - 支持精确匹配
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="category",
                field_schema=PayloadSchemaType.KEYWORD,
            )

            # 关键字字段 - 标签数组
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="tags",
                field_schema=PayloadSchemaType.KEYWORD,
            )

            # 整数字段 - 支持范围查询
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="price",
                field_schema=PayloadSchemaType.INTEGER,
            )

            # 浮点数字段
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="rating",
                field_schema=PayloadSchemaType.FLOAT,
            )

            print(f"✅ 集合 '{collection_name}' 创建成功，已设置字段 Schema")
            return True
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return False

    def insert_data(
        self,
        collection_name: str,
        vector: List[float],
        payload: Dict[str, Any],
        point_id: Optional[str] = None,
    ) -> Optional[str]:
        """插入数据"""
        if point_id is None:
            point_id = str(uuid.uuid4())

        try:
            self.client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)],
            )
            print(f"✅ 数据插入成功: {point_id}")
            return point_id
        except Exception as e:
            print(f"❌ 插入数据失败: {e}")
            return None

    def search_full_text(
        self,
        collection_name: str,
        query_text: str,
        field_name: str = "title",
        limit: int = 5,
    ) -> List[Any]:
        """
        全文模糊搜索
        使用 MatchText 进行词级别匹配
        注意：MatchText 需要完全匹配分词后的词，如搜索 "手机" 不会匹配 "智能手机"
        如需子串匹配，请使用 search_substring 方法
        """
        try:
            query_filter = Filter(
                must=[FieldCondition(key=field_name, match=MatchText(text=query_text))]
            )

            results = self.client.query_points(
                collection_name=collection_name,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 全文搜索 '{query_text}' 完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 全文搜索失败: {e}")
            return []

    def search_substring(
        self,
        collection_name: str,
        query_text: str,
        field_name: str = "title",
        limit: int = 5,
    ) -> List[Any]:
        """
        子串模糊搜索
        搜索包含指定子串的所有记录
        由于 Qdrant 不直接支持子串匹配，这里使用 scroll 遍历所有数据并在客户端过滤
        适用于数据量较小的场景
        """
        try:
            all_points = []
            offset = None

            # 获取所有数据
            while True:
                points, offset = self.client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                )
                all_points.extend(points)
                if offset is None:
                    break

            # 在客户端进行子串匹配
            matched_points = []
            for point in all_points:
                field_value = point.payload.get(field_name, "")
                if query_text.lower() in str(field_value).lower():
                    matched_points.append(point)

            print(f"✅ 子串搜索 '{query_text}' 完成，找到 {len(matched_points)} 个结果")
            return matched_points[:limit]
        except Exception as e:
            print(f"❌ 子串搜索失败: {e}")
            return []

    def search_exact_match(
        self,
        collection_name: str,
        field_name: str,
        value: Any,
        limit: int = 10,
    ) -> List[Any]:
        """
        精确匹配搜索
        """
        try:
            query_filter = Filter(
                must=[FieldCondition(key=field_name, match=MatchValue(value=value))]
            )

            results = self.client.query_points(
                collection_name=collection_name,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 精确匹配搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 精确匹配搜索失败: {e}")
            return []

    def search_any_match(
        self,
        collection_name: str,
        field_name: str,
        values: List[Any],
        limit: int = 10,
    ) -> List[Any]:
        """
        多值匹配搜索（匹配任意一个值）
        例如：匹配 "电子产品" 或 "服装" 类别的商品
        """
        try:
            query_filter = Filter(
                must=[FieldCondition(key=field_name, match=MatchAny(any=values))]
            )

            results = self.client.query_points(
                collection_name=collection_name,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 多值匹配搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 多值匹配搜索失败: {e}")
            return []

    def search_range(
        self,
        collection_name: str,
        field_name: str,
        gt: Optional[float] = None,
        gte: Optional[float] = None,
        lt: Optional[float] = None,
        lte: Optional[float] = None,
        limit: int = 10,
    ) -> List[Any]:
        """
        范围查询
        gt: 大于, gte: 大于等于, lt: 小于, lte: 小于等于
        """
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key=field_name,
                        range=Range(gt=gt, gte=gte, lt=lt, lte=lte),
                    )
                ]
            )

            results = self.client.query_points(
                collection_name=collection_name,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 范围查询完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 范围查询失败: {e}")
            return []

    def search_combined(
        self,
        collection_name: str,
        query_vector: List[float],
        text_query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        limit: int = 5,
    ) -> List[Any]:
        """
        组合搜索：向量相似度 + 过滤条件
        """
        try:
            must_conditions = []

            # 全文搜索条件
            if text_query:
                must_conditions.append(
                    FieldCondition(key="title", match=MatchText(text=text_query))
                )

            # 类别精确匹配
            if category:
                must_conditions.append(
                    FieldCondition(key="category", match=MatchValue(value=category))
                )

            # 价格范围
            if min_price is not None or max_price is not None:
                must_conditions.append(
                    FieldCondition(
                        key="price",
                        range=Range(gte=min_price, lte=max_price),
                    )
                )

            query_filter = Filter(must=must_conditions) if must_conditions else None

            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 组合搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 组合搜索失败: {e}")
            return []

    def close(self):
        self.client.close()
        print("✅ 已关闭 Qdrant 连接")


def demo_advanced_features():
    """高级功能演示"""
    print("=" * 60)
    print("Qdrant 高级功能示例")
    print("=" * 60)

    manager = AdvancedQdrantManager(host="localhost", port=6333)
    collection_name = "advanced_demo"

    # 1. 创建集合并设置 Schema
    print("\n📋 步骤1: 创建集合并设置字段 Schema")
    manager.create_collection_with_schema(collection_name, vector_size=768)

    # 2. 插入示例数据
    print("\n📋 步骤2: 插入示例数据")
    products = [
        {
            "vector": [0.1] * 768,
            "payload": {
                "title": "苹果 iPhone 15 Pro 智能手机",
                "category": "电子产品",
                "tags": ["手机", "苹果", "旗舰"],
                "price": 8999,
                "rating": 4.8,
            },
        },
        {
            "vector": [0.15] * 768,
            "payload": {
                "title": "华为 Mate 60 Pro 智能手机",
                "category": "电子产品",
                "tags": ["手机", "华为", "旗舰"],
                "price": 6999,
                "rating": 4.7,
            },
        },
        {
            "vector": [0.2] * 768,
            "payload": {
                "title": "小米 14 智能手机",
                "category": "电子产品",
                "tags": ["手机", "小米", "性价比"],
                "price": 3999,
                "rating": 4.5,
            },
        },
        {
            "vector": [0.8] * 768,
            "payload": {
                "title": "Nike 运动T恤",
                "category": "服装",
                "tags": ["服装", "运动", "Nike"],
                "price": 299,
                "rating": 4.3,
            },
        },
        {
            "vector": [0.85] * 768,
            "payload": {
                "title": "Adidas 运动裤",
                "category": "服装",
                "tags": ["服装", "运动", "Adidas"],
                "price": 399,
                "rating": 4.4,
            },
        },
        {
            "vector": [0.5] * 768,
            "payload": {
                "title": "索尼 WH-1000XM5 降噪耳机",
                "category": "电子产品",
                "tags": ["耳机", "索尼", "降噪"],
                "price": 2499,
                "rating": 4.6,
            },
        },
    ]

    for product in products:
        manager.insert_data(
            collection_name=collection_name,
            vector=product["vector"],
            payload=product["payload"],
        )

    # 3. 全文模糊搜索（词级别匹配）
    print("\n📋 步骤3: 全文模糊搜索 - 词级别匹配（搜索 '手机'）")
    print("   说明：MatchText 需要完全匹配分词后的词")
    results = manager.search_full_text(collection_name, query_text="手机", limit=5)
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} - ¥{point.payload.get('price')}")
    if not results:
        print("   未找到结果，因为 '手机' 和 '智能手机' 被视为不同的词")

    # 3b. 子串模糊搜索
    print("\n📋 步骤3b: 子串模糊搜索（搜索 '手机'）")
    print("   说明：子串匹配可以找到包含 '手机' 的所有记录")
    results = manager.search_substring(collection_name, query_text="手机", limit=5)
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} - ¥{point.payload.get('price')}")

    # 4. 模糊搜索 - 搜索品牌
    print("\n📋 步骤4: 全文模糊搜索（搜索 '苹果'）")
    results = manager.search_full_text(collection_name, query_text="苹果", limit=5)
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} - ¥{point.payload.get('price')}")

    # 5. 精确匹配 - 按类别
    print("\n📋 步骤5: 精确匹配搜索（category = 电子产品）")
    results = manager.search_exact_match(
        collection_name, field_name="category", value="电子产品"
    )
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')}")

    # 6. 多值匹配 - 匹配多个类别
    print("\n📋 步骤6: 多值匹配搜索（category = 电子产品 或 服装）")
    results = manager.search_any_match(
        collection_name, field_name="category", values=["电子产品", "服装"]
    )
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} ({point.payload.get('category')})")

    # 7. 范围查询 - 价格区间
    print("\n📋 步骤7: 范围查询（1000 <= price <= 5000）")
    results = manager.search_range(
        collection_name, field_name="price", gte=1000, lte=5000
    )
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} - ¥{point.payload.get('price')}")

    # 8. 范围查询 - 评分大于 4.5
    print("\n📋 步骤8: 范围查询（rating > 4.5）")
    results = manager.search_range(collection_name, field_name="rating", gt=4.5)
    for i, point in enumerate(results, 1):
        print(
            f"   {i}. {point.payload.get('title')} - 评分: {point.payload.get('rating')}"
        )

    # 9. 组合搜索：向量相似度 + 过滤条件
    print("\n📋 步骤9: 组合搜索（向量搜索 + 类别=电子产品 + 价格<=6000）")
    query_vector = [0.12] * 768  # 接近手机的向量
    results = manager.search_combined(
        collection_name=collection_name,
        query_vector=query_vector,
        category="电子产品",
        max_price=6000,
        limit=3,
    )
    for i, point in enumerate(results, 1):
        print(
            f"   {i}. {point.payload.get('title')} - ¥{point.payload.get('price')} (Score: {point.score:.4f})"
        )

    # 10. 组合搜索：向量搜索 + 全文搜索
    print("\n📋 步骤10: 组合搜索（向量搜索 + 标题包含 '智能'）")
    results = manager.search_combined(
        collection_name=collection_name,
        query_vector=query_vector,
        text_query="智能",
        limit=3,
    )
    for i, point in enumerate(results, 1):
        print(f"   {i}. {point.payload.get('title')} (Score: {point.score:.4f})")

    # 清理
    # print("\n📋 步骤11: 清理集合")
    # try:
    #     manager.client.delete_collection(collection_name)
    #     print(f"✅ 集合 '{collection_name}' 已删除")
    # except Exception as e:
    #     print(f"❌ 删除集合失败: {e}")

    manager.close()

    print("\n" + "=" * 60)
    print("高级功能示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_advanced_features()
