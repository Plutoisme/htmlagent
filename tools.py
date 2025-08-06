import os
from typing import Dict, Any

def modify_file_tool(file_path: str, modifications: Dict[str, str]) -> Dict[str, Any]:
    """
    修改文件内容，根据行号和修改后的代码进行更新
    
    Args:
        file_path: 文件路径
        modifications: 格式为 {"line_number": "modified_code"} 的字典
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"文件 {file_path} 不存在"}
        
        # 读取原文件
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # 应用修改
        modified_lines = lines.copy()
        
        for line_num_str, new_content in modifications.items():
            try:
                line_num = int(line_num_str)
                if line_num <= 0:
                    return {"error": f"行号必须大于0，收到: {line_num}"}
                
                # 处理删除操作（空字符串表示删除）
                if new_content == "":
                    if line_num <= len(modified_lines):
                        modified_lines[line_num - 1] = None
                    else:
                        return {"error": f"行号 {line_num} 超出文件范围"}
                # 处理修改操作
                elif line_num <= len(modified_lines):
                    modified_lines[line_num - 1] = new_content + '\n'
                # 处理新增操作（行号超出当前文件长度）
                else:
                    # 填充空行直到目标行号
                    while len(modified_lines) < line_num:
                        modified_lines.append('\n')
                    modified_lines[line_num - 1] = new_content + '\n'
                    
            except ValueError:
                return {"error": f"无效的行号: {line_num_str}"}
        
        # 过滤掉None值（被删除的行）
        modified_lines = [line for line in modified_lines if line is not None]
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(modified_lines)
        
        return {"success": True, "message": f"文件 {file_path} 修改成功", "modifications": modifications}
        
    except Exception as e:
        return {"error": f"修改文件失败: {str(e)}"} 