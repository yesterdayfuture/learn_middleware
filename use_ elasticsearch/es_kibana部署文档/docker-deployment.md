# Elasticsearch Docker 部署指南

本文档介绍如何使用 Docker 和 Docker Compose 部署 Elasticsearch、Kibana 和 elasticsearch-head。

## 环境要求

- Docker >= 20.10
- Docker Compose >= 2.0
- 系统内存 >= 4GB（建议 8GB+）

## 快速部署

### 方式一：使用 Docker Compose 一键部署（推荐）

#### 1. 创建 elasticsearch.yml 配置文件

在项目根目录创建 [elasticsearch.yml](file:///Users/zhangtian/gitProject/learn_middleware/use_%20elasticsearch/elasticsearch.yml) 文件：

```yaml
cluster.name: "docker-cluster"
network.host: 0.0.0.0
http.cors.enabled: true
http.cors.allow-origin: "*"
```

#### 2. 创建 docker-compose.yml

在项目根目录创建 [docker-compose.yml](file:///Users/zhangtian/gitProject/learn_middleware/use_%20elasticsearch/docker-compose.yml) 文件：

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=elasticsearch-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - xpack.security.enabled=false
      - xpack.security.enrollment.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    ulimits:
      memlock:
        soft: -1
        hard: -1
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
      - ./elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - elasticsearch-network
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\"\\|\"status\":\"yellow\"'"]
      interval: 30s
      timeout: 10s
      retries: 5

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      elasticsearch:
        condition: service_healthy
    networks:
      - elasticsearch-network

  elasticsearch-head:
    image: mobz/elasticsearch-head:5
    container_name: elasticsearch-head
    ports:
      - "9100:9100"
    networks:
      - elasticsearch-network

volumes:
  elasticsearch-data:
    driver: local

networks:
  elasticsearch-network:
    driver: bridge
```

**关键配置说明：**
- `./elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml` - 将本地配置文件挂载到容器内
- `http.cors.enabled: true` 和 `http.cors.allow-origin: "*"` - 启用跨域访问，允许 elasticsearch-head 连接
- `network.host: 0.0.0.0` - 允许外部访问

#### 3. 启动服务

```bash
docker-compose up -d
```

#### 4. 验证服务

检查所有容器运行状态：

```bash
docker-compose ps
```

预期输出：
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
elasticsearch       "/bin/tini eswrapper…"   elasticsearch       running (healthy)   0.0.0.0:9200->9200/tcp, 0.0.0.0:9300->9300/tcp
elasticsearch-head   "/docker-entrypoint.…"   elasticsearch-head  running             0.0.0.0:9100->9100/tcp
kibana              "/bin/tini -- /usr/l…"   kibana              running             0.0.0.0:5601->5601/tcp
```

### 方式二：使用 Docker 单独部署

如需单独部署每个服务，可以使用以下命令：

#### 1. 创建 elasticsearch.yml 配置文件

```bash
mkdir -p ~/elasticsearch
cd ~/elasticsearch
cat > elasticsearch.yml << 'EOF'
cluster.name: "docker-cluster"
network.host: 0.0.0.0
http.cors.enabled: true
http.cors.allow-origin: "*"
EOF
```

#### 2. 启动 Elasticsearch

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e node.name=elasticsearch \
  -e cluster.name=docker-cluster \
  -e discovery.type=single-node \
  -e xpack.security.enabled=false \
  -e "ES_JAVA_OPTS=-Xms2g -Xmx2g" \
  -v ~/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
  docker.elastic.co/elasticsearch/elasticsearch:8.12.0
```

#### 3. 启动 Kibana（需等待 Elasticsearch 启动完成）

```bash
docker run -d \
  --name kibana \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://localhost:9200 \
  --link elasticsearch \
  docker.elastic.co/kibana/kibana:8.12.0
```

#### 4. 启动 elasticsearch-head

```bash
docker run -d \
  --name elasticsearch-head \
  -p 9100:9100 \
  mobz/elasticsearch-head:5
```

#### 5. 验证服务

```bash
# 检查容器状态
docker ps

# 检查 Elasticsearch 健康状态
curl http://localhost:9200

# 检查集群健康状态
curl http://localhost:9200/_cluster/health
```

## 服务访问

| 服务 | 地址 | 说明 |
|------|------|------|
| Elasticsearch | http://localhost:9200 | REST API 端点 |
| Kibana | http://localhost:5601 | 可视化界面 |
| elasticsearch-head | http://localhost:9100 | 集群管理界面 |

## 常用命令

### Docker Compose 方式

```bash
# 查看所有容器日志
docker-compose logs

# 查看指定服务日志
docker-compose logs -f elasticsearch
docker-compose logs -f kibana

# 查看最近 100 行日志
docker-compose logs --tail=100 elasticsearch

# 停止服务
docker-compose down

# 重新启动服务
docker-compose restart

# 完全清除（包括数据卷）
docker-compose down -v

# 重建服务
docker-compose up -d --force-recreate
docker-compose up -d --force-recreate --build elasticsearch
```

### Docker 单独部署方式

```bash
# 查看容器日志
docker logs -f elasticsearch
docker logs -f kibana
docker logs -f elasticsearch-head

# 停止容器
docker stop elasticsearch kibana elasticsearch-head

# 删除容器
docker rm elasticsearch kibana elasticsearch-head

# 重启容器
docker restart elasticsearch kibana elasticsearch-head

# 查看容器状态
docker ps

# 查看 Elasticsearch 集群健康状态
curl http://localhost:9200/_cluster/health

# 查看所有索引
curl http://localhost:9200/_cat/indices
```

## 数据持久化

### Docker Compose 方式

Elasticsearch 数据存储在 Docker volume 中：

```bash
# 查看 volume 列表
docker volume ls

# 查看 volume 详细信息
docker volume inspect use__elasticsearch_elasticsearch-data
```

### Docker 单独部署方式

数据存储在本地目录：

```bash
# 查看数据目录
ls -la ~/elasticsearch/
```

如需备份数据，可以将本地目录挂载到容器：

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -v ~/elasticsearch/data:/usr/share/elasticsearch/data \
  -v ~/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml \
  docker.elastic.co/elasticsearch/elasticsearch:8.12.0
```

## 常见问题

### 1. Elasticsearch 启动失败

检查内存是否充足：
```bash
docker stats
```

确保宿主机有足够的内存分配给 Docker。

### 2. Kibana 无法连接 Elasticsearch

等待 Elasticsearch 健康检查通过后再启动 Kibana。检查网络连接：
```bash
docker exec -it kibana curl http://elasticsearch:9200
```

### 3. elasticsearch-head 连接被拒绝

确保 elasticsearch.yml 配置了跨域：
```yaml
http.cors.enabled: true
http.cors.allow-origin: "*"
```

并正确挂载到容器内：
```bash
docker run -v ~/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
```

### 4. 端口冲突

如果宿主机端口已被占用，修改端口映射：

Docker Compose 方式：
```yaml
ports:
  - "19200:9200"  # 改为其他端口
```

Docker 单独部署：
```bash
-p 19200:9200
```

## 安全设置（可选）

如需启用安全认证：

Docker Compose 方式：
```yaml
environment:
  - xpack.security.enabled=true
  - xpack.security.enrollment.enabled=true
```

Docker 单独部署：
```bash
-e xpack.security.enabled=true
```

然后初始化内置用户：
```bash
docker exec -it elasticsearch /usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive
```

## 开发环境推荐配置

对于开发环境，可以使用以下优化配置 [docker-compose-dev.yml](file:///Users/zhangtian/gitProject/learn_middleware/use_%20elasticsearch/docker-compose-dev.yml)：

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=elasticsearch-cluster
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
      - ./elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
    networks:
      - elastic-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    networks:
      - elastic-network

  elasticsearch-head:
    image: mobz/elasticsearch-head:5
    container_name: elasticsearch-head
    ports:
      - "9100:9100"
    networks:
      - elastic-network

volumes:
  elasticsearch-data:

networks:
  elastic-network:
    driver: bridge
```

启动开发环境：
```bash
docker-compose -f docker-compose-dev.yml up -d
```

## 清理资源

### Docker Compose 方式

```bash
docker-compose down -v
docker system prune -f
docker volume prune -f
```

### Docker 单独部署方式

```bash
# 停止并删除所有容器
docker stop elasticsearch kibana elasticsearch-head
docker rm elasticsearch kibana elasticsearch-head

# 删除数据目录
rm -rf ~/elasticsearch

# 清理未使用的镜像
docker image prune -f
```