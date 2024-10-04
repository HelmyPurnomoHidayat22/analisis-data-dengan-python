import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Fungsi untuk memuat dataset menggunakan cache_data yang baru
@st.cache_data
def load_data():
    customers = pd.read_csv('https://github.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/dashboard/olist_customers_dataset.csv')
    orders = pd.read_csv('https://github.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/dashboard/olist_orders_dataset.csv')
    payments = pd.read_csv('https://github.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/dashboard/olist_order_payments_dataset.csv')
    
    # Gabungkan dataset
    merged_data = pd.merge(customers, orders, on='customer_id')
    merged_data = pd.merge(merged_data, payments, on='order_id')
    
    # Tambahkan kolom tanggal ke dalam data pesanan
    merged_data['order_purchase_timestamp'] = pd.to_datetime(merged_data['order_purchase_timestamp'])
    
    return merged_data

# Memuat data
data = load_data()

# Sidebar untuk filter tanggal, bulan, dan tahun
st.sidebar.title("Filter Data Berdasarkan Tanggal")
start_date = st.sidebar.date_input("Pilih Tanggal Mulai", data['order_purchase_timestamp'].min().date())
end_date = st.sidebar.date_input("Pilih Tanggal Akhir", data['order_purchase_timestamp'].max().date())

# Filter data berdasarkan rentang tanggal yang dipilih
filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) & 
                     (data['order_purchase_timestamp'].dt.date <= end_date)]

# Pilihan untuk filter bulan dan tahun secara spesifik
st.sidebar.title("Filter Berdasarkan Bulan dan Tahun")
year_options = sorted(data['order_purchase_timestamp'].dt.year.unique())
selected_year = st.sidebar.selectbox("Pilih Tahun", year_options)

month_options = list(range(1, 13))
selected_month = st.sidebar.selectbox("Pilih Bulan", month_options)

# Filter data berdasarkan bulan dan tahun yang dipilih
filtered_data_by_month_year = data[(data['order_purchase_timestamp'].dt.year == selected_year) & 
                                   (data['order_purchase_timestamp'].dt.month == selected_month)]

# Pilihan jenis diagram di sidebar
st.sidebar.title("Pilih Jenis Diagram")
chart_type = st.sidebar.selectbox(
    "Pilih tipe visualisasi:",
    ['Diagram Garis', 'Diagram Lingkaran', 'Histogram', 'Diagram Pencar', 'Diagram Kotak Garis', 
     'Diagram Pareto', 'Diagram Jaring Laba-laba']
)

# Fungsi untuk menampilkan visualisasi sesuai dengan pilihan
def plot_visualizations():
    st.header(f"Visualisasi: {chart_type}")
    
    if chart_type == 'Diagram Garis':
        # Diagram Garis
        plt.figure(figsize=(10, 6))
        filtered_data_by_month_year.groupby('order_purchase_timestamp')['order_id'].count().plot(kind='line')
        plt.title('Jumlah Pesanan per Hari')
        plt.xlabel('Tanggal')
        plt.ylabel('Jumlah Pesanan')
        st.pyplot(plt)
    
    elif chart_type == 'Diagram Lingkaran':
        # Diagram Lingkaran
        plt.figure(figsize=(8, 8))
        payment_analysis = filtered_data_by_month_year.groupby('payment_type')['order_id'].count()
        plt.pie(payment_analysis, labels=payment_analysis.index, autopct='%1.1f%%')
        plt.title('Distribusi Metode Pembayaran')
        st.pyplot(plt)
    
    elif chart_type == 'Histogram':
        # Histogram
        plt.figure(figsize=(10, 6))
        plt.hist(filtered_data_by_month_year['payment_value'], bins=30)
        plt.title('Distribusi Nilai Pembayaran')
        plt.xlabel('Nilai Pembayaran')
        plt.ylabel('Frekuensi')
        st.pyplot(plt)
    
    elif chart_type == 'Diagram Pencar':
        # Diagram Pencar (Scatter)
        plt.figure(figsize=(10, 6))
        plt.scatter(filtered_data_by_month_year['payment_value'], filtered_data_by_month_year['order_id'])
        plt.title('Diagram Pencar: Nilai Pembayaran vs Pesanan')
        plt.xlabel('Nilai Pembayaran')
        plt.ylabel('Jumlah Pesanan')
        st.pyplot(plt)
    
    elif chart_type == 'Diagram Kotak Garis':
        # Diagram Kotak Garis (Box Plot)
        plt.figure(figsize=(10, 6))
        sns.boxplot(x='payment_type', y='payment_value', data=filtered_data_by_month_year)
        plt.title('Distribusi Nilai Pembayaran Berdasarkan Metode Pembayaran')
        plt.xlabel('Metode Pembayaran')
        plt.ylabel('Nilai Pembayaran')
        st.pyplot(plt)
    
    elif chart_type == 'Diagram Pareto':
        # Diagram Pareto
        payment_counts = filtered_data_by_month_year['payment_type'].value_counts()
        payment_cumsum = payment_counts.cumsum() / payment_counts.sum() * 100
        fig, ax = plt.subplots()
        ax.bar(payment_counts.index, payment_counts.values, color="C0")
        ax2 = ax.twinx()
        ax2.plot(payment_counts.index, payment_cumsum, color="C1", marker="D", ms=7)
        ax.set_xlabel('Metode Pembayaran')
        ax.set_ylabel('Jumlah Pesanan')
        ax2.set_ylabel('Persentase Kumulatif')
        plt.title('Diagram Pareto: Metode Pembayaran')
        st.pyplot(fig)
    
    elif chart_type == 'Diagram Jaring Laba-laba':
        # Diagram Jaring Laba-laba (Radar Chart)
        categories = ['Credit Card', 'Debit', 'PayPal', 'Transfer Bank']
        values = [320, 250, 150, 80]
        values += values[:1]
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, values, color='teal', alpha=0.25)
        ax.plot(angles, values, color='teal', linewidth=2)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        plt.title('Diagram Jaring Laba-laba: Metode Pembayaran')
        st.pyplot(fig)

# Tampilkan visualisasi sesuai pilihan
plot_visualizations()

