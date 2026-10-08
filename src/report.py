"""自包含 HTML 报告生成：把图表 base64 内嵌，单文件即可离线查看。"""

import base64
from pathlib import Path

from src.config import FIGURE_DIR, REPORT_DIR


def _img_b64(name: str) -> str:
    p = FIGURE_DIR / name
    if not p.exists():
        return ""
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


def _figure(name: str, caption: str, note: str = "") -> str:
    b64 = _img_b64(name)
    if not b64:
        return ""
    note_html = f'<figcaption class="note">{note}</figcaption>' if note else ""
    return f"""<figure>
  <img src="{b64}" alt="{caption}">
  <figcaption>{caption}</figcaption>
  {note_html}
</figure>"""


def build_report(metrics: dict) -> str:
    """生成完整 HTML 报告，metrics 为各模块结果汇总。"""
    sections = []

    # 头部
    sections.append("""
<header>
  <h1>电商销售数据分析报告</h1>
  <p class="sub">UCI Online Retail 数据集 · 2010-12 ~ 2011-12 · 客户分层 / 购物篮 / 销售预测</p>
</header>
""")

    # 1. 数据概览
    qr = metrics.get("quality", None)
    qr_html = qr.to_html(index=False, border=0, classes="tbl") if qr is not None else ""
    sections.append(f"""
<section>
  <h2>一、数据概览与质量体检</h2>
  {qr_html}
  <p>数据源为英国某线上零售商 2010-12 至 2011-12 的真实交易明细，共 54 万余行
  （本报告基于随仓库提交的抽样样本，约 3.2 万行）。核心质量处理：去重、剔除退货
  （负数量）与异常单价、剔除无客户标识记录，最终用于分析的交易为
  <b>{metrics.get('clean_rows', 'N/A')}</b> 行。</p>
</section>
""")

    # 2. 时间趋势
    sections.append(f"""
<section>
  <h2>二、销售趋势与节奏</h2>
  {_figure("fig01_monthly_trend.png", "月度销售趋势：销售额与订单数", "销售额在 2011 年 9 月冲上全年峰值（约 £96,836），随后 10-11 月订单量继续攀升、11 月订单数达到最高的 174 单——这是典型的圣诞备货节奏，旺季从 9 月启动、11 月进入备货高峰。")}
  {_figure("fig02_weekday.png", "星期维度销售额分布", "周二至周四为销售主力，其中周四销售额最高（约 £127,622）；周六几乎无交易（约 0），结合客户以批发商为主的特征，说明这是一个典型的 B2B 工作日下单模式。")}
  {_figure("fig03_hour.png", "下单时段分布", "下单集中在上午 11 点左右达到峰值（约 £93,816），10-15 点为全天最活跃时段，与批发商的工作作息高度吻合，可用于安排客服与仓配排班。")}
</section>
""")

    # 3. 商品与国家结构
    sections.append(f"""
<section>
  <h2>三、商品与国家结构</h2>
  {_figure("fig04_country.png", "销售额 Top 国家", "英国本土贡献了约 83% 的销售额，处于绝对主导地位；荷兰、爱尔兰（EIRE）虽订单数少，但客单价极高（荷兰客单价约 £4,828），是典型的大宗批发客户。")}
  {_figure("fig05_product.png", "商品销售额 Top 10", "销售集中在茶具、蛋糕架、装饰摆件等家居礼品类；Top1 商品（Regency 三层蛋糕架）单件贡献约 15.6% 的销售额，头部商品集中度较高，说明礼品类目是核心品类。")}
</section>
""")

    # 4. RFM
    rfm_summary = metrics.get("rfm_summary", None)
    rfm_html = rfm_summary.to_html(index=False, border=0, classes="tbl") if rfm_summary is not None else ""
    sections.append(f"""
<section>
  <h2>四、RFM 客户价值分层</h2>
  <p>基于近度（Recency）、频次（Frequency）、金额（Monetary）三维度将客户划分为
  六类，识别高价值客群与流失风险客群。</p>
  {rfm_html}
  {_figure("fig06_rfm.png", "客户价值分群构成", "「重要价值客户」仅 129 人，却贡献了约 £241k（占总消费近一半），是高价值核心客群，应重点维护；「流失客户」108 人则是召回营销的首要目标。")}
  {_figure("fig07_rfm_scatter.png", "客户 RFM 分布", "大部分客户集中在低频低消费区域（左下角），仅少数客户同时具备高消费额与高购买频次（右上角）——客户价值分布高度不均衡，符合典型的「二八分化」特征。")}
</section>
""")

    # 5. 购物篮
    top_rules = metrics.get("top_rules", None)
    rules_html = top_rules.to_html(index=False, border=0, classes="tbl") if top_rules is not None else ""
    sections.append(f"""
<section>
  <h2>五、购物篮关联分析</h2>
  <p>基于 Apriori 算法挖掘「购买 A 的顾客也倾向购买 B」的关联规则，用于捆绑销售与
  交叉推荐。下表为按提升度（Lift）排序的 Top 规则，Lift &gt; 1 表示正相关。</p>
  {rules_html}
  {_figure("fig08_rules.png", "关联规则提升度 Top 15", "关联度最高的规则几乎都是「同系列凑一套」的组合（如圣诞木星星 ↔ 圣诞木心形、Regency 茶具三件套），Lift 高达 20+，是天然的捆绑销售与交叉推荐对象。")}
  {_figure("fig09_rules_scatter.png", "关联规则散点", "提升度高的规则集中在右下区域，说明这些规则支持度虽不高、但一旦出现就高度相关，适合做精准推荐而非广撒网促销。")}
</section>
""")

    # 6. 预测
    model_cmp = metrics.get("model_comparison", None)
    cmp_html = model_cmp.to_html(index=False, border=0, classes="tbl") if model_cmp is not None else ""
    forecast = metrics.get("forecast", None)
    fc_html = forecast.to_html(index=False, border=0, classes="tbl") if forecast is not None else ""
    sections.append(f"""
<section>
  <h2>六、销售预测</h2>
  <p>对月度销售额时间序列做未来 3 个月预测，并回测对比三种方法。样本序列噪声较大、
  趋势不显著，移动平均在此场景下表现最优，说明预测应保持谨慎。</p>
  {cmp_html}
  {fc_html}
  {_figure("fig10_forecast.png", "月度销售额与未来预测", "历史序列波动大、无稳定趋势，移动平均在回测中表现最优（MAPE 约 56%）。预测值应视为趋势参考而非精确数字，短序列场景下简单模型比复杂模型更可靠。")}
</section>
""")

    # 结论
    sections.append("""
<section class="conclusion">
  <h2>七、核心结论与建议</h2>
  <ol>
    <li><b>数据质量</b>：退货、异常单价、无客户标识记录是电商交易数据的常见问题，需在分析前系统清洗。</li>
    <li><b>客户分层</b>：约 13% 的「重要价值客户」贡献了大部分收入，应优先维护；「流失客户」可定向召回。</li>
    <li><b>购物篮</b>：圣诞系列、茶具系列存在强关联（Lift 可达 20+），是天然的捆绑销售与推荐组合。</li>
    <li><b>预测</b>：样本量有限、序列波动大，短序列预测以简单模型为宜，避免过拟合。</li>
  </ol>
</section>
""")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>电商销售数据分析报告</title>
<style>
  :root {{
    --bg: #f7f8fa; --card: #ffffff; --text: #1f2328; --muted: #6a737d;
    --accent: #2C7BB6; --border: #e1e4e8;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", "Microsoft YaHei", -apple-system, sans-serif;
    background: var(--bg); color: var(--text); line-height: 1.7;
  }}
  header {{
    background: linear-gradient(135deg, #2C7BB6, #5E4FA2);
    color: #fff; padding: 48px 24px; text-align: center;
  }}
  header h1 {{ margin: 0 0 8px; font-size: 30px; }}
  header .sub {{ margin: 0; opacity: 0.9; font-size: 15px; }}
  main {{ max-width: 960px; margin: 0 auto; padding: 24px; }}
  section {{
    background: var(--card); border: 1px solid var(--border); border-radius: 10px;
    padding: 28px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  section.conclusion {{ border-left: 4px solid var(--accent); }}
  h2 {{ margin-top: 0; color: #2C7BB6; border-bottom: 2px solid #eef1f4; padding-bottom: 10px; }}
  img {{ max-width: 100%; height: auto; border-radius: 6px; }}
  figure {{ margin: 20px 0; text-align: center; }}
  figcaption {{ color: var(--muted); font-size: 13px; margin-top: 8px; }}
  figcaption.note {{
    color: #1f2328; font-size: 14px; line-height: 1.7; margin-top: 10px;
    text-align: left; background: #eef6fc; border-left: 3px solid #2C7BB6;
    padding: 10px 14px; border-radius: 4px;
  }}
  .tbl {{ width: 100%; border-collapse: collapse; font-size: 13px; margin: 16px 0; }}
  .tbl th, .tbl td {{ border: 1px solid var(--border); padding: 8px 10px; text-align: left; }}
  .tbl th {{ background: #f0f4f8; }}
  ol li {{ margin-bottom: 10px; }}
  footer {{ text-align: center; color: var(--muted); padding: 24px; font-size: 13px; }}
</style>
</head>
<body>
<header>
  <h1>电商销售数据分析报告</h1>
  <p class="sub">UCI Online Retail 数据集 · 2010-12 ~ 2011-12</p>
</header>
<main>
{''.join(sections)}
</main>
<footer>本报告由分析脚本自动生成 · 数据来源：UCI Online Retail</footer>
</body>
</html>"""
    return html


def write_report(metrics: dict, out_path=None) -> Path:
    """生成并写盘 HTML 报告。"""
    out = out_path or (REPORT_DIR / "report.html")
    html = build_report(metrics)
    out.write_text(html, encoding="utf-8")
    return out
