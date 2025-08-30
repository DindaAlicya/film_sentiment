import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Konfigurasi Halaman ---
st.set_page_config(
    page_title="Dashboard Analisis Sentimen Komentar Film",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Memuat Data dari File CSV ---
try:
    # Ganti dengan nama file CSV yang benar jika berbeda
    df = pd.read_csv('Hasil_Labelling_Data_3class.csv')
except FileNotFoundError:
    st.error("File 'analisis_sentimen_komentar_final.csv' tidak ditemukan.")
    st.markdown("Pastikan Anda sudah mengunggah file tersebut di folder yang sama dengan `app.py`.")
    st.image("https://placehold.co/600x400/FFCCCC/000000?text=File+CSV+Tidak+Ditemukan")
    st.stop() # Menghentikan eksekusi aplikasi jika file tidak ada

# Memastikan kolom yang dibutuhkan ada
required_cols = ['genre', 'stemming_data', 'Sentiment']
if not all(col in df.columns for col in required_cols):
    st.error("Kolom yang diperlukan ('Film', 'Genre', 'Komentar', 'Sentiment') tidak ditemukan dalam file CSV.")
    st.stop()

# --- Judul Halaman ---
st.title("🎬 Dashboard Analisis Sentimen Komentar Film")
st.markdown("---")
st.write(
    "Selamat datang di dashboard interaktif untuk analisis sentimen komentar dari beberapa film."
)

# --- Ringkasan Keseluruhan ---
st.header("Ringkasan Sentimen Keseluruhan")
total_sentimen = df['Sentiment'].value_counts().reset_index()
total_sentimen.columns = ['Sentimen', 'Jumlah']

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Jumlah Komentar per Sentimen")
    fig_bar = px.bar(
        total_sentimen,
        x='Sentimen',
        y='Jumlah',
        color='Sentimen',
        color_discrete_map={'Positif': 'green', 'Netral': 'blue', 'Negatif': 'red'},
        text='Jumlah',
        labels={'Sentimen': 'Kategori Sentimen', 'Jumlah': 'Total Komentar'},
        title='Total Komentar Berdasarkan Sentimen'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown("##### Distribusi Sentimen")
    fig_pie = px.pie(
        total_sentimen,
        values='Jumlah',
        names='Sentimen',
        color='Sentimen',
        color_discrete_map={'Positif': 'green', 'Netral': 'blue', 'Negatif': 'red'},
        title='Persentase Distribusi Sentimen'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- Informasi per Genre ---
st.header("Analisis Sentimen per Genre")
genre_list = df['genre'].unique()

# Inisialisasi session state untuk pagination
if 'page_number' not in st.session_state:
    st.session_state.page_number = {}
for genre in genre_list:
    if genre not in st.session_state.page_number:
        st.session_state.page_number[genre] = 0

for genre in genre_list:
    with st.expander(f"### 🎬 Genre: {genre}"):
        st.markdown("---")

        genre_data = df[df['genre'] == genre]
        sentimen_genre = genre_data['Sentiment'].value_counts().reset_index()
        sentimen_genre.columns = ['Sentimen', 'Jumlah']

        col_left, col_right = st.columns(2)
        with col_left:
            st.markdown(f"#### Distribusi Sentimen di Genre `{genre}`")
            fig_genre_pie = px.pie(
                sentimen_genre,
                values='Jumlah',
                names='Sentimen',
                color='Sentimen',
                color_discrete_map={'Positif': 'green', 'Netral': 'blue', 'Negatif': 'red'},
            )
            st.plotly_chart(fig_genre_pie, use_container_width=True)

        with col_right:
            st.markdown("#### Contoh Komentar Teratas")

            # Logika pagination
            rows_per_page = 5
            total_comments = len(genre_data)
            total_pages = (total_comments + rows_per_page - 1) // rows_per_page
            
            # Hitung indeks untuk slicing dataframe
            start_idx = st.session_state.page_number[genre] * rows_per_page
            end_idx = start_idx + rows_per_page

            # Tampilkan komentar
            st.dataframe(
                genre_data[['stemming_data', 'Sentiment']].iloc[start_idx:end_idx].style.applymap(
                    lambda x: 'background-color: lightgreen' if x == 'Positif' else ('background-color: salmon' if x == 'Negatif' else ''),
                    subset=['Sentiment']
                ),
                use_container_width=True,
                hide_index=True
            )

            # Tombol navigasi
            nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
            with nav_col1:
                if st.button("Previous", key=f"prev_{genre}"):
                    if st.session_state.page_number[genre] > 0:
                        st.session_state.page_number[genre] -= 1
                        st.experimental_rerun()
            with nav_col2:
                st.markdown(f"<p style='text-align: center;'>Halaman {st.session_state.page_number[genre] + 1} dari {total_pages}</p>", unsafe_allow_html=True)
            with nav_col3:
                if st.button("Next", key=f"next_{genre}"):
                    if st.session_state.page_number[genre] < total_pages - 1:
                        st.session_state.page_number[genre] += 1
                        st.experimental_rerun()
