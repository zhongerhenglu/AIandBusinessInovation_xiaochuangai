import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from research.document_parser import DocumentParserFactory
from research.keyword_extractor import KeywordExtractor
from research.chart_analyzer import ChartAnalyzer
from research.report_fetcher import ReportManager
from vertical_agents.research_agent import ResearchAgent


def test_pdf_parsing():
    print("=" * 80)
    print("测试1: PDF文档解析")
    print("=" * 80)
    
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '课程大报告论文')
    
    pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files[:5]:
        pdf_path = os.path.join(report_dir, pdf_file)
        print(f"\n--- 解析: {pdf_file} ---")
        
        try:
            parser = DocumentParserFactory.get_parser(pdf_path)
            if parser:
                parsed = parser.parse(pdf_path)
                
                if 'error' in parsed:
                    print(f"  ❌ 解析失败: {parsed['error']}")
                else:
                    print(f"  ✅ 解析成功")
                    print(f"  文本长度: {len(parsed['text'])} 字符")
                    print(f"  表格数量: {len(parsed.get('tables', []))}")
                    print(f"  图片数量: {len(parsed.get('images', []))}")
                    print(f"  页数: {parsed.get('metadata', {}).get('page_count', '未知')}")
                    print(f"  标题: {parsed.get('metadata', {}).get('title', '未知')}")
                    
                    if parsed.get('text', ''):
                        print(f"\n  文本预览 (前200字):")
                        preview = parsed['text'][:200].replace('\n', ' ')
                        print(f"  {preview}...")
            else:
                print(f"  ⚠️ 不支持的格式")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_keyword_extraction():
    print("\n" + "=" * 80)
    print("测试2: 关键词提取")
    print("=" * 80)
    
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '课程大报告论文')
    
    pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
    keyword_extractor = KeywordExtractor()
    
    for pdf_file in pdf_files[:3]:
        pdf_path = os.path.join(report_dir, pdf_file)
        print(f"\n--- {pdf_file} ---")
        
        try:
            parsed = DocumentParserFactory.parse(pdf_path)
            
            if 'error' not in parsed and parsed.get('text'):
                keywords = keyword_extractor.extract_keywords(parsed['text'], top_n=10)
                entities = keyword_extractor.extract_entities(parsed['text'])
                numeric_info = keyword_extractor.extract_numeric_info(parsed['text'])
                
                print(f"  提取关键词:")
                for kw in keywords[:8]:
                    print(f"    - {kw['keyword']} (权重: {kw['weight']:.4f}, 类别: {kw['category']})")
                
                print(f"\n  提取实体:")
                for entity_type, items in entities.items():
                    if items:
                        print(f"    {entity_type}: {', '.join(items[:5])}")
                
                if numeric_info:
                    print(f"\n  提取数值信息:")
                    for num in numeric_info[:5]:
                        print(f"    {num['label']}: {num['value']}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_chart_analysis():
    print("\n" + "=" * 80)
    print("测试3: 图表分析")
    print("=" * 80)
    
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '课程大报告论文')
    
    pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
    chart_analyzer = ChartAnalyzer()
    
    for pdf_file in pdf_files[:3]:
        pdf_path = os.path.join(report_dir, pdf_file)
        print(f"\n--- {pdf_file} ---")
        
        try:
            parsed = DocumentParserFactory.parse(pdf_path)
            
            if 'error' not in parsed:
                tables = parsed.get('tables', [])
                chart_descriptions = chart_analyzer.extract_chart_descriptions(parsed.get('text', ''))
                
                print(f"  表格数量: {len(tables)}")
                print(f"  图表描述数量: {len(chart_descriptions)}")
                
                if chart_descriptions:
                    print(f"\n  图表描述:")
                    for desc in chart_descriptions[:5]:
                        print(f"    {'图' if desc.get('type') == 'chart' else '表'} {desc.get('number', '')}: {desc.get('title', '')}")
                
                if tables:
                    table_analysis = chart_analyzer.analyze_tables(tables)
                    print(f"\n  表格分析:")
                    for table in table_analysis[:3]:
                        print(f"    表格{table.get('table_index')}: 类型={table.get('type')}, 行列={table.get('rows')}x{table.get('columns')}")
                        if table.get('key_findings'):
                            for finding in table['key_findings'][:2]:
                                print(f"      - {finding}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_research_agent():
    print("\n" + "=" * 80)
    print("测试4: ResearchAgent综合分析")
    print("=" * 80)
    
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '课程大报告论文')
    research_agent = ResearchAgent()
    
    pdf_files = [f for f in os.listdir(report_dir) if f.endswith('.pdf')]
    
    for pdf_file in pdf_files[:3]:
        pdf_path = os.path.join(report_dir, pdf_file)
        print(f"\n--- {pdf_file} ---")
        
        try:
            result = research_agent.execute('summarize_report', {'file_path': pdf_path})
            
            if 'error' in result:
                print(f"  ❌ 分析失败: {result['error']}")
            else:
                print(f"  ✅ 分析成功")
                print(f"  标题: {result.get('title', '未知')}")
                
                print(f"\n  核心关键词:")
                for kw in result.get('keywords', [])[:8]:
                    print(f"    - {kw}")
                
                print(f"\n  关键发现:")
                for finding in result.get('key_findings', [])[:5]:
                    print(f"    - {finding}")
                
                summary = result.get('summary', {})
                if summary.get('key_points'):
                    print(f"\n  关键要点:")
                    for i, point in enumerate(summary['key_points'][:3], 1):
                        print(f"    {i}. {point}")
        except Exception as e:
            print(f"  ❌ 异常: {str(e)}")


def test_report_fetcher():
    print("\n" + "=" * 80)
    print("测试5: 研报获取")
    print("=" * 80)
    
    report_manager = ReportManager()
    
    print("\n--- 获取本地研报 ---")
    local_reports = report_manager.get_reports(source='local', limit=10)
    print(f"  本地研报数量: {len(local_reports)}")
    
    for report in local_reports[:5]:
        print(f"    - {report.get('title')} ({report.get('date_str')})")
    
    print("\n--- 获取分类统计 ---")
    categories = report_manager.get_report_categories()
    for cat, count in categories.items():
        print(f"    {cat}: {count} 份")
    
    print("\n--- 搜索研报 ---")
    search_results = report_manager.search_reports('因子')
    print(f"  搜索'因子'结果: {len(search_results)} 份")
    for report in search_results[:3]:
        print(f"    - {report.get('title')}")


if __name__ == '__main__':
    test_report_fetcher()
    test_pdf_parsing()
    test_keyword_extraction()
    test_chart_analysis()
    test_research_agent()
    
    print("\n" + "=" * 80)
    print("所有测试完成!")
    print("=" * 80)