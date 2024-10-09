
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import requests
import io  # Tambahkan import io

# Set style untuk matplotlib
sns.set_style("whitegrid")

# Fungsi untuk memuat data dari GitHub
@st.cache_data
def load_data_from_github(url):
    download = requests.get(url).content
    df = pd.read_csv(io.StringIO(download.decode('utf-8')))
    return df

# Contoh URL file CSV dari GitHub
customers_url = 'https://raw.githubusercontent.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/main/dashboard/data/olist_customers_dataset.csv'
orders_url = 'https://raw.githubusercontent.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/main/dashboard/data/olist_orders_dataset.csv'
payments_url = 'https://raw.githubusercontent.com/HelmyPurnomoHidayat22/analisis-data-dengan-python/main/dashboard/data/olist_order_payments_dataset.csv'

# Fungsi untuk memuat dan membersihkan data
@st.cache_data
def load_and_clean_data():
    try:
        # Load data
        customers = load_data_from_github(customers_url)
        orders = load_data_from_github(orders_url)
        payments = load_data_from_github(payments_url)

        # Gabungkan dataset
        merged_data = pd.merge(customers, orders, on='customer_id')
        merged_data = pd.merge(merged_data, payments, on='order_id')

        # Data cleaning
        merged_data = merged_data.dropna()
        merged_data = merged_data.drop_duplicates()
        merged_data['order_purchase_timestamp'] = pd.to_datetime(merged_data['order_purchase_timestamp'])


        

        # Menghapus outlier pada payment_value
        Q1 = merged_data['payment_value'].quantile(0.25)
        Q3 = merged_data['payment_value'].quantile(0.75)
        IQR = Q3 - Q1
        merged_data = merged_data[(merged_data['payment_value'] >= Q1 - 1.5 * IQR) & 
                                  (merged_data['payment_value'] <= Q3 + 1.5 * IQR)]

        # Pastikan kolom yang dibutuhkan ada
        required_columns = ['order_purchase_timestamp', 'payment_type', 'payment_value']
        for col in required_columns:
            if col not in merged_data.columns:
                st.error(f"Kolom yang dibutuhkan '{col}' tidak ada dalam dataset.")
                return None

        return merged_data
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat atau membersihkan data: {str(e)}")
        return None

# Memuat data
data = load_and_clean_data()

if data is not None

    # Judul aplikasi
    st.title("Dashboard Analisis E-commerce")

    # Sidebar untuk filter tanggal
    st.sidebar.title("Filter Data")
    min_date = data['order_purchase_timestamp'].min().date()
    max_date = data['order_purchase_timestamp'].max().date()

    start_date = st.sidebar.date_input("Pilih Tanggal Mulai", min_date)
    end_date = st.sidebar.date_input("Pilih Tanggal Akhir", max_date)

    # Validasi input tanggal
    if start_date > end_date:
        st.sidebar.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    else:
        # Filter data berdasarkan rentang tanggal yang dipilih
        filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) & 
                             (data['order_purchase_timestamp'].dt.date <= end_date)]

        if filtered_data.empty:
            st.warning("Tidak ada data yang sesuai dengan rentang tanggal yang dipilih.")
        else:
            # Pilihan jenis grafik
            chart_type = st.sidebar.selectbox(
                "Pilih Jenis Grafik",
                ["Grafik Garis", "Grafik Batang", "Grafik Lingkaran", "Grafik Area"]
            )

            # Fungsi untuk menampilkan visualisasi
            def plot_visualizations(chart_type):
                if chart_type == "Grafik Garis":
                    st.subheader("Tren Penjualan Harian")
                    daily_sales = filtered_data.groupby('order_purchase_timestamp')['payment_value'].sum().reset_index()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.plot(daily_sales['order_purchase_timestamp'], daily_sales['payment_value'], marker='o')
                    ax.set_xlabel('Tanggal')
                    ax.set_ylabel('Total Penjualan')
                    ax.set_title('Tren Penjualan Harian')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

                elif chart_type == "Grafik Batang":
                    st.subheader("Jumlah Pesanan per Metode Pembayaran")
                    payment_counts = filtered_data['payment_type'].value_counts()
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x=payment_counts.index, y=payment_counts.values, ax=ax, palette="viridis")
                    ax.set_xlabel('Metode Pembayaran')
                    ax.set_ylabel('Jumlah Pesanan')
                    ax.set_title('Jumlah Pesanan per Metode Pembayaran')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

                elif chart_type == "Grafik Lingkaran":
                    st.subheader("Distribusi Metode Pembayaran")
                    payment_distribution = filtered_data['payment_type'].value_counts()
                    fig, ax = plt.subplots(figsize=(8, 8))
                    ax.pie(payment_distribution, labels=payment_distribution.index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  # Agar pie chart proporsional
                    ax.set_title('Distribusi Metode Pembayaran')
                    st.pyplot(fig)

                elif chart_type == "Grafik Area":
                    st.subheader("Tren Penjualan Kumulatif")
                    daily_sales = filtered_data.groupby('order_purchase_timestamp')['payment_value'].sum().cumsum().reset_index()
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.fill_between(daily_sales['order_purchase_timestamp'], daily_sales['payment_value'], color='skyblue', alpha=0.4)
                    ax.plot(daily_sales['order_purchase_timestamp'], daily_sales['payment_value'], color='Slateblue', alpha=0.6)
                    ax.set_xlabel('Tanggal')
                    ax.set_ylabel('Penjualan Kumulatif')
                    ax.set_title('Tren Penjualan Kumulatif')
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)

            # Tampilkan visualisasi berdasarkan pilihan pengguna
            plot_visualizations(chart_type)

            # Tambahan informasi
            st.subheader("Ringkasan Statistik")
            st.write(filtered_data.describe())

            # Pertanyaan Bisnis
            st.subheader("Pertanyaan Bisnis")
            st.write("1. Bagaimana tren penjualan harian selama periode yang dipilih?")
            st.write("2. Apa metode pembayaran yang paling populer dan bagaimana distribusinya?")

            # Jawaban untuk pertanyaan bisnis
            st.subheader("Jawaban Pertanyaan Bisnis")

            # Jawaban untuk pertanyaan 1
            st.write("**Jawaban 1: Tren Penjualan Harian**")
            daily_sales = filtered_data.groupby('order_purchase_timestamp')['payment_value'].sum().reset_index()
            st.line_chart(daily_sales.set_index('order_purchase_timestamp')['payment_value'])

            # Jawaban untuk pertanyaan 2
            st.write("**Jawaban 2: Metode Pembayaran Populer**")
            payment_distribution = filtered_data['payment_type'].value_counts()
            st.bar_chart(payment_distribution)

else:
    st.error("Tidak dapat memuat data. Silakan periksa file sumber data Anda.")
