"""全局配置：路径、常量、中文字体与绘图风格。"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 无界面环境安全绘图

# 路径
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FIGURE_DIR = ROOT / "reports" / "figures"
TABLE_DIR = ROOT / "reports" / "tables"
REPORT_DIR = ROOT / "reports"

# 原始数据文件名（完整数据，本地运行用）
RAW_DATA = RAW_DIR / "OnlineRetail.csv"
# 压缩样本数据（随仓库提交，保证他人可跑通；优先 .csv.gz，其次 .csv）
SAMPLE_DATA = PROCESSED_DIR / "OnlineRetail_sample.csv"
SAMPLE_DATA_GZ = PROCESSED_DIR / "OnlineRetail_sample.csv.gz"

# 数据编码：源文件为 latin1（含 £ 等特殊字符）
RAW_ENCODING = "latin1"

# 业务常量
BASKET_ITEM_THRESHOLD = 1  # 关联规则最低支持度商品出现次数
TOP_N = 10  # 常用 TopN

# 中文字体配置（跨平台）
def apply_style():
    """设置统一绘图风格与中文字体。"""
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    # 按优先级探测可用的中文字体
    candidates = [
        "Microsoft YaHei", "SimHei", "PingFang SC", "Noto Sans CJK SC",
        "Source Han Sans SC", "WenQuanYi Micro Hei", "Arial Unicode MS",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = next((c for c in candidates if c in available), None)
    if chosen:
        plt.rcParams["font.sans-serif"] = [chosen, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["figure.figsize"] = (9, 5)

    # 统一配色（色盲友好）
    plt.rcParams["axes.prop_cycle"] = plt.cycler(
        color=["#2C7BB6", "#D7191C", "#FDAE61", "#ABD9E9", "#5E4FA2",
               "#66C2A5", "#F46D43", "#3288BD", "#A6D854", "#E6F598"]
    )
    return chosen
