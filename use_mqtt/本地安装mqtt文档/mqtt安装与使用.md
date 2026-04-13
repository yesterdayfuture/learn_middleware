# mqtt 安装与使用



## docker 部署

#### 1. Mosquitto（轻量级推荐）

- **特点**：轻量级（仅约13MB）、资源占用少、适合边缘设备和小型项目
- **适用场景**：树莓派、嵌入式设备、开发测试环境
- **镜像名**：`eclipse-mosquitto`

#### 2. EMQX（企业级推荐）

- **特点**：高性能、支持集群、提供管理界面、完整支持MQTT 5.0
- **适用场景**：生产环境、需要高可用性和管理功能的场景
- **镜像名**：`emqx/emqx`

### 部署Mosquitto

#### 开发环境部署

```shell
# 拉取官方镜像
docker pull eclipse-mosquitto:latest

# 运行容器（最简方式）
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto
```

#### 生产环境部署

##### 步骤1：创建持久化目录

```bash
mkdir -p /usr/local/mosquitto/{config,data,log}
chmod -R 777 /usr/local/mosquitto/  # 避免权限问题
```

##### 步骤2：创建配置文件

```bash
cat > /usr/local/mosquitto/config/mosquitto.conf << EOF
# 基础配置
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
listener 1883 0.0.0.0
port 1883

# WebSocket支持（可选）
listener 9001
protocol websockets

# 安全配置
allow_anonymous true  # 测试环境可开启，生产环境建议关闭
# password_file /mosquitto/config/passwd

# 性能配置
max_connections -1
connection_messages true
EOF
```

##### 步骤3：启动容器

```bash
docker run -d \
  --name mosquitto \
  -p 1883:1883 \
 -p 9001:9001 \
  -v /usr/local/mosquitto/config:/mosquitto/config \
  -v /usr/local/mosquitto/data:/mosquitto/data \
  -v /usr/local/mosquitto/log:/mosquitto/log \
  --restart unless-stopped \
  eclipse-mosquitto
```

**关键参数说明**：

- `-v`：将宿主机目录挂载到容器，实现配置和数据持久化
- `--restart unless-stopped`：容器随Docker自动重启，确保服务高可用
- `-p 9001:9001`：开放WebSocket端口，支持浏览器客户端连接

##### 启用密码认证

1. **创建用户和密码文件**：

   ```bash
   docker exec -it mosquitto mosquitto_passwd -c /mosquitto/config/passwd mqtt_admin
   docker exec -it mosquitto mosquitto_passwd /mosquitto/config/passwd device_001
   ```

2. **修改配置文件**：

   ```bash
   echo "allow_anonymous false" >> /usr/local/mosquitto/config/mosquitto.conf
   echo "password_file /mosquitto/config/passwd" >> /usr/local/mosquitto/config/mosquitto.conf
   ```

3. **重启容器**：

   ```bash
   docker restart mosquitto
   ```

#### Docker Compose部署（生产环境推荐）

创建`docker-compose.yml`文件：

```yaml
version: '3.8'
services:
  mosquitto:
    image: eclipse-mosquitto:2
    container_name: mosquitto
    restart: unless-stopped
    ports:
      - "1883:1883"   # MQTT端口
      - "9001:9001"   # WebSocket端口
      - "8883:8883"   # SSL端口（可选）
    volumes:
      - ./config:/mosquitto/config
      - ./data:/mosquitto/data
      - ./log:/mosquitto/log
    environment:
      - TZ=Asia/Shanghai  # 设置时区
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

**启动命令**：

```bash
docker-compose up -d
docker-compose logs -f  # 查看日志
```



### 部署emqx/emqx:latest

使用Docker部署EMQX是物联网应用开发中高效构建MQTT消息服务器的关键方法，**通过官方Docker镜像可快速启动单节点或集群环境，支持社区版和企业版，关键在于正确配置端口映射、数据持久化和集群发现策略**。以下是详细部署指南：

#### 单节点部署步骤

##### 1. 基础部署（快速测试）
```bash
# 拉取最新社区版镜像
docker pull emqx/emqx:latest

# 启动单节点容器（最简方式）
docker run -d --name emqx \
-p 1883:1883 \
-p 8083:8083 \
-p 8084:8084 \
-p 8883:8883 \
-p 18083:18083 \
emqx/emqx:latest
```
**关键端口说明**：
- **1883**：MQTT非加密端口
- **8883**：MQTT SSL加密端口
- **8083**：MQTT WebSocket端口
- **8084**：MQTT WebSocket安全端口
- **18083**：EMQX管理控制台端口

##### 2. 生产环境部署（推荐）

###### 步骤1：创建持久化目录
```bash
mkdir -p /data/emqx/{conf,data,log}
chmod -R 777 /data/emqx/  # 赋予读写权限
```

###### 步骤2：启动容器（带持久化）
```bash
docker run -d \
--name emqx \
-p 1883:1883 \
-p 8083:8083 \
-p 8084:8084 \
-p 8883:8883 \
-p 18083:18083 \
-v /data/emqx/conf:/opt/emqx/etc \
-v /data/emqx/data:/opt/emqx/data \
-v /data/emqx/log:/opt/emqx/log \
-e EMQX_ADMIN_PASSWORD=admin123 \  # 设置管理密码
--restart=always \  # 随Docker自动启动
emqx/emqx:5.6.0
```
**关键参数说明**：
- `-v`：将宿主机目录挂载到容器，实现配置和数据持久化
- `--restart=always`：确保服务高可用
- `-e EMQX_ADMIN_PASSWORD`：设置管理控制台密码（默认为`public`）

###### 步骤3：验证部署
```bash
# 查看容器状态
docker ps | grep emqx

# 查看日志确认启动成功
docker logs -f emqx

# 访问管理控制台
http://localhost:18083  # 用户名：admin，密码：admin123
```
成功日志应包含：`EMQX 5.6.0 is running now! Dashboard: http://0.0.0.0:18083`

#### 集群部署步骤（Docker Compose）

##### 1. 创建`docker-compose.yml`文件
```yaml
version: '3'
services:
  emqx1:
    image: emqx/emqx:5.6.0
    container_name: emqx1
    environment:
      - "EMQX_NODE_NAME=emqx@node1.emqx.com"
      - "EMQX_CLUSTER__DISCOVERY_STRATEGY=static"
      - "EMQX_CLUSTER__STATIC__SEEDS=[emqx@node1.emqx.com,emqx@node2.emqx.com]"
    networks:
      emqx-bridge:
        aliases:
          - node1.emqx.com
    ports:
      - 1883:1883
      - 8083:8083
      - 8084:8084
      - 8883:8883
      - 18083:18083
    # volumes:
    #   - $PWD/emqx1_data:/opt/emqx/data

  emqx2:
    image: emqx/emqx:5.6.0
    container_name: emqx2
    environment:
      - "EMQX_NODE_NAME=emqx@node2.emqx.com"
      - "EMQX_CLUSTER__DISCOVERY_STRATEGY=static"
      - "EMQX_CLUSTER__STATIC__SEEDS=[emqx@node1.emqx.com,emqx@node2.emqx.com]"
    networks:
      emqx-bridge:
        aliases:
          - node2.emqx.com
    # volumes:
    #   - $PWD/emqx2_data:/opt/emqx/data

networks:
  emqx-bridge:
    driver: bridge
```
**关键配置说明**：
- `EMQX_NODE_NAME`：必须使用固定FQDN或IP，避免节点名称变动导致数据丢失
- `EMQX_CLUSTER__DISCOVERY_STRATEGY=static`：使用静态节点发现策略
- `EMQX_CLUSTER__STATIC__SEEDS`：指定集群所有节点

##### 2. 启动集群
```bash
# 切换到docker-compose.yml所在目录
cd /opt/emqx-cluster

# 启动集群
docker-compose up -d

# 查看集群状态
docker exec -it emqx1 sh -c "emqx ctl cluster status"
```
成功输出应包含：`Cluster status: #{running_nodes => ['emqx@node1.emqx.com','emqx@node2.emqx.com']`

#### 配置管理要点

##### 1. 持久化配置
- **必须挂载的目录**：
  - `/opt/emqx/etc`：配置文件目录
  - `/opt/emqx/data`：运行数据存储
  - `/opt/emqx/log`：日志文件
- **权限设置**：确保宿主机目录有足够权限（推荐`chmod -R 777`）

##### 2. 管理控制台配置
- **默认登录信息**：用户名`admin`，密码`public`
- **首次登录后**：系统会要求修改密码（企业版必须修改）
- **关键配置**：
  - 监听器配置：管理端口和协议
  - 认证授权：配置客户端认证方式
  - 规则引擎：配置消息处理规则

##### 3. 环境变量配置
```bash
# 设置管理密码
-e EMQX_ADMIN_PASSWORD=admin123

# 设置节点名称（集群必需）
-e EMQX_NODE_NAME=emqx@192.168.1.10

# 设置集群发现策略
-e EMQX_CLUSTER__DISCOVERY_STRATEGY=static
```
**重要提示**：节点名称必须使用固定FQDN或IP，避免因节点名称变动导致数据丢失

