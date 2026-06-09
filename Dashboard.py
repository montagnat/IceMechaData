########################################################################################################
##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++####
##**************************************************************************************************####
########################################################################################################


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from pathlib import Path
import altair as alt
from PIL import Image
from pathlib import Path


# the size of the list marker should be more than the different loading
list_marker=["circle","square","triangle-up","diamond","cross","triangle-down"]

# -------------------- Page Configuration --------------------
st.set_page_config(
    page_title="Ice Test Dashboard",
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
CSV_FILE = "data/creep_data.csv"

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
    rename_map = {
        "Temperature [°C]": "Temperature (°C)",
        "Stress [Mpa]": "Stress (MPa)",
        "Minimum strain rate [s^(-1)]": "Minimum strain rate (s-1)",
        "Loading": "Load",
        "Specimen dimension [mm]": "Specimen Dimension (mm)",
        "Number of Grains": "Grain number",
        "Size of Grains [mm]": "Grain size [mm]"
    }


    df = df.rename(columns=rename_map)
    # Coerce numeric
    for col in ["Stress (MPa)", "Minimum strain rate (s-1)", "Temperature (°C)", "Grain number", "Grain size [mm]"]:
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

Users and researchers are also encouraged to contribute to and **enrich** this database by uploading new datasets. This can be done by downloading the provided template via the **"Add your experimental results"** button and submitting the completed CSV file to Maurine or Olivier.""")

st.markdown("---")

# -------------------- User Controls --------------------
# Filters
tests = creep_df["Test"].unique().tolist() if "Test" in creep_df.columns else []
selected_tests = st.multiselect("🧪Select Type of Test *", tests, default=tests[:1] if tests else [])
loads = creep_df["Load"].unique().tolist() if "Load" in creep_df.columns else []
selected_loads = st.multiselect("⚒️ Select Loading Conditions *", loads, default=loads[:1] if loads else [])
selected_regime = st.multiselect("⚒️ Select Creep Regime ", creep_df["Regime"].dropna().unique() if "Regime" in creep_df.columns else [])
selected_origin = st.multiselect("🧊 Select Ice Specimen Origin", creep_df["Origin"].dropna().unique() if "Origin" in creep_df.columns else [])
selected_nature = st.multiselect("🔬 Select Ice Nature", creep_df["Nature"].dropna().unique() if "Nature" in creep_df.columns else [])
selected_microstructure = st.multiselect("🧬 Select microstructure Type", creep_df["Microstructure"].dropna().unique() if "Microstructure" in creep_df.columns else [])
selected_texture = st.multiselect("❄️ Select Ice Texture", creep_df["Texture"].dropna().unique() if "Texture" in creep_df.columns else [])


# Sliders
selected_reference     = st.multiselect("📚 Select Reference from the database", creep_df["Reference"].dropna().unique() if "Reference" in creep_df.columns else [])
temp_min, temp_max     = st.slider("🌡️ Temperature Range (°C)", -65.0, 0.0, (-65.0, 0.0))
stress_min, stress_max = st.slider("🧱 Stress range (MPa)", 0.0 , 10.0, (0.0,10.0) )
strain_rate_min, strain_rate_max = st.slider("🧱 Strain rate range (x 10^(-8) s^(-1))", 0.00 , 1000.00, (0.00,10000.00))
strain_rate_min, strain_rate_max = strain_rate_min*(1e-8), strain_rate_max*(1e-8)




# Ploting:
plot_mode = st.radio("📊 Plot the selected data or your experimental data :", ["Macroscopic response", "Add your experimental results"])

# -------------------- Plotting --------------------
if plot_mode == "Macroscopic response":
    # Obligatory filters
    filtered_df = creep_df[
        (creep_df["Test"].isin(selected_tests)) &
        (creep_df["Load"].isin(selected_loads)) &
        (creep_df["Temperature (°C)"].between(temp_min, temp_max)) &
        (creep_df["Stress (MPa)"].between(stress_min, stress_max)) &
        (creep_df["Minimum strain rate (s-1)"].between(strain_rate_min, strain_rate_max))
    ].copy()

    # optionaly filters
    if selected_microstructure:
        filtered_df = filtered_df[filtered_df["Microstructure"].isin(selected_microstructure)]
    if selected_regime:
        filtered_df = filtered_df[filtered_df["Regime"].isin(selected_regime)]        
    if selected_nature:
        filtered_df = filtered_df[filtered_df["Nature"].isin(selected_nature)]
    if selected_texture:
        filtered_df = filtered_df[filtered_df["Texture"].isin(selected_texture)]   
    if selected_origin:
        filtered_df = filtered_df[filtered_df["Origin"].isin(selected_origin)]                
    if selected_reference:
        filtered_df = filtered_df[filtered_df["Reference"].isin(selected_reference)]



# if there is no data
    if filtered_df.empty:
        st.warning("No data matches selected filters.")
    else:
        if plot_mode == "Macroscopic response":
            plot_type = st.radio(
                "📊 Select Curve Type",
                ["Strain rate vs. Stress", "Strain rate vs. Stress (Log)", "Stress vs. Strain rate", "Stress vs. Strain rate (Log)",  "Strain rate vs. Temperature", "Stress vs. Temperature"]
            )

            if plot_type=="Strain rate vs. Temperature":
                # Labels for "Strain rate vs. Temperature"
                filtered_df["Curve Label"] = (
                    filtered_df.get("Stress (MPa)", "").astype(str) + " MPa; " +
                    filtered_df["Reference"].astype(str)+ "; "+
                    filtered_df["Load"].astype(str) + " at " +
                    filtered_df["Test"].astype(str) 
                )    
            elif plot_type=="Stress vs. Temperature":
                # label for "Stress vs. Temperature"
                filtered_df["Curve Label"] = (
                    filtered_df.get("Minimum strain rate (s-1)", "").astype(str) + " s-1; " +
                    filtered_df["Reference"].astype(str)+ "; "+
                    filtered_df["Load"].astype(str) + " at " +
                    filtered_df["Test"].astype(str) 
                )      
            else:
            # Labels for ["Strain rate vs. Stress", "Strain rate vs. Stress (Log)", "Stress vs. Strain rate", "Stress vs. Strain rate (Log)"]
                filtered_df["Curve Label"] = (
                    filtered_df.get("Temperature (°C)", "").astype(str) + "°C; " +
                    filtered_df["Reference"].astype(str)+ "; "+
                    filtered_df["Load"].astype(str) + " at " +
                    filtered_df["Test"].astype(str) 
                
                )

            df_plot = filtered_df.copy()
            if plot_type == "Strain rate vs. Stress":
                x_col, y_col = "Stress (MPa)", "Minimum strain rate (s-1)"
                x_log, y_log = False, False
            elif plot_type == "Strain rate vs. Stress (Log)":
                x_col, y_col = "Stress (MPa)", "Minimum strain rate (s-1)"
                df_plot = df_plot[(df_plot["Stress (MPa)"] > 0) & (df_plot["Minimum strain rate (s-1)"] > 0)]
                x_log, y_log = True, True
            elif plot_type == "Stress vs. Strain rate":
                x_col, y_col = "Minimum strain rate (s-1)", "Stress (MPa)"
                x_log, y_log = False, False
            elif plot_type == "Stress vs. Strain rate (Log)":
                x_col, y_col = "Minimum strain rate (s-1)", "Stress (MPa)"                
                df_plot = df_plot[(df_plot["Stress (MPa)"] > 0) & (df_plot["Minimum strain rate (s-1)"] > 0)]
                x_log, y_log = True, True                
            elif plot_type == "Strain rate vs. Temperature":
                x_col, y_col = "Temperature (°C)", "Minimum strain rate (s-1)"
                x_log, y_log = False, True
            elif plot_type == "Stress vs. Temperature":
                x_col, y_col = "Temperature (°C)", "Stress (MPa)" 
                x_log, y_log = False, True
            
            # Marker types for scatter points 
            marker_map = {}
            for i in range(len(loads)):
                marker_map[loads[i]] = list_marker[i]
           
           # Features of each scatter points (shown after puting the cursor on the data point)
            tooltip_cols = [c for c in ["Test","Load", "Regime","Temperature (°C)",x_col,y_col,"Stress (MPa)","Microstructure","Nature","Origin","Texture",  "Density [kg/m3]","Reference","Remarks"] if c in df_plot.columns]
            legend_selection = alt.selection_point(fields=["Curve Label"], bind="legend")
            chart = alt.Chart(df_plot).mark_point(size=60, opacity=0.7).encode(
                x=alt.X(x_col, scale=alt.Scale(type='log' if x_log else 'linear')),
                y=alt.Y(y_col, scale=alt.Scale(type='log' if y_log else 'linear')),
                color="Curve Label:N",
                shape=alt.Shape("Load:N", scale=alt.Scale(domain=list(marker_map.keys()), range=list(marker_map.values()))),
                tooltip=tooltip_cols,
                opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2))
            ).add_params(legend_selection)
            st.altair_chart(chart, use_container_width=True)



 

    # --------------------------------- Download buttons ---------------------------------
    # Dowload csv file
        file_name = st.text_input("Save your selected data in a csv file:",value="ice_data")
        csv = df_plot.to_csv(index=False).encode("utf-8")
        st.download_button(label="📄 Download Data as csv file", data=csv, file_name=f"{file_name}.csv", mime="text/csv")


    # References
    st.markdown("### 📚 Others informations and References of your selected experimental data")
    # protect against missing fields in filtered_df
    if not filtered_df.empty and {"Reference", "Load"}.issubset(filtered_df.columns):
        for _, row in filtered_df.drop_duplicates("Reference").iterrows():
            # safe accesses with .get and fallback
            texture = row.get("Texture", "") if isinstance(row, dict) else row.get("Texture", "")
            nature = row.get("Nature", "") if isinstance(row, dict) else row.get("Nature", "")
            density = row.get("Density [kg/m3]", "") if isinstance(row, dict) else row.get("Density [kg/m3]", "")
            microstructure =  row.get("Microstructure", "") if isinstance(row, dict) else row.get("Microstructure", "")
            regime =  row.get("Regime", "") if isinstance(row, dict) else row.get("Regime", "")
            origin_ice = row.get("Origin", "") if isinstance(row, dict) else row.get("Origin", "")
            texture_availability = row.get("Texture availability", "") if isinstance(row, dict) else row.get("Texture availability", "")
            spec = row.get("Specimen Dimension (mm)", "") if isinstance(row, dict) else row.get("Specimen Dimension (mm)", "")
            grain_num = row.get("Grain number", "") if isinstance(row, dict) else row.get("Grain number", "")
            grain_size = row.get("Grain size [mm]", "") if isinstance(row, dict) else row.get("Grain size [mm]", "")
            url = row.get("URL", "#") if isinstance(row, dict) else row.get("URL", "#")
            st.markdown(
                f"- **{row['Load']}** test for {texture} {nature} {origin_ice} ice,<br>"
                f"**{microstructure}** microstructure,<br>"
                f"Density [kg/m3]: **{density}**,<br>"
                f"Texture is available as **{texture_availability}**,<br>" 
                f"Data available: **{regime}**,<br>"
                f"Specimen dimension [mm]: **{spec}**; Number of Grains: **{grain_num}**; Grain size [mm]: **{grain_size}**,<br>"
                f"Reference : [{row['Reference']}]({url})",
                unsafe_allow_html=True
            )

else:
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













































#plot_mode = st.radio("📊 Mode", ["Macroscopic response", "Add New Data"])
# if plot_mode == "Add New Data":
#     st.subheader("➕ Add New Creep Data")

#     col1, col2 = st.columns(2)

#     # --- Column 1 ---
#     with col1:
#         new_test = st.selectbox("Test", ["Creep", "Relaxiation"])        
#         new_load = st.selectbox("Load", ["Compression", "Tensile", "Shear", "Twist", "Compression/Shear"])
#         new_temperature = st.number_input("Temperature (°C)", value=0.0, min_value=-100.0, max_value=0.0, step=0.1)
#         new_stress = st.number_input("Stress (MPa)", value=0.0)
#         new_strain_rate = st.number_input("Minimum strain rate (s-1)", value=1e-10, step=1e-10, format="%.10e")

#         # Only show bidirectional inputs if Compression/Shear is selected
#         if new_load == "Compression/Shear":
#             new_strain_rate_bid = st.number_input(
#                 "Minimum strain rate bidirectional (s-1)", value=1e-10, step=1e-10, format="%.10e"
#             )
#             new_stress_bid = st.number_input("Stress bidirectional (MPa)", value=0.0)
#         else:
#             new_strain_rate_bid = None
#             new_stress_bid = None

#         new_nature = st.selectbox("Nature", ["pure", "impure"])
#         new_density = st.number_input("Density (kg/m3)", value=0.0)

#     # --- Column 2 ---
#     with col2:
#         new_origin_ice = st.selectbox("Origin", ['artificial', 'sea', 'sheet', 'glacier'])
#         new_texture = st.selectbox("Texture", ["isotropic", "anisotropic"])
#         new_microstructure = st.selectbox("Microstructure", ["Monocrystal", "Polycrystal"])
#         new_grains = st.number_input("Grain number", value=0)
#         new_grain_size = st.number_input("Grain size (mm)", value=0.0)
#         new_grain_size_method = st.text_input("Grain size computing methods")
#         new_specimen = st.text_input("Specimen Dimension (mm)")
#         new_reference = st.text_input("Reference")
#         new_url = st.text_input("URL")
#         new_remarks = st.text_area("Remarks")

#     # --- Submit Button ---
#     if st.button("Add Data"):
#         new_row = {
#             "Test": new_test,
#             "Load": new_load,
#             "Specimen Dimension (mm)": new_specimen,
#             "Temperature (°C)": new_temperature,
#             "Stress (MPa)": new_stress,
#             "Minimum strain rate (s-1)": new_strain_rate,
#             "Stress bidirectional (MPa)": new_stress_bid,
#             "Minimum strain rate bidirectional (s-1)": new_strain_rate_bid,
#             "Origin": new_origin_ice,
#             "Texture": new_texture,
#             "Nature": new_nature,
#             "Density [kg/m3]": new_density,
#             "Microstructure": new_microstructure,
#             "Grain number": new_grains,
#             "Grain size [mm]": new_grain_size,
#             "Grain size computing methods": new_grain_size_method,
#             "Reference": new_reference,
#             "URL": new_url,
#             "Remarks": new_remarks
#         }

#         df_new = pd.DataFrame([new_row])
#         if Path(CSV_FILE).exists():
#             df_new.to_csv(CSV_FILE, mode="a", index=False, header=False)
#         else:
#             df_new.to_csv(CSV_FILE, index=False)

#         st.success("✅ New data added successfully!")

#         # Update your DataFrame
#         creep_df = pd.concat([creep_df, df_new], ignore_index=True)


# # -------------------- Plotting --------------------
# else:
#     filtered_df = creep_df[
#         (creep_df["Test"].isin(selected_tests)) &
#         (creep_df["Load"].isin(selected_loads)) &
#         (creep_df["Temperature (°C)"].between(temp_min, temp_max)) &
#         (creep_df["Stress (MPa)"].between(stress_min, stress_max)) &
#         (creep_df["Minimum strain rate (s-1)"].between(strain_rate_min, strain_rate_max))
#     ].copy()
#     if selected_microstructure:
#         filtered_df = filtered_df[filtered_df["Microstructure"].isin(selected_microstructure)]
#     if selected_regime:
#         filtered_df = filtered_df[filtered_df["Regime"].isin(selected_regime)]        
#     if selected_nature:
#         filtered_df = filtered_df[filtered_df["Nature"].isin(selected_nature)]
#     if selected_texture:
#         filtered_df = filtered_df[filtered_df["Texture"].isin(selected_texture)]   
#     if selected_origin:
#         filtered_df = filtered_df[filtered_df["Origin"].isin(selected_origin)]                
#     if selected_reference:
#         filtered_df = filtered_df[filtered_df["Reference"].isin(selected_reference)]

#     if filtered_df.empty:
#         st.warning("No data matches selected filters.")
#     else:
#         if plot_mode == "Macroscopic response":
#             # Curve labels
#             filtered_df["Curve Label"] = (
#                 filtered_df.get("Temperature (°C)", "").astype(str) + "°C; " +
#                 filtered_df["Reference"].astype(str)+ "; "+
#                 filtered_df["Load"].astype(str) + " at " +
#                 filtered_df["Test"].astype(str) 
                
#             )
#             plot_type = st.radio(
#                 "📊 Select Curve Type",
#                 ["Strain rate vs. Stress", "Strain rate vs. Stress (Log)", "Stress vs. Strain rate", "Stress vs. Strain rate (Log)",  "Strain rate vs. Temperature", "Stress vs. Temperature"]
#             )
#             df_plot = filtered_df.copy()
#             if plot_type == "Strain rate vs. Stress":
#                 x_col, y_col = "Stress (MPa)", "Minimum strain rate (s-1)"
#                 x_log, y_log = False, False
#             elif plot_type == "Strain rate vs. Stress (Log)":
#                 x_col, y_col = "Stress (MPa)", "Minimum strain rate (s-1)"
#                 df_plot = df_plot[(df_plot["Stress (MPa)"] > 0) & (df_plot["Minimum strain rate (s-1)"] > 0)]
#                 x_log, y_log = True, True
#             elif plot_type == "Stress vs. Strain rate":
#                 x_col, y_col = "Minimum strain rate (s-1)", "Stress (MPa)"
#                 x_log, y_log = False, False
#             elif plot_type == "Stress vs. Strain rate (Log)":
#                 x_col, y_col = "Minimum strain rate (s-1)", "Stress (MPa)"                
#                 df_plot = df_plot[(df_plot["Stress (MPa)"] > 0) & (df_plot["Minimum strain rate (s-1)"] > 0)]
#                 x_log, y_log = True, True                
#             elif plot_type == "Strain rate vs. Temperature":
#                 filtered_df["Curve Label"] = (
#                     filtered_df["Load"].astype(str) + " (" + filtered_df.get("Stress (MPa)", "").astype(str) + " MPa) | " + filtered_df["Reference"].astype(str)
#                 )
#                 df_plot = filtered_df.copy()
#                 stress_with_multiple_temps = (
#                     df_plot.groupby("Stress (MPa)")["Temperature (°C)"].nunique().reset_index()
#                 )
#                 stress_with_multiple_temps = stress_with_multiple_temps[stress_with_multiple_temps["Temperature (°C)"] >= 2]["Stress (MPa)"].unique()
#                 df_plot = df_plot[df_plot["Stress (MPa)"].isin(stress_with_multiple_temps)]
#                 if len(stress_with_multiple_temps) == 0:
#                     st.warning("⚠️ No stress values found under multiple temperatures.")
#                 else:
#                     stress_val = st.selectbox("🧱 Select Fixed Stress (MPa)", options=np.sort(np.round(stress_with_multiple_temps,2)))
#                     tolerance = 0.1
#                     df_plot = df_plot[np.abs(df_plot["Stress (MPa)"] - stress_val) <= tolerance]
#                 x_col, y_col = "Temperature (°C)", "Minimum strain rate (s-1)"
#                 x_log, y_log = False, True
#             elif plot_type == "Stress rate vs. Temperature":
#                 filtered_df["Curve Label"] = (
#                     filtered_df["Load"].astype(str) + " (" + filtered_df.get("Minimum strain rate (s-1)", "").astype(str) + " s^(-1)) | " + filtered_df["Reference"].astype(str)
#                 )
#                 df_plot = filtered_df.copy()
#                 streain_rate_with_multiple_temps = (
#                     df_plot.groupby("Minimum strain rate (s-1)")["Temperature (°C)"].nunique().reset_index()
#                 )
#                 strain_rate_with_multiple_temps = stress_with_multiple_temps[strain_rate_with_multiple_temps["Temperature (°C)"] >= 2]["Minimum strain rate (s-1)"].unique()
#                 df_plot = df_plot[df_plot["Minimum strain rate (s-1)"].isin(strain_rate_with_multiple_temps)]
#                 if len(strain_rate_with_multiple_temps) == 0:
#                     st.warning("⚠️ No strain values found under multiple temperatures.")
#                 else:
#                     strain_rate_val = st.selectbox("🧱 Select Fixed Strain rate (s^(-1))", options=np.sort(np.round(strain_rate_with_multiple_temps,2)))
#                     tolerance = 0.00000001
#                     df_plot = df_plot[np.abs(df_plot["Minimum strain rate (s-1)"] - strain_rate_val) <= tolerance]
#                 x_col, y_col = "Minimum strain rate (s-1)", "Temperature (°C)"
#                 x_log, y_log = False, True
#             # Altair Plot
#             marker_map = {"Compression":"circle","Tensile":"square","Shear":"triangle-up","Twist":"diamond","Compression/Shear":"cross","Bending":"triangle-down"}
#             tooltip_cols = [c for c in ["Test","Load", "Regime","Temperature (°C)",x_col,y_col,"Stress (MPa)","Microstructure","Nature","Origin","Texture",  "Density [kg/m3]","Reference","Remarks"] if c in df_plot.columns]
#             legend_selection = alt.selection_point(fields=["Curve Label"], bind="legend")
#             chart = alt.Chart(df_plot).mark_point(size=60, opacity=0.7).encode(
#                 x=alt.X(x_col, scale=alt.Scale(type='log' if x_log else 'linear')),
#                 y=alt.Y(y_col, scale=alt.Scale(type='log' if y_log else 'linear')),
#                 color="Curve Label:N",
#                 shape=alt.Shape("Load:N", scale=alt.Scale(domain=list(marker_map.keys()), range=list(marker_map.values()))),
#                 tooltip=tooltip_cols,
#                 opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2))
#             ).add_params(legend_selection)
#             st.altair_chart(chart, use_container_width=True)

#         # else:  # Pole Figures
#         #     st.subheader("📌 Crystallographic Pole Figures")
#         #     grouped = filtered_df.groupby(["Load", "Temperature (°C)", "Reference"])
#         #     n_cols = 2
#         #     col_index = 0
#         #     cols = st.columns(n_cols)
#         #     for (load, temp, ref), group in grouped:
#         #         n_points = 300
#         #         theta = np.arccos(1 - 2 * np.random.rand(n_points))
#         #         phi = 2 * np.pi * np.random.rand(n_points)
#         #         x = np.sin(theta) * np.cos(phi)
#         #         y = np.sin(theta) * np.sin(phi)
#         #         z = np.cos(theta)
#         #         X_proj = x / (1 + z)
#         #         Y_proj = y / (1 + z)
#         #         fig, ax = plt.subplots(figsize=(4,4), facecolor='#0A0A0A')
#         #         ax.set_facecolor('#0A0A0A')
#         #         ax.set_aspect('equal')
#         #         circle = plt.Circle((0,0),1,color='white',fill=False,lw=1.5)
#         #         ax.add_patch(circle)
#         #         ax.scatter(X_proj, Y_proj, s=10, color='#81D4FA', alpha=0.7)
#         #         ax.set_xlim([-1.05,1.05])
#         #         ax.set_ylim([-1.05,1.05])
#         #         ax.axis('off')
#         #         ax.set_title(f"{load} | {temp}°C", fontsize=10, color='#81D4FA')
#         #         cols[col_index].pyplot(fig)
#         #         col_index = (col_index + 1) % n_cols


#     # ---------------------------------- Matplotlib Scatter ------------------------------------
#     fig, ax = plt.subplots(figsize=(8, 5))
#     shape_map = {
#         "circle": 'o',
#         "square": 's',
#         "triangle-up": '^',
#         "triangle-down": 'v',
#         "diamond": 'D',
#         "cross": 'X'
#     }

#     if not df_plot.empty:
#         for (load, curve_label), group in df_plot.groupby(["Load", "Curve Label"]):
#             marker = shape_map.get(marker_map.get(load, "circle"), 'o')
#             ax.scatter(group[x_col], group[y_col], label=curve_label, marker=marker, s=40)

#     if x_log:
#         ax.set_xscale('log')
#     if y_log:
#         ax.set_yscale('log')
#     ax.grid(True, which='both', linestyle='--', linewidth=0.5)

#     ax.set_xlabel(x_col)
#     ax.set_ylabel(y_col)
#     ax.legend(fontsize=7)
#     ax.set_title(plot_type)


#     # --------------------------------- Download buttons ---------------------------------
#     # buf = BytesIO()
#     # fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
#     # buf.seek(0)
#     # st.download_button("🖼️ Download Plot as PNG", buf.getvalue(), "creep_curves.png", "image/png")

#     # csv = df_plot.to_csv(index=False).encode("utf-8")
#     # st.download_button("📄 Download Data as CSV", csv, "creep_data.csv", "text/csv")  #creep_data.csv
#     file_name = st.text_input("Save your selected data in a csv file:",value="ice_data")
#     csv = df_plot.to_csv(index=False).encode("utf-8")
#     st.download_button(label="📄 Download Data as csv file", data=csv, file_name=f"{file_name}.csv", mime="text/csv")



#     st.markdown("### 📚 References of your selected experimental data")
#     # protect against missing fields in filtered_df
#     if not filtered_df.empty and {"Reference", "Load"}.issubset(filtered_df.columns):
#         for _, row in filtered_df.drop_duplicates("Reference").iterrows():
#             # safe accesses with .get and fallback
#             texture = row.get("Texture", "") if isinstance(row, dict) else row.get("Texture", "")
#             nature = row.get("Nature", "") if isinstance(row, dict) else row.get("Nature", "")
#             origin_ice = row.get("Origin", "") if isinstance(row, dict) else row.get("Origin", "")
#             spec = row.get("Specimen Dimension (mm)", "") if isinstance(row, dict) else row.get("Specimen Dimension (mm)", "")
#             grain_num = row.get("Grain number", "") if isinstance(row, dict) else row.get("Grain number", "")
#             grain_size = row.get("Grain size [mm]", "") if isinstance(row, dict) else row.get("Grain size [mm]", "")
#             url = row.get("URL", "#") if isinstance(row, dict) else row.get("URL", "#")
#             st.markdown(
#                 f"- **{row['Load']}** test |--> {texture} {nature} {origin_ice} ice | "
#                 f"Specimen dimension [mm]: {spec} | Number of Grains: {grain_num} | Grain size [mm]: {grain_size} || [{row['Reference']}]({url})"
#             )

