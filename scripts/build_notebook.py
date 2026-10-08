"""构建 notebooks/ecommerce_analysis.ipynb（供生成后执行）。

用法：
    python scripts/build_notebook.py
"""

import sys
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OUT = ROOT / "notebooks" / "ecommerce_analysis.ipynb"


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


CELLS = [
    md("""
# 电商销售数据分析

**数据来源**：UCI Machine Learning Repository · Online Retail 数据集
（英国某线上零售商 2010-12 ~ 2011-12 的真实交易明细）

**分析目标**：在真实电商交易数据上完成从数据质量体检、销售分析、客户价值分层（RFM）、
购物篮关联规则到销售预测的完整链路。

**使用说明**：本 notebook 默认加载随仓库提交的抽样样本（3.2 万行），保证可一键复现；
设置环境变量 `USE_FULL_DATA=1` 可切换到完整 45 万行数据。

---

## 0. 环境准备
"""),
    code("""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# 让 notebook 能 import 到 src 包
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

from src import analysis, data_loader, market_basket, modeling, visualize
from src.config import apply_style

apply_style()
pd.set_option("display.unicode.east_asian_width", True)
pd.set_option("display.max_columns", 50)

from IPython.display import Image, display


def show(path):
    # 重新加载 PNG 显示（绘图函数内部会关闭 figure，因此不能依赖 inline 输出）
    display(Image(filename=str(path)))


print("工作目录:", ROOT)
"""),

    md("""
---

## 1. 数据加载与质量体检

第一步不是算指标，而是**搞清楚这份数据能回答什么问题**。
"""),
    code("""
raw = data_loader.load_raw()
print(f"原始数据：{raw.shape[0]:,} 行 × {raw.shape[1]} 列")
raw.head()
"""),
    code("""
quality = data_loader.quality_report(raw)
quality
"""),
    md("""
### 1.1 关键数据质量问题

- **CustomerID 缺失约 26%**：多为无账户的散客或退货记录，无法做客户级分析
- **负数量（退货）约 1.9%**：发票号以 C 开头的是取消订单
- **单价 ≤ 0 约 0.5%**：多为赠品/坏损调整，不应计入销售
- **重复行**：同一发票完全相同的行需要去重

> 分析口径：清洗时剔除无客户ID记录与退货/异常单价，
> 得到「正常销售交易」用于客户分析与购物篮分析。
"""),
    code("""
df = data_loader.load_clean()
print(f"清洗后：{df.shape[0]:,} 行，{df['InvoiceNo'].nunique():,} 张发票，"
      f"{df['CustomerID'].nunique():,} 个客户")
print(f"总销售额：£{(df['Quantity'] * df['UnitPrice']).sum():,.0f}")
"""),

    md("""
---

## 2. 销售趋势分析

### 2.1 月度趋势
"""),
    code("""
monthly = analysis.monthly_trend(df)
show(visualize.plot_monthly_trend(monthly))
monthly
"""),
    md("""
**观察**：9-11 月是明显的销售旺季（圣诞备货），9 月出现峰值；
2011-12 只有 9 天数据，不代表当月真实水平。
"""),
    code("""
weekday = analysis.weekday_distribution(df)
hour = analysis.hour_distribution(df)
show(visualize.plot_weekday(weekday))
show(visualize.plot_hour(hour))
weekday
"""),
    md("""
**观察**：周中（周二至周四）是下单高峰，**周六无交易**（该零售商周六不营业）；
时段集中在 10:00-15:00，与英国办公时间一致，说明客户以批发商/企业采购为主。
"""),

    md("""
---

## 3. 商品与国家结构
"""),
    code("""
country = analysis.country_breakdown(df)
show(visualize.plot_country(country))
country.head(10)
"""),
    code("""
product = analysis.product_breakdown(df, top_n=10)
show(visualize.plot_product(product))
product
"""),
    md("""
**观察**：英国本土占绝对主导（样本中约 80%+），其他市场以欧洲为主；
商品结构高度分散，头部商品多为装饰类、礼品类小商品，客单价低但复购率高。
"""),

    md("""
---

## 4. RFM 客户价值分层

RFM 是最经典的客户价值模型：

- **R（Recency）**：最近一次购买距今天数（越小越好）
- **F（Frequency）**：购买次数
- **M（Monetary）**：累计消费金额
"""),
    code("""
rfm = analysis.rfm_segmentation(df)
summary = analysis.rfm_summary(rfm)
show(visualize.plot_rfm(rfm))
summary
"""),
    code("""
show(visualize.plot_rfm_scatter(rfm))
analysis.top_customers(rfm, 10)
"""),
    md("""
**观察与策略**：

- **重要价值客户（R高F高M高）**：核心客群，优先维护，VIP 服务
- **重要挽留客户（F/M高但R低）**：有流失风险的高价值客户，需定向召回
- **新客户**：首购转化，重点培养复购习惯
- **流失客户**：低成本召回或放弃，控制营销预算
"""),

    md("""
---

## 5. 购物篮关联分析

基于 Apriori 算法挖掘「买 A 的顾客也倾向买 B」：

- **支持度（Support）**：同时包含 A、B 的订单占比
- **置信度（Confidence）**：买 A 的人中有多少也买 B
- **提升度（Lift）**：A 对 B 的拉动倍数，>1 为正相关，越大越强
"""),
    code("""
basket = market_basket.build_basket(df)
print(f"购物篮数：{len(basket):,}，商品数：{basket.shape[1]:,}")
frequent = market_basket.frequent_itemsets(basket, min_support=0.02)
rules = market_basket.get_rules(frequent, metric="lift", min_threshold=1.0)
print(f"频繁项集：{len(frequent)}，关联规则：{len(rules)}")
"""),
    code("""
top_rules = market_basket.top_rules(rules, n=15)
show(visualize.plot_rules(top_rules))
top_rules
"""),
    md("""
**观察**：最强关联集中在「同系列不同款式」——圣诞木星星/心形、
园艺跪垫、午餐盒、Regency 茶具系列。这些是**天然的捆绑销售与推荐组合**：
顾客买了一件还会买同系列其他款式做搭配。
"""),
    code("""
show(visualize.plot_rules_scatter(rules))
"""),

    md("""
---

## 6. 销售预测

对月度销售额做时间序列预测。样本只有 13 个月，季节项统计意义不足，
因此使用 **Holt 线性趋势平滑**，并与朴素法、移动平均做回测对比。
"""),
    code("""
series = modeling.build_monthly_series(df)
model_comparison = modeling.evaluate_models(series, test_size=3)
model_comparison
"""),
    md("""
**观察**：移动平均表现最优（MAPE 56%），Holt 次之。这说明序列噪声大、
趋势不显著——**短序列上简单模型反而更稳**，强行上复杂模型容易过拟合。
"""),
    code("""
forecast = modeling.forecast_next(series, horizon=3)
show(visualize.plot_forecast(series, forecast))
forecast
"""),

    md("""
---

## 7. 小结

| 分析方向 | 核心结论 |
| :--- | :--- |
| 数据质量 | CustomerID 缺失 26%、退货 1.9%、异常单价 0.5%，清洗后 22,679 行有效交易 |
| 时间趋势 | 9-11 月圣诞备货旺季；周中高峰、周六不营业；下单集中在 10-15 点 |
| 商品结构 | 英国主导、欧洲市场为主；头部商品为礼品/装饰类小商品 |
| RFM 分层 | 129 个重要价值客户贡献 £241k（占 46%），是核心维护对象 |
| 购物篮 | 同系列商品强关联（Lift 20+），是天然捆绑销售组合 |
| 销售预测 | 短序列下移动平均最优（MAPE 56%），预测需保持谨慎 |

**完整图表与报告**：见 `reports/report.html`
"""),
]

def main():
    nb = nbf.v4.new_notebook(cells=CELLS)
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.13"},
    }
    nbf.write(nb, str(OUT))
    print(f"已生成：{OUT}")


if __name__ == "__main__":
    main()