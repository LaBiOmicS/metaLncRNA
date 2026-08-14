
import pandas as pd
import plotly.express as px

# Nature-inspired palette
COLORS = {"coding": "#D62728", "noncoding": "#1F77B4", "unknown": "#95A5A6"}

def generate_html_report(final_df, results_dict, sequence_stats, output_path):
    stats_df = (
        pd.DataFrame.from_dict(sequence_stats, orient='index')
        .reset_index()
        .rename(columns={'index': 'sequence_id'})
    )
    df = pd.merge(final_df, stats_df, on='sequence_id', how='left')

    # 1. Consensus Distribution
    fig_sun = px.sunburst(df, path=['consensus_label'], title="Overall Transcript Classification",
                          color='consensus_label', color_discrete_map=COLORS)

    # 2. Confidence Landscape
    fig_conf = px.scatter(df, x='length', y='meta_score', color='consensus_label',
                          hover_data=['sequence_id', 'consensus_support'],
                          title="Classification Confidence vs. Transcript Length",
                          color_discrete_map=COLORS, template="plotly_white")

    # 3. Tool Agreement Matrix (Using Probs)
    prob_cols = [c for c in df.columns if c.endswith("_prob")]
    # Force conversion to numeric
    prob_df = df[prob_cols].apply(pd.to_numeric, errors='coerce')
    corr = prob_df.corr()
    tools = [c.replace("_prob", "").upper() for c in prob_cols]
    fig_heat = px.imshow(corr, x=tools, y=tools, title="Tool Probability Correlation Matrix",
                         color_continuous_scale="RdBu", text_auto=".2f")
    fig_heat.update_layout(width=600, height=600)

    # Generate HTML
    html = f"""
    <html>
    <head>
        <title>metaLncRNA Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{ font-family: 'Arial', sans-serif; background: #f4f6f7; padding: 30px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <h1>metaLncRNA Analysis Dashboard</h1>
        <div class="grid">
            <div class="card">{fig_sun.to_html(full_html=False, include_plotlyjs=False)}</div>
            <div class="card">{fig_heat.to_html(full_html=False, include_plotlyjs=False)}</div>
            <div class="card" style="grid-column: span 2;">
                {fig_conf.to_html(full_html=False, include_plotlyjs=False)}
            </div>
        </div>
        <div class="card" style="margin-top:20px;">
            <h2>Top 100 Predictions</h2>
            {df.head(100).to_html(index=False)}
        </div>
    </body>
    </html>
    """
    with open(output_path, "w") as f: f.write(html)
