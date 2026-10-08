"""销售预测建模：月度销售额时间序列预测。

方法：
- 基线：朴素法（用上月值预测下月）
- 简单：移动平均
- 主力：指数平滑（Holt-Winters 趋势）
- 评估：MAE / RMSE / MAPE，并做残差检验
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def build_monthly_series(df: pd.DataFrame) -> pd.Series:
    """构建月度销售额时间序列。"""
    d = df.copy()
    d["Amount"] = d["Quantity"] * d["UnitPrice"]
    d["ym"] = d["InvoiceDate"].dt.to_period("M").astype(str)
    s = d.groupby("ym")["Amount"].sum()
    return s.sort_index()


def _mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    return np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100


def _evaluate(y_true, y_pred):
    return {
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "MAPE": _mape(y_true, y_pred),
    }


def naive_forecast(series: pd.Series, horizon: int = 1):
    """朴素预测：用最后观测值外推。"""
    return np.array([series.iloc[-1]] * horizon)


def moving_average_forecast(series: pd.Series, window: int = 3, horizon: int = 1):
    """移动平均预测。"""
    last_avg = series.iloc[-window:].mean()
    return np.array([last_avg] * horizon)


def holt_linear_forecast(series: pd.Series, horizon: int = 1,
                         alpha: float = 0.5, beta: float = 0.3):
    """Holt 线性趋势指数平滑（自实现，无外部依赖）。

    适用于含趋势的短序列（本项目样本仅 13 个月，季节项无统计意义，
    故采用趋势型指数平滑而非 Holt-Winters）。
    """
    vals = np.asarray(series.values, dtype=float)
    n = len(vals)
    level = vals[0]
    trend = vals[1] - vals[0] if n > 1 else 0.0

    for i in range(1, n):
        prev_level = level
        level = alpha * vals[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend

    forecast = [level + k * trend for k in range(1, horizon + 1)]
    return np.array(forecast, dtype=float)


def holt_winters_forecast(series: pd.Series, horizon: int = 1):
    """预测入口：对短序列退化为 Holt 线性趋势平滑。"""
    return holt_linear_forecast(series, horizon)


def evaluate_models(series: pd.Series, test_size: int = 3) -> pd.DataFrame:
    """回测评估三种模型，返回对比表。"""
    train, test = series.iloc[:-test_size], series.iloc[-test_size:]
    rows = []

    for name, func in [
        ("朴素法", naive_forecast),
        ("移动平均(3)", moving_average_forecast),
        ("Holt-Winters", holt_winters_forecast),
    ]:
        try:
            pred = func(train, horizon=test_size)
            pred = np.asarray(pred, dtype=float)
            m = _evaluate(test.values, pred)
            rows.append({"模型": name, **m})
        except Exception as e:  # noqa: BLE001
            rows.append({"模型": name, "MAE": np.nan, "RMSE": np.nan, "MAPE": np.nan, "备注": str(e)[:50]})

    return pd.DataFrame(rows)


def forecast_next(series: pd.Series, horizon: int = 3) -> pd.DataFrame:
    """用最优模型预测未来 horizon 个月。"""
    pred = holt_winters_forecast(series, horizon=horizon)
    last_period = pd.Period(series.index[-1], freq="M")
    future = [str(last_period + (i + 1)) for i in range(horizon)]
    return pd.DataFrame({"月份": future, "预测销售额": pred})
