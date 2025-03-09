import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
hour_df = pd.read_csv("dashboard/hour_data.csv")
day_df = pd.read_csv("dashboard/day_data.csv")

# Judul dashboard
st.title("Analisis Penyewaan Sepeda")

# Sidebar untuk memilih visualisasi
st.sidebar.header("Pilih Visualisasi")
visualization_options = [
    "Penyewaan Sepeda Berdasarkan Waktu",
    "Pengaruh Cuaca terhadap Penyewaan Sepeda",
    "Kontribusi Penyewa Kasual dan Terdaftar",
    "RFM Analysis",
    "Clustering Analysis"
]
selected_visualizations = st.sidebar.multiselect("Pilih visualisasi yang ingin ditampilkan:", visualization_options)

# 1. Analisis Penyewaan Sepeda Berdasarkan Waktu
if "Penyewaan Sepeda Berdasarkan Waktu" in selected_visualizations:
    st.header("Penyewaan Sepeda Berdasarkan Waktu")
    def condition(hour):
        if 0 <= hour <= 11:
            return 'Morning'
        elif 12 <= hour <= 17:
            return 'Afternoon'
        elif 18 <= hour <= 23:
            return 'Night'

    hour_df['time_period'] = hour_df['hr'].apply(condition)
    time_period_rentals = hour_df.groupby('time_period')['cnt'].sum()

    fig, ax = plt.subplots()
    sns.barplot(x=time_period_rentals.index, y=time_period_rentals.values, ax=ax)
    ax.set_xlabel("Time Period")
    ax.set_ylabel("Total Bike Rentals")
    st.pyplot(fig)

# 2. Pengaruh Cuaca terhadap Penyewaan Sepeda
if "Pengaruh Cuaca terhadap Penyewaan Sepeda" in selected_visualizations:
    st.header("Pengaruh Cuaca terhadap Penyewaan Sepeda")
    weather_rentals = day_df.groupby(['month', 'weathersit'])['cnt'].sum().unstack()
    fig, ax = plt.subplots(figsize=(10, 5))
    weather_rentals.plot(kind='line', marker='o', ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("Total Bike Rentals")
    ax.legend(title="Weather Condition", labels=["Cerah", "Berawan", "Hujan Ringan", "Hujan Lebat"])
    st.pyplot(fig)

# 3. Kontribusi Penyewa Kasual dan Terdaftar
if "Kontribusi Penyewa Kasual dan Terdaftar" in selected_visualizations:
    st.header("Kontribusi Penyewa Kasual dan Terdaftar")
    total_casual = day_df['casual'].sum()
    total_registered = day_df['registered'].sum()
    total_cnt = day_df['cnt'].sum()

    percent_casual = round((total_casual / total_cnt) * 100, 2)
    percent_registered = round((total_registered / total_cnt) * 100, 2)

    fig, ax = plt.subplots()
    ax.pie([percent_casual, percent_registered], labels=["Casual", "Registered"], autopct='%1.1f%%', colors=['blue', 'orange'])
    st.pyplot(fig)

# 4. RFM Analysis
if "RFM Analysis" in selected_visualizations:
    st.header("RFM Analysis")
    day_df['date'] = pd.to_datetime(day_df['dteday'])
    recent_date = day_df['date'].max()
    rfm_df = day_df.groupby('instant').agg({
        'date': lambda x: (recent_date - x.max()).days,
        'cnt': 'count',
        'registered': 'sum'
    }).reset_index()
    rfm_df.columns = ['customer_id', 'recency', 'frequency', 'monetary']

    fig, ax = plt.subplots()
    sns.scatterplot(x='recency', y='monetary', size='frequency', data=rfm_df, ax=ax)
    ax.set_xlabel("Recency (days)")
    ax.set_ylabel("Monetary (total rentals)")
    st.pyplot(fig)

# 5. Clustering Analysis
if "Clustering Analysis" in selected_visualizations:
    st.header("Clustering Analysis")
    day_df['season_group'] = pd.cut(day_df['cnt'], bins=3, labels=['Low', 'Medium', 'High'])
    fig, ax = plt.subplots()
    sns.countplot(x='season_group', data=day_df, ax=ax)
    ax.set_xlabel("Cluster Group")
    ax.set_ylabel("Number of Days")
    st.pyplot(fig)
