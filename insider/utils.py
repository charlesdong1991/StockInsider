import plotly.graph_objects as go


def set_layout():
    layout = go.Layout(xaxis=dict(type="category", tickangle=270))
    return layout


def calculate_surged_limit(p):
    """Calculate the price if upper surged limit is reached."""
    surged = round(p * 1.1, 2)
    return surged
