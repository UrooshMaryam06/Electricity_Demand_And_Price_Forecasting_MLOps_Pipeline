"""
Association rules: display top rules from the Apriori mining module.
Includes filterable table, scatter chart, and contextual query.
"""
from pathlib import Path

import streamlit as st
import pandas as pd
st.set_page_config(page_title="Association Rules", layout="wide")

with open(Path(__file__).resolve().parents[1] / "assets" / "style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

from components.sidebar import render_sidebar
from services.api_client import get_top_associations, query_associations
from components.charts import association_network

render_sidebar()
st.markdown("## Association Rule Mining")
st.caption(
    "Apriori algorithm discovers co-occurrence patterns across energy system states. "
    "Minimum support: 5%. Minimum confidence: 50%. Minimum lift: 1.2."
)
st.divider()

# ── Top rules table ───────────────────────────────────────────────────────────
n_rules = st.slider("Number of rules to display", 5, 50, 20)
rules_data = get_top_associations(n=n_rules)

if rules_data:
    debug_data = rules_data.get("debug") if isinstance(rules_data, dict) else None
    rules_list = rules_data if isinstance(rules_data, list) else rules_data.get("rules", [])
    if rules_list:
        rules_df = pd.DataFrame(rules_list)
        def _clean_join(x):
            if isinstance(x, list):
                return ", ".join(x)
            if isinstance(x, str):
                s = x.replace('\n', ',').replace('|', ',')
                parts = [p.strip() for p in s.split(',') if p and p.strip()]
                return ", ".join(parts)
            return str(x)

        if "antecedents" in rules_df.columns:
            rules_df["antecedents"] = rules_df["antecedents"].apply(_clean_join)
            rules_df["consequents"] = rules_df["consequents"].apply(_clean_join)

        st.dataframe(
            rules_df[["antecedents", "consequents", "support", "confidence", "lift"]]
            .sort_values("lift", ascending=False)
            .style.background_gradient(subset=["lift"], cmap="YlOrRd"),
            use_container_width=True,
            hide_index=True,
        )

        # Scatter chart
        st.divider()
        if all(c in rules_df.columns for c in ["support", "confidence", "lift"]):
            fig = association_network(rules_df)
            st.plotly_chart(fig, use_container_width=True)
    elif debug_data:
        st.warning("Association rules endpoint is unavailable. Showing backend diagnostics instead.")
        st.json(debug_data)
    else:
        st.info("No association rules available right now.")

# ── Contextual query ──────────────────────────────────────────────────────────
st.divider()
st.markdown("### Query Rules by Energy State")
st.caption("Find which rules apply given a partial energy condition.")

c1, c2, c3 = st.columns(3)
with c1:
    demand_f  = st.selectbox("Demand level",    [None, "LOW", "MED", "HIGH"])
with c2:
    price_f   = st.selectbox("Price level",     [None, "LOW", "MED", "HIGH"])
with c3:
    renew_f   = st.selectbox("Renewable level", [None, "LOW", "MED", "HIGH"])

if st.button("Find Matching Rules"):
    result = query_associations(
        demand_level=demand_f,
        price_level=price_f,
        renewable_level=renew_f,
    )
    if result:
        if isinstance(result, dict) and result.get("debug") and not result.get("rules"):
            st.warning("Rule query is unavailable. Showing backend diagnostics instead.")
            st.json(result.get("debug"))
            st.stop()
        matched = result.get("rules", [])
        if matched:
            for r in matched:
                def _fmt(item):
                    if isinstance(item, list):
                        return ", ".join(item)
                    if isinstance(item, str):
                        s = item.replace('\n', ',').replace('|', ',')
                        parts = [p.strip() for p in s.split(',') if p and p.strip()]
                        return ", ".join(parts)
                    return str(item)

                ant = _fmt(r["antecedents"])
                con = _fmt(r["consequents"])
                st.info(
                    f"**[{ant}]** → **[{con}]**  "
                    f"| support={r['support']:.3f}  "
                    f"confidence={r['confidence']:.3f}  "
                    f"lift={r['lift']:.3f}"
                )
        else:
            st.warning("No rules found for this combination.")
