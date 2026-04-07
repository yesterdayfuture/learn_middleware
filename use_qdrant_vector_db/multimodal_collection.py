"""
Qdrant 多模态集合示例
支持文本、图像等多种模态数据的向量存储和检索
"""

import uuid
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)


class ModalityType(str, Enum):
    """模态类型"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class MultimodalData:
    """多模态数据结构"""
    id: Optional[Union[str, int]] = None
    text_vector: Optional[List[float]] = None
    image_vector: Optional[List[float]] = None
    audio_vector: Optional[List[float]] = None
    text_content: Optional[str] = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MultimodalCollectionManager:
    """多模态集合管理器"""

    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        初始化连接
        :param host: Qdrant服务器地址
        :param port: Qdrant服务器端口
        """
        self.client = QdrantClient(host=host, port=port)
        print(f"✅ 已连接到 Qdrant 服务器: {host}:{port}")

    def create_multimodal_collection(
        self,
        collection_name: str,
        text_vector_size: int = 768,
        image_vector_size: int = 512,
        audio_vector_size: int = 256,
    ) -> bool:
        """
        创建多模态集合
        包含多个向量字段：文本、图像、音频
        :param collection_name: 集合名称
        :param text_vector_size: 文本向量维度
        :param image_vector_size: 图像向量维度
        :param audio_vector_size: 音频向量维度
        :return: 是否创建成功
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                    "text": VectorParams(
                        size=text_vector_size, distance=Distance.COSINE
                    ),
                    "image": VectorParams(
                        size=image_vector_size, distance=Distance.COSINE
                    ),
                    "audio": VectorParams(
                        size=audio_vector_size, distance=Distance.COSINE
                    ),
                },
            )
            print(f"✅ 多模态集合 '{collection_name}' 创建成功")
            print(f"   - 文本向量维度: {text_vector_size}")
            print(f"   - 图像向量维度: {image_vector_size}")
            print(f"   - 音频向量维度: {audio_vector_size}")
            return True
        except Exception as e:
            print(f"❌ 创建多模态集合失败: {e}")
            return False

    def insert_multimodal_data(
        self,
        collection_name: str,
        data: MultimodalData,
    ) -> Optional[str]:
        """
        插入多模态数据
        :param collection_name: 集合名称
        :param data: 多模态数据
        :return: 数据ID
        """
        if data.id is None:
            data.id = str(uuid.uuid4())

        # 构建向量字典（只包含非None的向量）
        vector = {}
        if data.text_vector is not None:
            vector["text"] = data.text_vector
        if data.image_vector is not None:
            vector["image"] = data.image_vector
        if data.audio_vector is not None:
            vector["audio"] = data.audio_vector

        # 构建载荷
        payload = {
            "text_content": data.text_content,
            "image_url": data.image_url,
            "audio_url": data.audio_url,
            "metadata": data.metadata or {},
        }

        # 添加模态类型信息
        modalities = []
        if data.text_vector is not None:
            modalities.append("text")
        if data.image_vector is not None:
            modalities.append("image")
        if data.audio_vector is not None:
            modalities.append("audio")
        payload["modalities"] = modalities

        point = PointStruct(id=data.id, vector=vector, payload=payload)

        try:
            self.client.upsert(collection_name=collection_name, points=[point])
            print(f"✅ 成功插入多模态数据: {data.id}")
            print(f"   包含模态: {modalities}")
            return data.id
        except Exception as e:
            print(f"❌ 插入多模态数据失败: {e}")
            return None

    def search_by_text(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """
        使用文本向量搜索
        :param collection_name: 集合名称
        :param query_vector: 查询向量
        :param limit: 返回结果数量
        :param score_threshold: 分数阈值
        :return: 搜索结果
        """
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                using="text",
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            print(f"✅ 文本搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 文本搜索失败: {e}")
            return []

    def search_by_image(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """
        使用图像向量搜索
        :param collection_name: 集合名称
        :param query_vector: 查询向量
        :param limit: 返回结果数量
        :param score_threshold: 分数阈值
        :return: 搜索结果
        """
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                using="image",
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            print(f"✅ 图像搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 图像搜索失败: {e}")
            return []

    def search_by_audio(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Any]:
        """
        使用音频向量搜索
        :param collection_name: 集合名称
        :param query_vector: 查询向量
        :param limit: 返回结果数量
        :param score_threshold: 分数阈值
        :return: 搜索结果
        """
        try:
            results = self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                using="audio",
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
            )
            print(f"✅ 音频搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 音频搜索失败: {e}")
            return []

    def search_multimodal(
        self,
        collection_name: str,
        text_vector: Optional[List[float]] = None,
        image_vector: Optional[List[float]] = None,
        audio_vector: Optional[List[float]] = None,
        weights: Optional[Dict[str, float]] = None,
        limit: int = 5,
    ) -> List[Any]:
        """
        多模态融合搜索
        支持文本、图像、音频向量的加权融合搜索
        :param collection_name: 集合名称
        :param text_vector: 文本查询向量
        :param image_vector: 图像查询向量
        :param audio_vector: 音频查询向量
        :param weights: 各模态权重 {"text": 0.5, "image": 0.3, "audio": 0.2}
        :param limit: 返回结果数量
        :return: 搜索结果
        """
        if weights is None:
            weights = {"text": 0.4, "image": 0.4, "audio": 0.2}

        try:
            # 构建查询向量列表
            query_vectors = []

            if text_vector is not None and weights.get("text", 0) > 0:
                query_vectors.append(
                    {
                        "vector": {"name": "text", "vector": text_vector},
                        "weight": weights["text"],
                    }
                )

            if image_vector is not None and weights.get("image", 0) > 0:
                query_vectors.append(
                    {
                        "vector": {"name": "image", "vector": image_vector},
                        "weight": weights["image"],
                    }
                )

            if audio_vector is not None and weights.get("audio", 0) > 0:
                query_vectors.append(
                    {
                        "vector": {"name": "audio", "vector": audio_vector},
                        "weight": weights["audio"],
                    }
                )

            if not query_vectors:
                print("❌ 至少需要提供一个查询向量")
                return []

            results = self.client.query_points(
                collection_name=collection_name,
                prefetch=query_vectors,
                query=None,  # 使用融合搜索
                limit=limit,
                with_payload=True,
            )
            print(f"✅ 多模态融合搜索完成，找到 {len(results.points)} 个结果")
            return results.points
        except Exception as e:
            print(f"❌ 多模态搜索失败: {e}")
            return []

    def filter_by_modality(
        self,
        collection_name: str,
        modality: ModalityType,
        limit: int = 10,
    ) -> List[Any]:
        """
        按模态类型过滤数据
        :param collection_name: 集合名称
        :param modality: 模态类型
        :param limit: 返回结果数量
        :return: 过滤结果
        """
        try:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="modalities", match=MatchValue(value=modality.value)
                    )
                ]
            )
            results = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                scroll_filter=query_filter,
                with_payload=True,
            )
            print(f"✅ 找到 {len(results[0])} 个包含 {modality.value} 模态的数据")
            return results[0]
        except Exception as e:
            print(f"❌ 过滤失败: {e}")
            return []

    def get_point(self, collection_name: str, point_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """
        获取单个多模态数据点
        :param collection_name: 集合名称
        :param point_id: 数据点ID
        :return: 数据点信息
        """
        try:
            # 将字符串ID转换为整数（如果是数字字符串）
            if isinstance(point_id, str) and point_id.isdigit():
                point_id = int(point_id)
            points = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=True,
                with_vectors=True,
            )
            if points:
                point = points[0]
                return {
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload,
                }
            return None
        except Exception as e:
            print(f"❌ 获取数据点失败: {e}")
            return None

    def delete_point(self, collection_name: str, point_id: Union[str, int]) -> bool:
        """
        删除数据点
        :param collection_name: 集合名称
        :param point_id: 数据点ID
        :return: 是否删除成功
        """
        try:
            # 将字符串ID转换为整数（如果是数字字符串）
            if isinstance(point_id, str) and point_id.isdigit():
                point_id = int(point_id)
            self.client.delete(
                collection_name=collection_name, points_selector=[point_id]
            )
            print(f"✅ 成功删除数据点: {point_id}")
            return True
        except Exception as e:
            print(f"❌ 删除数据点失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        self.client.close()
        print("✅ 已关闭 Qdrant 连接")


def demo_multimodal():
    """多模态集合演示"""
    print("=" * 60)
    print("Qdrant 多模态集合示例")
    print("=" * 60)

    # 初始化管理器
    manager = MultimodalCollectionManager(host="localhost", port=6333)
    collection_name = "multimodal_demo"

    # 1. 创建多模态集合
    print("\n📋 步骤1: 创建多模态集合")
    manager.create_multimodal_collection(
        collection_name=collection_name,
        text_vector_size=768,
        image_vector_size=512,
        audio_vector_size=256,
    )

    # 2. 插入纯文本数据
    print("\n📋 步骤2: 插入纯文本数据")
    text_data = MultimodalData(
        id=1,
        text_vector=[0.1] * 768,
        text_content="这是一段示例文本内容",
        metadata={"source": "文档", "language": "zh"},
    )
    manager.insert_multimodal_data(collection_name, text_data)

    # 3. 插入纯图像数据
    print("\n📋 步骤3: 插入纯图像数据")
    image_data = MultimodalData(
        id=2,
        image_vector=[0.2] * 512,
        image_url="https://example.com/image1.jpg",
        metadata={"source": "相册", "format": "jpg"},
    )
    manager.insert_multimodal_data(collection_name, image_data)

    # 4. 插入纯音频数据
    print("\n📋 步骤4: 插入纯音频数据")
    audio_data = MultimodalData(
        id=3,
        audio_vector=[0.3] * 256,
        audio_url="https://example.com/audio1.mp3",
        metadata={"source": "录音", "duration": 120},
    )
    manager.insert_multimodal_data(collection_name, audio_data)

    # 5. 插入多模态融合数据（同时包含文本和图像）
    print("\n📋 步骤5: 插入多模态融合数据（文本+图像）")
    multimodal_data = MultimodalData(
        id=4,
        text_vector=[0.4] * 768,
        image_vector=[0.5] * 512,
        text_content="这是一张带有描述的图片",
        image_url="https://example.com/image2.jpg",
        metadata={"source": "社交媒体", "type": "图文"},
    )
    manager.insert_multimodal_data(collection_name, multimodal_data)

    # 6. 插入全模态数据
    print("\n📋 步骤6: 插入全模态数据（文本+图像+音频）")
    full_multimodal_data = MultimodalData(
        id=5,
        text_vector=[0.6] * 768,
        image_vector=[0.7] * 512,
        audio_vector=[0.8] * 256,
        text_content="这是一个视频的描述",
        image_url="https://example.com/video_thumbnail.jpg",
        audio_url="https://example.com/video_audio.mp3",
        metadata={"source": "视频平台", "type": "视频", "duration": 300},
    )
    manager.insert_multimodal_data(collection_name, full_multimodal_data)

    # 7. 文本搜索
    print("\n📋 步骤7: 文本向量搜索")
    query_text_vector = [0.15] * 768
    results = manager.search_by_text(
        collection_name=collection_name,
        query_vector=query_text_vector,
        limit=3,
    )
    for i, result in enumerate(results, 1):
        print(f"   {i}. ID: {result.id}, Score: {result.score:.4f}")
        print(f"      内容: {result.payload.get('text_content', 'N/A')}")

    # 8. 图像搜索
    print("\n📋 步骤8: 图像向量搜索")
    query_image_vector = [0.55] * 512
    results = manager.search_by_image(
        collection_name=collection_name,
        query_vector=query_image_vector,
        limit=3,
    )
    for i, result in enumerate(results, 1):
        print(f"   {i}. ID: {result.id}, Score: {result.score:.4f}")
        print(f"      图像URL: {result.payload.get('image_url', 'N/A')}")

    # 9. 按模态类型过滤
    print("\n📋 步骤9: 按模态类型过滤（仅文本）")
    text_results = manager.filter_by_modality(
        collection_name=collection_name,
        modality=ModalityType.TEXT,
        limit=10,
    )
    for point in text_results:
        print(f"   ID: {point.id}, 模态: {point.payload.get('modalities')}")

    # 10. 获取单个数据点
    print("\n📋 步骤10: 获取单个多模态数据点")
    point = manager.get_point(collection_name, 5)
    if point:
        print(f"   ID: {point['id']}")
        print(f"   模态: {point['payload'].get('modalities')}")
        print(f"   向量字段: {list(point['vector'].keys()) if point['vector'] else 'N/A'}")

    # # 11. 删除数据点
    # print("\n📋 步骤11: 删除数据点")
    # manager.delete_point(collection_name, 3)

    # # 清理：删除集合
    # print("\n📋 步骤12: 清理集合")
    # try:
    #     manager.client.delete_collection(collection_name)
    #     print(f"✅ 集合 '{collection_name}' 已删除")
    # except Exception as e:
    #     print(f"❌ 删除集合失败: {e}")

    # 关闭连接
    manager.close()

    print("\n" + "=" * 60)
    print("多模态集合示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_multimodal()
