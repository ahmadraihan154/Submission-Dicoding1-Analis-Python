import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import date
import os

sns.set(style='dark')

# Memuat Data dari kode 1
file_path_day = os.path.join(os.path.dirname(__file__), 'day_cleaned.csv')
file_path_hour = os.path.join(os.path.dirname(__file__), 'hour_cleaned.csv')
day_df = pd.read_csv('day_cleaned.csv', parse_dates=['date'])
hour_df = pd.read_csv('hour_cleaned.csv', parse_dates=['date'])

# Fungsi untuk clustering (Grafik 6)
def temperature_cluster(temp):
    if temp < 10:
        return "Cold"
    elif 10 <= temp <= 25:
        return "Mild"
    else:
        return "Hot"

def wind_cluster(wind):
    if wind < 10:
        return "Calm"
    elif 10 <= wind <= 20:
        return "Breezy"
    else:
        return "Windy"

def humidity_cluster(hum):
    if hum < 40:
        return "Dry"
    elif 40 <= hum <= 70:
        return "Moderate"
    else:
        return "Humid"

# Mengatur tanggal
datetime_columns = ["date"]
day_df.sort_values(by="date", inplace=True)
day_df.reset_index(inplace=True)

hour_df.sort_values(by="date", inplace=True)
hour_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date_days = day_df["date"].min()
max_date_days = day_df["date"].max()

min_date_hour = hour_df["date"].min()
max_date_hour = hour_df["date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://storage.googleapis.com/gweb-uniblog-publish-prod/original_images/image1_hH9B4gs.jpg")
    
    # Mengambil start_date & end_date dari date_input
    date_input = st.date_input(
        label='Rentang Waktu',
        min_value=min_date_days,
        max_value=max_date_days,
        value=[min_date_days, max_date_days]) 
    
    # Error handling cek apakah pengguna memasukkan dua tanggal
    if isinstance(date_input, tuple) and len(date_input) == 2:
        start_date, end_date = date_input
    else:
        st.error("Silakan pilih rentang tanggal dengan benar (dua tanggal).")
        st.image("https://cdn.pixabay.com/photo/2017/02/12/21/29/false-2061131_1280.png", width=300)
        st.stop()

    # Error handling untuk filter tanggal
    if start_date > end_date:
        st.error("**Kesalahan Filter Tanggal**: Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
        st.image("https://cdn.pixabay.com/photo/2017/02/12/21/29/false-2061131_1280.png", width=300)  # Gambar error
        st.stop()  
        
    # Widget Multiselect untuk memilih musim
    selected_season = st.multiselect(
        label="Pilih Musim",
        options=day_df['season'].unique(),
        default=day_df['season'].unique()
    )

    # Widget Multiselect untuk memilih kondisi cuaca
    selected_weather = st.multiselect(
        label="Pilih Kondisi Cuaca",
        options=day_df['weather_condition'].unique(),
        default=day_df['weather_condition'].unique()
    )

    # Widget Multiselect untuk memilih jenis hari
    selected_day_type = st.multiselect(
        label="Pilih Jenis Hari",
        options=['Hari Kerja', 'Hari Libur'],
        default=['Hari Kerja', 'Hari Libur']
    )

    # Widget Slider untuk memilih rentang suhu
    min_temp, max_temp = st.slider(
        label="Pilih Rentang Suhu",
        min_value=float(day_df['temperature'].min()),
        max_value=float(day_df['temperature'].max()),
        value=(float(day_df['temperature'].min()), float(day_df['temperature'].max()))
    )

    # Widget Slider untuk memilih rentang kecepatan angin
    min_wind, max_wind = st.slider(
        label="Pilih Rentang Kecepatan Angin",
        min_value=float(day_df['windspeed'].min()),
        max_value=float(day_df['windspeed'].max()),
        value=(float(day_df['windspeed'].min()), float(day_df['windspeed'].max()))
    )

    # Widget Slider untuk memilih rentang kelembaban
    min_hum, max_hum = st.slider(
        label="Pilih Rentang Kelembaban",
        min_value=float(day_df['humidity'].min()),
        max_value=float(day_df['humidity'].max()),
        value=(float(day_df['humidity'].min()), float(day_df['humidity'].max()))
    )

# Filter data berdasarkan rentang tanggal yang dipilih
main_df_days = day_df[(day_df["date"] >= pd.to_datetime(start_date)) & 
                      (day_df["date"] <= pd.to_datetime(end_date))]

main_df_hour = hour_df[(hour_df["date"] >= pd.to_datetime(start_date)) & 
                       (hour_df["date"] <= pd.to_datetime(end_date))]

# Filter data berdasarkan widget
main_df_days = main_df_days[
    (main_df_days['season'].isin(selected_season)) &
    (main_df_days['weather_condition'].isin(selected_weather)) &
    (main_df_days['temperature'] >= min_temp) &
    (main_df_days['temperature'] <= max_temp) &
    (main_df_days['is_workingday'].isin([1 if day == 'Hari Kerja' else 0 for day in selected_day_type])) &
    (main_df_days['windspeed'] >= min_wind) &
    (main_df_days['windspeed'] <= max_wind) &
    (main_df_days['humidity'] >= min_hum) &
    (main_df_days['humidity'] <= max_hum)
]

# Error handling untuk filter slider
if main_df_days.empty:
    st.error("**Kesalahan Filter Data**: Tidak ada data yang sesuai dengan kriteria filter yang dipilih.")
    st.image("https://cdn.pixabay.com/photo/2017/02/12/21/29/false-2061131_1280.png", width=300)  # Gambar error
    st.stop()  # Hentikan eksekusi kode lebih lanjut

# Menghitung metrik
total_sharing_bike = main_df_days['combined_users'].sum()
total_registered = main_df_days['registered_users'].sum()
total_casual = main_df_days['casual_users'].sum()

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Bike Sharing :sparkles:')

# Menampilkan metrik
st.subheader('Daily Sharing')
col1, col2, col3 = st.columns(3)
 
with col1:
    st.metric("Total Sharing Bike", value=f"{total_sharing_bike:,}")

with col2:
    st.metric("Total Registered", value=f"{total_registered:,}")

with col3:
    st.metric("Total Casual", value=f"{total_casual:,}")

# Grafik 1: Jumlah Penyewa Sepeda per Quarter
st.subheader("Jumlah Penyewa Sepeda per Quarter")
day_df_month = main_df_days.groupby(main_df_days['date'].dt.to_period('Q')).agg({'combined_users':'sum'})
fig1, ax1 = plt.subplots(figsize=(20, 10))
ax1.plot(day_df_month.index.astype('str'), day_df_month.values, marker='o')
ax1.set_title('Grafik Jumlah Penyewa Sepeda per Quarter')
ax1.set_xlabel('Bulan')
ax1.set_ylabel('Jumlah Penyewa Sepeda')
st.pyplot(fig1)

# Grafik 2: Perbandingan Jumlah Penyewa Sepeda pada Hari Kerja vs Hari Libur
st.subheader("Perbandingan Jumlah Penyewa Sepeda pada Hari Kerja vs Hari Libur")
fig2, ax2 = plt.subplots(figsize=(5, 5), dpi=150)
g = sns.barplot(data=main_df_days, x='is_workingday', y='combined_users', palette='Set1', errorbar=None, estimator=sum, ax=ax2)
ax2.set_title('Perbandingan Jumlah Penyewa Sepeda pada Hari Kerja terhadap Hari Libur', pad=20)
ax2.set_xticks(ticks=[0, 1], labels=['Holiday', 'Working day'])
ax2.set_xlabel('Kategori Hari')
ax2.set_ylabel('Jumlah Penyewa Sepeda')
ax2.ticklabel_format(style='plain', axis='y')
for p in g.patches:
    g.annotate(f'{int(p.get_height()):,}',  
               (p.get_x() + p.get_width() / 2, p.get_height()), 
               ha='center', va='bottom', color='black', fontsize=10)
st.pyplot(fig2)

# Grafik 3: Perbandingan Jumlah Penyewa Sepeda dalam Berbagai Kondisi Cuaca
st.subheader("Perbandingan Jumlah Penyewa Sepeda dalam Berbagai Kondisi Cuaca")
day_df_weather = main_df_days.groupby('weather_condition').agg({'combined_users':'sum'}).sort_values(by='combined_users', ascending=False).reset_index()
fig3, ax3 = plt.subplots(figsize=(5, 5), dpi=150)
g = sns.barplot(data=day_df_weather, x='weather_condition', y='combined_users', hue='weather_condition', palette=["#4682B4", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax3)
ax3.set_title('Perbandingan Jumlah Penyewa Sepeda dalam Berbagai Kondisi Cuaca', pad=20)
ax3.set_xlabel('Kondisi Cuaca')
ax3.set_ylabel('Jumlah Penyewa Sepeda')
for p in g.patches:
    g.annotate(f'{int(p.get_height()):,}',  
               (p.get_x() + p.get_width() / 2, p.get_height()), 
               ha='center', va='bottom', color='black', fontsize=10)
st.pyplot(fig3)

# Grafik 4: Perbandingan Jumlah Penyewa Sepeda berdasarkan Musim
st.subheader("Perbandingan Jumlah Penyewa Sepeda berdasarkan Musim")
day_df_season = main_df_days.groupby('season').agg({'combined_users':'sum'}).sort_values(by='combined_users', ascending=False).reset_index()
fig4, ax4 = plt.subplots(figsize=(8, 5), dpi=150)
g = sns.barplot(data=main_df_days, x='season', y='combined_users', hue='is_workingday', palette='viridis', errorbar=None, estimator=sum, order=day_df_season['season'], ax=ax4)
ax4.set_title('Perbandingan Jumlah Penyewa Sepeda berdasarkan Musim', pad=20)
ax4.set_xlabel('Musim')
ax4.set_ylabel('Jumlah Penyewa Sepeda')
handles, labels = g.get_legend_handles_labels()
new_labels = ['Hari Libur', 'Hari Kerja']
plt.legend(handles, new_labels, title="Kategori Hari", loc='upper right')
for p in g.patches:
    if p.get_height() > 0:
        g.annotate(f'{int(p.get_height()):,}',  
                   (p.get_x() + p.get_width() / 2, p.get_height()), 
                   ha='center', va='bottom', color='black', fontsize=10)
st.pyplot(fig4)

# Grafik 5: Perbandingan Jumlah Penyewa Sepeda berdasarkan Jam
st.subheader("Perbandingan Jumlah Penyewa Sepeda berdasarkan Jam")
hour_df_hour_high = main_df_hour.groupby('hour').agg({'combined_users':'sum'}).sort_values(by='combined_users', ascending=False).reset_index().head()
hour_df_hour_low = main_df_hour.groupby('hour').agg({'combined_users':'sum'}).sort_values(by='combined_users', ascending=True).reset_index().head()
fig5, ax5 = plt.subplots(figsize=(12, 5), dpi=150, ncols=2, nrows=1)
sns.barplot(data=hour_df_hour_high, x='hour', y='combined_users', palette=["#4682B4", "#A9A9A9", "#A9A9A9", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax5[0], order=hour_df_hour_high['hour'])
sns.barplot(data=hour_df_hour_low, x='hour', y='combined_users', palette=["#4682B4", "#A9A9A9", "#A9A9A9", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax5[1], order=hour_df_hour_low['hour'])
ax5[0].set_title('Dari 5 Jam Terbanyak')
ax5[0].set_xlabel('Jam')
ax5[0].set_ylabel('Jumlah Penyewa Sepeda')
ax5[1].set_title('Dari 5 Jam Tersedikit')
ax5[1].set_xlabel('Jam')
ax5[1].set_ylabel('Jumlah Penyewa Sepeda')
plt.tight_layout(w_pad=3)
st.pyplot(fig5)

# Grafik 6: Perbandingan Jumlah Penyewa Sepeda berdasarkan Kondisi Lingkungan
st.subheader("Perbandingan Jumlah Penyewa Sepeda berdasarkan Kondisi Lingkungan")
main_df_days["temperature_cluster"] = main_df_days["temperature"].apply(temperature_cluster)
main_df_days["wind_cluster"] = main_df_days["windspeed"].apply(wind_cluster)
main_df_days["humidity_cluster"] = main_df_days["humidity"].apply(humidity_cluster)
day_df_temp = main_df_days.groupby("temperature_cluster")["combined_users"].sum().sort_values(ascending=False).reset_index()
day_df_wind = main_df_days.groupby("wind_cluster")["combined_users"].sum().sort_values(ascending=False).reset_index()
day_df_hum = main_df_days.groupby("humidity_cluster")["combined_users"].sum().sort_values(ascending=False).reset_index()
fig6, ax6 = plt.subplots(figsize=(15, 5), dpi=150, ncols=3, nrows=1)
sns.barplot(data=day_df_temp, x='temperature_cluster', y='combined_users', palette=["#4682B4", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax6[0])
sns.barplot(data=day_df_wind, x='wind_cluster', y='combined_users', palette=["#4682B4", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax6[1])
sns.barplot(data=day_df_hum, x='humidity_cluster', y='combined_users', palette=["#4682B4", "#A9A9A9", "#A9A9A9"], errorbar=None, estimator=sum, ax=ax6[2])
ax6[0].set_title('Temperatur')
ax6[0].set_xlabel('Temperatur')
ax6[0].set_ylabel('Jumlah Penyewa Sepeda')
ax6[1].set_title('Kecepatan Angin')
ax6[1].set_xlabel('Kecepatan Angin')
ax6[1].set_ylabel('Jumlah Penyewa Sepeda')
ax6[2].set_title('Kelembaban')
ax6[2].set_xlabel('Kelembaban')
ax6[2].set_ylabel('Jumlah Penyewa Sepeda')
plt.tight_layout(w_pad=3)
st.pyplot(fig6)

# Grafik 7: Analisis RFM
st.subheader("Analisis RFM")
daily_rentals = main_df_days.groupby('date').agg({'casual_users':'sum', 'registered_users': 'sum'}).reset_index()
last_date = daily_rentals['date'].max()
peak_rental_day_casual = daily_rentals.loc[daily_rentals['casual_users'].idxmax()]
peak_rental_day_registered = daily_rentals.loc[daily_rentals['registered_users'].idxmax()]
recency_days_casual = (last_date - peak_rental_day_casual["date"]).days
recency_days_registered = (last_date - peak_rental_day_registered["date"]).days
frequency_casual = daily_rentals['casual_users'].count()
frequency_registered = daily_rentals['registered_users'].count()
monetary_casual = daily_rentals['casual_users'].sum()
monetary_registered = daily_rentals['registered_users'].sum()
rfm_df = pd.DataFrame({
    'User' : ['Casual Users', 'Registered Users'],
    'Recency (days)': [recency_days_casual, recency_days_registered],
    'Frequency (times)': [frequency_casual, frequency_registered],
    'Monetary (total bike sharing)': [monetary_casual, monetary_registered]
})
fig7, ax7 = plt.subplots(figsize=(15, 5), dpi=150, ncols=3, nrows=1)
sns.barplot(data=rfm_df, x='User', y='Recency (days)', errorbar=None, estimator=sum, ax=ax7[0])
sns.barplot(data=rfm_df, x='User', y='Frequency (times)', errorbar=None, estimator=sum, ax=ax7[1])
ax7[2].pie(
    x=main_df_days[['casual_users', 'registered_users']].sum(), 
    labels=['Casual User', 'Registered User'], 
    explode=[0.15, 0],
    autopct='%1.1f%%',
    colors=['#66B3FF', '#FFA07A'],
    shadow=True
)
ax7[0].set_title('By Recency')
ax7[0].set_xlabel('Jenis Pengguna')
ax7[0].set_ylabel('Hari')
ax7[1].set_title('By Frequency')
ax7[1].set_xlabel('Jenis Pengguna')
ax7[1].set_ylabel('Kali')
ax7[2].set_title('By Monetary')
plt.tight_layout(w_pad=3)
st.pyplot(fig7)
