"""
图像处理工具
"""

import base64
import io
from typing import Union, Tuple, Optional
from typing import Dict, Any
from app.services.segmentation import SegmentationService
from app.utils.color_utils import parse_color, get_color_info

from PIL import Image


def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
    """
    将PIL图像对象转换为base64编码字符串

    参数:
        img: PIL图像对象
        format: 图像格式，默认为PNG

    返回:
        base64编码的图像字符串
    """
    buffered = io.BytesIO()
    img.save(buffered, format=format)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def base64_to_image(base64_str: str) -> Optional[Image.Image]:
    """
    将base64编码字符串转换为PIL图像对象

    参数:
        base64_str: base64编码的图像字符串

    返回:
        PIL图像对象，解析失败时返回None
    """
    try:
        # 如果字符串包含data URI前缀，则移除
        if "base64," in base64_str:
            base64_str = base64_str.split("base64,")[1]

        # 解码base64字符串
        img_data = base64.b64decode(base64_str)

        # 创建PIL图像
        return Image.open(io.BytesIO(img_data))
    except Exception as e:
        return None


def resize_image_to_limit(img: Image.Image, max_size: Tuple[int, int] = (1920, 1080)) -> Image.Image:
    """
    调整图像大小，使其不超过指定的最大尺寸，但保持纵横比

    参数:
        img: PIL图像对象
        max_size: 最大尺寸(宽度, 高度)

    返回:
        调整大小后的图像
    """
    orig_width, orig_height = img.size
    max_width, max_height = max_size

    # 检查是否需要调整大小
    if orig_width <= max_width and orig_height <= max_height:
        return img

    # 计算宽高比
    ratio = min(max_width / orig_width, max_height / orig_height)

    # 计算新尺寸
    new_width = int(orig_width * ratio)
    new_height = int(orig_height * ratio)

    # 调整大小
    return img.resize((new_width, new_height), Image.LANCZOS)


def get_image_format(img: Image.Image) -> str:
    """
    获取PIL图像对象的格式

    参数:
        img: PIL图像对象

    返回:
        图像格式字符串
    """
    format = getattr(img, "format", None)
    if format:
        return format
    return "PNG"  # 默认格式

def process_image(
    image: Image.Image,
    bg_type: str,
    bg_color: str,
    segmentation_service: SegmentationService,
) -> Dict[str, Any]:
    """
    处理图像并移除背景

    参数:
        image: PIL图像对象
        bg_type: 背景类型 (transparent 或 color)
        bg_color: 十六进制背景颜色值 (当bg_type=color时使用)
        segmentation_service: 分割服务依赖

    返回:
        包含处理结果的字典
    """
    # 限制图片大小，避免过大的图片导致处理过慢
    image = resize_image_to_limit(image, (3000, 3000))

    # 处理背景颜色
    background_color = None
    if bg_type == "color":
        background_color = parse_color(bg_color)
        if background_color is None:
            raise ValueError("无效的背景颜色格式")

    # 使用服务进行抠图
    result_image, metrics = segmentation_service.segment_image(image, bg_color if bg_type == "color" else None)

    # 将图像转换为base64编码
    result_base64 = image_to_base64(result_image)
    orig_base64 = image_to_base64(image)

    # 获取背景颜色信息
    bg_color_info = get_color_info(background_color)

    return {
        "result_image": result_base64,
        "original_image": orig_base64,
        "metrics": metrics,
        "bg_color_info": bg_color_info,
    }