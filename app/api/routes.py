"""
API路由
"""
import base64
import io
import logging
import binascii

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, Request
from fastapi.templating import Jinja2Templates
from PIL import Image
from starlette.responses import StreamingResponse

from app import config
from app.api.dependencies import get_segmentation_service, get_model_manager
from app.services.segmentation import SegmentationService
from app.models.model_manager import ModelManager
from app.utils.image_utils import image_to_base64, process_image

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

        # 处理图像并移除背景
        result = process_image(image, bg_type, bg_color, segmentation_service)

        # 返回结果页面
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "result_image": result["result_image"],
                "original_image": result["original_image"],
                "metrics": result["metrics"],
                "bg_color_info": result["bg_color_info"],
                "config": config
            },
        )

    except Exception as e:
        logger.error(f"处理图片时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}")

@router.post("/remove-background-base64")
async def remove_background_base64(
    bg_type: str = Form("transparent", regex="^(transparent|color)$", description="背景类型，必须是transparent或color"),
    bg_color: str = Form("#00000000"),
    image_base64: str = Form(...),
    output_type: str = Form("file", regex="^(file|base64)$", description="输入类型，必须是file或base64"),
    segmentation_service: SegmentationService = Depends(get_segmentation_service),
):
    """
    从Base64编码的图像中移除背景并返回文件

    参数:
        image_base64: Base64编码的图像
        bg_type: 背景类型 (transparent 或 color)
        bg_color: 十六进制背景颜色值 (当bg_type=color时使用)
        segmentation_service: 分割服务依赖

    返回:
        处理后的图像文件
    """
    try:
        # 验证Base64字符串是否有效
        try:
            if "base64," in image_base64:
                image_base64 = image_base64.split("base64,")[1]

            image_data = io.BytesIO(base64.b64decode(image_base64))
        except (binascii.Error, ValueError):
            raise HTTPException(status_code=400, detail="无效的Base64编码")

        # 验证解码后的数据是否为有效图片
        try:
            image = Image.open(image_data)
            image.verify()  # 验证图片完整性
            image = Image.open(image_data)  # 重新加载图片
        except Exception:
            raise HTTPException(status_code=400, detail="Base64解码后不是有效的图片")

        # 调用封装的公共方法处理图像
        result = process_image(image, bg_type, bg_color, segmentation_service)

        if output_type == "base64":
            # 将处理后的图像转换为Base64字符串
            image_base64 = image_to_base64(result["result_image"])
            return {
                "result_image": image_base64,
                "original_image": result["original_image"],
                "metrics": result["metrics"],
                "bg_color_info": result["bg_color_info"]
            }
        else:
            # 将处理后的图像转换为二进制流
            result_image = Image.open(io.BytesIO(base64.b64decode(result["result_image"])))
            image_stream = io.BytesIO()
            result_image.save(image_stream, format="PNG")
            image_stream.seek(0)

            # 返回文件响应
            return StreamingResponse(image_stream, media_type="image/png")

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"处理Base64图片时出错: {str(e)}")
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