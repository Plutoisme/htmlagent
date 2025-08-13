"""
Debug分析脚本 - 读取和分析test.txt文件中的Agent输出
"""
import re
from pathlib import Path

class DebugAnalyzer:
    def __init__(self, log_file: str = "test.txt"):
        self.log_file = log_file
        self.content = ""
        self.sections = {}
        
    def load_log_file(self) -> bool:
        try:
            if not Path(self.log_file).exists():
                print(f"错误: 日志文件 {self.log_file} 不存在")
                return False
                
            with open(self.log_file, "r", encoding="utf-8") as f:
                self.content = f.read()
            
            print(f"成功加载日志文件: {self.log_file}")
            return True
            
        except Exception as e:
            print(f"加载日志文件失败: {e}")
            return False
    
    def parse_sections(self):
        sections = {}
        section_pattern = r"=== (.+?) ===\n(.*?)(?=\n=== |$)"
        matches = re.findall(section_pattern, self.content, re.DOTALL)
        
        for section_name, section_content in matches:
            section_name = section_name.strip()
            sections[section_name] = section_content.strip()
        
        self.sections = sections
        return sections
    
    def analyze_agent_outputs(self):
        analysis = {}
        agent_sections = [
            "数据规范化Agent输出",
            "需求分析Agent输出", 
            "产品转换Agent输出",
            "评分计算Agent输出",
            "场景匹配Agent输出",
            "报告组装Agent输出"
        ]
        
        for section_name in agent_sections:
            if section_name in self.sections:
                content = self.sections[section_name]
                analysis[section_name] = self._analyze_agent_section(content)
            else:
                analysis[section_name] = {"status": "missing"}
        
        return analysis
    
    def _analyze_agent_section(self, content: str):
        analysis = {
            "status": "found",
            "output_type": None,
            "has_dict_method": False,
            "content_length": len(content)
        }
        
        type_match = re.search(r"输出类型: <class '(.+?)'>", content)
        if type_match:
            analysis["output_type"] = type_match.group(1)
        
        if "输出字典:" in content:
            analysis["has_dict_method"] = True
        
        return analysis
    
    def generate_summary_report(self):
        summary = []
        summary.append("=" * 80)
        summary.append("DEBUG分析报告")
        summary.append("=" * 80)
        
        summary.append(f"日志文件: {self.log_file}")
        summary.append(f"文件大小: {len(self.content)} 字符")
        summary.append(f"解析的部分数量: {len(self.sections)}")
        summary.append("")
        
        agent_analysis = self.analyze_agent_outputs()
        summary.append("Agent输出分析:")
        summary.append("-" * 40)
        
        for agent_name, analysis in agent_analysis.items():
            status = analysis.get("status", "unknown")
            output_type = analysis.get("output_type", "unknown")
            has_dict = analysis.get("has_dict_method", False)
            
            summary.append(f"{agent_name}:")
            summary.append(f"  状态: {status}")
            summary.append(f"  输出类型: {output_type}")
            summary.append(f"  有dict方法: {has_dict}")
            summary.append("")
        
        summary.append("=" * 80)
        return "\n".join(summary)

def main():
    print("=== Debug分析器 ===")
    
    analyzer = DebugAnalyzer()
    
    if not analyzer.load_log_file():
        return
    
    sections = analyzer.parse_sections()
    print(f"解析完成，找到 {len(sections)} 个部分")
    
    print("\n找到的部分:")
    for section_name in sections.keys():
        print(f"  - {section_name}")
    
    report = analyzer.generate_summary_report()
    print(report)

if __name__ == "__main__":
    main() 