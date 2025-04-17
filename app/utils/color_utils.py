"""
颜色处理工具
"""

import re
from typing import Optional, Tuple


def parse_color(color_str: str, with_alpha: bool = True) -> Optional[Tuple[int, int, int, int]]:
    """
    解析和验证颜色字符串

    参数:
        color_str: 十六进制颜色字符串 (例如 "#FF0000" 或 "#FF0000FF")
        with_alpha: 是否包含alpha通道

    返回:
        RGBA颜色元组，解析失败时返回None
    """
    # 如果为空，返回None
    if not color_str:
        return None

    # 去除井号前缀
    if color_str.startswith('#'):
        color_str = color_str[1:]

    # 处理简写形式 (#RGB 或 #RGBA)
    if len(color_str) == 3:
        color_str = ''.join([c * 2 for c in color_str])
    elif len(color_str) == 4:
        color_str = ''.join([c * 2 for c in color_str])

    # 验证十六进制格式
    if not re.match(r'^[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?$', color_str):
        return None

    # 转换为RGB或RGBA
    if len(color_str) == 6:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        if with_alpha:
            return (r, g, b, 255)  # 完全不透明
        else:
            return (r, g, b)
    elif len(color_str) == 8:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
        a = int(color_str[6:8], 16)
        if with_alpha:
            return (r, g, b, a)
        else:
            return (r, g, b)

    return None


def color_to_hex(color: Tuple[int, ...]) -> str:
    """
    将颜色元组转换为十六进制字符串

    参数:
        color: RGB或RGBA颜色元组

    返回:
        十六进制颜色字符串
    """
    if len(color) == 3:
        r, g, b = color
        return f"#{r:02x}{g:02x}{b:02x}"
    elif len(color) == 4:
        r, g, b, a = color
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    else:
        raise ValueError("颜色元组必须是RGB或RGBA格式")


def get_color_info(color: Optional[Tuple[int, int, int, int]]) -> str:
    """
    获取颜色信息的可读描述

    参数:
        color: RGBA颜色元组

    返回:
        颜色描述字符串
    """
    if color is None:
        return "透明"

    r, g, b, a = color
    opacity = a / 255

    if opacity < 0.01:
        return "透明"
    elif opacity < 1.0:
        return f"RGB({r}, {g}, {b}), 透明度: {opacity:.2f}"
    else:
        return f"RGB({r}, {g}, {b})"