# HTML报告生成管道

这个目录包含了用于生成HTML购物决策报告的自动化管道。

## 文件说明

- `generate_pipeline.py`: 主要的生成脚本，调用硅基流动模型生成HTML报告
- `prompt.py`: 包含完整的提示词模板
- `README.md`: 本说明文件

## 使用方法

### 1. 环境准备

确保已安装所需依赖：
```bash
pip install -r ../requirements.txt
```

### 2. 环境变量配置

在项目根目录的 `.env` 文件中配置：
```
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

### 3. 运行生成脚本

```bash
cd report_generate
python generate_pipeline.py
```

## 功能说明

- **模型调用**: 使用硅基流动模型的 Pro/deepseek-ai/DeepSeek-R1 模型（流式输出）
- **模型配置**: 
  - Temperature: 0.6
  - Max Tokens: 52509
  - Top-P: 0.95
  - Frequency Penalty: 0.0
  - Thinking Budget: 17996（如果API支持）
- **输出方式**: 流式输出，实时显示生成内容
- **生成次数**: 自动调用模型5次，生成5份不同的HTML报告
- **文件命名**: 报告文件按 `report_{序号}_{时间戳}.html` 格式命名
- **保存位置**: 所有生成的HTML文件保存在 `report_generate` 目录中
- **错误处理**: 包含完整的错误处理和日志输出

## 输出示例

运行成功后，会在 `report_generate` 目录中生成类似以下文件：
```
report_1_1703123456.html
report_2_1703123460.html
report_3_1703123464.html
report_4_1703123468.html
report_5_1703123472.html
```

## 注意事项

1. 确保网络连接正常，能够访问硅基流动API
2. 每次调用之间有3秒间隔，避免过于频繁的API调用
3. 生成的HTML报告包含完整的购物决策分析内容
4. 如果某次调用失败，程序会继续执行后续调用 