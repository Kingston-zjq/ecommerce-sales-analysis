"""数据可视化：统一风格的专业图表，输出到 reports/figures/。"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.config import FIGURE_DIR, apply_style

apply_style()


def _save(fig, name):
    path = FIGURE_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_monthly_trend(monthly: pd.DataFrame):
    """月度销售趋势（双轴）。"""
    fig, ax1 = plt.subplots(figsize=(10, 5.5))
    x = range(len(monthly))
    ax1.plot(x, monthly["销售额"], marker="o", color="#2C7BB6", label="销售额", linewidth=2)
    ax1.set_ylabel("销售额（£）", color="#2C7BB6")
    ax1.tick_params(axis="y", labelcolor="#2C7BB6")

    ax2 = ax1.twinx()
    ax2.bar(x, monthly["订单数"], alpha=0.25, color="#D7191C", label="订单数")
    ax2.set_ylabel("订单数", color="#D7191C")
    ax2.tick_params(axis="y", labelcolor="#D7191C")

    ax1.set_xticks(list(x))
    ax1.set_xticklabels(monthly["year_month"], rotation=45, ha="right")
    ax1.set_title("月度销售趋势（销售额 vs 订单数）")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
    return _save(fig, "fig01_monthly_trend.png")


def plot_weekday(weekday: pd.DataFrame):
    """星期销售分布。"""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(weekday["weekday_name"], weekday["销售额"], color="#2C7BB6")
    ax.set_ylabel("销售额（£）")
    ax.set_title("星期维度销售额分布")
    ax.tick_params(axis="x", rotation=30)
    return _save(fig, "fig02_weekday.png")


def plot_hour(hour: pd.DataFrame):
    """时段销售分布。"""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(hour["hour"], hour["销售额"], color="#66C2A5")
    ax.set_xlabel("小时")
    ax.set_ylabel("销售额（£）")
    ax.set_title("下单时段分布（销售额）")
    return _save(fig, "fig03_hour.png")


def plot_country(country: pd.DataFrame, top_n: int = 8):
    """国家销售结构（Top N）。"""
    d = country.head(top_n)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(d)))
    ax.barh(d["Country"][::-1], d["销售额"][::-1], color=colors[::-1])
    ax.set_xlabel("销售额（£）")
    ax.set_title(f"销售额 Top {top_n} 国家")
    return _save(fig, "fig04_country.png")


def plot_product(product: pd.DataFrame, top_n: int = 10):
    """商品销售额 Top N。"""
    d = product.head(top_n)
    # 商品描述过长，截断显示
    labels = [desc[:20] + ("…" if len(desc) > 20 else "") for desc in d["Description"]]
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = plt.cm.Reds(np.linspace(0.4, 0.9, len(d)))
    ax.barh(range(len(d))[::-1], d["销售额"][::-1], color=colors[::-1])
    ax.set_yticks(range(len(d))[::-1])
    ax.set_yticklabels(labels[::-1], fontsize=8)
    ax.set_xlabel("销售额（£）")
    ax.set_title(f"商品销售额 Top {top_n}")
    return _save(fig, "fig05_product.png")


def plot_rfm(rfm: pd.DataFrame):
    """RFM 客户分群构成。"""
    summary = rfm.groupby("客户分群")["CustomerID"].count().reset_index()
    summary.columns = ["客户分群", "客户数"]
    summary = summary.sort_values("客户数", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#2C7BB6", "#66C2A5", "#FDAE61", "#D7191C", "#5E4FA2", "#ABD9E9"]
    wedges, _, autotexts = ax.pie(
        summary["客户数"], labels=summary["客户分群"], autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.75)
    for t in autotexts:
        t.set_color("white")
        t.set_fontsize(9)
    ax.set_title("RFM 客户价值分群构成")
    return _save(fig, "fig06_rfm.png")


def plot_rfm_scatter(rfm: pd.DataFrame):
    """RFM 分布散点（消费额 vs 频次，按近度着色）。"""
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(rfm["Frequency"], rfm["Monetary"], c=rfm["Recency"],
                    cmap="RdYlBu_r", s=40, alpha=0.7, edgecolors="w", linewidth=0.5)
    ax.set_xlabel("购买频次（Frequency）")
    ax.set_ylabel("消费金额（Monetary，£）")
    ax.set_title("客户 RFM 分布（颜色=近度 Recency，越蓝越近）")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("Recency（天）")
    return _save(fig, "fig07_rfm_scatter.png")


def _fmt_itemset(x) -> str:
    """把项集格式化为可读字符串，兼容字符串与 frozenset。"""
    if isinstance(x, (frozenset, set)):
        return " + ".join(sorted(x))
    return str(x)


def plot_rules(rules: pd.DataFrame):
    """关联规则提升度 Top 15。兼容中/英文列名与字符串/集合前件。"""
    d = rules.head(15)
    if "前件" in d.columns:
        ante, cons, lift = "前件", "后件", "提升度"
    else:
        ante, cons, lift = "antecedents", "consequents", "lift"
    labels = [f"{_fmt_itemset(r[ante])} → {_fmt_itemset(r[cons])}" for _, r in d.iterrows()]
    fig, ax = plt.subplots(figsize=(10, 7))
    y = range(len(d))[::-1]
    ax.barh(list(y), d[lift], color="#5E4FA2")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("提升度（Lift）")
    ax.set_title("关联规则提升度 Top 15（前件 → 后件）")
    ax.axvline(x=1, color="gray", linestyle="--", linewidth=1)
    return _save(fig, "fig08_rules.png")


def plot_rules_scatter(rules: pd.DataFrame):
    """关联规则散点（支持度 vs 置信度，按提升度着色）。兼容中/英文列名。"""
    if "支持度" in rules.columns:
        sup, conf, lift = "支持度", "置信度", "提升度"
    else:
        sup, conf, lift = "support", "confidence", "lift"
    fig, ax = plt.subplots(figsize=(9, 6))
    sc = ax.scatter(rules[sup], rules[conf], c=rules[lift],
                    cmap="YlGnBu", s=rules[lift] * 40, alpha=0.7,
                    edgecolors="w", linewidth=0.5)
    ax.set_xlabel("支持度（Support）")
    ax.set_ylabel("置信度（Confidence）")
    ax.set_title("关联规则散点（气泡大小/颜色=提升度）")
    cbar = fig.colorbar(sc, ax=ax)
    cbar.set_label("提升度（Lift）")
    return _save(fig, "fig09_rules_scatter.png")


def plot_forecast(series: pd.Series, forecast: pd.DataFrame):
    """月度序列与未来预测。"""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x_hist = list(series.index)
    y_hist = series.values
    ax.plot(x_hist, y_hist, marker="o", color="#2C7BB6", label="历史销售额", linewidth=2)

    # 拼接未来点
    x_future = list(forecast["月份"])
    y_future = forecast["预测销售额"].values
    x_all = x_hist + x_future
    y_all = list(y_hist) + list(y_future)
    ax.plot(x_all, y_all, linestyle="--", color="#D7191C", label="预测", linewidth=1.5)
    ax.scatter(x_future, y_future, color="#D7191C", zorder=5)

    ax.set_ylabel("销售额（£）")
    ax.set_title("月度销售额与未来 3 个月预测（Holt 趋势平滑）")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="best")
    return _save(fig, "fig10_forecast.png")
