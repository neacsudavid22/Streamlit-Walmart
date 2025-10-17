# Streamlit Walmart Dashboard

This project analyzes Walmart sales and inventory data to highlight how effective visualizations can support inventory management and operational decisions.

Live demo: https://neacsudavid22-streamlit-walmart-main-2oodkv.streamlit.app/

## Contents
- `main.py` - Streamlit app (data loading, processing, and visualizations).
- `Walmart.csv` - Dataset used by the app (expected at project root).
- `requirements.txt` - Python dependencies.
- `.streamlit/`, `.devcontainer/`, `.vscode/` - optional environment and editor configs.

## Features
- Interactive sidebar filters (store location, category).
- Key metrics: total sales, transaction count, average basket size.
- Time-series sales with seasonal coloring.
- Sales by age group and gender.
- Sales by weather, holiday vs. normal day, and weekday trends.
- Promotion trends with handling when no promotion data exists.