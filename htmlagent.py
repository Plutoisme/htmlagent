import os
from typing import Dict, Any, Type
from dotenv import load_dotenv
from openai import OpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from prompt import HTML_REPAIR_PROMPT
from tools import modify_file_tool

# 加载环境变量
load_dotenv()

class ModifyFileInput(BaseModel):
    file_path: str = Field(description="要修改的文件路径")
    modifications: Dict[str, str] = Field(description="修改内容，格式为 {'line_number': 'modified_code'}")

class ModifyFileTool(BaseTool):
    name: str = "modify_file_tool"
    description: str = "修改文件内容，根据行号和修改后的代码进行更新。这是修复HTML代码的唯一工具，必须使用此工具来执行所有修复操作。参数：file_path（文件路径），modifications（修改内容字典，格式为{'line_number': 'modified_code'}）"
    args_schema: Type[BaseModel] = ModifyFileInput
    
    def _run(self, file_path: str, modifications: Dict[str, str]) -> Dict[str, Any]:
        return modify_file_tool(file_path, modifications)

class HTMLAgent:
    def __init__(self):
        """初始化HTML修复Agent"""
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
        
        if not self.api_key:
            raise ValueError("请设置SILICONFLOW_API_KEY环境变量")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 初始化LangChain模型
        self.llm = ChatOpenAI(
            model="Pro/deepseek-ai/DeepSeek-V3",
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            temperature=0
        )
        
        # 创建工具（只有修改文件工具）
        self.tools = [ModifyFileTool()]
        
        # 创建简化的prompt模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", HTML_REPAIR_PROMPT),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        self.agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def repair_html(self, input_file: str, output_file: str = None) -> Dict[str, Any]:
        """
        修复HTML文件中的错误
        
        Args:
            input_file: 输入HTML文件路径
            output_file: 输出HTML文件路径（可选，默认覆盖原文件）
            
        Returns:
            Dict[str, Any]: 修复结果
        """
        try:
            # 如果指定了输出文件，先复制输入文件到输出文件
            if output_file and output_file != input_file:
                import shutil
                shutil.copy2(input_file, output_file)
                target_file = output_file
            else:
                target_file = input_file
            
            # 读取HTML文件内容
            with open(target_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 将HTML内容按行分割，构建行号和代码的字典
            lines = html_content.split('\n')
            html_lines = {}
            for i, line in enumerate(lines, 1):
                html_lines[str(i)] = line
            
            # 构建Agent的输入消息，包含HTML代码
            message = f"""请修复以下HTML代码中的错误：

HTML代码（行号和内容）：
{html_lines}

**重要**：你必须使用 `modify_file_tool` 工具来修复发现的错误。不要只是分析错误，要实际调用工具执行修复。

**文件路径**：{target_file}

请分析这些代码中的错误，并使用 `modify_file_tool` 工具进行修复。工具调用时请使用正确的文件路径：{target_file}"""
            
            # 执行Agent
            result = self.agent_executor.invoke({"input": message})
            
            return {
                "success": True,
                "message": "HTML修复完成",
                "result": result,
                "input_file": input_file,
                "output_file": target_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"修复HTML文件失败: {str(e)}",
                "input_file": input_file,
                "output_file": output_file
            }
    
    def repair_html_content(self, html_content: str) -> Dict[str, Any]:
        """
        修复HTML内容字符串
        
        Args:
            html_content: HTML内容字符串
            
        Returns:
            Dict[str, Any]: 修复结果
        """
        try:
            # 创建临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(html_content)
                temp_file_path = temp_file.name
            
            # 修复临时文件
            result = self.repair_html(temp_file_path)
            
            # 读取修复后的内容
            if result["success"]:
                with open(temp_file_path, 'r', encoding='utf-8') as f:
                    repaired_content = f.read()
                result["repaired_content"] = repaired_content
            
            # 清理临时文件
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"修复HTML内容失败: {str(e)}"
            } 