# 泛商品推荐报告生成系统

这是一个基于多智能体协作的泛商品推荐报告生成系统，能够根据用户需求、事理图谱和产品数据，自动生成结构化的推荐报告。

## 系统架构

系统采用LangGraph框架，包含以下6个专门的Agent：

1. **数据规范化Agent** - 预处理和标准化数据
2. **需求分析Agent** - 分析用户需求，生成需求维度
3. **产品转换Agent** - 将产品数据转换为标准格式
4. **评分计算Agent** - 计算各维度评分和生成图表配置
5. **场景匹配Agent** - 生成场景分析和推荐方案
6. **报告组装Agent** - 组装最终的完整报告

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

1. 设置硅基流动API密钥：
```bash
export SILICONFLOW_API_KEY="your_api_key_here"
```

2. 或者在`.env`文件中配置：
```
SILICONFLOW_API_KEY=your_api_key_here
```

## 使用方法

### 1. 基本使用

```python
from main import ReportGenerator

async def generate_report():
    generator = ReportGenerator()
    
    result = await generator.generate_report(
        user_query="用户需求描述",
        eventic_graph="事理图谱内容",
        summary_base="产品基础数据"
    )
    
    return result

# 运行
import asyncio
result = asyncio.run(generate_report())
```

### 2. 运行示例

```bash
python main.py
```

### 3. 运行测试

```bash
python test_system.py
```

## 输入数据格式

### 用户查询 (user_query)
用户的购买需求描述，例如：
```
请为我提供一些购车建议：想买一辆新能源车，家在甘肃白银（考虑冬天气温），预算15万元...
```

### 事理图谱 (eventic_graph)
描述购买决策流程的图谱，例如：
```
# 汽车用品线上购物决策事理图谱
graph TD
A[用户需求分析] --> B[商品筛选与比较]
B --> C[决策与购买]
...
```

### 基础数据 (summary_base)
产品的基础信息，JSON格式：
```json
{
  "产品名称1": {
    "核心参数": {
      "类型": "纯电动SUV",
      "续航": "520km",
      "价格": "14.98万"
    },
    "安全配置": {...},
    "使用成本": {...}
  }
}
```

## 输出格式

系统生成完整的`reportData`结构，包含：

- **meta**: 报告元信息
- **nav**: 导航菜单
- **hero**: 主要展示区域
- **graphInsights**: 事理图谱洞察
- **decisionFactors**: 决策因素
- **products**: 产品列表
- **charts**: 图表配置
- **table**: 对比表
- **scenarios**: 场景分析
- **elimination**: 淘汰说明
- **recommendations**: 推荐方案

## 自定义配置

### Agent参数配置

在`config.py`中可以调整各个Agent的参数：

```python
AGENT_CONFIG = {
    "data_normalizer": {
        "temperature": 0.3,
        "max_tokens": 2000
    },
    # ... 其他Agent配置
}
```

### 模型配置

```python
SILICONFLOW_CONFIG = {
    "base_url": "https://api.siliconflow.cn/v1",
    "model": "deepseek-ai/DeepSeek-R1",
    "temperature": 0.7,
    "max_tokens": 4000
}
```

## 扩展开发

### 添加新的Agent

1. 在`agents/`目录下创建新的Agent类
2. 继承相应的输出模型
3. 在`main.py`中添加节点和边
4. 更新状态模型

### 自定义输出格式

1. 修改`models.py`中的数据模型
2. 更新HTML模板
3. 调整HTML渲染器

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查环境变量设置
   - 确认API密钥有效

2. **模型调用失败**
   - 检查网络连接
   - 确认API配额充足

3. **数据格式错误**
   - 检查输入数据格式
   - 查看日志输出

### 日志查看

系统会输出详细的日志信息，包括：
- Agent执行状态
- 模型调用结果
- 错误信息

## 技术特点

- **多智能体协作**: 使用LangGraph实现Agent间的协作
- **异步处理**: 支持异步执行，提高性能
- **错误处理**: 完善的错误处理和备用方案
- **模块化设计**: 易于扩展和维护
- **通用性**: 支持各种商品类型的推荐

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。 