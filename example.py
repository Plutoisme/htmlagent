#!/usr/bin/env python3
"""
HTML修复Agent使用示例
"""

from htmlagent import HTMLAgent

def main():
    """示例：修复HTML内容"""
    
    # 示例HTML内容（包含错误）
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
<div>
    <h4 class="font-bold mb-2">安全配置</h4>
    <p><span class="font-medium">主动安全：</span>ESP/胎压监测标配</p>
    <p><span class="font-medium">被动安全：</span>4安全气囊</p>
</div>
div> <!-- 此处是错误的 -->
    <h4 class="font-bold mb-2">使用成本</h4>
    <p><span class="font-medium">单次充满：</span>参数缺失</p>
    <p><span class="font-medium">百公里电费：</span>约10.32元</p>
</div>
'''
    
    print("🔍 原始HTML内容（包含错误）:")
    print(html_content)
    print("=" * 50)
    
    try:
        # 初始化Agent
        print("🔧 初始化HTMLAgent...")
        agent = HTMLAgent()
        
        # 修复HTML内容
        print("🛠️ 开始修复HTML内容...")
        result = agent.repair_html_content(html_content)
        
        if result["success"]:
            print("✅ HTML修复成功!")
            print("\n🟢 修复后的HTML内容:")
            print(result["repaired_content"])
        else:
            print("❌ HTML修复失败:")
            print(result["error"])
            
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main() 