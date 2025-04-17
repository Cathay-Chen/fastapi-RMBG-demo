"""
FastAPI应用主入口点
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.cors import CORSMiddleware

from app import config
from app.api.routes import router as api_router

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 生命周期事件处理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Debug mode: {config.DEBUG}")
    logger.info(f"Model path: {config.MODEL_PATH}")

    yield  # 应用运行期间

    # 关闭事件
    logger.info(f"Shutting down {config.APP_NAME}")

# 创建FastAPI应用
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    debug=config.DEBUG,
    lifespan=lifespan,  # 注册生命周期管理器
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")

# 设置模板
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# 包含API路由
app.include_router(api_router)

# 根路由
@app.get("/")
async def root(request: Request):
    """根路由，返回首页模板"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "config": config  # 传递配置对象给模板
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )