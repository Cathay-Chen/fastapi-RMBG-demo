"""
图像分割服务，处理图像抠图逻辑
"""

import logging
import time
from typing import Tuple, Optional, Dict, Any, Union

import numpy as np
from PIL import Image

from app.models.model_manager import ModelManager
from app.utils.color_utils import parse_color

logger = logging.getLogger(__name__)


class SegmentationService:
    """图像分割服务，提供图像抠图功能"""

    def __init__(self):
        """初始化分割服务"""
        self.model_manager = ModelManager()

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理图像，准备模型输入

        参数:
            image: 输入图像，numpy数组形式

        返回:
            预处理后的图像
        """
        # 获取模型输入尺寸
        model_input_size = self.model_manager.get_input_size()

        # 如果图像是灰度图，添加一个维度使其成为彩色图像
        if len(image.shape) < 3:
            image = image[:, :, np.newaxis]

        # 调整图像大小以匹配模型输入尺寸
        try:
            im_resized = np.array(Image.fromarray(image).resize(model_input_size, Image.BILINEAR))
        except Exception as e:
            logger.error(f"调整图像大小时出错: {str(e)}")
            raise RuntimeError(f"调整图像大小时出错: {str(e)}")

        # 将像素值归一化到[0, 1]范围
        image_normalized = im_resized.astype(np.float32) / 255.0

        # 进一步标准化图像数据
        mean = np.array([0.5, 0.5, 0.5], dtype=np.float32)
        std = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        image_normalized = (image_normalized - mean) / std

        # 转换图像到所需形状
        image_normalized = image_normalized.transpose(2, 0, 1)  # 改变维度顺序(通道, 高度, 宽度)
        image_normalized = np.expand_dims(image_normalized, axis=0)  # 添加批处理维度

        return image_normalized

    def postprocess_mask(self, mask: np.ndarray, orig_size: Tuple[int, int]) -> np.ndarray:
        """
        后处理模型输出的掩码

        参数:
            mask: 模型输出的掩码
            orig_size: 原始图像尺寸

        返回:
            后处理的掩码，值范围[0, 255]
        """
        # 移除批次维度
        mask = np.squeeze(mask)

        # 调整掩码大小以匹配原始图像尺寸
        try:
            mask_resized = np.array(Image.fromarray(mask).resize(orig_size, Image.BILINEAR))
        except Exception as e:
            logger.error(f"调整掩码大小时出错: {str(e)}")
            raise RuntimeError(f"调整掩码大小时出错: {str(e)}")

        # 标准化掩码数据
        mask_min = mask_resized.min()
        mask_max = mask_resized.max()
        if mask_max > mask_min:
            mask_normalized = (mask_resized - mask_min) / (mask_max - mask_min)
        else:
            mask_normalized = np.zeros_like(mask_resized)

        # 转换为uint8图像
        mask_uint8 = (mask_normalized * 255).astype(np.uint8)

        return mask_uint8

    def apply_mask(self, image: Image.Image, mask: Image.Image,
                   bg_color: Optional[Tuple[int, int, int, int]] = None) -> Image.Image:
        """
        将掩码应用到图像上，生成透明背景或自定义背景色

        参数:
            image: 原始图像
            mask: 分割掩码
            bg_color: 背景颜色，None表示透明背景

        返回:
            处理后的图像
        """
        # 确保原始图像有alpha通道
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # 创建目标图像
        if bg_color is None:
            # 透明背景
            result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        else:
            # 自定义背景色
            result = Image.new("RGBA", image.size, bg_color)

        # 将前景粘贴到新背景上
        result.paste(image, mask=mask)

        return result

    def segment_image(self, image: Image.Image, bg_color_str: Optional[str] = None) -> Tuple[
        Image.Image, Dict[str, Any]]:
        """
        执行图像分割，移除背景

        参数:
            image: 输入图像
            bg_color_str: 背景颜色字符串，None表示透明背景

        返回:
            处理后的图像和性能指标
        """
        # 记录开始时间
        start_time = time.time()

        # 获取图像尺寸
        image_size = image.size

        # 处理背景颜色
        bg_color = None
        if bg_color_str:
            bg_color = parse_color(bg_color_str)

        # 转换图像为RGB并获取numpy数组
        rgb_image = image.convert("RGB")
        image_array = np.array(rgb_image)

        # 预处理图像
        preprocessed_image = self.preprocess_image(image_array)
        preprocessing_time = time.time() - start_time

        # 获取ONNX会话
        ort_session = self.model_manager.get_session()

        # 准备输入
        input_name = ort_session.get_inputs()[0].name
        ort_inputs = {input_name: preprocessed_image}

        # 执行推理
        inference_start = time.time()
        try:
            ort_outputs = ort_session.run(None, ort_inputs)
        except Exception as e:
            logger.error(f"模型推理时出错: {str(e)}")
            raise RuntimeError(f"模型推理时出错: {str(e)}")
        inference_time = time.time() - inference_start

        # 后处理掩码
        postprocess_start = time.time()
        mask_array = self.postprocess_mask(ort_outputs[0][0][0], image_size)
        mask_image = Image.fromarray(mask_array)
        postprocess_time = time.time() - postprocess_start

        # 应用掩码
        apply_mask_start = time.time()
        result_image = self.apply_mask(image, mask_image, bg_color)
        apply_mask_time = time.time() - apply_mask_start

        # 总处理时间
        total_time = time.time() - start_time

        # 返回结果和性能指标
        metrics = {
            "total_time": total_time,
            "preprocessing_time": preprocessing_time,
            "inference_time": inference_time,
            "postprocess_time": postprocess_time,
            "apply_mask_time": apply_mask_time,
            "image_size": image_size,
        }

        return result_image, metrics