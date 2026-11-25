from pathlib import Path
from functools import lru_cache
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PACKAGE_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PACKAGE_ROOT / "Parquet"


# ============================================================
# DATASETS
# ============================================================

DATASETS = {
    "cohort_composition": "cohort_composition.parquet",
    "mrna_expression_summary": "mrna_expression_summary.parquet",
    "mirna_expression_summary": "mirna_expression_summary.parquet",
    "features": "features.parquet",

    "mrna_deseq2": "mrna_deseq2.parquet",
    "mrna_meta": "mrna_meta.parquet",


    "module_membership": "module_membership.parquet",
    "module_summary": "module_summary.parquet",

    "pathway_results": "pathway_results.parquet",
    "pathway_concordance": "pathway_concordance.parquet",

    "clinical_correlations": "clinical_correlations.parquet",

    "mirna_de": "mirna_de.parquet",

    "mrna_mirna_integration": "mrna_mirna_integration.parquet",
    "integration_pathways": "integration_pathways.parquet",

    "senescence_features": "senescence_features.parquet",
    "senescence_consensus": "senescence_consensus.parquet",

    "overview_table1": "overview_table1.parquet",
}


# ============================================================
# GENERIC LOADER
# ============================================================

@lru_cache(maxsize=None)
def _read_parquet(filename):

    path = DATA_DIR / filename

    if not path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {path}"
        )

    return pd.read_parquet(path)


def load_table(name):

    if name not in DATASETS:

        raise KeyError(
            f"Unknown dataset: {name}"
        )

    return _read_parquet(
        DATASETS[name]
    ).copy()


def style_explorer_plot(fig, cohorts):
    """Shared styling for expression summaries and fold-change figures."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, Helvetica, sans-serif", size=13, color="#102536"),
        height=370 if len(cohorts) > 1 else 390,
        margin=dict(l=55, r=20, t=45, b=42),
    )
    fig.update_xaxes(showgrid=False, showline=True, linecolor="#A9BAC5",
                     linewidth=1, ticks="", automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor="#D7E3EA", gridwidth=1,
                     zeroline=False, showline=False, ticks="", automargin=True)
    titles = set(cohorts.values())
    for annotation in fig.layout.annotations:
        if annotation.text in titles:
            annotation.update(text=f"<b>{annotation.text}</b>",
                              font=dict(size=15, color="#05365D"))
    return fig


def fold_change_plot(de, cohorts, stars, show_se=False):
    import math
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    comparisons = {"IC_VS_HC": ("S-II vs HC", "#7E57C2"),
                   "CLI_VS_HC": ("S-IV vs HC", "#43A047")}
    fig = make_subplots(rows=1, cols=len(cohorts),
                        subplot_titles=list(cohorts.values()), shared_yaxes=True)
    bounds = [0.0]
    for i, cohort in enumerate(cohorts, 1):
        for key, (label, color) in comparisons.items():
            rows = de[(de.cohort_id == cohort) & (de.comparison_id == key)]
            if rows.empty or pd.isna(rows.iloc[0].log2_fold_change):
                continue
            r = rows.iloc[0]
            value = float(r.log2_fold_change)
            if not math.isfinite(value):
                continue
            se = r.get("lfc_se") if show_se else None
            se = float(se) if pd.notna(se) and math.isfinite(float(se)) and float(se) >= 0 else None
            bounds.extend([value-(se or 0), value+(se or 0)])
            fig.add_trace(go.Bar(x=[label], y=[value], marker_color=color,
                name=label, showlegend=False, width=0.55,
                error_y=dict(type="data", array=[se], visible=True) if se is not None else None,
                customdata=[[r.fdr if pd.notna(r.fdr) else None]],
                hovertemplate="%{x}<br>log2 fold change: %{y:.3f}<br>FDR: %{customdata[0]}<extra></extra>"), row=1, col=i)
            mark = stars(r.fdr)
            if mark:
                fig.add_annotation(x=label, y=value+(se or 0) if value>=0 else value-(se or 0),
                    text=mark, showarrow=False, yshift=10 if value>=0 else -10,
                    yanchor="bottom" if value>=0 else "top", font=dict(size=16), row=1,col=i)
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=[v[0] for v in comparisons.values()], row=1,col=i)
        fig.add_hline(y=0, line_color="#777777", line_width=1, row=1,col=i)
    span=max(max(bounds)-min(bounds), 0.5)
    fig.update_yaxes(range=[min(bounds)-.25*span,max(bounds)+.25*span])
    fig.update_yaxes(title_text="Log2 fold change", row=1,col=1)
    fig.update_layout(template="simple_white", height=430, margin=dict(l=45,r=20,t=50,b=45))
    if not fig.data:
        fig.add_annotation(text="No differential expression estimates available", x=.5,y=.5,xref="paper",yref="paper",showarrow=False)
    return style_explorer_plot(fig, cohorts)


@lru_cache(maxsize=256)
def load_expression_summary(modality, feature_id):
    return pd.read_parquet(DATA_DIR / DATASETS[f"{modality}_expression_summary"],
                           filters=[("feature_id", "==", feature_id)])


def expression_summary_plot(expr, de, cohorts, stars, ylabel):
    import math
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    groups = {"HC": ("HC", "#9e9e9e", None),
              "IC": ("S-II", "#7E57C2", "IC_VS_HC"),
              "CLI": ("S-IV", "#43A047", "CLI_VS_HC")}
    fig = make_subplots(rows=1, cols=len(cohorts), subplot_titles=list(cohorts.values()), shared_yaxes=True)
    bounds = []
    marks = []
    for i, cohort in enumerate(cohorts, 1):
        for group, (label, color, comparison) in groups.items():
            rows = expr[(expr.cohort_id == cohort) & (expr.group_id == group)]
            if rows.empty:
                continue
            r = rows.iloc[0]
            vals = [float(r[k]) for k in ["lower_fence", "q1", "median", "q3", "upper_fence"]]
            if not all(math.isfinite(v) for v in vals) or vals != sorted(vals):
                continue
            lo, q1, med, q3, hi = vals
            bounds.extend([lo, hi])
            fig.add_trace(go.Box(x=[label], q1=[q1], median=[med], q3=[q3], lowerfence=[lo], upperfence=[hi], name=label, marker_color=color, boxpoints=False, showlegend=False), row=1, col=i)
            hit = de[(de.cohort_id == cohort) & (de.comparison_id == comparison)]
            if comparison and not hit.empty:
                mark = stars(hit.iloc[0].fdr)
                if mark: marks.append((i, label, mark))
        fig.update_xaxes(type="category", categoryorder="array", categoryarray=[v[0] for v in groups.values()], row=1,col=i)
    if bounds:
        lo, hi = min(bounds), max(bounds)
        span = max(hi-lo, .5)
        for i,label,mark in marks:
            fig.add_annotation(x=label,y=hi+.08*span,text=mark,showarrow=False,yanchor="bottom",font=dict(size=17),row=1,col=i)
        fig.update_yaxes(range=[lo-.05*span,hi+.22*span])
    else:
        fig.add_annotation(text="No expression summaries available",xref="paper",yref="paper",x=.5,y=.5,showarrow=False)
    fig.update_yaxes(title_text=ylabel,row=1,col=1)
    fig.update_layout(template="simple_white",height=430,margin=dict(l=45,r=20,t=50,b=45))
    return style_explorer_plot(fig, cohorts)
