"""
Qdrant 集合管理示例
包含集合的增删改查操作
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionInfo
from typing import Optional, List


class CollectionManager:
    """集合管理器"""

    def __init__(self, host: str = "localhost", port: int = 6333):
        """
        初始化连接
        :param host: Qdrant服务器地址
        :param port: Qdrant服务器端口
        """
        self.client = QdrantClient(host=host, port=port)
        print(f"✅ 已连接到 Qdrant 服务器: {host}:{port}")

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 1536,
        distance: Distance = Distance.COSINE,
    ) -> bool:
        """
        创建集合
        :param collection_name: 集合名称
        :param vector_size: 向量维度
        :param distance: 距离度量方式 (COSINE, EUCLID, DOT)
        :return: 是否创建成功
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
            print(f"✅ 集合 '{collection_name}' 创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建集合失败: {e}")
            return False

    def get_collection(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        获取集合信息
        :param collection_name: 集合名称
        :return: 集合信息
        """
        try:
            info = self.client.get_collection(collection_name=collection_name)
            print(f"✅ 获取集合 '{collection_name}' 信息成功")
            return info
        except Exception as e:
            print(f"❌ 获取集合信息失败: {e}")
            return None

    def list_collections(self) -> List[str]:
        """
        列出所有集合
        :return: 集合名称列表
        """
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]
            print(f"✅ 发现 {len(collection_names)} 个集合: {collection_names}")
            return collection_names
        except Exception as e:
            print(f"❌ 获取集合列表失败: {e}")
            return []

    def update_collection(
        self,
        collection_name: str,
        optimizers_config: Optional[dict] = None,
    ) -> bool:
        """
        更新集合配置
        :param collection_name: 集合名称
        :param optimizers_config: 优化器配置
        :return: 是否更新成功
        """
        try:
            self.client.update_collection(
                collection_name=collection_name,
                optimizers_config=optimizers_config,
            )
            print(f"✅ 集合 '{collection_name}' 更新成功")
            return True
        except Exception as e:
            print(f"❌ 更新集合失败: {e}")
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """
        删除集合
        :param collection_name: 集合名称
        :return: 是否删除成功
        """
        try:
            self.client.delete_collection(collection_name=collection_name)
            print(f"✅ 集合 '{collection_name}' 删除成功")
            return True
        except Exception as e:
            print(f"❌ 删除集合失败: {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """
        检查集合是否存在
        :param collection_name: 集合名称
        :return: 是否存在
        """
        try:
            exists = self.client.collection_exists(collection_name)
            status = "存在" if exists else "不存在"
            print(f"ℹ️ 集合 '{collection_name}' {status}")
            return exists
        except Exception as e:
            print(f"❌ 检查集合失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        self.client.close()
        print("✅ 已关闭 Qdrant 连接")


def demo_collection_crud():
    """集合CRUD演示"""
    print("=" * 60)
    print("Qdrant 集合管理示例")
    print("=" * 60)

    # 初始化管理器
    manager = CollectionManager(host="localhost", port=6333)

    collection_name = "demo_collection"

    # 1. 检查集合是否存在
    print("\n📋 步骤1: 检查集合是否存在")
    manager.collection_exists(collection_name)

    # 2. 创建集合
    print("\n📋 步骤2: 创建集合")
    manager.create_collection(
        collection_name=collection_name,
        vector_size=1536,
        distance=Distance.COSINE,
    )

    # 3. 获取集合信息
    print("\n📋 步骤3: 获取集合信息")
    info = manager.get_collection(collection_name)
    if info:
        print(f"   向量维度: {info.config.params.vectors.size}")
        print(f"   距离度量: {info.config.params.vectors.distance}")
        print(f"   向量数量: {info.points_count}")

    # 4. 列出所有集合
    print("\n📋 步骤4: 列出所有集合")
    manager.list_collections()

    # 5. 再次检查集合是否存在
    print("\n📋 步骤5: 再次检查集合是否存在")
    manager.collection_exists(collection_name)

    # # 6. 删除集合
    # print("\n📋 步骤6: 删除集合")
    # manager.delete_collection(collection_name)

    # # 7. 验证删除
    # print("\n📋 步骤7: 验证删除")
    # manager.collection_exists(collection_name)

    # 关闭连接
    manager.close()

    print("\n" + "=" * 60)
    print("集合管理示例完成!")
    print("=" * 60)


if __name__ == "__main__":
    demo_collection_crud()
