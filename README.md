# 🧊 Welcome to IceMechaData Dashboard 

## Overview
This interactive platform is designed for the exploration and analysis of experimental data on the mechanical behavior and creep of ice. The database compiles results from studies spanning from the early 20th century to the present day, bringing together a wide range of experimental conditions, including specimen geometry, temperature, applied stress or strain rate, loading history, and key microstructural characteristics.

The dashboard enables users to visualize and compare **experimental results** under diverse mechanical conditions, facilitating a deeper understanding of ice deformation processes and supporting the development and validation of constitutive flow laws.

While efforts have been made to standardize and pre-filter the available data to ensure consistency and usability, users are strongly encouraged to consult the original publications to verify experimental details, particularly regarding sample preparation, loading procedures, and measurement conditions. In particular, attention should be paid to the definitions of stress and strain rate, especially when comparing different experimental configurations, as equivalence between reported quantities (e.g., octahedral vs. uniaxial measures) is not always guaranteed.

## Contributing to the Database
We welcome contributions to expand and enrich the IceMechaData database.

To contribute:

1. Click **"Add your experimental results"** in the dashboard, or use the CSV template available in this repository under **"data_template.csv"**
2. Download the provided CSV template
3. Fill it with your experimental data
4. Send the completed file to:

- Maurine Montagnat — maurine.montagnat@univ-grenoble-alpes.fr  
- Olivier Castelnau — olivier.castelnau@ensam.eu  
- Mohammed Idrissi El Fallaki — idrissielfallaki@gmail.com  

---


# Temporary external access to the application (For Maurine)
The current deployment of the dashboard is available at:

https://icemechadata-dashboard-xfese6nntnuhad84uazeuw.streamlit.app/




# Installation and Local Deployment

## 1- Create a Virtual Environment (Recommended)

### Windows

Create a virtual environment:

```bash
python -m venv venv_name
```

Activate it:

```bash
venv_name\Scripts\activate
```

### Linux/macOS 

Create a virtual environment:

```bash
python3 -m venv venv_name
```

Activate it:

```bash
source venv_name/bin/activate
```


## 2- Install Streamlit

```bash
pip install streamlit
```

## 3- Launch the Dashboard 

Run the Streamlit application:

```bash
streamlit run Dashboard.py
```

Once the server starts, Streamlit will display a local URL similar to:
Local URL: http://localhost:8501

Open this URL in your web browser to access the dashboard.

## 4- Stop the application

To stop the Streamlit server, press:

```bash
Ctrl + C
```

in the terminal where the application is running.

## 5- Deactivate the environment

When you are finished, deactivate the virtual environment:

```bash
deactivate
```

# Citation

If you use the IceMechaData Dashboard or its underlying database in your research, please cite the corresponding publication(s) and the original experimental studies from which the data were obtained.


