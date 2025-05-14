import streamlit as st
import pandas as pd
import plotly.express as px

# === 1. Load data ============================================================
@st.cache_data
def load_data():
    return pd.read_csv("./Walmart.csv", parse_dates=['transaction_date'])

df = load_data()

st.title("Dashboard Vânzări Walmart")

# === 2. Sidebar filters ======================================================
st.sidebar.header("Filter")
store = st.sidebar.multiselect("Store Location", df["store_location"].unique())
category = st.sidebar.multiselect("Category", df["category"].unique())

filtered_df = df.copy()
if store:
    filtered_df = filtered_df[filtered_df["store_location"].isin(store)]
if category:
    filtered_df = filtered_df[filtered_df["category"].isin(category)]

# ==== 3. Helper columns on filtered data =====================================
filtered_df["total_sales"] = filtered_df["quantity_sold"] * filtered_df["unit_price"]
filtered_df["date"]        = filtered_df["transaction_date"].dt.date

# Age groups
bins   = [0, 25, 35, 45, 55, 65, 100]
labels = ["18‑25", "26‑35", "36‑45", "46‑55", "56‑65", "65+"]
filtered_df["age_group"] = pd.cut(filtered_df["customer_age"],
                                  bins=bins, labels=labels, right=False)

# === 4. Key metrics ==========================================================
st.subheader("Metrici Importante")
col1, col3, col2 = st.columns(3)
col1.metric("Total vânzări",
            f"${filtered_df['total_sales'].sum():,.2f}")
col2.metric("Tranzacții",
            f"{filtered_df['transaction_id'].nunique()}")
col3.metric("Mărimea medie a coșului de cumpărături",
            f"{filtered_df['quantity_sold'].mean():.2f} produse")

# === 5. Sales over time ======================================================

# Adăugăm o coloană pentru anotimp
def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return "Iarnă"
    elif month in [3, 4, 5]:
        return "Primăvară"
    elif month in [6, 7, 8]:
        return "Vară"
    else:
        return "Toamnă"

sales_by_date = (filtered_df.groupby('date')['total_sales']
                 .sum().reset_index())
sales_by_date['season'] = pd.to_datetime(sales_by_date['date']).apply(get_season)

# Afișăm cu colorare după sezon
fig_time = px.line(
    sales_by_date,
    x='date',
    y='total_sales',
    color='season',
    line_group='season',
    title='Vânzări Totale de-a lungul Timpului - Strat Sezonier',
    labels={'date': 'Dată', 'total_sales': 'Vânzări', 'season': 'Anotimp'},
    color_discrete_sequence=["#2f77c3", "#f8b3ec", "#a4d13a", "#fc5e1d"]  # Iarnă, Primăvară, Vară, Toamnă
)
st.plotly_chart(fig_time)


# === 6. Sales by Age & Gender ===============================================
# Normalize gender values

gender = filtered_df["customer_gender"].unique().tolist()

if gender:
    filtered_df = filtered_df[filtered_df["customer_gender"].isin(gender)]
st.subheader("Vânzări după Grupe de Vârstă și Sex")
age_gender = (
    filtered_df.groupby(['age_group', 'customer_gender'])['total_sales']
    .sum().reset_index()
)

fig_age = px.bar(age_gender, x='age_group', y='total_sales',
                 color='customer_gender', barmode='group',
                 labels={'age_group': 'Grupa de Vârstă',
                         'total_sales': 'Vânzări Totale',
                         'customer_gender': 'Sex'},
                 title='Vânzări în funcție de vârstă și sex',
                 color_discrete_map={"Male": "#1126a5", "Female": "#ff0000 ", "Other": "#999999"})
st.plotly_chart(fig_age)


# === 7. Weather, Holiday, Weekday ===========================================
st.subheader("Vânzări în funcție de Condiții de Mediu și Timp")

# a) Weather
weather_sales = (filtered_df.groupby('weather_conditions')['total_sales']
                 .sum().reset_index())
fig_weather = px.bar(weather_sales, x='weather_conditions', y='total_sales',
                     color='weather_conditions',
                     labels={'weather_conditions':'Condiții Meteo',
                             'total_sales':'Vânzări Totale'},
                     title='Vânzări pe Condiții Meteo',
                     color_discrete_sequence=["#ADD8E6", "#9c9ce4", "#808080", "#f9cd48"])  # cloudy, rainy, stormy, sunny
st.plotly_chart(fig_weather)

# b) Holiday vs normal day
holiday_sales = (filtered_df.groupby('holiday_indicator')['total_sales']
                 .sum().reset_index())
holiday_sales['holiday_indicator'] = holiday_sales['holiday_indicator'] \
    .map({True: 'Sărbătoare', False: 'Zi normală'})
fig_holiday = px.pie(holiday_sales, names='holiday_indicator',
                     values='total_sales',
                     title='Vânzări în Zile de Sărbătoare vs. Zile Normale',
                     color_discrete_sequence=["#fc4545", "#ADD8E6"])  # sărbătoare, zile normale
st.plotly_chart(fig_holiday)

# c) Weekday
weekday_order = ["Monday","Tuesday","Wednesday",
                 "Thursday","Friday","Saturday","Sunday"]
weekday_sales = (filtered_df.groupby('weekday')['total_sales']
                 .sum().reindex(weekday_order).reset_index())
fig_weekday = px.line(weekday_sales, x='weekday', y='total_sales',
                      markers=True,
                      labels={'weekday':'Zi','total_sales':'Vânzări'},
                      title='Vânzări după Ziua Săptămânii',
                      color_discrete_sequence=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"])  # Fiecare zi săptămână cu o culoare diferită
st.plotly_chart(fig_weekday)

# === 8. Promotions trend =====================================================
st.subheader("Trendul Vânzărilor în Funcție de Promoții")

# a) Cu vs. Fără promoție
promo_trend = (filtered_df.groupby(['date', 'promotion_applied'])['total_sales']
               .sum().reset_index())
promo_trend['promotion_applied'] = promo_trend['promotion_applied'] \
    .map({True: 'Cu Promoție', False: 'Fără Promoție'})
fig_promo = px.line(promo_trend, x='date', y='total_sales',
                    color='promotion_applied',
                    labels={'date':'Dată','total_sales':'Vânzări'},
                    title='Trend zilnic: Cu vs. Fără Promoție',
                    color_discrete_sequence=["#2f77c3", "#fc4545"])  #  fără promoție, cu promoție
st.plotly_chart(fig_promo)

# b) Pe tipuri de promoție (doar unde există promoții)
type_trend = (filtered_df[filtered_df['promotion_applied']]
              .groupby(['date','promotion_type'])['total_sales']
              .sum().reset_index())
if not type_trend.empty:
    fig_type = px.line(type_trend, x='date', y='total_sales',
                       color='promotion_type',
                       labels={'date':'Dată','total_sales':'Vânzări'},
                       title='Trend zilnic pe Tipuri de Promoție',
                       color_discrete_sequence=["#2f77c3", "#fc4545"])  # Set1 oferă culori distincte pentru fiecare tip de promoție
    st.plotly_chart(fig_type)
else:
    st.info("Nu există date cu promoții pentru filtrele selectate.")

