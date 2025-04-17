# 模型目录

此目录用于存放ONNX模型文件。

## 模型说明

将下载的RMBG ONNX模型文件放在此目录下，并命名为`model.onnx`（或者在`.env`文件中更新`MODEL_PATH`）。

## 模型获取

您可以从以下途径获取RMBG ONNX模型：

1. 从Hugging Face下载：
   - [RMBG-1.4 ONNX 模型](https://huggingface.co/briaai/RMBG-1.4/tree/main)
   - [RMBG-2.0 ONNX 模型](https://huggingface.co/briaai/RMBG-2.0/tree/main)
   - 下载 .onnx 格式的模型文件

2. 从官方仓库获取：
   - 如果有官方仓库，请访问其发布页面下载模型

## 注意事项

- 模型文件较大，通常不会包含在Git仓库中
- 如果您的模型文件名不是`model.onnx`，请更新`.env`文件中的`MODEL_PATH`设置
- 确保模型与代码中的预处理和后处理步骤兼容