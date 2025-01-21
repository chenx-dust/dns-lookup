from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
import dns.resolver
import dns.rdatatype
import socket
import requests
from typing import Optional
import os

app = FastAPI()

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

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 挂载静态文件
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
app.mount("/", StaticFiles(directory=current_dir, html=True), name="root")

class DNSResponse(BaseModel):
    Status: int = 0
    TC: bool = False
    RD: bool = True
    RA: bool = True
    AD: bool = False
    CD: bool = False
    Question: list = []
    Answer: Optional[list] = None
    Authority: Optional[list] = None
    Comment: Optional[str] = None
    edns_client_subnet: Optional[str] = None

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

@app.get("/ip")
async def get_ip(request: Request):
    ip = get_client_ip(request)
    return {"ip": ip}

@app.get("/resolve")
async def resolve_dns(name: str, type: str = "A", edns_client_subnet: str = None):
    try:
        # 创建解析器
        resolver = dns.resolver.Resolver()
        
        # 设置 Google DNS 服务器作为上游服务器
        resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        
        # 获取记录类型
        try:
            if type == "255" or type == "ALL":
                rdtype = "ANY"
            else:
                rdtype = type
            rdtype = dns.rdatatype.from_text(rdtype)
        except Exception:
            raise HTTPException(status_code=400, detail=f"Invalid record type: {type}")

        # 执行查询
        try:
            answers = resolver.resolve(name, rdtype)
        except dns.resolver.NXDOMAIN:
            return DNSResponse(
                Status=3,
                Question=[{"name": name, "type": rdtype}],
                Comment="Domain does not exist"
            )
        except dns.resolver.NoAnswer:
            return DNSResponse(
                Status=0,
                Question=[{"name": name, "type": rdtype}],
                Comment="No records found"
            )
        except Exception as e:
            return DNSResponse(
                Status=2,
                Question=[{"name": name, "type": rdtype}],
                Comment=str(e)
            )

        # 构建响应
        response = DNSResponse(
            Question=[{
                "name": name,
                "type": rdtype
            }]
        )

        # 添加应答记录
        response.Answer = []
        for rdata in answers:
            response.Answer.append({
                "name": name,
                "type": rdtype,
                "TTL": answers.ttl,
                "data": str(rdata)
            })

        # 如果提供了 ECS，添加到响应中
        if edns_client_subnet:
            response.edns_client_subnet = edns_client_subnet

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        proxy_headers=True,
        forwarded_allow_ips="*",
        proxy_protocol=True
    ) 