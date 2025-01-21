# DNS 查询工具

一个简单的 DNS 查询工具，支持各种 DNS 记录类型查询和 EDNS Client Subnet (ECS) 功能。完全使用大语言模型编写。

## 赞助商

感谢 [YxVM](https://yxvm.com) 为本项目提供服务器支持！

## 功能特性

- 支持多种 DNS 记录类型查询

  - A/AAAA 记录
  - CNAME 记录
  - MX 记录
  - TXT 记录
  - NS 记录
  - SOA 记录
  - PTR 记录
  - SRV 记录
  - CAA 记录等
- EDNS Client Subnet 支持

  - 自动获取本机 IP
  - 自定义 ECS 子网
  - 支持 IPv4/IPv6
- RESTful API

  - 简单易用的 API 接口
  - JSON 格式响应
  - 详细的状态信息
  - 完整的错误处理

## 快速开始

### Docker 部署

1. 拉取镜像：

```bash
docker pull ghcr.io/chenx-dust/dns-lookup:latest
```

2. 运行容器：

```bash
docker run -d -p 8000:8000 ghcr.io/chenx-dust/dns-lookup:latest
```

### 使用 docker-compose

1. 创建 docker-compose.yml：

```yaml
version: '3.8'

services:
  app:
    image: ghcr.io/chenx-dust/dns-lookup:latest
    restart: always
    ports:
      - "8000:8000"
    networks:
      - app_network

networks:
  app_network:
    driver: bridge
```

2. 启动服务：

```bash
docker-compose up -d
```

### 手动部署

1. 克隆仓库：

```bash
git clone https://github.com/chenx-dust/dns-lookup.git
cd your-repo
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 运行服务：

```bash
python app.py
```

## API 使用

### 获取客户端 IP

```bash
GET /api/ip
```

响应示例：

```json
{
    "ip": "1.2.3.4"
}
```

### DNS 查询

```bash
GET /api/resolve?name={domain}&type={record_type}&edns_client_subnet={subnet}
```

参数说明：

- name: 要查询的域名（必填）
- type: 记录类型，如 A、AAAA、CNAME 等（可选，默认为 A）
- edns_client_subnet: EDNS 客户端子网（可选）

响应示例：

```json
{
    "Status": 0,
    "TC": false,
    "RD": true,
    "RA": true,
    "AD": false,
    "CD": false,
    "Question": [
        {
            "name": "example.com",
            "type": 1
        }
    ],
    "Answer": [
        {
            "name": "example.com",
            "type": 1,
            "TTL": 300,
            "data": "93.184.216.34"
        }
    ],
    "edns_client_subnet": "1.2.3.4/24"
}
```

## 环境要求

- Python 3.8+
- FastAPI
- dnspython
- uvicorn

## 开发

1. 安装开发依赖：

```bash
pip install -r requirements.txt
```

2. 运行开发服务器：

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 生产部署建议

1. 使用反向代理（如 Nginx、Caddy）
2. 配置 HTTPS
3. 设置适当的 CORS 策略
4. 启用请求速率限制
5. 配置日志记录

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License
