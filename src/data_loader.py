"""数据加载与质量体检。

说明：默认使用压缩样本数据（随仓库提交），保证他人可一键跑通；
如需复现完整结果，将环境变量 USE_FULL_DATA=1 即切换到完整 45MB 数据。
"""

import os

import numpy as np
import pandas as pd

from src.config import RAW_DATA, RAW_ENCODING, SAMPLE_DATA, SAMPLE_DATA_GZ


def _resolve_sample_path():
    """样本数据优先用 .csv，不存在则回退到 .csv.gz（pandas 可自动解压）。"""
    if SAMPLE_DATA.exists():
        return SAMPLE_DATA
    if SAMPLE_DATA_GZ.exists():
        return SAMPLE_DATA_GZ
    return SAMPLE_DATA


def load_raw() -> pd.DataFrame:
    """加载原始交易明细（默认样本，可切完整数据）。"""
    use_full = os.environ.get("USE_FULL_DATA") == "1"
    if use_full and RAW_DATA.exists():
        path, encoding = RAW_DATA, RAW_ENCODING
    else:
        path, encoding = _resolve_sample_path(), "utf-8-sig"
    df = pd.read_csv(path, encoding=encoding, low_memory=False)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    return df


def quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """输出数据质量体检表。"""
    rows = []
    total = len(df)

    rows.append(("总行数", f"{total:,}"))
    rows.append(("唯一发票数", f"{df['InvoiceNo'].nunique():,}"))
    rows.append(("唯一客户数", f"{df['CustomerID'].nunique():,}"))
    rows.append(("唯一商品数", f"{df['StockCode'].nunique():,}"))
    rows.append(("时间范围", f"{df['InvoiceDate'].min()} ~ {df['InvoiceDate'].max()}"))
    rows.append(("覆盖国家数", str(df["Country"].nunique())))

    for col in ["CustomerID", "Description"]:
        miss = df[col].isna().sum()
        rows.append((f"{col} 缺失", f"{miss:,} ({miss / total:.1%})"))

    rows.append(("重复行", f"{df.duplicated().sum():,}"))
    rows.append(("负数量（退货）", f"{(df['Quantity'] < 0).sum():,} ({(df['Quantity'] < 0).mean():.2%})"))
    rows.append(("单价 <= 0", f"{(df['UnitPrice'] <= 0).sum():,} ({(df['UnitPrice'] <= 0).mean():.2%})"))
    rows.append(("取消订单（C开头）", f"{df['InvoiceNo'].str.startswith('C', na=False).sum():,}"))

    return pd.DataFrame(rows, columns=["指标", "数值"])


def load_clean() -> pd.DataFrame:
    """加载并完成基础清洗的数据（供分析模块使用）。"""
    df = load_raw()
    df = df.copy()
    # 去重
    df = df.drop_duplicates()
    # 去掉无客户ID的记录（RFM/购物篮分析需要客户标识）
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int)
    # 只保留正常销售：数量>0 且 单价>0
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    return df.reset_index(drop=True)
