# Super Agent - AI量化投资智能体系统

> 基于 Beyond Gradients + Beyond RAG + Harness 架构的多智能体量化投资系统

## 📊 系统概览

Super Agent 是一个完整的 AI 量化投资智能体系统，集成了研报分析、量化分析、宏观情景分析和通知服务等核心功能模块。

## ✨ 核心功能

### 📚 研报分析模块
- **多格式文档解析**: 支持 PDF/DOCX/TXT 等格式文档读取
- **关键词提取**: 基于 TF-IDF 和 TextRank 算法提取金融领域关键词
- **图表分析**: 表格识别和关键数据提取
- **研报管理**: 本地文件和 API 模拟获取

### 📈 量化分析模块
- **时间段分析**: 支持 2024下半年~2026下半年多时间段分析
- **沪深300成分分析**: 成分股变化和行业分布
- **因子表现分析**: 多因子 IC/IR 分析
- **趋势预测**: 基于历史数据的走势预测
- **策略回测**: 模拟交易策略回测

### 🔮 宏观情景分析模块
- **多情景建模**: 支持美联储利率、日韩股市、央行救市等多因素情景分析
- **市场影响评估**: 综合评估各因素对市场的影响
- **行业评级**: 基于情景的行业推荐评级
- **股票推荐**: 重点关注股票清单
- **风险评估**: 全面的风险因素识别

### 🧠 Beyond RAG知识体系模块
- **版本控制Wiki**: 基于Git风格的版本控制，支持页面历史回溯
- **知识图谱**: 股票、因子、行业之间的关系建模
- **增强知识库**: Wiki + 图谱 + RAG 三位一体架构
- **智能查询**: 多模态知识检索和融合
- **定时更新统计**: 每天8/12/16/20/24点发送知识更新

### 📬 通知服务模块
- **定时推送**: 每日8:30发送股市热点报告，每周五8:30发送周报
- **多周期报告**: 支持日报、周报、月报、半年报
- **知识更新通知**: 每4小时发送知识体系更新统计
- **经济数据更新**: 每4小时抓取宏观经济数据
- **PushPlus集成**: 多渠道消息推送
- **消息队列**: 异步消息处理

### 📊 宏观经济数据模块
- **中国经济指标**: GDP、CPI、PPI、M2、PMI、社融等12项指标
- **全球经济数据**: 美国、欧元区、日本主要经济指标
- **政策新闻**: 央行、财政部、证监会等政策动态
- **定时更新**: 每4小时自动抓取和更新

## 📁 项目结构

```
super_agent/
├── config.py                # 系统配置
├── requirements.txt         # Python依赖
├── main.py                  # 主入口
├── PROJECT_STRUCTURE.md     # 详细项目结构
├── logs/                    # 日志文件
├── data/                    # 数据缓存
├── output/                  # 输出文件(图表、报告)
├── perception/              # 感知层
│   ├── data_providers.py    # 数据提供者
│   ├── feature_engine.py    # 特征工程
│   ├── perception_layer.py  # 统一感知层
│   ├── ths_data_provider.py # 同花顺数据接口
│   └── economic_data_provider.py # 宏观经济数据
├── brain/                   # 大脑层
│   ├── agent_base.py        # 基础智能体类
│   ├── llm_client.py        # LLM客户端
│   ├── reasoning_chain.py   # 推理链
│   └── brain_layer.py       # 统一大脑层
├── action/                  # 行动层
│   ├── risk_manager.py      # 风险管理
│   ├── position_manager.py  # 仓位管理
│   └── action_layer.py      # 统一行动层
├── knowledge/               # 知识层(Beyond RAG)
│   ├── document_store.py    # 文档存储
│   ├── vector_store.py      # 向量存储
│   ├── structured_wiki.py   # 结构化维基
│   └── knowledge_base.py    # 统一知识库
├── factor_library/          # 因子库(AQRA风格)
│   ├── factor_library.py    # 因子定义和计算
│   └── factor_analyzer.py   # IC/IR分析
├── vertical_agents/         # 垂直智能体
│   ├── alpha_agent.py       # Alpha策略执行
│   ├── factor_agent.py      # 因子研究
│   ├── risk_agent.py        # 风险管理
│   ├── review_agent.py      # 审查优化
│   └── research_agent.py    # 研报分析
├── quant/                   # 量化分析模块
│   ├── quant_analyzer.py    # 量化分析器
│   ├── data_simulator.py    # 数据模拟器
│   ├── macro_scenario_analyzer.py  # 宏观情景分析
│   └── chart_generator.py   # 图表生成器
├── research/                # 研报分析模块
│   ├── document_parser.py   # 文档解析器
│   ├── keyword_extractor.py # 关键词提取器
│   ├── chart_analyzer.py    # 图表分析器
│   └── report_fetcher.py    # 研报获取器
├── notification/            # 通知服务模块
│   ├── message_sender.py    # 消息发送器(PushPlus)
│   ├── task_scheduler.py    # 定时任务调度器
│   ├── message_queue.py     # 消息队列
│   └── market_notification_service.py  # 市场通知服务
└── utils/                   # 工具模块
    ├── logging_utils.py     # 日志工具
    ├── data_utils.py        # 数据工具
    └── time_utils.py        # 时间工具
```

## 🚀 快速开始

### 环境要求
- Python 3.10+
- 依赖库见 `requirements.txt`

### 安装依赖
```bash
cd super_agent
pip install -r requirements.txt
```

### 运行主程序
```bash
python main.py
```

### 启动通知服务
```bash
python start_notification_service.py
```

### 运行测试
```bash
# 量化分析测试
python test_quant_analysis.py

# 研报分析测试
python test_research.py

# 情景分析测试
python test_scenario_analysis.py

# 通知服务测试
python test_notification.py
```

## 🔧 配置说明

### PushPlus通知配置

#### 方式一：环境变量（推荐）
```bash
export PUSH_PLUS_TOKEN=your_pushplus_token
```

#### 方式二：代码中设置
在 `notification/message_sender.py` 中配置：
```python
self.token = 'your_pushplus_token'
```

#### 方式三：创建 .env 文件
```bash
# 创建 .env 文件
echo "PUSH_PLUS_TOKEN=your_pushplus_token" > .env
```

### 消息同步机制

#### 市场通知（每日）
- **08:30**: 股市热点报告（日韩股市、美股热点统计）
- **每周五08:30**: 股市周报
- **每月1日08:30**: 股市月报
- **每年1月/7月1日08:30**: 股市半年报
- **每周一08:30**: 强势因子推荐报告

#### 知识体系更新通知（每4小时）
- **08:00**: 知识体系更新统计 + 宏观经济数据
- **12:00**: 知识体系更新统计 + 宏观经济数据
- **16:00**: 知识体系更新统计 + 宏观经济数据
- **20:00**: 知识体系更新统计 + 宏观经济数据
- **24:00**: 知识体系更新统计 + 宏观经济数据

#### 数据更新任务（每4小时）
- **08:00**: 经济数据抓取、知识库更改记录
- **12:00**: 经济数据抓取、知识库更改记录
- **16:00**: 经济数据抓取、知识库更改记录
- **20:00**: 经济数据抓取、知识库更改记录
- **24:00**: 经济数据抓取、知识库更改记录

#### 其他定时任务
- **15:30**: 每日数据截面生成（交易结束后）
- **每周五10:00**: 周度预测验证报告
- **23:59**: 每日数据归档

#### 消息队列机制
系统使用消息队列确保消息可靠发送：
1. 消息进入队列后立即保存到本地
2. 发送失败时自动重试（最多3次）
3. 重试失败的消息会记录到日志并在下次发送时重试

### 环境变量
```bash
export OPENAI_API_KEY=your_key
export DEEPSEEK_API_KEY=your_key
export KIMI_API_KEY=your_key
export GLM_API_KEY=your_key
export PUSH_PLUS_TOKEN=your_pushplus_token
export THS_USERNAME=your_ths_username
export THS_PASSWORD=your_ths_password
```

### 同花顺数据接口配置

系统支持同花顺数据接口获取真实股票数据，配置方式：

#### 方式一：环境变量
```bash
export THS_USERNAME=ceshi5101
export THS_PASSWORD=76wPY4Uf
```

#### 方式二：创建 .env 文件
```bash
cp .env.example .env
# 编辑 .env 文件，填写 THS_USERNAME 和 THS_PASSWORD
```

#### 方式三：代码中设置（不推荐）
在 `config.py` 中配置：
```python
config.ths.username = 'your_username'
config.ths.password = 'your_password'
```

**注意**: 同花顺账号信息属于敏感信息，请勿提交到版本控制系统！系统会自动忽略 `.env` 文件。

### 数据自动归档

系统会自动归档每日数据：
- 归档目录: `./data/archive/`
- 归档内容: 市场概况、市场统计、热门股票、行业表现
- 报告归档: 早间/午间/下午/晚间/每日汇总报告
- 自动清理: 保留最近30天的数据，自动删除旧数据

## 📊 输出文件

系统运行后会在 `output/` 目录生成以下文件：
- `period_returns.png` - 各时间段收益率对比图
- `equity_curve.png` - 收益曲线图
- `factor_ic.png` - 因子IC分析图
- `csi300_composition.png` - 沪深300成分分析图
- `sector_distribution.png` - 行业分布图
- `statistics_summary.png` - 统计摘要表
- `daily_report_YYYY-MM-DD.json` - 日报数据
- `scenario_analysis_2026H2.json` - 情景分析报告

## 📈 2026下半年市场预测

基于宏观情景分析（美联储利率不变+日韩股市崩盘+央行2万亿救市）：

| 指标 | 数值 |
|------|------|
| 预期收益率 | +16.73% |
| 年化收益率 | +34.67% |
| 夏普比率 | 1.50 |
| 最大回撤 | -12.66% |

### 推荐行业
- **银行**: +16.0% (强烈推荐)
- **科技成长**: +14.0% (强烈推荐)
- **基建**: +12.0% (强烈推荐)
- **非银行金融**: +10.0% (强烈推荐)

## ☁️ 云服务器部署（24小时不间断运行）

为了确保数据后台推送在TRAE关闭或电脑关机后仍能持续运行，推荐部署到云服务器。

### 方式一：Docker部署（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/zhongerhenglu/AIandBusinessInovation_xiaochuangai.git
cd AIandBusinessInovation_xiaochuangai

# 2. 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件，填写 PUSH_PLUS_TOKEN, THS_USERNAME, THS_PASSWORD 等

# 3. 启动服务
docker-compose up -d --build

# 4. 查看日志
docker logs -f super_agent_service

# 5. 重启服务
docker-compose restart

# 6. 停止服务
docker-compose down
```

### 方式二：自动部署脚本

```bash
# 使用部署脚本一键部署到云服务器
chmod +x deploy_to_cloud.sh
./deploy_to_cloud.sh root@your_server_ip
```

### 方式三：手动部署到Linux服务器

```bash
# 1. 登录服务器
ssh root@your_server_ip

# 2. 安装依赖
apt-get update && apt-get install -y python3 python3-pip git
pip3 install -r requirements.txt

# 3. 克隆仓库
git clone https://github.com/zhongerhenglu/AIandBusinessInovation_xiaochuangai.git
cd AIandBusinessInovation_xiaochuangai

# 4. 设置环境变量
export PUSH_PLUS_TOKEN=your_token
export THS_USERNAME=ceshi5101
export THS_PASSWORD=76wPY4Uf

# 5. 使用nohup后台运行
nohup python3 start_background_service.py > service.log 2>&1 &

# 6. 查看进程
ps aux | grep start_background_service
```

### 部署注意事项

1. **选择云服务器**: 阿里云、腾讯云、华为云等，推荐配置：2核4G内存
2. **防火墙设置**: 确保服务器可以访问外网（PushPlus、同花顺API）
3. **数据持久化**: 使用Docker volumes或手动挂载目录保存数据
4. **日志监控**: 定期查看日志确保服务正常运行
5. **自动重启**: 使用Docker restart: always或systemd服务

### Docker Compose配置说明

```yaml
version: '3.8'

services:
  super-agent:
    restart: always          # 容器退出自动重启
    environment:             # 通过环境变量传递敏感信息
      - PUSH_PLUS_TOKEN=${PUSH_PLUS_TOKEN}
      - THS_USERNAME=${THS_USERNAME}
      - THS_PASSWORD=${THS_PASSWORD}
    volumes:                 # 数据持久化存储
      - ./data:/app/data
      - ./knowledge:/app/knowledge
      - ./logs:/app/logs
```

## 📦 提交为GitHub项目

### 创建GitHub仓库

1. 在 GitHub 上创建新仓库
2. 将项目文件推送到仓库：

```bash
cd super_agent
git init
git add .
git commit -m "Initial commit: Super Agent AI量化投资智能体系统"
git remote add origin https://github.com/your-username/super-agent.git
git push -u origin main
```

### 项目结构说明

提交前请确保包含以下核心文件：

| 文件/目录 | 说明 | 是否必需 |
|-----------|------|----------|
| `README.md` | 项目说明文档 | ✅ |
| `requirements.txt` | Python依赖 | ✅ |
| `config.py` | 系统配置 | ✅ |
| `main.py` | 主入口 | ✅ |
| `notification/` | 通知服务模块 | ✅ |
| `quant/` | 量化分析模块 | ✅ |
| `research/` | 研报分析模块 | ✅ |
| `vertical_agents/` | 垂直智能体 | ✅ |
| `factor_library/` | 因子库 | ✅ |
| `brain/` | 大脑层 | ✅ |
| `perception/` | 感知层 | ✅ |
| `action/` | 行动层 | ✅ |
| `knowledge/` | 知识层 | ✅ |
| `utils/` | 工具模块 | ✅ |

### 推送注意事项

1. **敏感信息**: 请确保 `notification/message_sender.py` 中的 PushPlus Token 使用环境变量
2. **API密钥**: LLM API密钥应通过环境变量配置，不要硬编码
3. **日志文件**: 将 `logs/` 加入 `.gitignore`
4. **数据文件**: 将 `data/archive/` 加入 `.gitignore`

### .gitignore 示例

```gitignore
# Logs
logs/
*.log

# Data
data/archive/
*.parquet
*.json

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
env/

# Output
output/*.png

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 代码规范
- 遵循 PEP 8 代码风格
- 添加详细的注释
- 编写单元测试

### 提交规范
- `feat`: 新功能
- `fix`: 修复Bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试更新

## 📄 许可证

MIT License

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件

---

**Super Agent** - AI驱动的量化投资智能体系统