"""
模型管理器，负责加载和管理ONNX模型
"""

import logging
import os
import time
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

import numpy as np
import onnxruntime as ort

from app import config

logger = logging.getLogger(__name__)


class ModelManager:
    """ONNX模型管理器"""

    _instance = None

    def __new__(cls):
        """单例模式，确保只有一个模型实例"""
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化模型管理器"""
        if self._initialized:
            return

        self.model_path = config.MODEL_PATH
        self.model_input_size = config.MODEL_INPUT_SIZE_LIST
        self.ort_session = None
        self.load_model()
        self._initialized = True

    def load_model(self) -> None:
        """加载ONNX模型"""
        try:
            # 检查模型文件是否存在
            if not Path(self.model_path).exists():
                raise FileNotFoundError(f"模型文件不存在: {self.model_path}")

            # 验证模型路径
            if not self.model_path.endswith(".onnx"):
                raise ValueError("模型文件必须是ONNX格式")

            # 记录开始时间
            start_time = time.time()
            logger.info(f"正在加载模型: {self.model_path}")

            # 配置ONNX运行时
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            # 加载模型
            self.ort_session = ort.InferenceSession(
                self.model_path,
                sess_options=session_options
            )

            # 记录完成时间
            elapsed_time = time.time() - start_time
            logger.info(f"模型加载完成，用时: {elapsed_time:.2f}秒")

        except Exception as e:
            logger.error(f"加载模型时出错: {str(e)}")
            raise RuntimeError(f"无法加载ONNX模型: {str(e)}")

    def get_session(self) -> ort.InferenceSession:
        """获取ONNX会话实例"""
        if self.ort_session is None:
            self.load_model()
        return self.ort_session

    def get_input_size(self) -> List[int]:
        """获取模型输入尺寸"""
        return self.model_input_size

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if self.ort_session is None:
            return {"status": "not_loaded"}

        try:
            # 获取模型元数据
            metadata = self.ort_session.get_modelmeta()
            inputs = self.ort_session.get_inputs()
            outputs = self.ort_session.get_outputs()

            return {
                "status": "loaded",
                "model_path": self.model_path,
                "input_size": self.model_input_size,
                "model_name": metadata.name if metadata.name else "Unknown",
                "inputs": [
                    {
                        "name": inp.name,
                        "shape": inp.shape,
                        "type": inp.type,
                    }
                    for inp in inputs
                ],
                "outputs": [
                    {
                        "name": out.name,
                        "shape": out.shape,
                        "type": out.type,
                    }
                    for out in outputs
                ],
            }
        except Exception as e:
            logger.error(f"获取模型信息时出错: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
            }