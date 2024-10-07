import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Fungsi untuk memuat dan membersihkan dataset
@st.cache_data
def load_and_clean_data():
    try:
        # Memuat dataset
        customers = pd.read_csv('data/olist_customers_dataset.csv')
        orders = pd.read_csv('data/olist_orders_dataset.csv')
        payments = pd.read_csv('data/olist_order_payments_dataset.csv')

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

        return merged_data
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat atau membersihkan data: {str(e)}")
        return None

# Memuat data
data = load_and_clean_data()

if data is not None:
    # Judul aplikasi
    st.title("Dashboard Analisis E-commerce")

    # Sidebar untuk filter tanggal
    st.sidebar.title("Filter Data")
    start_date = st.sidebar.date_input("Pilih Tanggal Mulai", data['order_purchase_timestamp'].min().date())
    end_date = st.sidebar.date_input("Pilih Tanggal Akhir", data['order_purchase_timestamp'].max().date())

    # Filter data berdasarkan rentang tanggal yang dipilih
    filtered_data = data[(data['order_purchase_timestamp'].dt.date >= start_date) & 
                         (data['order_purchase_timestamp'].dt.date <= end_date)]

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
            ax.plot(daily_sales['order_purchase_timestamp'], daily_sales['payment_value'])
            ax.set_xlabel('Tanggal')
            ax.set_ylabel('Total Penjualan')
            ax.set_title('Tren Penjualan Harian')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        elif chart_type == "Grafik Batang":
            st.subheader("Jumlah Pesanan per Metode Pembayaran")
            payment_counts = filtered_data['payment_type'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(payment_counts.index, payment_counts.values)
            ax.set_xlabel('Metode Pembayaran')
            ax.set_ylabel('Jumlah Pesanan')
            ax.set_title('Jumlah Pesanan per Metode Pembayaran')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        elif chart_type == "Grafik Lingkaran":
            st.subheader("Distribusi Metode Pembayaran")
            payment_distribution = filtered_data['payment_type'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.pie(payment_distribution, labels=payment_distribution.index, autopct='%1.1f%%', startangle=90)
            ax.set_title('Distribusi Metode Pembayaran')
            st.pyplot(fig)

        elif chart_type == "Grafik Area":
            st.subheader("Tren Penjualan Kumulatif")
            daily_sales = filtered_data.groupby('order_purchase_timestamp')['payment_value'].sum().cumsum().reset_index()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.fill_between(daily_sales['order_purchase_timestamp'], daily_sales['payment_value'])
            ax.set_xlabel('Tanggal')
            ax.set_ylabel('Penjualan Kumulatif')
            ax.set_title('Tren Penjualan Kumulatif')
            plt.xticks(rotation=45)
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
    st.write("Jawaban 1: Tren Penjualan Harian")
    daily_sales = filtered_data.groupby('order_purchase_timestamp')['payment_value'].sum().reset_index()
    st.line_chart(daily_sales.set_index('order_purchase_timestamp')['payment_value'])

    # Jawaban untuk pertanyaan 2
    st.write("Jawaban 2: Metode Pembayaran Populer")
    payment_distribution = filtered_data['payment_type'].value_counts()
    st.bar_chart(payment_distribution)

else:
    st.error("Tidak dapat memuat data. Silakan periksa file sumber data Anda.")
