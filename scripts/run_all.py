"""一键运行完整电商销售分析流程。

用法（在项目根目录执行）：
    python scripts/run_all.py

流程：加载 → 质量体检 → 清洗 → EDA → RFM → 购物篮 → 预测 → 图表 → 报告 → 落盘
"""

import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import analysis, data_loader, market_basket, modeling, visualize  # noqa: E402
from src.config import TABLE_DIR, apply_style  # noqa: E402
from src.report import write_report  # noqa: E402

apply_style()


def banner(text):
    print(f"\n{'=' * 68}\n  {text}\n{'=' * 68}")


def save(df, name):
    df.to_csv(TABLE_DIR / name, index=False, encoding="utf-8-sig")
    print(f"  → tables/{name}")


def main():
    t0 = time.time()

    banner("STEP 1 / 7  加载原始数据")
    raw = data_loader.load_raw()
    print(f"  原始数据  {raw.shape[0]:,} 行 × {raw.shape[1]} 列")

    banner("STEP 2 / 7  数据质量体检")
    qr = data_loader.quality_report(raw)
    save(qr, "01_quality_report.csv")
    print(qr.to_string(index=False, max_colwidth=40))

    banner("STEP 3 / 7  数据清洗")
    df = data_loader.load_clean()
    print(f"  清洗后  {df.shape[0]:,} 行，唯一发票 {df['InvoiceNo'].nunique():,}，"
          f"唯一客户 {df['CustomerID'].nunique():,}")

    banner("STEP 4 / 7  EDA 与 RFM 客户分层")
    monthly = analysis.monthly_trend(df)
    weekday = analysis.weekday_distribution(df)
    hour = analysis.hour_distribution(df)
    country = analysis.country_breakdown(df)
    product = analysis.product_breakdown(df, top_n=10)
    rfm = analysis.rfm_segmentation(df)
    rfm_summary = analysis.rfm_summary(rfm)

    save(monthly, "02_monthly_trend.csv")
    save(weekday, "03_weekday.csv")
    save(hour, "04_hour.csv")
    save(country, "05_country.csv")
    save(product, "06_product_top10.csv")
    save(rfm, "07_rfm_customers.csv")
    save(rfm_summary, "08_rfm_summary.csv")

    print("\n  [RFM 分群]\n" + rfm_summary.to_string(index=False))

    banner("STEP 5 / 7  购物篮关联分析")
    basket = market_basket.build_basket(df)
    frequent = market_basket.frequent_itemsets(basket, min_support=0.02)
    rules = market_basket.get_rules(frequent, metric="lift", min_threshold=1.0)
    top_rules = market_basket.top_rules(rules, n=15)
    save(top_rules, "09_association_rules.csv")
    print(f"  频繁项集 {len(frequent)}，规则 {len(rules)}")
    print("\n  [Top 关联规则]\n" + top_rules.head(10).to_string(index=False))

    banner("STEP 6 / 7  销售预测")
    series = modeling.build_monthly_series(df)
    model_cmp = modeling.evaluate_models(series, test_size=3)
    forecast = modeling.forecast_next(series, horizon=3)
    save(model_cmp, "10_model_comparison.csv")
    save(forecast, "11_forecast.csv")
    print("\n  [模型对比]\n" + model_cmp.to_string(index=False))
    print("\n  [未来预测]\n" + forecast.to_string(index=False))

    banner("STEP 7 / 7  生成图表与报告")
    figs = [
        visualize.plot_monthly_trend(monthly),
        visualize.plot_weekday(weekday),
        visualize.plot_hour(hour),
        visualize.plot_country(country),
        visualize.plot_product(product),
        visualize.plot_rfm(rfm),
        visualize.plot_rfm_scatter(rfm),
        visualize.plot_rules(top_rules),
        visualize.plot_rules_scatter(rules),
        visualize.plot_forecast(series, forecast),
    ]
    print(f"  已生成 {len(figs)} 张图表 -> reports/figures/")

    metrics = {
        "quality": qr,
        "clean_rows": len(df),
        "rfm_summary": rfm_summary,
        "top_rules": top_rules,
        "model_comparison": model_cmp,
        "forecast": forecast,
    }
    report_path = write_report(metrics)
    print(f"  已生成报告 -> {report_path}")

    print(f"\n完成，总耗时 {time.time() - t0:.1f}s")
    print(f"图表目录：{ROOT / 'reports' / 'figures'}")
    print(f"数据表目录：{ROOT / 'reports' / 'tables'}")
    print(f"报告文件：{report_path}")


if __name__ == "__main__":
    main()
