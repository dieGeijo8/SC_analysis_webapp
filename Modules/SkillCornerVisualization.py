from skillcornerviz.standard_plots import scatter_plot as scatter, bar_plot as bar, summary_table as table, radar_plot as radar
import numpy as np

def scatter_chart_off_ball_runs(x_metric, y_metric, grouping_column, response_df):

    df_grouped = response_df.groupby([grouping_column])[
        [x_metric, y_metric]
    ].agg("mean").reset_index()

    # Flatten multi-index column names
    df_grouped.columns = ["_".join(col) if isinstance(col, tuple) else col for col in df_grouped.columns]

    # Sum the two count columns
    df_grouped.fillna(0, inplace=True)
    df_grouped["total_runs"] = df_grouped[x_metric] + df_grouped[y_metric]

    # Compute percentile thresholds
    top_25_threshold = round(np.percentile(df_grouped["total_runs"], 75), 2)# 75th percentile
    bottom_25_threshold = round(np.percentile(df_grouped["total_runs"], 25), 2)# 25th percentile

    # Get short names in the top 25% and bottom 25%
    top_15_short_names = df_grouped[df_grouped["total_runs"] >= top_25_threshold][grouping_column].tolist()
    bottom_15_short_names = df_grouped[df_grouped["total_runs"] <= bottom_25_threshold][grouping_column].tolist()
    fig, ax = scatter.plot_scatter(
        df=df_grouped,
        x_metric=x_metric,  # Updated column name
        y_metric=y_metric,  # Updated column name
        data_point_id=grouping_column,
        data_point_label=grouping_column,
        x_label=x_metric,
        y_label=y_metric,
        primary_highlight_group=top_15_short_names,
        secondary_highlight_group=bottom_15_short_names
    )

    return fig

def barplot_chart_off_ball_runs(metric, grouping_column, response_df):
    df_grouped = response_df.groupby([grouping_column])[
        [metric]
    ].agg("mean").reset_index()

    # Flatten multi-index column names
    df_grouped.columns = ["_".join(col) if isinstance(col, tuple) else col for col in df_grouped.columns]

    # Sort and filter
    df_grouped.fillna(0, inplace=True)
    df_grouped = df_grouped.sort_values(by=metric, ascending=False).head(10)

    fig, ax = bar.plot_bar_chart(df=df_grouped,
                                 metric=metric,
                                 label=metric,
                                 primary_highlight_group=list(df_grouped[grouping_column])[:3],
                                 add_bar_values=True,
                                 data_point_id=grouping_column,
                                 data_point_label=grouping_column)

    return fig

def summary_table_scouting(plot_metrics, df, top_n):

    fig, ax = table.plot_summary_table(df=df,
                                       metrics=list(plot_metrics.keys()),
                                       metric_col_names=plot_metrics.values(),
                                       percentiles_mode=True,
                                       data_point_id='short_name',
                                       data_point_label='short_name',
                                       highlight_group=top_n)

    return fig

def radar_plot_scouting(plot_metrics, df, player_name):
    fig, ax = radar.plot_radar(df=df,
                               data_point_id='short_name',
                               label=player_name,
                               metrics=plot_metrics.keys(),
                               metric_labels=plot_metrics,
                               percentiles_precalculated=False
                               )

    return fig