"""
API响应模型
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """错误响应模型"""
    detail: str

class SegmentationResult(BaseModel):
    """分割结果模型"""
    image_base64: str = Field(..., description="Base64编码的处理后图像")
    metrics: Dict[str, Any] = Field(..., description="处理性能指标")
    bg_color_info: str = Field(..., description="背景颜色信息")

class ModelInfo(BaseModel):
    """模型信息模型"""
    status: str = Field(..., description="模型状态")
    model_path: Optional[str] = Field(None, description="模型路径")
    input_size: Optional[List[int]] = Field(None, description="输入尺寸")
    model_name: Optional[str] = Field(None, description="模型名称")
    inputs: Optional[List[Dict[str, Any]]] = Field(None, description="输入信息")
    outputs: Optional[List[Dict[str, Any]]] = Field(None, description="输出信息")
    error: Optional[str] = Field(None, description="错误信息")