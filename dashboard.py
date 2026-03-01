import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd

# ── LOAD DATA ──
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "Online_Retail_Sample.csv"), encoding="latin1")
df.dropna(subset=["CustomerID"], inplace=True)
sales = df[df["IsReturn"] == False].copy()

# ── COUNTRIES LIST ──
countries = ["All"] + sorted(sales["Country"].unique().tolist())

# ── COLORS ──
BG     = "#080810"
CARD   = "#13131f"
BORDER = "#1e1e30"
CORAL  = "#ff6b6b"
TEAL   = "#00d4c8"
YELLOW = "#ffd166"
PURPLE = "#a855f7"
TEXT   = "#e8e8f5"
MUTED  = "#6b6b8a"

PLOT_LAYOUT = dict(
    paper_bgcolor=CARD,
    plot_bgcolor=CARD,
    font=dict(color=TEXT, family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=20, b=40),
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
)

# ── APP ──
app = dash.Dash(__name__)
server = app.server
app.title = "Retail Sales Dashboard"

app.layout = html.Div(style={"backgroundColor": BG, "minHeight": "100vh", "fontFamily": "Inter, sans-serif", "color": TEXT, "paddingBottom": "2rem"}, children=[

    # ── HEADER ──
    html.Div(style={"borderBottom": f"1px solid {BORDER}", "padding": "1.2rem 3rem", "display": "flex", "justifyContent": "space-between", "alignItems": "center", "backgroundColor": "rgba(8,8,16,0.95)"}, children=[
        html.Div([
            html.H1("Retail Sales Dashboard", style={"fontSize": "1.3rem", "fontWeight": "800", "color": TEXT, "margin": "0"}),
            html.P("541,909 transactions · 37 countries · 2010–2011", style={"color": MUTED, "fontSize": "0.78rem", "margin": "0"}),
        ]),
        html.Div(style={"display": "flex", "alignItems": "center", "gap": "0.8rem"}, children=[
            html.Label("Country:", style={"color": MUTED, "fontSize": "0.82rem"}),
            dcc.Dropdown(
                id="country-filter",
                options=[{"label": c, "value": c} for c in countries],
                value="All",
                clearable=False,
                style={"width": "180px", "fontSize": "0.85rem"},
            )
        ])
    ]),

    # ── KPI CARDS ──
    html.Div(id="kpi-cards", style={"display": "grid", "gridTemplateColumns": "repeat(4,1fr)", "gap": "1rem", "padding": "1.5rem 3rem 0"}),

    # ── ROW 1: Monthly Trend + Pie ──
    html.Div(style={"display": "grid", "gridTemplateColumns": "2fr 1fr", "gap": "1rem", "padding": "1rem 3rem 0"}, children=[
        html.Div(style={"backgroundColor": CARD, "border": f"1px solid {BORDER}", "borderRadius": "0.8rem", "padding": "1.2rem 1.5rem"}, children=[
            html.P("Monthly Revenue Trend", style={"color": MUTED, "fontSize": "0.75rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "margin": "0 0 0.5rem"}),
            dcc.Graph(id="monthly-trend", config={"displayModeBar": False}, style={"height": "260px"}),
        ]),
        html.Div(style={"backgroundColor": CARD, "border": f"1px solid {BORDER}", "borderRadius": "0.8rem", "padding": "1.2rem 1.5rem"}, children=[
            html.P("Customer Segments", style={"color": MUTED, "fontSize": "0.75rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "margin": "0 0 0.5rem"}),
            dcc.Graph(id="segment-pie", config={"displayModeBar": False}, style={"height": "260px"}),
        ]),
    ]),

    # ── ROW 2: Top Products + Country ──
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "1rem", "padding": "1rem 3rem 0"}, children=[
        html.Div(style={"backgroundColor": CARD, "border": f"1px solid {BORDER}", "borderRadius": "0.8rem", "padding": "1.2rem 1.5rem"}, children=[
            html.P("Top 10 Products by Revenue", style={"color": MUTED, "fontSize": "0.75rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "margin": "0 0 0.5rem"}),
            dcc.Graph(id="top-products", config={"displayModeBar": False}, style={"height": "300px"}),
        ]),
        html.Div(style={"backgroundColor": CARD, "border": f"1px solid {BORDER}", "borderRadius": "0.8rem", "padding": "1.2rem 1.5rem"}, children=[
            html.P("Revenue by Country (Top 10)", style={"color": MUTED, "fontSize": "0.75rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "margin": "0 0 0.5rem"}),
            dcc.Graph(id="country-revenue", config={"displayModeBar": False}, style={"height": "300px"}),
        ]),
    ]),

    html.Div("Built by Adapaka Guna Sekhar · Online Retail Sales Analysis", style={"textAlign": "center", "color": MUTED, "fontSize": "0.75rem", "padding": "1.5rem 0 0"}),
])


@app.callback(
    Output("kpi-cards", "children"),
    Output("monthly-trend", "figure"),
    Output("segment-pie", "figure"),
    Output("top-products", "figure"),
    Output("country-revenue", "figure"),
    Input("country-filter", "value")
)
def update_dashboard(country):
    filtered = sales.copy() if country == "All" else sales[sales["Country"] == country].copy()

    # KPIs
    total_revenue   = filtered["TotalSale"].sum()
    total_orders    = filtered["InvoiceNo"].nunique()
    total_customers = filtered["CustomerID"].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0

    def kpi_card(label, value, color):
        return html.Div([
            html.P(label, style={"color": MUTED, "fontSize": "0.72rem", "fontWeight": "600", "letterSpacing": "0.08em", "textTransform": "uppercase", "margin": "0 0 0.4rem"}),
            html.H2(value, style={"fontSize": "1.8rem", "fontWeight": "800", "color": color, "margin": "0"}),
        ], style={"backgroundColor": CARD, "border": f"1px solid {BORDER}", "borderLeft": f"3px solid {color}", "borderRadius": "0.6rem", "padding": "1.2rem 1.5rem"})

    cards = [
        kpi_card("Total Revenue",    f"£{total_revenue:,.0f}", CORAL),
        kpi_card("Total Orders",     f"{total_orders:,}",       TEAL),
        kpi_card("Unique Customers", f"{total_customers:,}",    YELLOW),
        kpi_card("Avg Order Value",  f"£{aov:,.0f}",            PURPLE),
    ]

    # Monthly Trend
    monthly = filtered.groupby("YearMonth")["TotalSale"].sum().reset_index()
    monthly.columns = ["Month", "Revenue"]
    monthly = monthly.sort_values("Month")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Revenue"],
        mode="lines+markers",
        line=dict(color=CORAL, width=2.5),
        marker=dict(color=CORAL, size=5),
        fill="tozeroy", fillcolor="rgba(255,107,107,0.07)",
        hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>"
    ))
    fig_trend.update_layout(**PLOT_LAYOUT)

    # Segment Pie
    try:
        cust_spend = filtered.groupby("CustomerID")["TotalSale"].sum()
        seg_labels = pd.qcut(cust_spend, q=3, labels=["Low Value", "Mid Value", "High Value"], duplicates="drop")
        seg_counts = seg_labels.value_counts()
        fig_pie = go.Figure(go.Pie(
            labels=seg_counts.index, values=seg_counts.values,
            hole=0.5,
            marker=dict(colors=[TEAL, YELLOW, CORAL]),
            textfont=dict(color=TEXT, size=11),
            hovertemplate="<b>%{label}</b><br>%{value} customers<extra></extra>"
        ))
        fig_pie.update_layout(**PLOT_LAYOUT, showlegend=True,
                              legend=dict(font=dict(color=TEXT, size=11), bgcolor=CARD, orientation="h", y=-0.15))
    except Exception as e:
        print(f"Pie error: {e}")
        fig_pie = go.Figure()
        fig_pie.update_layout(**PLOT_LAYOUT)

    # Top Products
    top_prods = filtered.groupby("Description")["TotalSale"].sum().nlargest(10).reset_index()
    top_prods.columns = ["Product", "Revenue"]
    top_prods["Product"] = top_prods["Product"].str[:28]
    fig_prods = go.Figure(go.Bar(
        x=top_prods["Revenue"], y=top_prods["Product"],
        orientation="h",
        marker=dict(color=TEAL, opacity=0.85),
        hovertemplate="<b>%{y}</b><br>£%{x:,.0f}<extra></extra>"
    ))
    fig_prods.update_layout(**PLOT_LAYOUT)
    fig_prods.update_yaxes(autorange="reversed", gridcolor=BORDER, zerolinecolor=BORDER)

    # Country Revenue
    country_rev = filtered.groupby("Country")["TotalSale"].sum().nlargest(10).reset_index()
    country_rev.columns = ["Country", "Revenue"]
    fig_country = go.Figure(go.Bar(
        x=country_rev["Country"], y=country_rev["Revenue"],
        marker=dict(color=PURPLE, opacity=0.85),
        hovertemplate="<b>%{x}</b><br>£%{y:,.0f}<extra></extra>"
    ))
    fig_country.update_layout(**PLOT_LAYOUT)

    return cards, fig_trend, fig_pie, fig_prods, fig_country


if __name__ == "__main__":
    app.run(debug=True)