# 电商销售数据分析作品集

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data](https://img.shields.io/badge/Data-UCI%20Online%20Retail-orange.svg)](https://archive.ics.uci.edu/dataset/352/online+retail)

> 基于 **UCI Online Retail** 真实电商交易数据（2010-12 ~ 2011-12，英国线上零售商），
> 完成从数据清洗、销售分析、**RFM 客户分层**、**购物篮关联规则**到**销售预测**的完整分析链路。

**作者**：Kingston-zjq ｜ **数据分析作品集项目**

---

## 一、项目亮点

- **真实交易数据**：54 万行订单明细（仓库内含抽样样本 3.2 万行可一键复现）
- **完整业务链路**：数据体检 → 清洗 → 销售分析 → 客户分层 → 关联挖掘 → 预测建模
- **RFM 客户价值模型**：六类客户分层 + 可落地的运营策略建议
- **购物篮关联分析**：Apriori 算法，挖掘出 Lift 20+ 的强关联商品组合
- **诚实的建模结论**：短序列预测明确说明局限，不硬凑复杂模型
- **一键复现**：`python scripts/run_all.py` 3 秒跑完全流程

## 二、核心结论速览

| 分析方向 | 核心结论 |
| :--- | :--- |
| 数据质量 | CustomerID 缺失 26%、退货 1.9%、异常单价 0.5% —— 清洗后 22,679 行有效交易 |
| 时间节奏 | **9-11 月圣诞备货旺季**（9 月峰值 £97k）；周中高峰、周六不营业；下单集中在 10-15 点 |
| 客户结构 | RFM 分层中 **129 个「重要价值客户」贡献 £241k（占 46%）**，是核心维护对象 |
| 购物篮 | 同系列商品强关联：圣诞木星星/心形（Lift 24.6）、Regency 茶具（Lift 21.0）等 |
| 销售预测 | 13 个月短序列上**移动平均最优**（MAPE 56%），说明该场景不宜强行复杂建模 |

## 三、查看方式

| 内容 | 入口 |
| :--- | :--- |
| 📊 **完整可视化报告**（含全部图表，强烈推荐） | [点击在线查看](https://kingston-zjq.github.io/ecommerce-sales-analysis/reports/report.html) |
| 📓 **交互式分析 Notebook** | [notebooks/ecommerce_analysis.ipynb](notebooks/ecommerce_analysis.ipynb) |
| 📈 **图表目录**（10 张） | [reports/figures/](reports/figures/) |
| 📋 **指标明细表**（11 份 CSV） | [reports/tables/](reports/tables/) |
| 💼 **项目介绍文案** | [docs/project_intro.md](docs/project_intro.md) |

> ⚠️ **报告与网页请用在线链接打开**：GitHub 不渲染仓库里的 `.html` 文件（点开会显示源码），
> 所以完整报告和项目主页都通过 GitHub Pages 在线查看（见上表链接）。
> 若 Notebook 显示 "Unable to render code block"（GitHub 渲染器偶发问题），
> 可用 nbviewer 兜底：
> https://nbviewer.org/github/Kingston-zjq/ecommerce-sales-analysis/blob/main/notebooks/ecommerce_analysis.ipynb

## 四、项目结构

```
ecommerce-sales-analysis/
├── data/
│   ├── raw/                      原始数据（本地，不入库）
│   └── processed/
│       └── OnlineRetail_sample.csv.gz   抽样样本（随仓库提交，441 KB）
├── src/
│   ├── config.py                 路径、字体与绘图风格配置
│   ├── data_loader.py            数据加载与质量体检
│   ├── analysis.py               时间/国家/商品分析与 RFM 分层
│   ├── market_basket.py          Apriori 购物篮关联规则
│   ├── modeling.py               销售预测（Holt / 移动平均 / 朴素法）
│   ├── visualize.py              10 张统一风格图表
│   └── report.py                 自包含 HTML 报告生成
├── scripts/
│   ├── run_all.py                一键运行完整流程
│   ├── build_notebook.py         生成分析 Notebook
│   └── optimize_notebook.py      压缩 Notebook（保证 GitHub 正常渲染）
├── notebooks/
│   └── ecommerce_analysis.ipynb  交互式分析笔记（含全部输出）
├── docs/
│   └── project_intro.md          项目介绍文案包（简历/作品集多版本）
└── reports/
    ├── figures/                  10 张图表 PNG
    ├── tables/                   11 份指标明细 CSV
    └── report.html               完整可视化报告（自包含）
```

## 五、快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 一键运行完整流程（加载 → 清洗 → EDA → RFM → 购物篮 → 预测 → 报告，约 3 秒）
python scripts/run_all.py

# 3. 重新生成并执行 Notebook（可选）
python scripts/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/ecommerce_analysis.ipynb
python scripts/optimize_notebook.py
```

> 想跑完整 45 万行数据？把 `data/raw/OnlineRetail.csv` 放入后设置
> 环境变量 `USE_FULL_DATA=1` 再运行即可（样本统计口径见 `docs/`）。

## 六、数据说明

| 项目 | 内容 |
| :--- | :--- |
| 数据来源 | [UCI Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail) |
| 时间跨度 | 2010-12-01 ~ 2011-12-09 |
| 原始规模 | 541,909 行 × 8 列，25,900 张发票，4,372 位客户，4,070 种商品 |
| 字段 | InvoiceNo（发票号）、StockCode（商品编码）、Description（描述）、Quantity（数量）、InvoiceDate（时间）、UnitPrice（单价，£）、CustomerID（客户ID）、Country（国家） |
| 仓库内样本 | 按发票号随机抽样 1,500 张发票 → 32,003 行（gzip 441 KB），抽样种子 42 保证可复现 |

## 七、方法论说明

- **清洗口径**：去重 → 剔除 CustomerID 缺失 → 剔除退货（负数量/C开头）→ 剔除单价≤0
- **RFM 打分**：按四分位数 1-4 打分，Recency 反向（越小分越高）
- **关联规则**：Apriori，min_support=0.02，Lift>1，mlxtend 实现
- **预测模型**：朴素法 / 3 期移动平均 / Holt 线性趋势（自实现，无 statsmodels 依赖），
  滚动回测 3 期，MAE/RMSE/MAPE 三指标对比
- **统计严谨性**：所有结论均注明样本口径，预测部分明确说明短序列局限

## 八、License

数据遵循 [UCI 数据集许可](https://archive.ics.uci.edu/)；代码部分 [MIT](LICENSE)。
