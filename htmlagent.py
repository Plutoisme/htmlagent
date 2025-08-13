import logging
import os
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from diff_tools import DiffTools
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('html_repair.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HTMLAgent:
    def __init__(self, api_key: Optional[str] = None):
        logger.info("🚀 初始化HTML修复Agent...")
        
        # 初始化diff工具（用于外部workflow）
        self.diff_tools = DiffTools()
        logger.info("✅ Diff工具初始化完成")
        
        # 设置OpenAI API
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        elif os.getenv("SILICONFLOW_API_KEY"):
            # 使用硅基流动的API密钥
            os.environ["OPENAI_API_KEY"] = os.getenv("SILICONFLOW_API_KEY")
            os.environ["OPENAI_API_BASE"] = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
            logger.info(f"✅ 使用硅基流动API: {os.getenv('OPENAI_API_BASE')}")
        else:
            logger.error("❌ 未找到API密钥配置")
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model="Pro/deepseek-ai/DeepSeek-V3",
            temperature=0.6,
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        logger.info("✅ LLM初始化完成")
        
        # 设置prompt
        from prompt import HTML_REPAIR_PROMPT
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", HTML_REPAIR_PROMPT),
            ("human", "{input}")
        ])
        logger.info("✅ Prompt模板设置完成")
        logger.info("🎉 HTML修复Agent初始化完成！")

    def analyze_html_errors(self, html_content: str) -> Dict[str, Any]:
        """分析HTML内容中的错误，返回JSON格式的错误信息"""
        logger.info("🔄 开始HTML错误分析...")
        logger.info(f"   内容长度: {len(html_content)} 字符")
        
        try:
            # 构建分析提示
            prompt = f"""
            请分析以下HTML代码中的所有错误，并输出JSON格式的结果：
            
            {html_content}
            
            请仔细检查整个HTML文件，找出所有语法错误、结构错误等，不要只找到第一个就停止。
            严格按照JSON格式输出，不要包含其他文本。
            """
            
            # 调用LLM进行分析
            logger.info("🤖 调用大模型进行HTML错误分析...")
            response = self.llm.invoke(prompt)
            logger.info("✅ 大模型分析完成")
            
            # 提取响应内容
            content = response.content
            logger.info(f"📝 原始响应: {content[:200]}...")
            
            # 尝试解析JSON
            try:
                # 查找JSON内容
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_content = content[json_start:json_end]
                    logger.info(f"🔍 提取的JSON内容: {json_content[:200]}...")
                    
                    # 尝试修复常见的JSON问题
                    try:
                        # 直接解析
                        errors_data = json.loads(json_content)
                    except json.JSONDecodeError:
                        # 如果解析失败，尝试修复常见的截断问题
                        logger.warning("⚠️ JSON解析失败，尝试修复截断问题...")
                        
                        # 查找最后一个完整的错误对象
                        last_complete_error = json_content.rfind('},')
                        if last_complete_error != -1:
                            # 截取到最后一个完整的错误对象
                            fixed_json = json_content[:last_complete_error + 1] + ']}'
                            logger.info(f"🔧 修复后的JSON: {fixed_json[:200]}...")
                            
                            try:
                                errors_data = json.loads(fixed_json)
                            except json.JSONDecodeError:
                                # 如果还是失败，尝试更激进的修复
                                logger.warning("⚠️ 修复后JSON仍解析失败，尝试更激进的修复...")
                                
                                # 查找最后一个完整的错误对象（更宽松的匹配）
                                last_complete = json_content.rfind('"type":')
                                if last_complete != -1:
                                    # 找到最后一个错误对象的开始
                                    start_pos = json_content.rfind('{', 0, last_complete)
                                    if start_pos != -1:
                                        # 构造一个最小的有效JSON
                                        minimal_json = '{"errors": []}'
                                        logger.warning("⚠️ 使用最小JSON结构")
                                        errors_data = json.loads(minimal_json)
                                    else:
                                        raise ValueError("无法找到有效的JSON结构")
                                else:
                                    raise ValueError("无法找到有效的JSON结构")
                        else:
                            raise ValueError("无法找到完整的错误对象")
                    
                    # 检查不同的JSON结构
                    if "errors" in errors_data:
                        total_errors = len(errors_data["errors"])
                        logger.info(f"✅ JSON解析成功，发现 {total_errors} 个错误")
                    elif "errors_found" in errors_data:
                        total_errors = errors_data.get("total_errors", len(errors_data["errors_found"]))
                        logger.info(f"✅ JSON解析成功，发现 {total_errors} 个错误")
                    else:
                        total_errors = 0
                        logger.warning("⚠️ JSON结构不明确，未找到错误列表")
                    
                    return {
                        "success": True,
                        "errors_data": errors_data,
                        "raw_response": content,
                        "total_errors": total_errors
                    }
                else:
                    logger.error("❌ 响应中未找到JSON内容")
                    return {
                        "success": False,
                        "error": "响应中未找到JSON内容",
                        "raw_response": content
                    }
                    
            except Exception as e:
                logger.error(f"❌ JSON解析失败: {str(e)}")
                return {
                    "success": False,
                    "error": f"JSON解析失败: {str(e)}",
                    "raw_response": content
                }
                
        except Exception as e:
            logger.error(f"❌ HTML错误分析过程中发生错误: {str(e)}")
            return {
                "success": False,
                "error": f"HTML错误分析失败: {str(e)}"
            }

def repair_html_workflow(input_file: str, output_file: str) -> Dict[str, Any]:
    """外部workflow：使用HTMLAgent分析错误，然后生成和应用diff"""
    logger.info(f"🔄 开始HTML修复workflow...")
    logger.info(f"   输入文件: {input_file}")
    logger.info(f"   输出文件: {output_file}")
    
    try:
        # 初始化Agent
        agent = HTMLAgent()
        
        # 读取输入文件
        logger.info("📖 读取输入文件...")
        with open(input_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        logger.info(f"✅ 文件读取成功，内容长度: {len(original_content)} 字符")
        
        # 第一步：使用Agent分析错误
        logger.info("🔍 第一步：使用Agent分析HTML错误...")
        analysis_result = agent.analyze_html_errors(original_content)
        
        if not analysis_result["success"]:
            logger.error(f"❌ HTML错误分析失败: {analysis_result.get('error')}")
            return analysis_result
        
        errors_data = analysis_result["errors_data"]
        total_errors = analysis_result["total_errors"]
        logger.info(f"✅ 错误分析完成，发现 {total_errors} 个错误")
        
        # 第二步：为每个错误生成diff补丁...
        logger.info("🔄 第二步：为每个错误生成diff补丁...")
        all_diffs = []
        
        # 获取错误列表，支持不同的JSON结构
        errors_list = []
        if "errors" in errors_data:
            errors_list = errors_data["errors"]
        elif "errors_found" in errors_data:
            errors_list = errors_data["errors_found"]
        else:
            logger.error("❌ 未找到错误列表")
            return {
                "success": False,
                "error": "未找到错误列表",
                "input_file": input_file,
                "output_file": output_file
            }
        
        for i, error in enumerate(errors_list):
            logger.info(f"   处理错误 {i+1}/{total_errors}: {error.get('description', '未知错误')}")
            
            # 获取原始内容和修复后的内容
            original_content = error.get("original_content", "")
            repaired_content = error.get("repaired_content", "")
            
            # 如果没有这些字段，尝试从其他字段构造
            if not original_content and "code" in error:
                original_content = error["code"]
            if not repaired_content and "fix" in error:
                # 这里需要根据fix描述生成修复后的内容
                # 暂时跳过这种类型的错误
                logger.warning(f"   ⚠️ 错误 {i+1} 缺少修复内容，跳过")
                continue
            
            if not original_content or not repaired_content:
                logger.warning(f"   ⚠️ 错误 {i+1} 缺少必要信息，跳过")
                continue
            
            # 生成diff
            diff_result = agent.diff_tools.generate_repair_diff(
                original_content,
                repaired_content,
                input_file
            )
            
            if diff_result["success"]:
                logger.info(f"   ✅ 错误 {i+1} 的diff生成成功")
                all_diffs.append({
                    "error_info": error,
                    "diff_content": diff_result["diff_content"]
                })
            else:
                logger.error(f"   ❌ 错误 {i+1} 的diff生成失败: {diff_result.get('message')}")
        
        # 第三步：应用所有diff
        logger.info("🔄 第三步：应用所有diff补丁...")
        if all_diffs:
            # 复制原文件到输出文件
            import shutil
            shutil.copy2(input_file, output_file)
            logger.info(f"✅ 文件复制完成: {input_file} -> {output_file}")
            
            # 逐个应用diff
            for i, diff_data in enumerate(all_diffs):
                logger.info(f"   应用diff {i+1}/{len(all_diffs)}...")
                
                apply_result = agent.diff_tools.apply_diff_patch(
                    output_file, 
                    diff_data["diff_content"]
                )
                
                if apply_result["success"]:
                    logger.info(f"   ✅ diff {i+1} 应用成功")
                else:
                    logger.error(f"   ❌ diff {i+1} 应用失败: {apply_result.get('message')}")
            
            logger.info(f"✅ 所有diff应用完成，共处理 {len(all_diffs)} 个错误")
            
            return {
                "success": True,
                "message": f"HTML修复成功，处理了 {len(all_diffs)} 个错误",
                "input_file": input_file,
                "output_file": output_file,
                "total_errors": total_errors,
                "errors_processed": len(all_diffs),
                "errors_data": errors_data
            }
        else:
            logger.warning("⚠️ 没有生成任何diff补丁")
            return {
                "success": False,
                "error": "没有生成任何diff补丁",
                "input_file": input_file,
                "output_file": output_file
            }
            
    except Exception as e:
        logger.error(f"❌ HTML修复workflow过程中发生错误: {str(e)}")
        return {
            "success": False,
            "error": f"修复HTML文件失败: {str(e)}",
            "input_file": input_file,
            "output_file": output_file
        } 