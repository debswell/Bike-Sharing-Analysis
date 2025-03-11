import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
hour_df = pd.read_csv("dashboard/hour_data.csv")
day_df = pd.read_csv("dashboard/day_data.csv")

# Judul dashboard
st.title("Analisis Penyewaan Sepeda")

# Sidebar untuk filter interaktif
st.sidebar.header("Filter Data")

# Batasi rentang tanggal hanya dari Januari 2011 hingga Desember 2012
min_date = pd.to_datetime("2011-01-01")
max_date = pd.to_datetime("2012-12-31")
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [min_date, max_date], 
    min_value=min_date,   
    max_value=max_date     
)

# Filter musim
season_filter = st.sidebar.selectbox("Pilih Musim", ["All", "Spring", "Summer", "Fall", "Winter"])

# Filter data berdasarkan tanggal dan musim
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
filtered_day_df = day_df[(day_df['dteday'] >= pd.to_datetime(date_range[0])) & (day_df['dteday'] <= pd.to_datetime(date_range[1]))]
if season_filter != "All":
    season_mapping = {"Spring": 1, "Summer": 2, "Fall": 3, "Winter": 4}
    filtered_day_df = filtered_day_df[filtered_day_df['season'] == season_mapping[season_filter]]

# 1. Analisis Penyewaan Sepeda Berdasarkan Waktu
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
st.header("Pengaruh Cuaca terhadap Penyewaan Sepeda")
weather_rentals = filtered_day_df.groupby(['mnth', 'weathersit'])['cnt'].sum().unstack()
fig, ax = plt.subplots(figsize=(10, 5))
weather_rentals.plot(kind='line', marker='o', ax=ax)
ax.set_xlabel("Month")
ax.set_ylabel("Total Bike Rentals")
ax.legend(title="Weather Condition", labels=["Cerah", "Berawan", "Hujan Ringan", "Hujan Lebat"])
st.pyplot(fig)

# 3. Kontribusi Penyewa Kasual dan Terdaftar
st.header("Kontribusi Penyewa Kasual dan Terdaftar")
total_casual = filtered_day_df['casual'].sum()
total_registered = filtered_day_df['registered'].sum()
total_cnt = filtered_day_df['cnt'].sum()

percent_casual = round((total_casual / total_cnt) * 100, 2)
percent_registered = round((total_registered / total_cnt) * 100, 2)

fig, ax = plt.subplots()
ax.pie([percent_casual, percent_registered], labels=["Casual", "Registered"], autopct='%1.1f%%', colors=['blue', 'orange'])
st.pyplot(fig)

# 4. RFM Analysis
st.header("RFM Analysis")
filtered_day_df['date'] = pd.to_datetime(filtered_day_df['dteday'])
recent_date = filtered_day_df['date'].max()
rfm_df = filtered_day_df.groupby('instant').agg({
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
st.header("Clustering Analysis")
filtered_day_df['season_group'] = pd.cut(filtered_day_df['cnt'], bins=3, labels=['Low', 'Medium', 'High'])
fig, ax = plt.subplots()
sns.countplot(x='season_group', data=filtered_day_df, ax=ax)
ax.set_xlabel("Cluster Group")
ax.set_ylabel("Number of Days")
st.pyplot(fig)
