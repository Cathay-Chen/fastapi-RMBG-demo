# RMBG 模型抠图服务 API

这是一个基于FastAPI和ONNX的图像抠图服务，使用RMBG模型进行背景移除。

## 功能特点

- 自动移除图像背景
- 支持透明背景或自定义颜色背景
- 支持调整背景透明度
- RESTful API接口
- 简洁的Web界面

## 安装与使用

### 前提条件

- Python 3.8+
- [RMBG-1.4 ONNX 模型](https://huggingface.co/briaai/RMBG-1.4)
- [RMBG-2.0 ONNX 模型](https://huggingface.co/briaai/RMBG-2.0)

### 使用pip安装

```bash
# 克隆代码库
git clone https://github.com/yourusername/rmbg-api.git
cd rmbg-api

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 下载模型
# 将.onnx模型文件放到models/目录下

# 运行应用
uvicorn app.main:app --reload
```

### 使用Docker Compose启动服务
docker-compose up -d