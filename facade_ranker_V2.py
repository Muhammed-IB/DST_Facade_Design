import streamlit as st
import pandas as pd
import os
import ahpy
import plotly.graph_objects as go
import streamlit.components.v1 as components
import hashlib

# --- Sub-criteria mapping (hardcoded)
criteria_groups = {
    "Environmental impact": [
        "Embodied energy and carbon emission",
        "Cooling load",
        "Heating load"
    ],
    "Cost": [
        "Material cost",
        "Maintenance cost"
    ],
    "Performance": [
        "Thermal resistance",
        "Weight",
        "Acoustic insulation"
    ]
}

# --- Page setup
st.set_page_config(page_title="Façade AHP App", layout="wide", initial_sidebar_state="expanded")
st.title("AHP Ranking of Façade Alternatives")
st.write("Adjust criteria and sub-criteria weights using the sidebar.")

# --- CSV Hash Tracker (to detect changes)
st.session_state.setdefault("csv_hash", "")

# --- Refresh Button
if st.sidebar.button("🔄 Refresh CSV Data"):
    # Save all slider states before clearing cache
    st.session_state["preserve_weights"] = {
        "env_weight": st.session_state.get("env_weight", 0.384),
        "cost_weight": st.session_state.get("cost_weight", 0.306),
        "perf_weight": st.session_state.get("perf_weight", 0.31),
        **{f"sub_weight_{sub}": st.session_state.get(f"sub_weight_{sub}", 0.3) for crit in criteria_groups.values() for sub in crit}
    }
    st.cache_data.clear()
    st.session_state["csv_hash"] = ""
    st.rerun()

# --- Load CSVs from Google Sheets
@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

def get_csv_hash(*dfs):
    hash_obj = hashlib.md5()
    for df in dfs:
        hash_obj.update(pd.util.hash_pandas_object(df, index=True).values)
    return hash_obj.hexdigest()

embodied = load_csv("https://docs.google.com/spreadsheets/d/1_AJSouqI112bksEEn6l7SCKNQ2hEjM5yUuBQQLn0Po8/export?format=csv")
load = load_csv("https://docs.google.com/spreadsheets/d/1vDEAI1BQlIl7CXQjIFqGvbfA9IGb8L9kfWb_Ke_Ss2E/export?format=csv")
material_cost = load_csv("https://docs.google.com/spreadsheets/d/1NUo2W1kDuBJNg_hdzZI0fr4BqqkmkGCZXvldHYD15bo/export?format=csv")
maintenance = load_csv("https://docs.google.com/spreadsheets/d/1zMnae3F6lK-dtnpPXtJwPXT93G5lrRGndnqTBLeSoMM/export?format=csv")
performance = load_csv("https://docs.google.com/spreadsheets/d/1N0U5D5TSJNvC__CEzPW-gYCu6QRfRcgd-XmqGvw6p4Y/export?format=csv")
acoustic = load_csv("https://docs.google.com/spreadsheets/d/1Co6mFTKuoh-CcCWl67wjOMpP2h7eJaYLB9fF-sX1Xr0/export?format=csv")

current_hash = get_csv_hash(embodied, load, material_cost, maintenance, performance, acoustic)
previous_hash = st.session_state.get("previous_csv_hash", "")

if previous_hash and current_hash != previous_hash:
    st.warning("⚠️ Your data has changed. Value inherited.")

# Store the current hash as latest known for next session
st.session_state["previous_csv_hash"] = current_hash

# --- Normalize
normalize_inverse = lambda series: (series.max() - series) / (series.max() - series.min()) + 1e-6
normalize_direct = lambda series: (series - series.min()) / (series.max() - series.min()) + 1e-6

df = pd.DataFrame()
df["Alternative"] = embodied["Alternative"]
df["Embodied"] = normalize_inverse(embodied["Total Embodied Carbon (KgCO2-e)"])
avg_load = (load["Peak Cooling Load (W)"] + load["Peak Heating Load (W)"]) / 2
df["Cooling_Heating"] = normalize_inverse(avg_load)
df["Material_Cost"] = normalize_inverse(material_cost.iloc[:, 2])
df["Maintenance_Cost"] = normalize_inverse(maintenance.iloc[:, 2])
df["Weight"] = normalize_inverse(embodied["Material Weight (kg)"])
df["Thermal_Resistance"] = normalize_direct(performance["Thermal Resistance (m²K/W)"])
df["Acoustic"] = normalize_direct(acoustic["Sound Reduction Index Rw (dB)"])

# --- AHP helpers
def create_pairwise(scores, names):
    comparisons = {}
    epsilon = 1e-6
    safe_scores = [s + epsilon for s in scores]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            comparisons[(names[i], names[j])] = safe_scores[i] / safe_scores[j]
    return comparisons

alt_names = list(df["Alternative"])

# --- Sub-criteria mapping (hardcoded)
criteria_groups = {
    "Environmental impact": [
        "Embodied energy and carbon emission",
        "Cooling load",
        "Heating load"
    ],
    "Cost": [
        "Material cost",
        "Maintenance cost"
    ],
    "Performance": [
        "Thermal resistance",
        "Weight",
        "Acoustic insulation"
    ]
}

sub_map = {
    'Embodied energy and carbon emission': 'Embodied',
    'Cooling load': 'Cooling_Heating',
    'Heating load': 'Cooling_Heating',
    'Material cost': 'Material_Cost',
    'Maintenance cost': 'Maintenance_Cost',
    'Weight': 'Weight',
    'Thermal resistance': 'Thermal_Resistance',
    'Acoustic insulation': 'Acoustic'
}

# --- Restore preserved weights if available
if "preserve_weights" in st.session_state:
    for k, v in st.session_state["preserve_weights"].items():
        st.session_state[k] = v
    del st.session_state["preserve_weights"]

# --- Sidebar sliders
st.sidebar.header("🔧 Criteria Weights")
def slider_with_state(key, label, min_val, max_val, default, step):
    return st.sidebar.slider(label, min_val, max_val, st.session_state.get(key, default), step, key=key)

env_w = slider_with_state("env_weight", "Environmental Impact", 0.01, 1.0, 0.384, 0.01)
cost_w = slider_with_state("cost_weight", "Cost", 0.01, 1.0, 0.306, 0.01)
perf_w = slider_with_state("perf_weight", "Performance", 0.01, 1.0, 0.31, 0.01)
total = env_w + cost_w + perf_w
env_w, cost_w, perf_w = env_w / total, cost_w / total, perf_w / total

st.sidebar.header("⚙️ Sub-Criteria Weights")
sub_weights = {}
for crit, subs in criteria_groups.items():
    st.sidebar.markdown(f"**{crit}**")
    for sub in subs:
        key = f"sub_weight_{sub}"
        if key not in st.session_state:
            st.session_state[key] = 0.3
        sub_weights[sub] = st.sidebar.slider(sub, 0.01, 1.0, st.session_state[key], 0.01, key=key)

# --- Build AHP Tree
sub_nodes = {}
for sub, col in sub_map.items():
    scores = df[col].tolist()
    sub_nodes[sub] = ahpy.Compare(sub, create_pairwise(scores, alt_names), precision=4)

group_nodes = {}
for crit, subs in criteria_groups.items():
    weights = [sub_weights[c] for c in subs]
    pairwise = {}
    for i in range(len(subs)):
        for j in range(i + 1, len(subs)):
            pairwise[(subs[i], subs[j])] = weights[i] / weights[j]
    group_nodes[crit] = ahpy.Compare(crit, pairwise)
    group_nodes[crit].add_children([sub_nodes[c] for c in subs])

top_comp = {
    ('Environmental impact', 'Cost'): env_w / cost_w,
    ('Cost', 'Performance'): cost_w / perf_w
}
final = ahpy.Compare("Overall Goal", top_comp)
final.add_children([group_nodes["Environmental impact"], group_nodes["Cost"], group_nodes["Performance"]])

# --- Ranking Results
st.subheader("🏆 Ranking Results")
ranked = sorted(final.target_weights.items(), key=lambda x: x[1], reverse=True)
ranking_df = pd.DataFrame(ranked, columns=["Alternative", "Score"])
st.dataframe(ranking_df.style.format({"Score": "{:.4f}"}))

# --- Ranked Images (grid view)
st.subheader("🖼️ Ranked Façade Alternatives")
image_path = "images"
cols_per_row = 3
rows = [ranked[i:i+cols_per_row] for i in range(0, len(ranked), cols_per_row)]

for row in rows:
    columns = st.columns(len(row))
    for (alt, score), col in zip(row, columns):
        with col:
            img_path = os.path.join(image_path, f"{alt}.png")
            st.markdown(f"**{alt}** – Score: `{score:.4f}`")
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Façade {alt}", width=250)
            else:
                st.warning(f"Image not found for {alt}")

# --- Consistency Ratio
st.markdown(f"📊 **Consistency Ratio:** `{round(final.consistency_ratio, 4)}`")

import streamlit as st
import plotly.graph_objects as go

# Sample setup
st.subheader("📉 Parallel Coordinates: Sub-Criteria Comparison")

# Assuming df and ranked are already defined earlier
plot_df = df.set_index("Alternative").loc[[alt for alt, _ in ranked]]

columns = [
    ('Embodied', 'Embodied Carbon'),
    ('Cooling_Heating', 'Cooling/Heating'),
    ('Material_Cost', 'Material Cost'),
    ('Maintenance_Cost', 'Maintenance Cost'),
    ('Weight', 'Weight'),
    ('Thermal_Resistance', 'Thermal Resistance'),
    ('Acoustic', 'Acoustic Insulation'),
]

dimensions = [
    dict(
        label=label,
        values=plot_df[col]
    )
    for col, label in columns
]

highlight_alt = ranked[0][0]
color_array = [1 if alt == highlight_alt else 0 for alt in plot_df.index]

fig = go.Figure(data=go.Parcoords(
    line=dict(color=color_array, colorscale=[[0, 'black'], [1, 'red']], showscale=False),
    dimensions=dimensions
))

fig.update_layout(
    margin=dict(l=40, r=40, t=40, b=40),
    height=500,
    font=dict(color='black'),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig, use_container_width=True)

