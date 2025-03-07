import streamlit as st
import pandas as pd

st.title("Analisis Kelayakan Rumah, Sanitasi, dan Perilaku Pasien TBC")

# Upload file CSV
df_file = st.file_uploader("Upload dataset CSV", type=["csv"])

if df_file is not None:
    try:
        # Mencoba membaca dengan delimiter otomatis
        df = pd.read_csv(df_file, encoding="utf-8", sep=None, engine="python")
        st.write("### Data Awal")
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
    
    # Identifikasi missing values
    missing_values = df.isnull().sum()
    missing_percentage = (missing_values / len(df)) * 100
    missing_data = pd.DataFrame({"Missing Values": missing_values, "Percentage": missing_percentage})
    missing_data = missing_data[missing_data["Missing Values"] > 0]

    if not missing_data.empty:
        st.write("### Missing Values")
        st.dataframe(missing_data.sort_values(by="Percentage", ascending=False))

        # Imputasi missing values
        df.fillna(df.mean(numeric_only=True), inplace=True)  # Untuk numerik
        df.fillna(df.astype(str).mode().iloc[0], inplace=True)  # Untuk kategori
    
        st.write("### Data Setelah Imputasi")
        st.dataframe(df.head())

    # Definisi kategori
    kategori_rumah = ['status_rumah', 'langit_langit', 'lantai', 'dinding', 'jendela_kamar_tidur',
                       'jendela_ruang_keluarga', 'ventilasi', 'lubang_asap_dapur', 'pencahayaan']
    
    if not set(kategori_rumah).issubset(df.columns):
        st.error("Kolom yang dibutuhkan tidak ditemukan dalam dataset.")
    else:
        df_rumah = df[kategori_rumah].dropna()

        # Bobot Skor Rumah
        bobot_rumah = {
            "langit_langit": {"Ada": 5, "Tidak ada": 1},
            "lantai": {"Ubin/keramik/marmer": 5, "Tanah": 1},
            "dinding": {"Permanen (tembok pasangan batu bata yang diplester)": 5, "Bukan tembok": 1},
            "jendela_kamar_tidur": {"Ada": 5, "Tidak ada": 1},
            "jendela_ruang_keluarga": {"Ada": 5, "Tidak ada": 1},
            "ventilasi": {"Baik": 5, "Tidak Ada": 1},
            "lubang_asap_dapur": {"Ada": 5, "Tidak Ada": 1},
            "pencahayaan": {"Terang/Dapat digunakan membaca normal": 5, "Tidak Terang": 1}
        }

        # Hitung skor kelayakan
        def hitung_skor(df, kategori, bobot):
            skor = []
            for _, row in df.iterrows():
                total_skor = sum(bobot.get(col, {}).get(row[col], 0) for col in kategori)
                max_skor = len(kategori) * 5
                skor.append((total_skor / max_skor) * 100 if max_skor > 0 else 0)
            df["Skor Kelayakan"] = skor
            return df

        df_rumah = hitung_skor(df_rumah, kategori_rumah, bobot_rumah)

        # Menentukan kategori "Layak" atau "Tidak Layak"
        threshold = 70
        df_rumah["Label"] = df_rumah["Skor Kelayakan"].apply(lambda x: "Layak" if x >= threshold else "Tidak Layak")

        # Menampilkan hasil
        st.write("### Skor Kelayakan Rumah")
        st.dataframe(df_rumah.head())

        # Persentase Rumah Tidak Layak
        persentase_tidak_layak_rumah = (df_rumah["Label"] == "Tidak Layak").mean() * 100
        st.metric(label="Persentase Rumah Tidak Layak", value=f"{persentase_tidak_layak_rumah:.2f}%")
