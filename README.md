# HTML修复Agent

这是一个基于DeepSeek-V3模型的HTML代码修复Agent，能够自动识别和修复HTML代码中的语法错误和结构问题。

## 功能特性

- 🔍 **自动错误检测**：识别HTML语法错误、未闭合标签、错误的标签名等
- 🛠️ **智能修复**：自动修复发现的HTML问题，保持代码格式和可读性
- 📁 **文件操作**：支持读取和修改HTML文件
- 🎯 **精确修复**：基于行号的精确修改，支持新增、修改、删除操作

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

1. 确保 `.env` 文件中设置了你的硅基流动API密钥：

```env
SILICONFLOW_API_KEY="your_api_key_here"
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

## 使用方法

### 1. 修复HTML文件

```python
from htmlagent import HTMLAgent

# 初始化Agent
agent = HTMLAgent()

# 修复HTML文件
result = agent.repair_html('input.html', 'output.html')

if result["success"]:
    print("修复成功！")
else:
    print(f"修复失败: {result['error']}")
```

### 2. 修复HTML内容字符串

```python
html_content = '''
<div class="flex items-center mb-6 p-4 bg-blue-50 rounded-lg">
    <div class="flex-shrink-0 mr-4">
        <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
    </div>
    <div>
        <h4 class="font-bold text-lg">比亚迪元PLUS 2025款</h4>
        <p class="text-blue-600 font-medium">14.58万元</p>
    </div>
</div>
'''

result = agent.repair_html_content(html_content)
if result["success"]:
    print("修复后的内容:")
    print(result["repaired_content"])
```

### 3. 运行测试

```bash
python test.py
```

### 4. 运行示例

```bash
python example.py
```

## 项目结构

```
htmlagent/
├── .env                          # 环境变量配置
├── requirements.txt              # Python依赖
├── README.md                     # 项目说明
├── cursor.md                     # 项目需求文档
├── tools.py                      # 工具函数（修改文件）
├── prompt.py                     # Agent提示词
├── htmlagent.py                  # 主要Agent实现
├── test.py                       # 测试脚本
├── example.py                    # 使用示例
├── input.html                    # 测试输入文件
└── output.html                   # 测试输出文件
```

## 架构说明

Agent采用简化的架构设计：

1. **外部读取**：HTML代码的读取在Agent外部进行，然后传递给Agent
2. **单一工具**：Agent只有一个工具 - `modify_file_tool`，用于修改文件内容
3. **行号映射**：通过行号和代码内容的字典形式传递HTML代码给Agent
4. **精确修复**：Agent分析代码后，使用工具进行精确的行级修改

## 修复示例

### 示例1：自闭合标签错误

**修复前：**
```html
<div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
```

**修复后：**
```html
<div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16"></div>
```

### 示例2：标签名错误

**修复前：**
```html
div> <!-- 此处是错误的 -->
    <h4 class="font-bold mb-2">使用成本</h4>
```

**修复后：**
```html
<div> <!-- 已修正 -->
    <h4 class="font-bold mb-2">使用成本</h4>
```

## 支持的错误类型

1. **自闭合标签错误**：`<div />` → `<div></div>`
2. **未闭合标签**：缺少对应的闭合标签
3. **错误的标签名**：`div>` → `<div>`
4. **属性语法错误**：属性值缺少引号或引号不匹配
5. **嵌套错误**：标签嵌套顺序不正确

## 注意事项

- 确保API密钥正确设置
- 网络连接正常
- 输入文件使用UTF-8编码
- 修复操作会保持原有的代码格式和缩进
- Agent只负责修复，不负责读取文件

## 许可证

MIT License 