"""
应用配置模块，处理环境变量和配置设置
"""

import os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 定义项目根目录
# 当前文件是 app/config.py，所以需要往上两级才是项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 打印调试信息
print(f"配置中的BASE_DIR: {BASE_DIR}")
print(f"models目录路径: {BASE_DIR / 'models'}")
print(f"models目录是否存在: {(BASE_DIR / 'models').exists()}")
print(f"模型文件路径: {BASE_DIR / 'models' / 'model.onnx'}")
print(f"模型文件是否存在: {(BASE_DIR / 'models' / 'model.onnx').exists()}")

# 应用设置
APP_NAME = os.getenv("APP_NAME", "RMBG 抠图服务演示")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
RMBG_VERSION = os.getenv("RMBG_VERSION", "1.4")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# 服务器设置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 模型设置
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "model.onnx"))

# 如果是相对路径，转换为绝对路径
if not os.path.isabs(MODEL_PATH):
    MODEL_PATH = os.path.abspath(os.path.join(str(BASE_DIR), MODEL_PATH))

print(f"最终使用的MODEL_PATH: {MODEL_PATH}")

MODEL_INPUT_SIZE = os.getenv("MODEL_INPUT_SIZE", "1024,1024")
MODEL_INPUT_SIZE_LIST = [
    int(size) for size in MODEL_INPUT_SIZE.split(",") if size.strip().isdigit()
]
if len(MODEL_INPUT_SIZE_LIST) != 2:
    MODEL_INPUT_SIZE_LIST = [1024, 1024]  # 默认值

# 模板目录
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

# 静态文件目录
STATIC_DIR = BASE_DIR / "static"

# 日志设置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")