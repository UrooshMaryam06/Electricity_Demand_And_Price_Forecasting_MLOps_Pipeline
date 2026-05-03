"""
Reusable Plotly chart factory functions.
All charts use the dark industrial theme from config.COLORS.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.config import COLORS


def _dark_layout(**kwargs) -> dict:
    """Base dark layout applied to every chart."""
    return dict(
        paper_bgcolor=COLORS["bg_card"],
        plot_bgcolor=COLORS["bg_card"],
        font=dict(color=COLORS["text_primary"], family="IBM Plex Mono, monospace"),
        xaxis=dict(gridcolor=COLORS["border"], color=COLORS["text_secondary"]),
        yaxis=dict(gridcolor=COLORS["border"], color=COLORS["text_secondary"]),
        margin=dict(l=40, r=20, t=40, b=40),
        **kwargs,
    )


def actual_vs_predicted(
    df: pd.DataFrame,
    actual_col: str,
    pred_col: str,
    title: str,
    y_label: str,
    color_actual: str = None,
    color_pred: str = None,
) -> go.Figure:
    """
    Line chart showing actual vs predicted time series.
    df must have a datetime index.
    """
    color_actual = color_actual or COLORS["demand_color"]
    color_pred   = color_pred   or COLORS["price_color"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df[actual_col],
        name="Actual", line=dict(color=color_actual, width=1.5),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df[pred_col],
        name="Predicted", line=dict(color=color_pred, width=1.5, dash="dot"),
    ))
    fig.update_layout(title=title, yaxis_title=y_label, **_dark_layout())
    return fig


def model_comparison_bar(
    model_names: list[str],
    rmse_values: list[float],
    r2_values: list[float],
    title: str = "Model Comparison",
) -> go.Figure:
    """Grouped bar chart: RMSE and R2 for each model."""
    fig = go.Figure(data=[
        go.Bar(name="RMSE", x=model_names, y=rmse_values,
               marker_color=COLORS["accent_amber"]),
        go.Bar(name="R2",   x=model_names, y=r2_values,
               marker_color=COLORS["accent_teal"]),
    ])
    fig.update_layout(
        title=title, barmode="group",
        yaxis_title="Score",
        **_dark_layout(),
    )
    return fig


def radar_chart(
    model_names: list[str],
    metric_names: list[str],
    values_matrix: list[list[float]],
) -> go.Figure:
    """
    Radar/spider chart comparing models across multiple metrics.
    values_matrix[i] = list of normalized metric scores for model i.
    Normalize all metrics to 0-1 before passing.
    """
    fig = go.Figure()
    colors = [COLORS["accent_amber"], COLORS["accent_teal"], COLORS["accent_green"],
              COLORS["accent_red"], "#ab47bc", "#42a5f5", "#26a69a", "#ff7043"]
    for i, (name, vals) in enumerate(zip(model_names, values_matrix)):
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=metric_names + [metric_names[0]],
            name=name,
            line=dict(color=colors[i % len(colors)]),
            fill="toself",
            opacity=0.25,
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=COLORS["bg_card"],
            radialaxis=dict(visible=True, color=COLORS["text_secondary"]),
            angularaxis=dict(color=COLORS["text_secondary"]),
        ),
        **_dark_layout(),
    )
    return fig


def correlation_heatmap(df: pd.DataFrame, columns: list[str]) -> go.Figure:
    """Correlation heatmap for selected numeric features."""
    corr = df[columns].corr()
    fig = px.imshow(
        corr,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        title="Feature Correlation Matrix",
    )
    fig.update_layout(**_dark_layout())
    return fig


def pca_scatter(
    x: list[float],
    y: list[float],
    labels: list[int],
    label_names: dict[int, str] = None,
) -> go.Figure:
    """
    2D scatter for PCA or t-SNE output, colored by cluster label.
    label_names: {0: 'High Renewable', 1: 'Peak Demand', ...}
    """
    colors = [COLORS["accent_teal"], COLORS["accent_amber"],
              COLORS["accent_green"], COLORS["accent_red"], "#ab47bc"]
    fig = go.Figure()
    unique_labels = sorted(set(labels))
    for i, lbl in enumerate(unique_labels):
        mask = [l == lbl for l in labels]
        name = (label_names or {}).get(lbl, f"Cluster {lbl}")
        fig.add_trace(go.Scatter(
            x=[xi for xi, m in zip(x, mask) if m],
            y=[yi for yi, m in zip(y, mask) if m],
            mode="markers",
            name=name,
            marker=dict(color=colors[i % len(colors)], size=4, opacity=0.6),
        ))
    fig.update_layout(title="PCA Cluster Visualization", **_dark_layout())
    return fig


def association_network(rules_df) -> go.Figure:
    """
    Simple scatter-style chart visualizing association rules.
    X = support, Y = confidence, size = lift, color = lift.
    rules_df must have columns: antecedents, consequents, support, confidence, lift.
    """
    fig = px.scatter(
        rules_df,
        x="support",
        y="confidence",
        size="lift",
        color="lift",
        hover_data=["antecedents", "consequents"],
        color_continuous_scale="Viridis",
        title="Association Rules — Support vs Confidence (size = Lift)",
    )
    fig.update_layout(**_dark_layout())
    return fig


def generation_mix_pie(df_row: pd.Series) -> go.Figure:
    """Pie chart of generation mix for a single row."""
    cols  = ["generation solar", "generation wind onshore",
             "generation fossil gas", "generation fossil hard coal",
             "generation nuclear", "generation hydro water reservoir"]
    vals  = [max(0, df_row.get(c, 0)) for c in cols]
    names = ["Solar", "Wind", "Gas", "Coal", "Nuclear", "Hydro"]
    fig = go.Figure(go.Pie(
        labels=names, values=vals,
        hole=0.4,
        marker=dict(colors=[
            COLORS["accent_amber"], COLORS["accent_teal"],
            COLORS["accent_red"], "#78909c",
            "#5c6bc0", "#26a69a"],
        ),
    ))
    fig.update_layout(title="Generation Mix", **_dark_layout())
    return fig
