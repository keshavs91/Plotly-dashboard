import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# --------------------------------------------------------------------------------
# Get datasets ready
df = pd.read_csv("aws_cost_breakup.csv")

df.columns = [col.replace("\n", " ") for col in df.columns]
df["Unnamed: 0"] = [item.replace("\n", " ") for item in df["Unnamed: 0"]]

for col in df.columns[1:]:
    df[col].astype(float)

df_total_cost = pd.DataFrame(data=[(col, df[col].sum()) for col in df.columns[1:]], columns=["service", "total"])
df_total_cost.head()

# --------------------------------------------------------------------------------
# Get charts ready
chart_bar_total_costs = px.bar(df_total_cost, x=df_total_cost.columns[0], y=df_total_cost.columns[1], title="Total Cost (All services)")

chart_bar_total_costs_threshold = px.bar(df_total_cost[df_total_cost["total"] > 10000], x=df_total_cost.columns[0], y=df_total_cost.columns[1], title="Total Cost (>₹10,000)")

chart_pie_total_costs_threshold = px.pie(df_total_cost[df_total_cost["total"] > 10000], values=df_total_cost.columns[1], names=df_total_cost.columns[0], title="AWS Services Cost Pie")

chart_bar_list_service_costs: list = [px.bar(df, x=df.columns[0], y=df.columns[index], title=f"Cost of {df.columns[index]}") for index in range(1, len(df.columns))]

# --------------------------------------------------------------------------------
# Setup the dashboard
graph1 = dcc.Graph(
    id="graph-1",
    figure=chart_bar_total_costs,
)
graph2 = dcc.Graph(
    id="graph-2",
    figure=chart_bar_total_costs_threshold,
)

graph3 = dcc.Graph(
    id="graph-3",
    figure=chart_pie_total_costs_threshold,
)

service_cost_graphs = [dcc.Graph(
    id=f"graph-{4+index}",
    figure=chart
)
    for index, chart in enumerate(chart_bar_list_service_costs)

]

app.layout = html.Div([

    html.H1("AWS Cost Breakup (Feb 2021 - Nov 2023)how to ", style={"text-align": "center"}),
    dcc.Dropdown(
        id="select-month",
        options=[{"label": item, "value": item} for item in df["Unnamed: 0"]],
        multi=False,
        value=None,
        style={"width": "50%"}
    ),

    graph1,

    graph2,

    graph3,

    html.Div(children=service_cost_graphs),

    # dcc.Dropdown(
    #     id="some-id",
    #     options=[
    #         {}
    #     ],
    #     multi=False,
    #     value=None,
    #     style={"width": "40%"}
    # ),
    #
    # html.Div(id="output_container", children=[]),
    # html.Br(),
    #
    # dcc.Graph(id="some_graph", figure={})
])


@app.callback(
    Output("graph-1", "figure"),
    Output("graph-2", "figure"),
    Output("graph-3", "figure"),
    Input("select-month", "value"),
)
def update_figure(selected_month):
    if not selected_month:
        print("No month")
        return chart_bar_total_costs
    filtered_df = df[df["Unnamed: 0"] == selected_month]
    total_filtered_df = pd.DataFrame(data=[(col, filtered_df[col].sum()) for col in filtered_df.columns[1:]], columns=["service", "total"])
    chart1 = px.bar(total_filtered_df, x=total_filtered_df.columns[0], y=total_filtered_df.columns[1],
                                   title=f"Total Cost (All services) for {selected_month}")

    chart2 = px.bar(total_filtered_df[total_filtered_df["total"] > 1000], x=total_filtered_df.columns[0],
                                             y=total_filtered_df.columns[1], title=f"Total Cost (>₹1,000) in {selected_month}")
    chart3 = px.pie(df_total_cost[total_filtered_df["total"] > 1000],
                                             values=total_filtered_df.columns[1], names=total_filtered_df.columns[0],
                                             title=f"AWS Services Cost Pie in {selected_month}")

    return chart1, chart2, chart3


if __name__ == "__main__":
    app.run_server(debug=True)
