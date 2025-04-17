"""
API端点测试
"""

import io
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)

# 测试目录
TEST_DIR = Path(__file__).parent
TEST_IMAGE = TEST_DIR / "test_image.jpg"

# 如果测试图像不存在，创建一个简单的测试图像
if not TEST_IMAGE.exists():
    # 创建一个简单的测试图像
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img.save(TEST_IMAGE)


def test_read_main():
    """测试主页端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert "RMBG 抠图服务" in response.text


def test_model_info():
    """测试模型信息端点"""
    response = client.get("/api/model-info")
    assert response.status_code == 200
    assert "status" in response.json()


def test_remove_background_bad_request():
    """测试不带图像的背景移除请求"""
    response = client.post("/api/remove-background")
    assert response.status_code == 422  # Unprocessable Entity


def test_remove_background_wrong_filetype():
    """测试错误文件类型的背景移除请求"""
    text_file = io.BytesIO(b"This is a text file, not an image")
    response = client.post(
        "/api/remove-background",
        files={"file": ("test.txt", text_file, "text/plain")},
        data={"bg_type": "transparent", "bg_color": "#00000000"},
    )
    assert response.status_code == 400
    assert "必须是图片" in response.json()["detail"]


@pytest.mark.skipif(
    not os.path.exists("models/model.onnx"),
    reason="需要模型文件才能运行此测试"
)
def test_remove_background():
    """测试背景移除功能"""
    with open(TEST_IMAGE, "rb") as f:
        image_data = f.read()

    response = client.post(
        "/api/remove-background",
        files={"file": ("test.jpg", image_data, "image/jpeg")},
        data={"bg_type": "transparent", "bg_color": "#00000000"},
    )

    assert response.status_code == 200
    assert "抠图结果" in response.text