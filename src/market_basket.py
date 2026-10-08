"""购物篮分析（Market Basket Analysis）：Apriori 关联规则。

用于挖掘「买了 A 的顾客也倾向买 B」的商品组合规律，
为捆绑销售、货架摆放、交叉推荐提供数据支撑。
"""

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def build_basket(df: pd.DataFrame, min_items: int = 1) -> pd.DataFrame:
    """把交易明细转换为 one-hot 购物篮矩阵（行=发票，列=商品）。"""
    basket = (
        df.groupby(["InvoiceNo", "Description"])["Quantity"]
        .sum()
        .unstack()
        .reset_index()
        .fillna(0)
        .set_index("InvoiceNo")
    )
    basket = (basket > 0).astype(bool)
    # 去掉只含单件商品、无法产生关联的篮子和过大的异常篮子
    basket = basket[(basket.sum(axis=1) > min_items)]
    return basket


def frequent_itemsets(basket: pd.DataFrame, min_support: float = 0.02):
    """挖掘频繁项集。"""
    return apriori(basket, min_support=min_support, use_colnames=True)


def get_rules(frequent, metric: str = "lift", min_threshold: float = 1.0):
    """从频繁项集生成关联规则。"""
    rules = association_rules(frequent, metric=metric, min_threshold=min_threshold)
    # 拆分前件/后件集合为可读字符串
    rules["前件"] = rules["antecedents"].apply(lambda x: " + ".join(sorted(x)))
    rules["后件"] = rules["consequents"].apply(lambda x: " + ".join(sorted(x)))
    return rules


def top_rules(rules, n: int = 10) -> pd.DataFrame:
    """按提升度排序的 Top 规则（可读格式）。"""
    cols = ["前件", "后件", "support", "confidence", "lift"]
    r = rules[cols].copy()
    r.columns = ["前件", "后件", "支持度", "置信度", "提升度"]
    r = r.sort_values("提升度", ascending=False).head(n)
    return r.reset_index(drop=True)
