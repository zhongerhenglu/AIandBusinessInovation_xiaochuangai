import re
import json
import logging
from typing import Dict, Any, List, Optional
from collections import Counter
import jieba
import jieba.analyse

logger = logging.getLogger(__name__)


class KeywordExtractor:
    def __init__(self):
        self._load_financial_dictionaries()
    
    def _load_financial_dictionaries(self):
        self.financial_keywords = {
            'factors': ['因子', 'Alpha', 'Beta', 'IC', 'IR', '夏普比率', '最大回撤', '收益率', '波动率'],
            'strategies': ['策略', '模型', '算法', '机器学习', '神经网络', '深度学习', '增强学习', '遗传算法'],
            'indicators': ['均线', 'MACD', 'RSI', 'KDJ', '布林带', 'ATR', 'CCI', 'VWAP'],
            'sectors': ['行业', '板块', '金融', '科技', '消费', '医药', '能源', '制造', '房地产'],
            'metrics': ['市盈率', '市净率', 'ROE', 'ROA', '毛利率', '净利率', '现金流', '负债'],
            'market': ['A股', '美股', '港股', '沪深300', '上证50', '中证500', '创业板', '科创板'],
            'research': ['研报', '报告', '分析', '预测', '评级', '目标价', '推荐', '买入', '卖出', '持有'],
            'risk': ['风险', '风控', '止损', '对冲', 'VaR', '回撤', '暴露'],
            'portfolio': ['组合', '配置', '仓位', '权重', '分散', '集中'],
        }
        
        self.stop_words = set([
            '的', '了', '和', '是', '就', '都', '而', '及', '与', '着', '或', '一个', '没有', '我们', '你们',
            '他们', '它们', '这', '那', '这些', '那些', '什么', '怎么', '如何', '为什么', '因为', '所以',
            '但是', '然而', '虽然', '如果', '可以', '可能', '应该', '必须', '需要', '已经', '正在', '将要',
            '曾经', '现在', '过去', '未来', '一些', '许多', '所有', '任何', '每一个', '某个', '其他', '另外',
            '以及', '等等', '例如', '比如', '包括', '通过', '根据', '按照', '基于', '关于', '对于', '至于',
            '由于', '鉴于', '为了', '以便', '以免', '否则', '要是', '只要', '只有', '除非', '不论', '不管',
            '尽管', '即使', '假如', '倘若', '万一', '要么', '或者', '与其', '不如', '宁可', '宁愿', '以便',
            '以防', '免得', '省得', '好在', '幸好', '可惜', '遗憾', '居然', '竟然', '果然', '难怪', '毕竟',
            '终究', '终于', '到底', '简直', '实在', '的确', '确实', '真的', '非常', '十分', '特别', '尤其',
            '格外', '更加', '越来越', '略微', '稍微', '差不多', '几乎', '将近', '大约', '大概', '左右', '上下',
            '之间', '以上', '以下', '以内', '以外', '以前', '以后', '之前', '之后', '以来', '为止', '至今',
            '目前', '当前', '现在', '如今', '今天', '昨天', '明天', '今年', '去年', '明年', '最近', '近来',
            '不久', '马上', '立刻', '立即', '顿时', '忽然', '突然', '渐渐', '逐渐', '慢慢', '缓缓', '悄悄',
            '默默', '偷偷', '暗暗', '公开', '秘密', '故意', '特意', '专门', '顺便', '趁机', '借机', '趁机',
            '顺便', '特意', '专门', '故意', '有意', '无意', '碰巧', '恰好', '刚好', '正好', '不巧', '偏巧',
            '索性', '干脆', '索性', '简直', '反正', '横竖', '无论', '不管', '任凭', '听凭', '随', '任由',
            '不妨', '何妨', '不如', '宁可', '宁愿', '毋宁', '与其', '孰若', '何如', '何妨', '不如', '宁可',
        ])
    
    def extract_keywords(self, text: str, top_n: int = 20, method: str = 'tfidf') -> List[Dict[str, Any]]:
        if not text or not isinstance(text, str):
            return []
        
        try:
            if method == 'tfidf':
                return self._extract_tfidf(text, top_n)
            elif method == 'textrank':
                return self._extract_textrank(text, top_n)
            elif method == 'mixed':
                tfidf_results = self._extract_tfidf(text, top_n)
                textrank_results = self._extract_textrank(text, top_n)
                return self._merge_results(tfidf_results, textrank_results)
            else:
                return self._extract_basic(text, top_n)
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return self._extract_basic(text, top_n)
    
    def _extract_tfidf(self, text: str, top_n: int) -> List[Dict[str, Any]]:
        keywords = jieba.analyse.extract_tags(text, topK=top_n, withWeight=True)
        results = []
        for keyword, weight in keywords:
            if len(keyword) > 1 and keyword not in self.stop_words:
                category = self._classify_keyword(keyword)
                results.append({
                    'keyword': keyword,
                    'weight': float(weight),
                    'category': category,
                    'method': 'tfidf',
                })
        return results
    
    def _extract_textrank(self, text: str, top_n: int) -> List[Dict[str, Any]]:
        keywords = jieba.analyse.textrank(text, topK=top_n, withWeight=True)
        results = []
        for keyword, weight in keywords:
            if len(keyword) > 1 and keyword not in self.stop_words:
                category = self._classify_keyword(keyword)
                results.append({
                    'keyword': keyword,
                    'weight': float(weight),
                    'category': category,
                    'method': 'textrank',
                })
        return results
    
    def _extract_basic(self, text: str, top_n: int) -> List[Dict[str, Any]]:
        words = jieba.lcut(text)
        filtered_words = [word for word in words if len(word) > 1 and word not in self.stop_words]
        word_counts = Counter(filtered_words)
        
        results = []
        for word, count in word_counts.most_common(top_n):
            category = self._classify_keyword(word)
            results.append({
                'keyword': word,
                'weight': float(count) / len(filtered_words),
                'category': category,
                'method': 'basic',
            })
        return results
    
    def _merge_results(self, list1: List[Dict], list2: List[Dict]) -> List[Dict[str, Any]]:
        merged = {}
        for item in list1 + list2:
            keyword = item['keyword']
            if keyword not in merged:
                merged[keyword] = {
                    'keyword': keyword,
                    'weight': 0,
                    'category': item['category'],
                    'methods': [],
                }
            merged[keyword]['weight'] += item['weight']
            if item['method'] not in merged[keyword]['methods']:
                merged[keyword]['methods'].append(item['method'])
        
        return sorted(merged.values(), key=lambda x: x['weight'], reverse=True)
    
    def _classify_keyword(self, keyword: str) -> str:
        for category, keywords in self.financial_keywords.items():
            for kw in keywords:
                if kw.lower() in keyword.lower() or keyword.lower() in kw.lower():
                    return category
        return 'other'
    
    def extract_sentences(self, text: str, max_sentences: int = 10) -> List[Dict[str, Any]]:
        sentences = re.split(r'(?<=[。！？；])', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        
        sentence_scores = []
        for sentence in sentences:
            score = self._score_sentence(sentence)
            sentence_scores.append({
                'sentence': sentence,
                'score': score,
                'length': len(sentence),
            })
        
        return sorted(sentence_scores, key=lambda x: x['score'], reverse=True)[:max_sentences]
    
    def _score_sentence(self, sentence: str) -> float:
        score = 0.0
        
        for category, keywords in self.financial_keywords.items():
            for kw in keywords:
                if kw in sentence:
                    score += 1.0
        
        words = jieba.lcut(sentence)
        financial_word_count = sum(1 for word in words if word in self._get_all_financial_words())
        score += financial_word_count * 0.5
        
        if len(sentence) > 50:
            score += 1.0
        
        return score
    
    def _get_all_financial_words(self) -> set:
        all_words = set()
        for keywords in self.financial_keywords.values():
            all_words.update(keywords)
        return all_words
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {
            'stocks': [],
            'funds': [],
            'indices': [],
            'companies': [],
            'factors': [],
            'strategies': [],
        }
        
        stock_pattern = re.compile(r'([0-9]{6})\s*(?:股票|股份|A股|港股)?')
        fund_pattern = re.compile(r'([0-9]{6})\s*(?:基金|ETF)')
        index_pattern = re.compile(r'(沪深300|上证50|中证500|创业板指|科创50|纳斯达克|标普500|道琼斯)')
        
        entities['stocks'] = list(set(stock_pattern.findall(text)))
        entities['funds'] = list(set(fund_pattern.findall(text)))
        entities['indices'] = list(set(index_pattern.findall(text)))
        
        for word in jieba.lcut(text):
            if len(word) > 2:
                if any(f in word for f in self.financial_keywords['factors']):
                    entities['factors'].append(word)
                elif any(s in word for s in self.financial_keywords['strategies']):
                    entities['strategies'].append(word)
        
        for key in entities:
            entities[key] = list(set(entities[key]))[:20]
        
        return entities
    
    def extract_numeric_info(self, text: str) -> List[Dict[str, Any]]:
        patterns = [
            (r'([\d.]+)\s*%', 'percentage'),
            (r'([\d.]+)\s*亿元', 'billion_rmb'),
            (r'([\d.]+)\s*万元', 'million_rmb'),
            (r'([\d.]+)\s*亿美元', 'billion_usd'),
            (r'([\d.]+)\s*%?\s*(?:同比|环比)\s*(?:增长|下降|减少|增加)', 'growth_rate'),
            (r'目标价\s*[：:]\s*([\d.]+)', 'target_price'),
            (r'估值\s*[：:]\s*([\d.]+)', 'valuation'),
            (r'PE\s*[：:]\s*([\d.]+)', 'pe_ratio'),
            (r'PB\s*[：:]\s*([\d.]+)', 'pb_ratio'),
            (r'ROE\s*[：:]\s*([\d.]+)', 'roe'),
            (r'收益率\s*[：:]\s*([\d.]+)', 'return_rate'),
            (r'回撤\s*[：:]\s*([\d.]+)', 'drawdown'),
            (r'夏普比率\s*[：:]\s*([\d.]+)', 'sharpe_ratio'),
        ]
        
        results = []
        for pattern, label in patterns:
            matches = re.findall(pattern, text)
            for match in matches[:5]:
                try:
                    value = float(match)
                    results.append({
                        'value': value,
                        'label': label,
                        'pattern': pattern,
                    })
                except ValueError:
                    continue
        
        return results
    
    def extract_research_highlights(self, text: str) -> Dict[str, Any]:
        return {
            'keywords': self.extract_keywords(text, top_n=15),
            'key_sentences': self.extract_sentences(text, max_sentences=8),
            'entities': self.extract_entities(text),
            'numeric_info': self.extract_numeric_info(text),
        }