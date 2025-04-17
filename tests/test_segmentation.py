"""
分割服务测试
"""

import os
from pathlib import Path

import pytest
import numpy as np
from PIL import Image

from app.services.segmentation import SegmentationService
from app.utils.color_utils import parse_color

# 测试目录
TEST_DIR = Path(__file__).parent
TEST_IMAGE = TEST_DIR / "test_image.jpg"

# 如果测试图像不存在，创建一个简单的测试图像
if not TEST_IMAGE.exists():
    # 创建一个简单的测试图像
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img.save(TEST_IMAGE)


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_segmentation_service_initialization():
    """测试分割服务初始化"""
    service = SegmentationService()
    assert service is not None
    assert service.model_manager is not None


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_preprocess_image():
    """测试图像预处理"""
    service = SegmentationService()
    image = np.array(Image.open(TEST_IMAGE))
    preprocessed = service.preprocess_image(image)

    # 检查预处理后的形状和类型
    assert preprocessed.ndim == 4  # 批次, 通道, 高度, 宽度
    assert preprocessed.shape[0] == 1  # 批次大小
    assert preprocessed.shape[1] == 3  # RGB通道
    assert preprocessed.dtype == np.float32


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_postprocess_mask():
    """测试掩码后处理"""
    service = SegmentationService()

    # 创建一个简单的测试掩码
    mask = np.random.rand(1, 1, 64, 64).astype(np.float32)
    processed_mask = service.postprocess_mask(mask, (100, 100))

    # 检查后处理后的掩码
    assert processed_mask.shape == (100, 100)
    assert processed_mask.dtype == np.uint8
    assert processed_mask.min() >= 0
    assert processed_mask.max() <= 255


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_apply_mask():
    """测试掩码应用"""
    service = SegmentationService()

    # 加载图像和创建简单掩码
    image = Image.open(TEST_IMAGE)
    mask = Image.new('L', image.size, 128)  # 半透明掩码

    # 测试透明背景
    result1 = service.apply_mask(image, mask, None)
    assert result1.mode == "RGBA"

    # 测试自定义背景色
    bg_color = (255, 0, 0, 255)  # 红色背景
    result2 = service.apply_mask(image, mask, bg_color)
    assert result2.mode == "RGBA"


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_color_parsing():
    """测试颜色解析功能"""
    # 测试有效颜色
    color1 = parse_color("#FF0000")
    assert color1 == (255, 0, 0, 255)

    color2 = parse_color("#00FF00FF")
    assert color2 == (0, 255, 0, 255)

    color3 = parse_color("#0000FF80")
    assert color3 == (0, 0, 255, 128)

    # 测试简写形式
    color4 = parse_color("#F00")
    assert color4 == (255, 0, 0, 255)

    # 测试无效颜色
    color5 = parse_color("invalid")
    assert color5 is None