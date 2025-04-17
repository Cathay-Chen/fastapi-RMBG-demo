"""
API路由
"""

import io
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from fastapi.templating import Jinja2Templates
from PIL import Image

from app import config
from app.api.dependencies import get_segmentation_service, get_model_manager
from app.services.segmentation import SegmentationService
from app.models.model_manager import ModelManager
from app.utils.color_utils import get_color_info, parse_color
from app.utils.image_utils import image_to_base64, resize_image_to_limit

# 配置日志
logger = logging.getLogger(__name__)

# 设置模板
templates = Jinja2Templates(directory=config.TEMPLATES_DIR)

# 创建路由器
router = APIRouter(prefix="/api", tags=["api"])

@router.post("/remove-background")
async def remove_background(
    request: Request,  # 添加请求参数
    file: UploadFile = File(...),
    bg_type: str = Form("transparent"),
    bg_color: str = Form("#00000000"),
    segmentation_service: SegmentationService = Depends(get_segmentation_service),
):
    """
    从图像中移除背景

    参数:
        file: 上传的图像文件
        bg_type: 背景类型 (transparent 或 color)
        bg_color: 十六进制背景颜色值 (当bg_type=color时使用)
        segmentation_service: 分割服务依赖

    返回:
        结果页面的HTML响应
    """
    # 检查文件是否为图片
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="上传的文件必须是图片")

    try:
        # 读取上传的图片
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # 限制图片大小，避免过大的图片导致处理过慢
        image = resize_image_to_limit(image, (3000, 3000))

        # 处理背景颜色
        background_color = None
        if bg_type == "color":
            background_color = parse_color(bg_color)
            if background_color is None:
                raise HTTPException(status_code=400, detail="无效的背景颜色格式")

        # 使用服务进行抠图
        result_image, metrics = segmentation_service.segment_image(image, bg_color if bg_type == "color" else None)

        # 将图像转换为base64编码
        result_base64 = image_to_base64(result_image)
        orig_base64 = image_to_base64(image)

        # 获取背景颜色信息
        bg_color_info = get_color_info(background_color)

        # 返回结果页面
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result_image": result_base64,
                "original_image": orig_base64,
                "metrics": metrics,
                "bg_color_info": bg_color_info,
                "config": config
            },
        )

    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}")

@router.get("/model-info")
async def get_model_info(model_manager: ModelManager = Depends(get_model_manager)):
    """
    获取模型信息

    参数:
        model_manager: 模型管理器依赖

    返回:
        模型信息
    """
    return model_manager.get_model_info()