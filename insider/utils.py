import plotly.graph_objects as go


def set_layout():
    layout = go.Layout(xaxis=dict(type="category", tickangle=270))
    return layout


def calculate_surged_limit(p):
    """Calculate the price if upper surged limit is reached."""
    surged = round(p * 1.1, 2)
    return surged


def reach_surged_limit(
    df, year_month_day: str, preprice_col: str = "preprice", close_col: str = "price"
):
    """Check"""
    df["calculated_surged_price"] = df[preprice_col].apply(
        lambda x: calculate_surged_limit(x)
    )
    df[year_month_day] = (
        (df["calculated_surged_price"] == df[close_col])
        & (df[preprice_col] != df[close_col])
    ).astype(int)

    cols = ["code", "name"]
    cols = cols.append(year_month_day)
    return df[cols]
