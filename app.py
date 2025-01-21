from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from uvicorn.protocols.utils import get_remote_addr, get_client_addr
from pydantic import BaseModel
import socket
import requests
from typing import Optional
import os

# 创建主应用和 API 子应用
app = FastAPI()
api_app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加可信主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # 在生产环境中应该设置具体的域名
)

# 添加代理头中间件
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 添加 PROXY Protocol 支持的中间件
@app.middleware("http")
async def proxy_protocol_middleware(request: Request, call_next):
    # 尝试从 PROXY Protocol 获取客户端信息
    client = request.scope.get("client")
    if client:
        request.scope["client"] = client
    
    response = await call_next(request)
    return response

def get_client_ip(request: Request = None):
    try:
        if request:
            # 尝试从各种头部获取真实 IP
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
            
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
            
            # 从代理协议中获取
            client = request.scope.get("client")
            if client:
                return client[0]

        # 如果上述方法都失败，则获取本机 IP
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception as e:
        return str(e)

@api_app.get("/ip")
async def get_ip(request: Request):
    ip = get_client_ip(request)
    return {"ip": ip}

@api_app.get("/resolve")
async def resolve_dns(name: str, type: str = "A", edns_client_subnet: str = None):
    try:
        # 构建 Google DNS-over-HTTPS 请求
        url = "https://dns.google/resolve"
        params = {
            "name": name,
            "type": type,
            "edns_client_subnet": edns_client_subnet
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 挂载 API 子应用和静态文件
app.mount("/api", api_app)
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
app.mount("/", StaticFiles(directory=current_dir, html=True), name="root")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips="*"
    ) 