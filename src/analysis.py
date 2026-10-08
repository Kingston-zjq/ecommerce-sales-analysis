"""业务分析：时间趋势、商品/国家结构、RFM 客户分层。"""

import numpy as np
import pandas as pd


def add_amount(df: pd.DataFrame) -> pd.DataFrame:
    """新增销售额与月份/星期等派生字段。"""
    d = df.copy()
    d["Amount"] = d["Quantity"] * d["UnitPrice"]
    d["year_month"] = d["InvoiceDate"].dt.to_period("M").astype(str)
    d["month"] = d["InvoiceDate"].dt.month
    d["weekday"] = d["InvoiceDate"].dt.dayofweek  # 0=周一
    d["weekday_name"] = d["InvoiceDate"].dt.day_name()
    d["hour"] = d["InvoiceDate"].dt.hour
    return d


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """月度销售趋势。"""
    d = add_amount(df)
    g = d.groupby("year_month").agg(
        订单数=("InvoiceNo", "nunique"),
        销售额=("Amount", "sum"),
        客户数=("CustomerID", "nunique"),
        平均客单价=("Amount", "mean"),
    ).reset_index()
    return g


def weekday_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """星期分布（0=周一）。"""
    d = add_amount(df)
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    g = d.groupby("weekday_name").agg(
        订单数=("InvoiceNo", "nunique"),
        销售额=("Amount", "sum"),
    ).reindex(order).reset_index()
    g["销售额占比"] = g["销售额"] / g["销售额"].sum()
    return g


def hour_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """下单时段分布。"""
    d = add_amount(df)
    g = d.groupby("hour").agg(订单数=("InvoiceNo", "nunique"), 销售额=("Amount", "sum")).reset_index()
    return g


def country_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """国家维度结构。"""
    d = add_amount(df)
    g = d.groupby("Country").agg(
        订单数=("InvoiceNo", "nunique"),
        销售额=("Amount", "sum"),
        客户数=("CustomerID", "nunique"),
        件数=("Quantity", "sum"),
    ).reset_index().sort_values("销售额", ascending=False)
    g["销售额占比"] = g["销售额"] / g["销售额"].sum()
    g["客单价"] = g["销售额"] / g["订单数"]
    return g


def product_breakdown(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """商品维度结构。"""
    d = add_amount(df)
    g = d.groupby(["StockCode", "Description"]).agg(
        销售额=("Amount", "sum"),
        件数=("Quantity", "sum"),
        订单数=("InvoiceNo", "nunique"),
    ).reset_index().sort_values("销售额", ascending=False)
    return g.head(top_n)


def rfm_segmentation(df: pd.DataFrame, reference_date=None) -> pd.DataFrame:
    """RFM 客户价值分层。

    返回 DataFrame，列：CustomerID, Recency, Frequency, Monetary,
    以及 R/F/M 得分（1-4 分）与客户分群标签。
    """
    d = add_amount(df)
    if reference_date is None:
        reference_date = d["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = d.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (reference_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Amount", "sum"),
    ).reset_index()

    # 分位数打分（1=差, 4=好；Recency 越小越好需反向）
    rfm["R_score"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)

    rfm["RFM_score"] = rfm["R_score"] * 100 + rfm["F_score"] * 10 + rfm["M_score"]

    def seg(r, f, m):
        if r >= 3 and f >= 3 and m >= 3:
            return "重要价值客户"
        if r >= 3 and f >= 3:
            return "重要保持客户"
        if r >= 3 and f < 3:
            return "新客户"
        if f >= 3 and m >= 3:
            return "重要挽留客户"
        if f >= 2:
            return "一般客户"
        return "流失客户"

    rfm["客户分群"] = rfm.apply(lambda x: seg(x["R_score"], x["F_score"], x["M_score"]), axis=1)
    return rfm


def rfm_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """RFM 分群汇总。"""
    g = rfm.groupby("客户分群").agg(
        客户数=("CustomerID", "nunique"),
        平均消费=("Monetary", "mean"),
        总消费=("Monetary", "sum"),
        平均频次=("Frequency", "mean"),
    ).reset_index().sort_values("总消费", ascending=False)
    return g


def top_customers(rfm: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """消费额 Top 客户。"""
    return rfm.sort_values("Monetary", ascending=False).head(n)
