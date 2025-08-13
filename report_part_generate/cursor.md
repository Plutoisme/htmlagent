## 分章节代码生成Agent
该项目想构造一个能稳定生成高质量泛商品推荐建议报告的Agent，想要通过若干个Agent从同一个模板中生成不同章节来实现。
模板html代码在./template.html。

本项目意图构建若干个part将数据带有逻辑性地填入html 模版。
以下是一些实现思路:
> 1. 用户原始查询 - 关于购买新能源车的需求
> 2. 事理图谱 - 汽车用品线上购物决策流程
> 3. 知识库 - 6款车型的详细参数和评价

需要注意的细节
> - 产品数据被多个部分引用（图表、对比表、推荐等）
> - 导航需要对应实际渲染的section
> - 图表的metricKey需要对应产品的attributes
> - 推荐的productId需要对应产品列表中的id
> 
> 从逻辑上看，可以按照以下方式拆分：
> 
> 1. **数据预处理Agent** - 将原始数据转换为reportData结构
> 2. **元信息和导航Agent** - 生成meta、nav、hero等顶层配置
> 3. **需求分析Agent** - 生成graphInsights和decisionFactors
> 4. **产品数据Agent** - 将车型数据转换为products数组
> 5. **可视化Agent** - 生成charts配置
> 6. **对比表Agent** - 生成table配置
> 7. **场景和推荐Agent** - 生成scenarios、elimination、recommendations
> 
> 每个agent需要：
> - 输入：用户query、事理图谱、知识库、前面agent的输出
> 
> 
> - 输出：reportData的特定部分
> - 约束：确保引用的id一致、数据格式符合模板要求

## Agent架构设计

### 1. **数据规范化Agent** (Data Normalizer)
**职责**：预处理和标准化数据
- 将知识库中的车型数据转换为统一格式
- 生成唯一的产品ID（如 `byd-song-plus-ev`）
- 提取共同属性维度，建立属性映射表

**输出示例**：
```javascript
{
  productIdMap: {
    "byd-song-plus-ev": "比亚迪宋PLUS EV 2025款",
    "byd-yuan-plus": "比亚迪元PLUS 2025款",
    // ...
  },
  commonAttributes: ["续航里程", "离地间隙", "充电时间", "安全配置", "价格"],
  // ...
}
```

### 2. **需求分析Agent** (Requirement Analyzer)
**职责**：分析用户query，生成需求维度
- 解析用户需求（预算、使用场景、功能偏好等）
- 基于事理图谱生成需求维度和决策因素
- 生成 `graphInsights` 和 `decisionFactors`

**输出示例**：
```javascript
{
  graphInsights: {
    dimensions: [
      { icon: "fa-snowflake", title: "低温适应性", description: "甘肃白银冬季低温，需要考虑电池低温性能和续航衰减" },
      { icon: "fa-road", title: "通过性要求", description: "4公里非铺装路面，需要较高离地间隙和ESP等安全配置" },
      // ...
    ]
  },
  decisionFactors: [
    { icon: "fa-battery-full", title: "冬季续航", description: "CLTC续航×低温衰减率，确保单程100km通勤" },
    // ...
  ]
}
```

### 3. **产品转换Agent** (Product Transformer)
**职责**：将车型数据转换为模板所需的products格式
- 提取核心参数作为attributes
- 计算使用成本
- 整理优缺点和标签

**输出示例**：
```javascript
{
  products: [
    {
      id: "byd-yuan-plus",
      name: "比亚迪元PLUS 智驾版",
      price: 145800,
      currency: "CNY",
      type: "纯电动SUV",
      tags: ["热泵空调", "7安全气囊", "L2辅助驾驶"],
      attributes: {
        "CLTC续航": 510,
        "冬季续航(实测)": 357,
        "离地间隙": 161.5,
        "充电时间(30-80%)": 30,
        "百公里电费": 10
      },
      // ...
    }
  ]
}
```

### 4. **评分计算Agent** (Scoring Calculator)
**职责**：计算各维度评分和排序
- 基于用户需求权重计算综合得分
- 生成图表数据配置
- 确定推荐等级

**输出示例**：
```javascript
{
  charts: [
    {
      id: "winter-range-chart",
      title: "冬季续航对比",
      type: "bar",
      metricKey: "冬季续航(实测)",
      unit: "km",
      suggestedMax: 400
    }
  ],
  scoringResults: {
    "byd-yuan-plus": { total: 88, winterScore: 90, safetyScore: 95 },
    // ...
  }
}
```

### 5. **场景匹配Agent** (Scenario Matcher)
**职责**：生成场景分析和推荐方案
- 基于评分结果生成推荐
- 匹配使用场景
- 生成淘汰说明

**输出示例**：
```javascript
{
  scenarios: [
    {
      icon: "fa-mountain",
      title: "非铺装路面通过性",
      bullets: [
        "比亚迪宋PLUS EV离地间隙166mm，接近角19°，满足需求",
        "创维EV6满载离地间隙仅159mm，通过性受限"
      ]
    }
  ],
  recommendations: [
    {
      title: "最佳选择",
      badge: { text: "推荐", tone: "primary", icon: "fa-crown" },
      productId: "byd-yuan-plus",
      fit: "冬季续航优秀，安全配置完善",
      reasons: ["热泵空调+直冷直热技术，-15℃续航达成率71.5%", "7安全气囊，同级最高"],
      tradeoffs: ["悬架偏舒适，非铺装路面滤震一般"]
    }
  ]
}
```

### 6. **报告组装Agent** (Report Assembler)
**职责**：组装最终的reportData
- 合并所有Agent的输出
- 生成导航和元信息
- 确保数据一致性（ID引用、属性名等）

## Agent协作流程

```
用户Query + 事理图谱 + 知识库
           ↓
    数据规范化Agent
           ↓
    需求分析Agent ←─────┐
           ↓            │
    产品转换Agent       │ 
           ↓            │ 数据流
    评分计算Agent       │
           ↓            │
    场景匹配Agent ──────┘
           ↓
    报告组装Agent
           ↓
      reportData
```

## 关键设计原则

1. **数据一致性**：使用统一的产品ID系统，确保跨模块引用正确
2. **属性标准化**：建立属性名映射表，避免硬编码
3. **渐进式生成**：每个Agent基于前面的输出继续构建
4. **验证机制**：每个Agent输出后验证数据完整性
5. **配置驱动**：通过配置文件控制各Agent的行为参数

这种设计既保证了各部分的独立性，又通过标准化的数据接口实现了必要的耦合。

生成报告需要用到的QUERY(用户需求), EVENTIC_GRAPH(事理图谱), SUMMARY_BASE(基本数据)示例在constant.py中。
最后达到的效果我希望像target.html那样。


## 技术实现细节：
1. 使用langgraph搭建多智能体Agent， 采用合适的State控制图中数据状态。
2. 实现所有章节agent并行执行任务。
3. 模型使用硅基流动的模型，参考以下官方给出的示例：https://docs.siliconflow.cn/cn/userguide/quickstart
4. 模型名为Pro/deepseek-ai/DeepSeek-R1
5. 时刻牢记我们做的是泛商品推荐报告生成，因此你在设计Agent提示词时尽可能少使用特定商品名/属性，不然会导致模型过拟合。
6. constant.py中只给出了示例输入，实际输入可能是多变的，各种各样的。