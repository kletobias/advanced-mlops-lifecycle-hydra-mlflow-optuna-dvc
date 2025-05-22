import json
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import Dash, dcc, html, dash_table

# Modify these paths as needed or dynamically discover them.
project_root = os.getenv("PROJECT_ROOT")
if not project_root:
    raise ValueError

METADATA_FILES = sorted([
    os.path.join(project_root,"data/v0/v0_metadata.json"),
    os.path.join(project_root,"data/v1/v1_metadata.json"),
    os.path.join(project_root,"data/v2/v2_metadata.json"),
    os.path.join(project_root,"data/v3/v3_metadata.json"),
    os.path.join(project_root,"data/v4/v4_metadata.json"),
    os.path.join(project_root,"data/v5/v5_metadata.json"),
    os.path.join(project_root,"data/v5_1/v5_1_metadata.json"),
    os.path.join(project_root,"data/v5_2/v5_2_metadata.json"),
    os.path.join(project_root,"data/v6/v6_metadata.json"),
    os.path.join(project_root,"data/v7/v7_metadata.json"),
    os.path.join(project_root,"data/v9/v9_metadata.json"),
    os.path.join(project_root,"data/v10/v10_metadata.json"),
    os.path.join(project_root,"data/v11/v11_metadata.json"),
    os.path.join(project_root,"data/v12/v12_metadata.json"),
    os.path.join(project_root,"data/v13/v13_metadata.json"),
])

def load_metadata(file_paths):
    records = []
    for p in file_paths:
        with open(p, "r") as f:
            meta = json.load(f)
        version = os.path.basename(p).split("_metadata.json")[0]  # e.g. "v10"
        record = {
            "version": version,
            "file_path": meta.get("file_path"),
            "timestamp": meta.get("timestamp"),
            "file_size_bytes": meta.get("file_size_bytes"),
            "num_rows": meta.get("num_rows"),
            "total_columns": meta.get("total_columns"),
            "df_hash": meta.get("df_hash"),
            "hash_sha256": meta.get("hash_sha256"),
        }
        records.append(record)
    return pd.DataFrame(records)

df_main = load_metadata(METADATA_FILES).sort_values("version")

# Create figures
fig_file_size = px.bar(
    df_main,
    x="version",
    y="file_size_bytes",
    title="File Size by Version (bytes)",
    text="file_size_bytes",
)
fig_file_size.update_layout(xaxis_title="Version", yaxis_title="File Size (bytes)")
fig_file_size.update_traces(textposition="outside")

fig_num_rows = px.bar(
    df_main,
    x="version",
    y="num_rows",
    title="Row Count by Version",
    text="num_rows",
)
fig_num_rows.update_layout(xaxis_title="Version", yaxis_title="Number of Rows")
fig_num_rows.update_traces(textposition="outside")

fig_num_cols = px.bar(
    df_main,
    x="version",
    y="total_columns",
    title="Total Columns by Version",
    text="total_columns",
)
fig_num_cols.update_layout(xaxis_title="Version", yaxis_title="Total Columns")
fig_num_cols.update_traces(textposition="outside")

# Table with main metadata
table_main = dash_table.DataTable(
    columns=[{"name": c, "id": c} for c in df_main.columns],
    data=df_main.to_dict("records"),
    page_size=10,
    style_table={"overflowX": "auto"},
    style_header={"fontWeight": "bold"},
)

# Build detail about columns from each version
# We'll flatten out each version's column metadata into a long DataFrame
details_records = []
for p in METADATA_FILES:
    with open(p, "r") as f:
        meta = json.load(f)
    version = os.path.basename(p).split("_metadata.json")[0]
    columns_meta = meta.get("columns", {})
    for col_name, col_info in columns_meta.items():
        details_records.append({
            "version": version,
            "column_name": col_name,
            "data_type": col_info.get("data_type"),
            "num_missing": col_info.get("num_missing"),
            "unique_values": col_info.get("unique_values"),
            "memory_usage_bytes": col_info.get("memory_usage_bytes"),
        })

df_details = pd.DataFrame(details_records).sort_values(["version", "column_name"])

fig_missing = px.box(
    df_details,
    x="version",
    y="num_missing",
    points="all",
    title="Distribution of 'num_missing' per Column by Version"
)
fig_missing.update_layout(xaxis_title="Version", yaxis_title="num_missing")

table_details = dash_table.DataTable(
    columns=[{"name": c, "id": c} for c in df_details.columns],
    data=df_details.to_dict("records"),
    page_size=10,
    style_table={"overflowX": "auto"},
    style_header={"fontWeight": "bold"},
)

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.H1("Metadata Dashboard"),
        html.Div(
            children=[
                html.H2("Overall Metadata Summary"),
                table_main,
                dcc.Graph(figure=fig_file_size),
                dcc.Graph(figure=fig_num_rows),
                dcc.Graph(figure=fig_num_cols),
            ]
        ),
        html.Hr(),
        html.Div(
            children=[
                html.H2("Detailed Column Statistics"),
                table_details,
                dcc.Graph(figure=fig_missing),
            ]
        ),
    ],
    style={"margin": "40px"},
)

if __name__ == "__main__":
    app.run(debug=True)
