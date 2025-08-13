import os
import time
import sys
import json
from typing import Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from prompt import ENTIRE_PROMPT

# 加载环境变量
load_dotenv()

class SiliconFlowModel:
    def __init__(self):
        """初始化硅基流动模型客户端"""
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        
        if not self.api_key:
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def generate_html_report(self, prompt: str) -> Dict[str, Any]:
        """
        调用硅基流动模型生成HTML报告
        
        Args:
            prompt: 用户提示词
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        try:
            print("🤖 开始调用硅基流动模型...")
            start_time = time.time()
            
            # 根据图片中的参数配置
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-ai/DeepSeek-R1",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.6,
                    max_tokens=52509,  # 根据图片中的配置
                    top_p=0.95,
                    # top_k=50,
                    frequency_penalty=0.0,
                    thinking_budget=17996  # 根据图片中的配置
                )
            except Exception as e:
                # 如果thinking_budget参数不被支持，尝试不使用该参数
                if "thinking_budget" in str(e):
                    print("⚠️ thinking_budget参数不被支持，将使用默认值")
                    response = self.client.chat.completions.create(
                        model="deepseek-ai/DeepSeek-R1",
                        messages=[
                            {
                                "role": "user",
                                "content": "写一篇800字左右的作文，命题为我的父亲"
                            }
                        ],
                        temperature=0.6,
                        max_tokens=52509,
                        top_p=0.95,
                        # top_k=50,
                        frequency_penalty=0.0
                    )
                else:
                    raise e
            
            # 结束计时
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"🤖 模型调用完成，耗时: {elapsed_time:.2f}秒")
            
            # 获取响应内容
            content = response.choices[0].message.content
            
            return {
                "success": True,
                "html_content": content,
                "model_call_time": elapsed_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"模型调用失败: {str(e)}"
            }

def main():
    """主函数：调用模型5次并保存HTML报告"""
    try:
        # 初始化模型
        model = SiliconFlowModel()
        
        # 获取当前脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 确保report_generate目录存在（相对于脚本目录）
        os.makedirs(script_dir, exist_ok=True)
        
        print("🚀 开始生成HTML报告...")
        print(f"📝 使用提示词长度: {len(ENTIRE_PROMPT)} 字符")
        
        # 调用模型5次
        for i in range(1, 6):
            print(f"\n📊 正在生成第 {i} 份报告...")
            
            # 调用模型
            result = model.generate_html_report(ENTIRE_PROMPT)
            
            if result["success"]:
                # 生成文件名
                timestamp = int(time.time())
                filename = f"report_{i}_{timestamp}.html"
                filepath = os.path.join(script_dir, filename)
                
                # 保存HTML内容
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result["html_content"])
                
                print(f"✅ 第 {i} 份报告已保存: {filename}")
                print(f"⏱️  生成耗时: {result['model_call_time']:.2f}秒")
                print(f"📄 文件大小: {len(result['html_content'])} 字符")
                
            else:
                print(f"❌ 第 {i} 份报告生成失败: {result['error']}")
            
            # 在每次调用之间稍作停顿，避免过于频繁的API调用
            if i < 5:
                print("⏳ 等待3秒后继续...")
                time.sleep(3)
        
        print(f"\n🎉 所有报告生成完成！共生成 {5} 份HTML报告")
        print(f"📁 报告保存在: {script_dir}")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}")

if __name__ == "__main__":
    main()
