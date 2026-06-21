
import streamlit as st
import pandas as pd
from pathlib import Path
import altair as alt



# the size of the list marker should be more than the different loading
list_marker=["circle","square","triangle-up","diamond","cross",
            "triangle-down","triangle-left","triangle-right","star",
            "star-open","hexagon","hexagon-open","circle-open", "square-open", 
            "diamond-open","triangle-up-open","triangle-down-open",
            "circle-dot","square-dot", "diamond-dot","triangle-up-dot",
            "triangle-down-dot","circle-cross","square-cross","diamond-cross",
            "triangle-up-cross","circle-x","square-x","diamond-x","triangle-up-x"]


    

    
# -------------------- Page Configuration --------------------
st.set_page_config(
    page_title="IceMechaData",
    page_icon="🧊",
)

# -------------------- Custom CSS --------------------

st.markdown("""
<style>

/* MODE CLAIR */
@media (prefers-color-scheme: light) {

    /* Selected tags in multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #4BA3D9 !important;
    }

    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
    }

    /* Slider active track */
    .stSlider [data-baseweb="slider"] > div > div:nth-child(1) {
        background: #4BA3D9 !important;
    }

    /* Slider handle */
    .stSlider [role="slider"] {
        background-color: #4BA3D9 !important;
        border-color: #4BA3D9 !important;
    }
}

/* MODE SOMBRE */
@media (prefers-color-scheme: dark) {

    /* Selected tags in multiselect */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #D9534F !important;
    }

    .stMultiSelect [data-baseweb="tag"] span {
        color: white !important;
    }
}

</style>
""", unsafe_allow_html=True)

# -------------------- Constants --------------------
# Load database
CSV_FILE ="data/Ice_Experimental_Data.csv"

# LOAD_ICONS = {
#     "Compression": "icons/compression.png",
#     "Tensile": "icons/tensile.png",
#     "Shear": "icons/shear.png",
#     "Twist": "icons/twist.png",
#     "Compression/Shear": "icons/compression_shear.png",
#     "Bending": "icons/bending.png",
# }

# -------------------- Load CSV --------------------
@st.cache_data
def load_csv(file_path=CSV_FILE):
    if not Path(file_path).exists():
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()

    # Coerce numeric
    for col in ["Stress (MPa)", "Minimum strain rate (s-1)", "Temperature (°C)", "Number of Grains", "Grain size"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

creep_df = load_csv()



# -------------------- Page Header --------------------
st.markdown("# 🧊 Experimental ice test Dashboard")

st.markdown("""
This interactive platform is designed for the exploration and analysis of **experimental data** on the mechanical behavior and creep of **ice**. The database compiles results from studies spanning from the early 20th century to the present day, bringing together a wide range of experimental conditions, including specimen geometry, temperature, applied stress or strain rate, loading history, and key microstructural characteristics.

The dashboard enables users to **visualize** and **compare** experimental results under diverse mechanical conditions, facilitating a deeper understanding of ice deformation processes and supporting the development and validation of constitutive flow laws.

While efforts have been made to standardize and pre-filter the available data to ensure consistency and usability, users are strongly encouraged to **consult the original publications** to verify experimental details, particularly regarding sample preparation, loading procedures, and measurement conditions. In particular, attention should be paid to the definitions of stress and strain rate, especially when comparing different experimental configurations, as equivalence between reported quantities (e.g., octahedral vs. uniaxial measures) is not always guaranteed.

Users and researchers are also encouraged to contribute to and **enrich** this database by uploading new datasets. This can be done by downloading the provided template via the **"Add your experimental data"** button and submitting the completed CSV file to Maurine or Olivier.""")

st.markdown("---")


st.markdown("## Search for mechanical ice experimental data")
# -------------------- User Controls --------------------
# Filters
tests = creep_df["Test"].unique().tolist() if "Test" in creep_df.columns else []
selected_tests = st.multiselect("🧪Select Type of Test *", tests, default=tests[:1] if tests else [])
loads = creep_df["Loading"].unique().tolist() if "Loading" in creep_df.columns else []
selected_loads = st.multiselect("⚒️ Select Loading Conditions *", loads, default=loads[:1] if loads else [])
selected_regime = st.multiselect("📈 Select Creep Regime ", creep_df["Regime"].dropna().unique() if "Regime" in creep_df.columns else [])
selected_specimen_type = st.multiselect("🧊 Select Ice Specimen type", creep_df["Specimen type"].dropna().unique() if "Specimen type" in creep_df.columns else [])
selected_composition = st.multiselect("🔬 Select Ice Composition", creep_df["Composition"].dropna().unique() if "Composition" in creep_df.columns else [])
selected_microstructure = st.multiselect("🧬 Select Microstructure type", creep_df["Microstructure"].dropna().unique() if "Microstructure" in creep_df.columns else [])
selected_texture = st.multiselect("❄️ Select Ice Texture", creep_df["Texture"].dropna().unique() if "Texture" in creep_df.columns else [])


# Sliders
selected_reference     = st.multiselect("📚 Select Reference from the database", creep_df["Reference"].dropna().unique() if "Reference" in creep_df.columns else [])
temp_min, temp_max     = st.slider("🌡️ Temperature Range (°C)", -90.0, 0.0, (-90.0, 0.0))
stress_min, stress_max = st.slider("🧱 Stress range (MPa)", 0.0 , 15.0, (0.0,15.0) )
strain_rate_min, strain_rate_max = st.slider("🧱 Strain rate range (x 10^(-8) s^(-1))", 0.00 , 1000.00, (0.00,10000.00))
strain_rate_min, strain_rate_max = strain_rate_min*(1e-8), strain_rate_max*(1e-8)



st.markdown("---")
# ============================================================
# Data filtering
# ============================================================

filtered_df = creep_df[
    (creep_df["Test"].isin(selected_tests))
    & (creep_df["Loading"].isin(selected_loads))
    & (creep_df["Temperature (°C)"].between(temp_min, temp_max))
    & (creep_df["Stress (MPa)"].between(stress_min, stress_max))
    & (creep_df["Minimum strain rate (s-1)"].between(strain_rate_min, strain_rate_max))
].copy()

# ============================================================
# Optional filters
# ============================================================

optional_filters = {
    "Microstructure": selected_microstructure,
    "Regime": selected_regime,
    "Composition": selected_composition,
    "Texture": selected_texture,
    "Specimen type": selected_specimen_type,
    "Reference": selected_reference,
}

for col, selected_values in optional_filters.items():
    if selected_values:
        filtered_df = filtered_df[
            filtered_df[col].isin(selected_values)
        ]

# ============================================================
# Check if data exists
# ============================================================

if filtered_df.empty:
    st.warning("No data matches selected filters.")

else:

    # ========================================================
    # Curve type selection
    # ========================================================

    plot_type = st.radio(
        "📊 Select Curve Type",
        [
            "Strain rate vs. Stress",
            "Stress vs. Strain rate",
            "Strain rate vs. Temperature",
            "Stress vs. Temperature",
        ],
        horizontal=True,
    )

    # ========================================================
    # Axis scale selection
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:
        x_scale = st.selectbox(
            "X-axis scale",
            ["Linear", "Log"],
            index=0,
        )

    with col2:
        y_scale = st.selectbox(
            "Y-axis scale",
            ["Linear", "Log"],
            index=0,
        )

    x_log = x_scale == "Log"
    y_log = y_scale == "Log"



    # ========================================================
    # Plot configuration
    # ========================================================

    plot_config = {
        "Strain rate vs. Stress": (
            "Stress (MPa)",
            "Minimum strain rate (s-1)",
        ),
        "Stress vs. Strain rate": (
            "Minimum strain rate (s-1)",
            "Stress (MPa)",
        ),
        "Strain rate vs. Temperature": (
            "Temperature (°C)",
            "Minimum strain rate (s-1)",
        ),
        "Stress vs. Temperature": (
            "Temperature (°C)",
            "Stress (MPa)",
        ),
    }

    x_col, y_col = plot_config[plot_type]

    # ========================================================
    # Curve labels
    # ========================================================

    if plot_type == "Strain rate vs. Temperature":

        filtered_df["Curve Label"] = (
            filtered_df["Stress (MPa)"].astype(str)
            + " MPa; "
            + filtered_df["Reference"].astype(str)
            + "; "
            + filtered_df["Loading"].astype(str)
            + " at "
            + filtered_df["Test"].astype(str)
        )

    elif plot_type == "Stress vs. Temperature":

        filtered_df["Curve Label"] = (
            filtered_df["Minimum strain rate (s-1)"].astype(str)
            + " s⁻¹; "
            + filtered_df["Reference"].astype(str)
            + "; "
            + filtered_df["Loading"].astype(str)
            + " at "
            + filtered_df["Test"].astype(str)
        )

    else:

        filtered_df["Curve Label"] = (
            filtered_df["Temperature (°C)"].astype(str)
            + " °C; "
            + filtered_df["Reference"].astype(str)
            + "; "
            + filtered_df["Loading"].astype(str)
            + " at "
            + filtered_df["Test"].astype(str)
        )

    # ========================================================
    # Prepare data for plotting
    # ========================================================

    df_plot = filtered_df.copy()

    if x_log:
        df_plot = df_plot[df_plot[x_col] > 0]

    if y_log:
        df_plot = df_plot[df_plot[y_col] > 0]

    # ========================================================
    # Marker mapping
    # ========================================================

    marker_map = {
        loads[i]: list_marker[i]
        for i in range(min(len(loads), len(list_marker)))
    }

    # ========================================================
    # Tooltips
    # ========================================================

    tooltip_cols = [
        c
        for c in [
            "Test",
            "Loading",
            "Regime",
            "Temperature (°C)",
            x_col,
            y_col,
            "Stress (MPa)",
            "Microstructure",
            "Composition",
            "Specimen type",
            "Origin",
            "Texture",
            "Density [kg/m3]",
            "Reference",
            "Remarks",
        ]
        if c in df_plot.columns
    ]

    # ========================================================
    # Interactive legend
    # ========================================================

    legend_selection = alt.selection_point(
        fields=["Curve Label"],
        bind="legend"
    )

    # ========================================================
    # Scatter plot
    # ========================================================

    chart = (
        alt.Chart(df_plot)
        .mark_point(size=70, opacity=0.75)
        .encode(
            x=alt.X(
                x_col,
                scale=alt.Scale(
                    type="log" if x_log else "linear"
                ),
            ),
            y=alt.Y(
                y_col,
                scale=alt.Scale(
                    type="log" if y_log else "linear"
                ),
            ),
            color=alt.Color(
                "Curve Label:N",
                title="Curve"
            ),
            shape=alt.Shape(
                "Loading:N",
                scale=alt.Scale(
                    domain=list(marker_map.keys()),
                    range=list(marker_map.values()),
                ),
            ),
            tooltip=tooltip_cols,
            opacity=alt.condition(
                legend_selection,
                alt.value(1),
                alt.value(0.15),
            ),
        )
        .add_params(legend_selection)
        .interactive()
    )

    st.altair_chart(
        chart,
        use_container_width=True,
    )

 



    # --------------------------------- Download buttons ---------------------------------
    # Dowload csv file
    file_name = st.text_input("Save your selected data in a csv file:",value="ice_data")
    csv = df_plot.to_csv(index=False).encode("utf-8")
    st.download_button(label="📄 Download Data as csv file", data=csv, file_name=f"{file_name}.csv", mime="text/csv")


    # References
    st.markdown("#### 📚 Others informations and References of your selected experimental data")
    # protect against missing fields in filtered_df
    if not filtered_df.empty and {"Reference", "Loading"}.issubset(filtered_df.columns):
        clean = lambda x: "" if pd.isna(x) else x
        def bold(x):
            return f"**{x}**" if x not in [None, "", "nan"] and not pd.isna(x) else ""

        for _, row in filtered_df.drop_duplicates("Reference").iterrows():
            # safe accesses with .get and fallback
            texture           =  clean(row.get("Texture", ""))
            composition       =  clean(row.get("Composition", ""))
            density           =  row.get("Density (kg/m3)", "") if isinstance(row, dict) else row.get("Density (kg/m3)", "")
            microstructure    =  clean(row.get("Microstructure", "")) 
            regime            =  clean(row.get("Regime", ""))
            ice_specimen_type =  clean(row.get("Specimen type", "")) 
            ice_origin        =  clean(row.get("Origin", "")) 
            texture_availability = clean(row.get("Texture availability", ""))
            if texture_availability == "":
                texture_availability = "Texture is not available"
            else:
                texture_availability = f"Texture is available as **{texture_availability}**"

            spec              = row.get("Specimen dimension (mm)", "") if isinstance(row, dict) else row.get("Specimen dimension (mm)", "")
            grain_num         = row.get("Number of Grains", "") if isinstance(row, dict) else row.get("Number of Grains", "")
            grain_size        = row.get("Grain size", "") if isinstance(row, dict) else row.get("Grain size", "")
            url               = clean(row.get("URL", "")) 
            st.markdown(
                f"- **{row['Loading']}** test for {bold(texture)} {bold(composition)} {bold(ice_specimen_type)} {bold(ice_origin)} ice ,<br>"
                f"**{microstructure}** microstructure,<br>"
                f"Density (kg/m3): **{density}**,<br>"
                f"{texture_availability},<br>" 
                f"Data available: {bold(regime)},<br>"
                f"Specimen dimension [mm]: **{spec}**; Number of Grains: **{grain_num}**; Grain size: **{grain_size}**,<br>"
                f"Reference : [{row['Reference']}]({url})",
                unsafe_allow_html=True
            )



st.markdown("---")

st.markdown("## ➕ Add your experimental ice data")
template_df = pd.DataFrame(columns=creep_df.columns)
csv = template_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📄 Download template CSV file",
    data=csv,
    file_name="your_ice_data.csv",
    mime="text/csv"
)

# ------------------------------------- Logos -----------------------------------------
st.markdown("---")
st.markdown("### 🏷️ Partners / Sponsors")

default_logos = [
    "logos/CNRS.png", "logos/AISSAI.jpg", "logos/ENSAM.png","logos/PIMM.jpg",
    "logos/UGA.png", "logos/IPGP.png", "logos/University_pens.jpg",
    "logos/UNF.jpg",  "logos/IGE.jpg"
]

logo_height = 80

# Split into 2 rows
mid = len(default_logos) // 2
row1 = default_logos[:mid]
row2 = default_logos[mid:]

def display_logos(logo_list):
    cols = st.columns(len(logo_list))
    for i, logo_path in enumerate(logo_list):
        with cols[i]:
            try:
                p = Path(logo_path)
                if p.exists():
                    img = Image.open(p)
                    w, h = img.size
                    aspect_ratio = w / h
                    img_resized = img.resize((int(logo_height * aspect_ratio), logo_height))
                    st.image(img_resized)
                else:
                    st.text("Logo not found")
            except Exception as e:
                st.error(f"Could not load logo: {logo_path}\n{e}")

# Display two rows
display_logos(row1)
display_logos(row2)

# ------------------------------------- Creators -----------------------------------------
st.markdown("---")
st.markdown("### 👨‍💻 Creators")

creators = [
    {
        "name": "Mohammed El Fallaki Idrissi",
        "photo": "logos/mohammed_el_fallaki.jpg",
        "profile": "https://scholar.google.com/citations?user=OkTyXZEAAAAJ&hl=fr&oi=ao"
    },
    {
        "name": "Olivier Castelnau",
        "photo": "logos/Olivier_Castelnau.jpg",
        "profile": "https://scholar.google.com/citations?user=Ex27gtsAAAAJ&hl=fr&oi=ao"
    },
    {
        "name": "Maurine Montagnat",
        "photo": "logos/Maurine_Montagnat.jpg",
        "profile": "https://scholar.google.com/citations?user=PIktjNoAAAAJ&hl=fr&oi=ao"
    },
    {
        "name": "Anne Mangeney",
        "photo": "logos/Anne_Mangeney.png",
        "profile": "https://scholar.google.com/citations?user=YxudVy0AAAAJ&hl=fr"
    },
    {
        "name": "Mikhael Tannous",
        "photo": "logos/Mikhael_Tannous.jpg",
        "profile": "https://scholar.google.com/citations?user=VSgWgTYAAAAJ&hl=fr"
    },    
    {
        "name": "Olivier Gagliardini",
        "photo": "logos/Olivier_Gagliardini.png",
        "profile": "https://scholar.google.com/citations?user=hkGnXdkAAAAJ&hl=fr&oi=ao"
    },
    {
        "name": "Chady Ghnatios",
        "photo": "logos/chady_ghnatios.jpeg",
        "profile": "https://scholar.google.com/citations?user=FtdnpGkAAAAJ&hl=fr"
    },
    {
        "name": "Pedro Ponte Castañeda",
        "photo": "logos/Pedro_Ponte.jpg",
        "profile": "https://scholar.google.com/citations?user=TO4xGe0AAAAJ&hl=fr&oi=ao"
    },    
    {
        "name": "Francisco Chinesta",
        "photo": "logos/Francisco_Chinesta.jpg",
        "profile": "https://scholar.google.com/citations?user=bUC7RZcAAAAJ&hl=fr&oi=ao"
    },
]



cols_creators = st.columns(len(creators))
fixed_height = 300  # all images will have the same display height

for i, creator in enumerate(creators):
    with cols_creators[i]:
        try:
            p = Path(creator["photo"])
            if p.exists():
                img = Image.open(p)
                # Resize while keeping aspect ratio, but force the same height
                w, h = img.size
                new_w = int((fixed_height / h) * w)
                img_resized = img.resize((new_w, fixed_height))
                st.image(img_resized, use_container_width=False)
            else:
                st.text("Photo not found")

            # Use the name itself as a clickable link
            st.markdown(f"[{creator['name']}]({creator['profile']})", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Could not load photo: {creator['photo']}\n{e}")

