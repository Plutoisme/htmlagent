## HTML 修复Agent
本项目提供一个修复HTML代码的Agent。

## 修复示例：

### Case 1
错误的html代码片段如下：
```html
<!-- 错误的代码片段 -->
<div class="flex items-center mb-6 p-4 bg-blue-50 rounded-lg">
    <div class="flex-shrink-0 mr-4">
        <!-- 问题就在这一行 -->
        <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16" />
    </div>
    <div>
        <h4 class="font-bold text-lg">比亚迪元PLUS 2025款</h4>
        <p class="text-blue-600 font-medium">14.58万元</p>
    </div>
</div>
```

修复过后：
```html
<!-- 正确的代码片段 -->
<div class="flex items-center mb-6 p-4 bg-blue-50 rounded-lg">
    <div class="flex-shrink-0 mr-4">
        <!-- 已修正 -->
        <div class="bg-gray-200 border-2 border-dashed rounded-xl w-16 h-16"></div>
    </div>
    <div>
        <h4 class="font-bold text-lg">比亚迪元PLUS 2025款</h4>
        <p class="text-blue-600 font-medium">14.58万元</p>
    </div>
</div>
```

### Case 2
错误的代码片段如下：
```html
<!-- ... -->
<div>
    <h4 class="font-bold mb-2">安全配置</h4>
    <p><span class="font-medium">主动安全：</span>ESP/胎压监测标配</p>
    <p><span class="font-medium">被动安全：</span>4安全气囊</p>
</div>
div> <!-- 此处是错误的 -->
    <h4 class="font-bold mb-2">使用成本</h4>
    <p><span class="font-medium">单次充满：</span>参数缺失</p>
    <p><span class="font-medium">百公里电费：</span>约10.32元</p>
    <p><span class="font-medium">口碑：</span>冬季开空调约300km（30%衰减）</p>
</div>
<!-- ... -->
```

修复后的代码片段：
```html
<!-- ... -->
<div>
    <h4 class="font-bold mb-2">安全配置</h4>
    <p><span class="font-medium">主动安全：</span>ESP/胎压监测标配</p>
    <p><span class="font-medium">被动安全：</span>4安全气囊</p>
</div>
<div> <!-- 已修正 -->
    <h4 class="font-bold mb-2">使用成本</h4>
    <p><span class="font-medium">单次充满：</span>参数缺失</p>
    <p><span class="font-medium">百公里电费：</span>约10.32元</p>
    <p><span class="font-medium">口碑：</span>冬季开空调约300km（30%衰减）</p>
</div>
<!-- ... -->
```

## Agent 实现
通过Langchain调用硅基流动的DeepSeekR1构建Agent，Agent需要配置两个工具(读取文件和修改文件)。  
API_KEY为
硅基流动基于OpenAI规范调用DeepSeekR1的官方代码如下：
```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY_FROM_CLOUD_SILICONFLOW_CN", 
                base_url="https://api.siliconflow.cn/v1")
response = client.chat.completions.create(
    model='Pro/deepseek-ai/DeepSeek-V3',
    messages=[
        {'role': 'user', 
        'content': "推理模型会给市场带来哪些新的机会"}
    ],
    stream=True
)

for chunk in response:
    if not chunk.choices:
        continue
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
    if chunk.choices[0].delta.reasoning_content:
        print(chunk.choices[0].delta.reasoning_content, end="", flush=True)
```

### 工具: 修改代码


### 你的编写架构：
1. 先写读取文件和修改文件的工具函数。
我们会在调用大模型外部进行html代码文件读取，代码会存放成一个字典:{"line": code} 表明行号和代码对应的关系。
大模型的修改工具接口也设计成:{"line": modified_code}的形式。 通过这种设计可以减少修改/新增/删除之间的冲突。
举例: 如果删除第i行，模型调用工具时直接给出两个参数"i" 和 ""即可。
新增的话，你自己想想办法吧。。。 在工具函数里面处理这种情况， 大模型应该聚焦于html逻辑以及语法本身。

2. 编写Agent的Prompt，写入prompt.py文件中。 Prompt中强调模型如何使用工具，解决html代码错误的逻辑。

3. 在htmlagent.py文件中编写该HTMLAgent代码，实现工具注入。

4. 在test.py中实现测试样例，实现对input.html的修改，输出到output.html中。

