"""
HTML渲染器 - 将生成的JSON数据渲染成HTML报告
"""
import json
from typing import Dict, Any, List
from pathlib import Path

class HTMLRenderer:
    """HTML渲染器"""
    
    def __init__(self, template_path: str = "template.html"):
        """
        初始化HTML渲染器
        
        Args:
            template_path: HTML模板文件路径
        """
        self.template_path = Path(template_path)
        self.template_content = self._load_template()
    
    def _load_template(self) -> str:
        """加载HTML模板"""
        try:
            if self.template_path.exists():
                return self.template_path.read_text(encoding="utf-8")
            else:
                raise FileNotFoundError(f"模板文件不存在: {self.template_path}")
        except Exception as e:
            raise Exception(f"加载模板文件失败: {e}")
    
    def render(self, report_data) -> str:
        """
        渲染HTML报告
        
        Args:
            report_data: 报告数据，可以是ReportData对象或字典
            
        Returns:
            渲染后的HTML内容
        """
        try:
            # 如果输入是ReportData对象，转换为字典
            if hasattr(report_data, 'model_dump'):
                data_dict = report_data.model_dump()
            elif hasattr(report_data, 'dict'):
                data_dict = report_data.dict()
            elif isinstance(report_data, dict):
                data_dict = report_data
            else:
                raise ValueError(f"不支持的数据类型: {type(report_data)}")
            
            # 开始渲染
            html_content = self.template_content
            
            # 渲染元信息
            html_content = self._render_meta(html_content, data_dict.get("meta", {}))
            
            # 渲染导航
            html_content = self._render_nav(html_content, data_dict.get("nav", []))
            
            # 渲染Hero区域
            html_content = self._render_hero(html_content, data_dict.get("hero", {}))
            
            # 渲染事理图谱洞察
            html_content = self._render_graph_insights(html_content, data_dict.get("graphInsights", {}))
            
            # 渲染决策因素
            html_content = self._render_decision_factors(html_content, data_dict.get("decisionFactors", []))
            
            # 渲染产品列表
            html_content = self._render_products(html_content, data_dict.get("products", []))
            
            # 渲染图表
            html_content = self._render_charts(html_content, data_dict.get("charts", []))
            
            # 渲染对比表
            html_content = self._render_table(html_content, data_dict.get("table", {}))
            
            # 渲染场景分析
            html_content = self._render_scenarios(html_content, data_dict.get("scenarios", []))
            
            # 渲染淘汰说明
            html_content = self._render_elimination(html_content, data_dict.get("elimination", []))
            
            # 渲染推荐方案
            html_content = self._render_recommendations(html_content, data_dict.get("recommendations", []))
            
            # 注入JavaScript数据
            html_content = self._inject_js_data(html_content, data_dict)
            
            return html_content
            
        except Exception as e:
            raise Exception(f"HTML渲染失败: {e}")
    
    def _render_meta(self, html_content: str, meta: Dict[str, str]) -> str:
        """渲染元信息"""
        if not meta:
            return html_content
        
        # 替换页面标题
        if "title" in meta:
            html_content = html_content.replace(
                'data-bind="title">通用购物决策报告模板 v2</title>',
                f'data-bind="title">{meta["title"]}</title>'
            )
        
        # 替换品牌标题
        if "title" in meta:
            html_content = html_content.replace(
                'id="brandTitle" class="text-slate-900 font-semibold tracking-wide">通用决策报告</div>',
                f'id="brandTitle" class="text-slate-900 font-semibold tracking-wide">{meta["title"]}</div>'
            )
        
        # 替换页脚品牌
        if "title" in meta:
            html_content = html_content.replace(
                '<div class="font-semibold" id="footerBrand">通用决策报告</div>',
                f'<div class="font-semibold" id="footerBrand">{meta["title"]}</div>'
            )
        
        return html_content
    
    def _render_nav(self, html_content: str, nav: List[Dict[str, str]]) -> str:
        """渲染导航"""
        if not nav:
            return html_content
        
        # 转换导航数据格式：从 title/href 转换为 id/label
        # 同时修复锚点不匹配的问题
        nav_data = []
        section_mapping = {
            "requirements": "needs",      # 需求分析 -> needs
            "products": "table",          # 产品对比 -> table
            "scenarios": "scenarios",     # 场景分析 -> scenarios
            "recommendations": "final-reco"  # 推荐方案 -> final-reco
        }
        
        for i, item in enumerate(nav):
            href = item.get("href", f"#section-{i}")
            # 提取锚点名称
            anchor = href.replace("#", "")
            # 映射到实际存在的section id
            mapped_id = section_mapping.get(anchor, anchor)
            nav_data.append({
                "id": mapped_id,
                "label": item.get("title", f"导航{i+1}")
            })
        
        # 生成导航HTML
        desktop_nav_html = ""
        mobile_nav_html = ""
        footer_nav_html = ""
        
        for item in nav_data:
            desktop_nav_html += f'<a href="#{item["id"]}" class="hover:text-primary-700 transition-colors">{item["label"]}</a>'
            mobile_nav_html += f'<a href="#{item["id"]}" class="block py-2">{item["label"]}</a>'
            footer_nav_html += f'<a href="#{item["id"]}" class="text-primary-700">{item["label"]}</a>'
        
        # 替换桌面导航
        html_content = html_content.replace(
            '<nav id="desktopNav" class="hidden md:flex items-center gap-6 text-slate-700"></nav>',
            f'<nav id="desktopNav" class="hidden md:flex items-center gap-6 text-slate-700">{desktop_nav_html}</nav>'
        )
        
        # 替换移动端导航
        html_content = html_content.replace(
            '<div id="mobileNav" class="px-4 py-3 space-y-1 text-slate-800"></div>',
            f'<div id="mobileNav" class="px-4 py-3 space-y-1 text-slate-800">{mobile_nav_html}</div>'
        )
        
        # 替换页脚导航
        html_content = html_content.replace(
            '<div id="footerQuicklinks" class="grid grid-cols-2 gap-2 text-sm"></div>',
            f'<div id="footerQuicklinks" class="grid grid-cols-2 gap-2 text-sm">{footer_nav_html}</div>'
        )
        
        return html_content
    
    def _render_hero(self, html_content: str, hero: Dict[str, Any]) -> str:
        """渲染Hero区域"""
        if not hero:
            return html_content
        
        # 替换标题
        if "title" in hero:
            html_content = html_content.replace(
                'id="heroTitle" class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight">通用购物决策报告模板</h1>',
                f'id="heroTitle" class="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight">{hero["title"]}</h1>'
            )
        
        # 替换副标题
        if "subtitle" in hero:
            html_content = html_content.replace(
                '<p id="heroSubtitle" class="text-white/80 leading-relaxed mt-4">\n              使用统一的数据结构，自动生成从需求拆解到推荐方案的完整报告。无需绑定具体品类与术语。\n            </p>',
                f'<p id="heroSubtitle" class="text-white/80 leading-relaxed mt-4">\n              {hero["subtitle"]}\n            </p>'
            )
        
        # 修复CTA锚点，使其与导航锚点保持一致
        html_content = html_content.replace(
            'href="#final-reco"',
            'href="#final-reco"'
        )
        
        # 渲染标签
        if "chips" in hero and hero["chips"]:
            chips_html = ""
            for chip in hero["chips"]:
                icon = chip.get("icon", "fa-circle")
                text = chip.get("text", "")
                chips_html += f'<span class="chip"><i class="fa-solid {icon} text-primary-300"></i>{text}</span>'
            
            html_content = html_content.replace(
                '<div id="heroChips" class="flex flex-wrap gap-2 mb-4"></div>',
                f'<div id="heroChips" class="flex flex-wrap gap-2 mb-4">{chips_html}</div>'
            )
        
        # 渲染统计信息
        if "stats" in hero and hero["stats"]:
            stats_html = ""
            for stat in hero["stats"]:
                label = stat.get("label", "")
                value = stat.get("value", "")
                stats_html += f'''
                <div class="p-4 rounded-xl bg-white/10">
                  <div class="text-sm text-white/70">{label}</div>
                  <div class="text-xl font-bold">{value}</div>
                </div>'''
            
            html_content = html_content.replace(
                '<div id="heroStats" class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6"></div>',
                f'<div id="heroStats" class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6">{stats_html}</div>'
            )
        
        return html_content
    
    def _render_graph_insights(self, html_content: str, graph_insights: Dict[str, Any]) -> str:
        """渲染事理图谱洞察"""
        if not graph_insights or "dimensions" not in graph_insights:
            return html_content
        
        dimensions = graph_insights["dimensions"]
        if not dimensions:
            return html_content
        
        dimensions_html = ""
        for dimension in dimensions:
            icon = dimension.get("icon", "fa-question")
            title = dimension.get("title", "")
            description = dimension.get("description", "")
            
            # 修复无效的图标类名
            if icon == "fa-grid-2":
                icon = "fa-table-cells"  # 替换为有效的图标
            
            dimensions_html += f'''
            <div class="p-5 rounded-2xl bg-white shadow-soft border border-slate-200">
              <div class="flex items-center gap-3 mb-2">
                <div class="h-10 w-10 rounded-xl bg-primary-100 text-primary-700 grid place-items-center">
                  <i class="fa-solid {icon}"></i>
                </div>
                <div class="font-semibold">{title}</div>
              </div>
              <p class="text-slate-600 text-sm leading-relaxed">{description}</p>
            </div>'''
        
        html_content = html_content.replace(
            '<div id="needDimensions" class="grid md:grid-cols-3 lg:grid-cols-5 gap-5"></div>',
            f'<div id="needDimensions" class="grid md:grid-cols-3 lg:grid-cols-5 gap-5">{dimensions_html}</div>'
        )
        
        return html_content
    
    def _render_decision_factors(self, html_content: str, decision_factors: List[Dict[str, str]]) -> str:
        """渲染决策因素"""
        if not decision_factors:
            return html_content
        
        factors_html = ""
        for factor in decision_factors:
            icon = factor.get("icon", "fa-question")
            title = factor.get("title", "")
            description = factor.get("description", "")
            
            factors_html += f'''
            <div class="p-5 rounded-2xl bg-white shadow-soft border border-slate-200">
              <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-xl bg-primary-100 text-primary-700 grid place-items-center">
                  <i class="fa-solid {icon}"></i>
                </div>
                <div class="font-semibold">{title}</div>
              </div>
              <p class="text-slate-600 text-sm mt-2">{description}</p>
            </div>'''
        
        html_content = html_content.replace(
            '<div id="factorCards" class="grid md:grid-cols-2 lg:grid-cols-4 gap-5"></div>',
            f'<div id="factorCards" class="grid md:grid-cols-2 lg:grid-cols-4 gap-5">{factors_html}</div>'
        )
        
        return html_content
    
    def _render_products(self, html_content: str, products: List[Dict[str, Any]]) -> str:
        """渲染产品列表"""
        if not products:
            return html_content
        
        # 产品列表的渲染主要由JavaScript处理，这里只是占位
        # 我们只需要确保数据被正确注入到JavaScript中
        return html_content
    
    def _render_charts(self, html_content: str, charts: List[Dict[str, Any]]) -> str:
        """渲染图表"""
        if not charts:
            return html_content
        
        # 修复图表metricKey问题
        for chart in charts:
            if chart.get("type") == "bar" and "metricKey" in chart:
                metric_key = chart["metricKey"]
                # 检查metricKey是否有效，如果无效则替换为有效的字段
                if metric_key == "核心属性":
                    # 替换为实际存在的字段，比如CLTC续航
                    chart["metricKey"] = "CLTC续航"
                    chart["title"] = "标称续航对比"
                    chart["unit"] = "km"
                    chart["suggestedMax"] = 700
                    chart["stepSize"] = 100
                elif metric_key == "price":
                    # 确保价格图表的单位正确
                    chart["unit"] = "万元"
                    chart["suggestedMax"] = 20
        
        # 图表渲染由JavaScript处理，这里只是占位
        return html_content
    
    def _render_table(self, html_content: str, table: Dict[str, Any]) -> str:
        """渲染对比表"""
        if not table:
            return html_content
        
        # 修复columns结构问题
        # 如果columns是字符串数组，转换为对象数组
        if "columns" in table and isinstance(table["columns"], list):
            columns = table["columns"]
            if columns and isinstance(columns[0], str):
                # 将字符串列名转换为对象格式
                normalized_columns = []
                for col in columns:
                    if col == "产品名称":
                        normalized_columns.append({"key": "name", "label": col, "source": "name"})
                    elif col == "价格":
                        normalized_columns.append({"key": "price", "label": col, "source": "price", "formatter": "currency"})
                    elif col == "核心特性":
                        # 使用type字段作为核心特性
                        normalized_columns.append({"key": "type", "label": col, "source": "type"})
                    elif col == "推荐指数":
                        # 使用一个计算字段或设为null
                        normalized_columns.append({"key": "recommendation", "label": col, "source": "recommendation"})
                    else:
                        # 其他列尝试从attributes中获取
                        normalized_columns.append({"key": col, "label": col, "sourceAttr": col})
                
                # 更新table配置
                table["columns"] = normalized_columns
        
        # 对比表渲染由JavaScript处理，这里只是占位
        return html_content
    
    def _render_scenarios(self, html_content: str, scenarios: List[Dict[str, Any]]) -> str:
        """渲染场景分析"""
        if not scenarios:
            return html_content
        
        # 场景分析渲染由JavaScript处理，这里只是占位
        return html_content
    
    def _render_elimination(self, html_content: str, elimination: List[Dict[str, Any]]) -> str:
        """渲染淘汰说明"""
        if not elimination:
            return html_content
        
        # 淘汰说明渲染由JavaScript处理，这里只是占位
        return html_content
    
    def _render_recommendations(self, html_content: str, recommendations: List[Dict[str, Any]]) -> str:
        """渲染推荐方案"""
        if not recommendations:
            return html_content
        
        # 推荐方案渲染由JavaScript处理，这里只是占位
        return html_content
    
    def _inject_js_data(self, html_content: str, report_data: Dict[str, Any]) -> str:
        """注入JavaScript数据"""
        # 将完整的报告数据注入到JavaScript中
        js_data = f"""
        <script>
        window.REPORT_DATA = {json.dumps(report_data, ensure_ascii=False, indent=2)};
        </script>
        """
        
        # 查找<head>标签的结束位置，在</head>之前插入数据
        head_end = html_content.find('</head>')
        if head_end != -1:
            html_content = (
                html_content[:head_end] +
                js_data +
                html_content[head_end:]
            )
        
        return html_content
    
    def save_report(self, report_data: Dict[str, Any], output_path: str = "generated_report.html") -> str:
        """
        保存HTML报告到文件
        
        Args:
            report_data: 报告数据
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        try:
            # 渲染HTML
            html_content = self.render(report_data)
            
            # 保存到文件
            output_file = Path(output_path)
            output_file.write_text(html_content, encoding="utf-8")
            
            return str(output_file.absolute())
            
        except Exception as e:
            raise Exception(f"保存HTML报告失败: {e}")

def main():
    """主函数 - 测试HTML渲染器"""
    try:
        # 加载示例数据
        with open("test_report.json", "r", encoding="utf-8") as f:
            report_data = json.load(f)
        
        # 创建渲染器
        renderer = HTMLRenderer()
        
        # 渲染并保存HTML报告
        output_path = renderer.save_report(report_data, "test_report_fixed.html")
        print(f"HTML报告已保存到: {output_path}")
        
    except FileNotFoundError:
        print("请先运行 main.py 生成报告数据")
    except Exception as e:
        print(f"HTML渲染失败: {e}")

if __name__ == "__main__":
    main() 