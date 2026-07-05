import asyncio
import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge import EnhancedKnowledgeBase, VersionedWiki, KnowledgeGraph
from notification.knowledge_notification_service import KnowledgeNotificationService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_versioned_wiki():
    logger.info("=" * 60)
    logger.info("测试1: VersionedWiki版本控制")
    logger.info("=" * 60)
    
    wiki = VersionedWiki()
    
    wiki.create_topic_page("动量因子研究", "动量因子是基于股票过去表现预测未来收益的因子", ["ROC_5", "ROC_20"])
    logger.info("✓ 创建Topic页面")
    
    wiki.create_factor_page("动量因子", "基于价格变化率的因子", "Momentum = ROC(20)", "momentum", 0.18)
    logger.info("✓ 创建Factor页面")
    
    wiki.create_strategy_page("动量策略", "基于动量因子的量化策略", ["买入ROC_20>0的股票", "持有20个交易日"])
    logger.info("✓ 创建Strategy页面")
    
    wiki.create_analysis_page("2026下半年市场分析", "基于宏观情景分析的2026下半年市场预测")
    logger.info("✓ 创建Analysis页面")
    
    wiki.update_page("动量因子研究", "动量因子是基于股票过去表现预测未来收益的因子。更新内容：新增因子衰减分析。", "添加衰减分析内容")
    logger.info("✓ 更新页面")
    
    stats = wiki.get_stats()
    logger.info(f"✓ Wiki统计: {stats}")
    
    recent_updates = wiki.get_recent_updates(24)
    logger.info(f"✓ 最近更新: {len(recent_updates)}条")
    
    search_results = wiki.search("动量")
    logger.info(f"✓ 搜索结果: {len(search_results)}条")
    
    change_log = wiki.get_change_log(24)
    logger.info(f"✓ 变更日志: {len(change_log)}条")
    
    return wiki


def test_knowledge_graph():
    logger.info("\n" + "=" * 60)
    logger.info("测试2: KnowledgeGraph知识图谱")
    logger.info("=" * 60)
    
    graph = KnowledgeGraph()
    
    graph.build_stock_knowledge("601318.SH", "中国平安", "银行", "金融", 12000)
    logger.info("✓ 添加股票节点")
    
    graph.build_stock_knowledge("300750.SZ", "宁德时代", "新能源", "科技", 8000)
    logger.info("✓ 添加股票节点")
    
    graph.build_factor_knowledge("ROC_5", "momentum", "5日收益率", ["ROC_20"])
    logger.info("✓ 添加因子节点")
    
    graph.build_factor_knowledge("PB_ratio", "value", "市净率")
    logger.info("✓ 添加因子节点")
    
    neighbors = graph.get_neighbors("stock_601318.sh")
    logger.info(f"✓ 中国平安邻居节点: {len(neighbors)}个")
    
    search_results = graph.search("动量")
    logger.info(f"✓ 搜索结果: {len(search_results)}条")
    
    stats = graph.get_stats()
    logger.info(f"✓ 图谱统计: {stats}")
    
    graph.save_to_storage()
    logger.info("✓ 图谱已保存")
    
    return graph


def test_enhanced_knowledge_base():
    logger.info("\n" + "=" * 60)
    logger.info("测试3: EnhancedKnowledgeBase增强知识库")
    logger.info("=" * 60)
    
    kb = EnhancedKnowledgeBase()
    
    logger.info(f"✓ 初始化完成，默认页面已创建")
    
    document = {
        'id': 'test_doc_001',
        'content': '宁德时代是新能源电池龙头企业，在动力电池领域占据领先地位。',
        'metadata': {
            'stock_code': '300750.SZ',
            'stock_name': '宁德时代',
            'industry': '新能源',
            'sector': '科技',
            'market_cap': 8000
        }
    }
    
    kb.ingest_document(document)
    logger.info("✓ 文档摄入完成")
    
    query_result = kb.query("新能源")
    logger.info(f"✓ 查询结果: {len(query_result['wiki_pages'])} Wiki页面, {len(query_result['graph_nodes'])} 图谱节点")
    
    kb.create_analysis_report("因子表现分析", "2026年上半年因子IC分析报告")
    logger.info("✓ 创建分析报告")
    
    stats = kb.get_stats()
    logger.info(f"✓ 知识库统计: {stats}")
    
    summary = kb.get_knowledge_summary()
    logger.info(f"✓ 知识摘要生成成功")
    
    recent_updates = kb.get_recent_updates(24)
    logger.info(f"✓ 最近更新: {recent_updates['update_count']}条")
    
    return kb


async def test_knowledge_notification_service():
    logger.info("\n" + "=" * 60)
    logger.info("测试4: KnowledgeNotificationService知识通知服务")
    logger.info("=" * 60)
    
    service = KnowledgeNotificationService()
    
    logger.info("测试生成知识报告...")
    report = await service._generate_knowledge_report()
    logger.info(f"✓ 报告生成成功")
    logger.info(f"  - 更新统计: {report['update_count']}")
    logger.info(f"  - 知识条目: {report['stats']['total_knowledge_items']}")
    
    logger.info("测试格式化报告...")
    content = service._format_knowledge_report(report)
    logger.info(f"✓ 报告格式化成功，长度: {len(content)}字符")
    
    logger.info("测试发送知识更新...")
    result = service.sender.send_markdown(
        f"📚 知识体系更新统计测试 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        content
    )
    
    if result.get('success'):
        logger.info("✓ 知识更新发送成功")
    else:
        logger.warning(f"✗ 知识更新发送失败: {result.get('error')}")
    
    return service


def test_stress_knowledge_base():
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 知识库压力测试")
    logger.info("=" * 60)
    
    kb = EnhancedKnowledgeBase()
    
    logger.info("开始批量添加100条文档...")
    for i in range(100):
        doc = {
            'id': f'stress_doc_{i:03d}',
            'content': f'测试文档{i}内容：股票分析报告，行业研究，因子分析等内容。',
            'metadata': {
                'stock_code': f'TEST{i:03d}.SH',
                'stock_name': f'测试股票{i}',
                'industry': '测试行业',
                'sector': '测试板块',
                'market_cap': 1000 + i
            }
        }
        kb.ingest_document(doc)
    
    stats = kb.get_stats()
    logger.info(f"✓ 批量添加完成")
    logger.info(f"  - 总知识条目: {stats['total_knowledge_items']}")
    logger.info(f"  - Wiki页面: {stats['wiki']['total_pages']}")
    logger.info(f"  - 图谱节点: {stats['graph']['total_nodes']}")
    
    logger.info("测试搜索性能...")
    import time
    start_time = time.time()
    for _ in range(10):
        kb.query("测试")
    elapsed = time.time() - start_time
    logger.info(f"✓ 搜索性能: 10次搜索耗时{elapsed:.2f}秒，平均{elapsed/10:.3f}秒/次")
    
    return kb


def main():
    logger.info("=" * 60)
    logger.info("Knowledge Base测试套件")
    logger.info("=" * 60)
    
    from datetime import datetime
    
    try:
        test_versioned_wiki()
        test_knowledge_graph()
        test_enhanced_knowledge_base()
        asyncio.run(test_knowledge_notification_service())
        test_stress_knowledge_base()
        
        logger.info("\n" + "=" * 60)
        logger.info("所有测试完成!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"测试失败: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    main()