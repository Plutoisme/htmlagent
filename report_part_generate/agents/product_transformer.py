"""
产品转换Agent - 将车型数据转换为模板所需的products格式
"""
import json
from typing import Dict, Any, List
from llm_client import SiliconFlowClient
from models import ProductTransformerOutput, Product, ProductDetails
from config import AGENT_CONFIG, PROMPT_TEMPLATES

class ProductTransformerAgent:
    """产品转换Agent"""
    
    def __init__(self, llm_client: SiliconFlowClient):
        self.llm_client = llm_client
        self.config = AGENT_CONFIG["product_transformer"]
    
    def run(self, user_query: str, eventic_graph: str, summary_base: str, 
            normalized_data: Dict[str, Any] = None, product_id_map: Dict[str, str] = None,
            common_attributes: List[str] = None) -> ProductTransformerOutput:
        """
        运行产品转换Agent
        
        Args:
            user_query: 用户查询
            eventic_graph: 事理图谱
            summary_base: 基础数据
            normalized_data: 规范化后的数据
            product_id_map: 产品ID映射
            common_attributes: 共同属性列表
            
        Returns:
            转换后的产品数据
        """
        try:
            # 构建提示词
            prompt = self._build_prompt(user_query, eventic_graph, summary_base, 
                                     normalized_data, product_id_map, common_attributes)
            
            # 调用模型
            messages = [
                {"role": "system", "content": PROMPT_TEMPLATES["system_prefix"]},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_client.chat_completion(
                messages=messages,
                temperature=self.config["temperature"],
                max_tokens=self.config["max_tokens"]
            )
            
            # 提取JSON数据
            data = self.llm_client.extract_json(response)
            
            # 验证响应
            expected_keys = ["products"]
            if not self.llm_client.validate_response(response, expected_keys):
                raise ValueError("模型响应格式不正确")
            
            # 构建产品列表
            products = []
            for product_data in data.get("products", []):
                try:
                    product = Product(**product_data)
                    products.append(product)
                except Exception as e:
                    # 如果单个产品解析失败，跳过
                    continue
            
            output = ProductTransformerOutput(products=products)
            return output
            
        except Exception as e:
            # 如果模型调用失败，使用备用方法
            return self._fallback_transformation(summary_base, normalized_data, product_id_map, common_attributes)
    
    def _build_prompt(self, user_query: str, eventic_graph: str, summary_base: str, 
                      normalized_data: Dict[str, Any] = None, product_id_map: Dict[str, str] = None,
                      common_attributes: List[str] = None) -> str:
        """构建提示词"""
        normalized_info = ""
        if normalized_data:
            normalized_info = f"\n规范化数据：{json.dumps(normalized_data, ensure_ascii=False, indent=2)}"
        
        product_id_info = ""
        if product_id_map:
            product_id_info = f"\n产品ID映射：{json.dumps(product_id_map, ensure_ascii=False, indent=2)}"
        
        attributes_info = ""
        if common_attributes:
            attributes_info = f"\n共同属性：{json.dumps(common_attributes, ensure_ascii=False, indent=2)}"
        
        return f"""
请将以下产品数据转换为模板所需的格式：

用户查询：{user_query}

事理图谱：{eventic_graph}

产品数据：{summary_base}{normalized_info}{product_id_info}{attributes_info}

请执行以下任务：
1. 将每个产品转换为标准的产品对象格式
2. 提取核心参数作为attributes
3. 计算使用成本
4. 整理优缺点和标签
5. 确保所有产品ID与规范化数据一致

请输出以下JSON格式：
{{
  "products": [
    {{
      "id": "产品ID",
      "name": "产品名称",
      "price": 价格,
      "currency": "CNY",
      "type": "产品类型",
      "tags": ["标签1", "标签2"],
      "highlights": ["亮点1", "亮点2"],
      "attributes": {{
        "属性名": "属性值"
      }},
      "details": {{
        "pros": ["优点1", "优点2"],
        "cons": ["缺点1", "缺点2"],
        "notes": ["备注1", "备注2"]
      }}
    }}
  ]
}}

注意：
- 保持通用性，避免使用特定商品名称
- 确保产品ID与规范化数据一致
- 属性值应该是数值或字符串，避免复杂对象
- 价格应该是数字类型
"""
    
    def _fallback_transformation(self, summary_base: str, normalized_data: Dict[str, Any] = None,
                                product_id_map: Dict[str, str] = None, common_attributes: List[str] = None) -> ProductTransformerOutput:
        """备用转换方法"""
        try:
            # 解析基础数据
            if isinstance(summary_base, str):
                data = json.loads(summary_base)
            else:
                data = summary_base
            
            products = []
            
            # 处理每个产品
            for product_name, product_info in data.items():
                try:
                    # 生成产品ID
                    product_id = self._generate_product_id(product_name)
                    
                    # 提取基本信息
                    name = product_name
                    price = self._extract_price(product_info)
                    product_type = self._extract_type(product_info)
                    
                    # 提取属性
                    attributes = self._extract_attributes(product_info)
                    
                    # 生成标签和亮点
                    tags = self._generate_tags(product_info)
                    highlights = self._generate_highlights(product_info)
                    
                    # 生成优缺点
                    details = self._generate_details(product_info)
                    
                    # 创建产品对象
                    product = Product(
                        id=product_id,
                        name=name,
                        price=price,
                        currency="CNY",
                        type=product_type,
                        tags=tags,
                        highlights=highlights,
                        attributes=attributes,
                        details=details
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    # 如果单个产品处理失败，跳过
                    continue
            
            return ProductTransformerOutput(products=products)
            
        except Exception as e:
            # 如果所有方法都失败，返回空结果
            return ProductTransformerOutput(products=[])
    
    def _generate_product_id(self, product_name: str) -> str:
        """生成产品ID"""
        import re
        id_str = re.sub(r'[^\w\s-]', '', product_name.lower())
        id_str = re.sub(r'\s+', '-', id_str.strip())
        return id_str
    
    def _extract_price(self, product_info: Dict[str, Any]) -> float:
        """提取价格"""
        if "价格" in product_info:
            price_str = str(product_info["价格"])
            # 提取数字
            import re
            price_match = re.search(r'(\d+(?:\.\d+)?)', price_str)
            if price_match:
                return float(price_match.group(1))
        return 0.0
    
    def _extract_type(self, product_info: Dict[str, Any]) -> str:
        """提取产品类型"""
        if "核心参数" in product_info and "车型类型" in product_info["核心参数"]:
            return product_info["核心参数"]["车型类型"]
        return "未知类型"
    
    def _extract_attributes(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """提取属性"""
        attributes = {}
        
        # 从核心参数提取
        if "核心参数" in product_info:
            core_params = product_info["核心参数"]
            for key, value in core_params.items():
                if value is not None and value != "":
                    attributes[key] = value
        
        # 从其他部分提取重要信息
        important_sections = ["冬季性能", "安全配置", "使用成本"]
        for section in important_sections:
            if section in product_info:
                section_data = product_info[section]
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if value is not None and value != "":
                            attributes[f"{section}_{key}"] = value
        
        return attributes
    
    def _generate_tags(self, product_info: Dict[str, Any]) -> List[str]:
        """生成标签"""
        tags = []
        
        # 基于产品信息生成标签
        if "核心参数" in product_info:
            core_params = product_info["核心参数"]
            if "热管理系统" in core_params:
                tags.append("热管理系统")
            if "电池类型" in core_params:
                tags.append(core_params["电池类型"])
        
        if "安全配置" in product_info:
            tags.append("安全配置")
        
        return tags[:5]  # 限制标签数量
    
    def _generate_highlights(self, product_info: Dict[str, Any]) -> List[str]:
        """生成亮点"""
        highlights = []
        
        # 基于产品信息生成亮点
        if "冬季性能" in product_info:
            highlights.append("冬季性能优化")
        
        if "安全配置" in product_info:
            highlights.append("安全配置完善")
        
        if "使用成本" in product_info:
            highlights.append("使用成本低")
        
        return highlights[:3]  # 限制亮点数量
    
    def _generate_details(self, product_info: Dict[str, Any]) -> ProductDetails:
        """生成优缺点详情"""
        pros = []
        cons = []
        notes = []
        
        # 基于产品信息生成优缺点
        if "口碑评价" in product_info:
            feedback = product_info["口碑评价"]
            if "西北地区用户反馈" in feedback:
                user_feedback = feedback["西北地区用户反馈"]
                for key, value in user_feedback.items():
                    if "优秀" in str(value) or "好" in str(value):
                        pros.append(f"{key}: {value}")
                    elif "一般" in str(value) or "差" in str(value):
                        cons.append(f"{key}: {value}")
        
        return ProductDetails(pros=pros, cons=cons, notes=notes) 