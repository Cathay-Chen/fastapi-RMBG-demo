"""
API依赖项，用于FastAPI依赖注入
"""

from fastapi import Depends, HTTPException, status
from app.services.segmentation import SegmentationService
from app.models.model_manager import ModelManager

def get_segmentation_service() -> SegmentationService:
    """提供分割服务的依赖项"""
    try:
        return SegmentationService()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"分割服务不可用: {str(e)}",
        )

def get_model_manager() -> ModelManager:
    """提供模型管理器的依赖项"""
    try:
        return ModelManager()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"模型管理器不可用: {str(e)}",
        )