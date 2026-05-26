import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

#  PAGE CONFIG
st.set_page_config(
    page_title="SPK Wisata Jogja - Metode SAW",
    layout="wide",
)

#  GLOBAL STYLE
st.markdown("""
<style>
    .main-title  { font-size:2rem; font-weight:700; color:#1a3a5c; margin-bottom:0; }
    .sub-title   { font-size:1rem; color:#5a7a9c; margin-top:0; }
    .metric-box  { background:#f0f6ff; border-left:4px solid #2563eb;
                   padding:12px 16px; border-radius:8px; margin:6px 0; }
    .saw-step    { background:#f8fafc; border:1px solid #e2e8f0;
                   border-radius:8px; padding:14px; margin:8px 0; }
</style>
""", unsafe_allow_html=True)


def fix_lat(val):
    s = str(val).replace(' ', '')
    sign = '-' if s.startswith('-') else ''
    digits = s.replace('-', '').replace('.', '')
    return float(sign + digits[0] + '.' + digits[1:])

def fix_lon(val):
    s = str(val).replace(' ', '')
    digits = s.replace('-', '').replace('.', '')
    return float(digits[0:3] + '.' + digits[3:])

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius bumi dalam km
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi    = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

#  LOAD & PERSIAPAN DATA

@st.cache_data
def load_data():
    df = pd.read_csv("tourism_jogja.csv")

    # C3: Jarak dari Pusat Kota (km)
    # Perbaiki format koordinat yang rusak di dataset
    df["lat"] = df["latitude"].apply(fix_lat)
    df["lon"] = df["longitude"].apply(fix_lon)

    LAT_PUSAT = -7.801363   # Koordinat pusat kota Yogyakarta
    LON_PUSAT = 110.364787

    df["jarak_km"] = haversine(df["lat"], df["lon"], LAT_PUSAT, LON_PUSAT)

    # C4: Kategori Wisata
    # Skor dihitung dari rata-rata rating aktual per jenis wisata
    # Bukan mapping manual — murni dari data
    avg_rating_per_type = df.groupby("type")["rating"].mean()
    df["kategori"] = df["type"].map(avg_rating_per_type).round(3)

    # C5: Skor Popularitas – normalisasi berbasis rating
    df["popularitas"] = (
        pd.cut(df["rating"], bins=[0, 3.9, 4.2, 4.5, 4.7, 5.0],
               labels=[1, 2, 3, 4, 5]).astype(float)
    ).fillna(3).astype(int)

    return df

df_raw = load_data()

KRITERIA = {
    "C1": {"label": "Rating Wisatawan",      "col": "rating",      "tipe": "benefit"},
    "C2": {"label": "Harga Tiket (HTM)",     "col": "htm",         "tipe": "cost"},
    "C3": {"label": "Jarak dari Pusat Kota", "col": "jarak_km",    "tipe": "cost"},
    "C4": {"label": "Kategori Wisata",       "col": "kategori",    "tipe": "benefit"},
    "C5": {"label": "Popularitas", "col": "popularitas", "tipe": "benefit"},
}

#  SIDEBAR NAVIGATION

with st.sidebar:
    st.markdown("## SPK Wisata Jogja")
    st.markdown("**Metode:** Simple Additive Weighting (SAW)")
    st.markdown("---")
    halaman = st.radio(
        "Navigasi Halaman",
        ["Beranda", "Dataset", "Hitung SPK", "Visualisasi"],
    )
    st.markdown("---")
    st.caption("Dataset: Tourism Jogja (437 destinasi)")
    st.caption("Sumber: Kaggle / Data Primer")


#  HALAMAN 1 – BERANDA
if halaman == "Beranda":
    st.markdown('<p class="main-title">Sistem Pendukung Keputusan</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Rekomendasi Destinasi Wisata Yogyakarta – Metode SAW</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Destinasi", f"{len(df_raw):,}")
    col2.metric("Jenis Wisata", df_raw["type"].nunique())
    col3.metric("Rata-rata Rating", f"{df_raw['rating'].mean():.2f}")
    col4.metric("Rata-rata HTM", f"Rp {df_raw['htm'].mean():,.0f}")

    st.markdown("---")
    st.markdown("### Tentang Sistem Ini")
    st.info(
        "Sistem ini membantu wisatawan memilih destinasi terbaik di Yogyakarta "
        "berdasarkan 5 kriteria menggunakan metode Simple Additive Weighting (SAW). "
        "Seluruh kriteria diturunkan dari data asli dataset — tidak ada nilai simulasi."
    )

    st.markdown("### Kriteria Penilaian")
    df_kriteria = pd.DataFrame([
        {
            "Kode"      : k,
            "Kriteria"  : v["label"],
            "Tipe"      : v["tipe"].capitalize(),
            "Sumber Data": {
                "C1": "Kolom 'rating'",
                "C2": "Kolom 'htm'",
                "C3": "Kolom 'latitude' & 'longitude' pake Haversine",
                "C4": "Kolom 'type' rata-rata rating per kategori",
                "C5": "Kolom 'rating' normalisasi ke 5 kelas",
            }[k]
        }
        for k, v in KRITERIA.items()
    ])
    st.dataframe(df_kriteria, use_container_width=True, hide_index=True)

    st.markdown("### Alur Metode SAW")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.markdown("**1. Input Data**\n\nDataset 437 destinasi wisata Jogja")
    col_b.markdown("**2. Normalisasi**\n\nMatriks ternormalisasi (benefit/cost)")
    col_c.markdown("**3. Pembobotan**\n\nSkor = Jumlah(bobot × nilai ternormalisasi)")
    col_d.markdown("**4. Perangkingan**\n\nUrut dari skor tertinggi")


#  HALAMAN 2 – DATASET
elif halaman == "Dataset":
    st.title("Dataset Destinasi Wisata Jogja")
    st.markdown(f"Total **{len(df_raw)} baris** data | **{len(df_raw.columns)} kolom**")

    col1, col2 = st.columns([1, 3])
    with col1:
        filter_tipe = st.multiselect(
            "Filter Jenis Wisata",
            options=sorted(df_raw["type"].unique()),
            default=[],
            placeholder="Semua jenis",
        )
        min_rating = st.slider("Minimum Rating", 2.5, 5.0, 4.0, 0.1)

    df_view = df_raw.copy()
    if filter_tipe:
        df_view = df_view[df_view["type"].isin(filter_tipe)]
    df_view = df_view[df_view["rating"] >= min_rating]

    with col2:
        st.markdown(f"Menampilkan **{len(df_view)} destinasi** sesuai filter")
        st.dataframe(
            df_view[["place_id", "name", "type", "rating", "htm",
                      "jarak_km", "kategori", "popularitas"]].rename(columns={
                "place_id"   : "ID",
                "name"       : "Nama Destinasi",
                "type"       : "Jenis",
                "rating"     : "Rating",
                "htm"        : "HTM (Rp)",
                "jarak_km"   : "Jarak (km)",
                "kategori"   : "Skor Kategori",
                "popularitas": "Popularitas",
            }),
            use_container_width=True,
            height=460,
        )

    st.markdown("---")
    st.markdown("### Statistik Deskriptif")
    st.dataframe(
        df_raw[["rating", "htm", "jarak_km", "kategori", "popularitas"]]
        .describe().round(2),
        use_container_width=True
    )

#  HALAMAN 3 – HITUNG SPK
elif halaman == "Hitung SPK":
    st.title("Perhitungan SPK - Metode SAW")

    st.markdown("### Input Bobot Kriteria")
    st.markdown("Atur bobot setiap kriteria (total harus = 100%). Bobot mencerminkan prioritas kamu.")

    col1, col2, col3, col4, col5 = st.columns(5)
    w1 = col1.slider("C1 - Rating",     0, 100, 30, 5, help="Bobot Rating Wisatawan")
    w2 = col2.slider("C2 - HTM",        0, 100, 25, 5, help="Bobot Harga Tiket")
    w3 = col3.slider("C3 - Jarak",      0, 100, 20, 5, help="Bobot Jarak dari Pusat Kota")
    w4 = col4.slider("C4 - Kategori",   0, 100, 15, 5, help="Bobot Kategori Wisata")
    w5 = col5.slider("C5 - Popularitas",0, 100, 10, 5, help="Popularitas")

    total_bobot = w1 + w2 + w3 + w4 + w5
    if total_bobot != 100:
        st.warning(f"Total bobot saat ini = **{total_bobot}** (harus tepat 100 agar valid)")
    else:
        st.success(f"Total bobot = {total_bobot} – Valid!")

    st.markdown("### Filter Preferensi")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filter_jenis = st.multiselect(
            "Jenis Wisata yang Diminati",
            options=sorted(df_raw["type"].unique()),
            default=["Alam", "Budaya Dan Sejarah", "Pantai"],
        )
    with col_f2:
        max_htm = st.number_input(
            "Batas Maksimal HTM (Rp)", min_value=0, max_value=1_500_000,
            value=100_000, step=5_000,
        )
    with col_f3:
        top_n = st.selectbox("Tampilkan Top N Hasil", [10, 20, 30, 50, 100], index=1)

    st.markdown("---")
    hitung = st.button("Jalankan Perhitungan SAW", type="primary", use_container_width=True)

    if hitung:
        if total_bobot != 100:
            st.error("Harap sesuaikan bobot hingga totalnya tepat 100 sebelum menghitung.")
        else:
            df_calc = df_raw.copy()
            if filter_jenis:
                df_calc = df_calc[df_calc["type"].isin(filter_jenis)]
            df_calc = df_calc[df_calc["htm"] <= max_htm].reset_index(drop=True)

            if len(df_calc) < 2:
                st.error("Data terlalu sedikit setelah filter. Longgarkan filter terlebih dahulu.")
            else:
                bobot = np.array([w1, w2, w3, w4, w5]) / 100
                cols  = [v["col"]  for v in KRITERIA.values()]
                tipes = [v["tipe"] for v in KRITERIA.values()]

                matriks = df_calc[cols].values.astype(float)

                # STEP 1: Matriks Keputusan
                with st.expander("STEP 1 - Matriks Keputusan (10 baris pertama)", expanded=True):
                    df_matriks = pd.DataFrame(
                        matriks[:10],
                        columns=[v["label"] for v in KRITERIA.values()],
                        index=df_calc["name"].iloc[:10]
                    ).round(4)
                    st.dataframe(df_matriks, use_container_width=True)

                # STEP 2: Normalisasi SAW
                # Benefit → r_ij = x_ij / max(x_j)
                # Cost    → r_ij = min(x_j) / x_ij
                norm = np.zeros_like(matriks)
                for j, tipe in enumerate(tipes):
                    col_vals = matriks[:, j]
                    if tipe == "benefit":
                        denom = col_vals.max()
                        norm[:, j] = col_vals / denom if denom != 0 else 0
                    else:
                        nonzero = col_vals[col_vals > 0]
                        if len(nonzero) > 0:
                            denom = nonzero.min()
                            norm[:, j] = np.where(col_vals == 0, 1.0, denom / col_vals)
                        else:
                            norm[:, j] = 1.0

                with st.expander("STEP 2 - Matriks Normalisasi SAW (10 baris pertama)"):
                    df_norm = pd.DataFrame(
                        norm[:10],
                        columns=[v["label"] for v in KRITERIA.values()],
                        index=df_calc["name"].iloc[:10]
                    ).round(4)
                    st.dataframe(df_norm, use_container_width=True)

                # STEP 3: Pembobotan
                with st.expander("STEP 3 - Bobot yang Digunakan"):
                    df_bobot = pd.DataFrame({
                        "Kriteria"  : [v["label"] for v in KRITERIA.values()],
                        "Tipe"      : [v["tipe"].capitalize() for v in KRITERIA.values()],
                        "Bobot"     : bobot,
                        "Bobot (%)" : [f"{b*100:.0f}%" for b in bobot],
                    })
                    st.dataframe(df_bobot, use_container_width=True, hide_index=True)

                # Hitung skor akhir: V_i = Σ(w_j × r_ij)
                skor = np.dot(norm, bobot)
                df_calc["Skor SAW"] = np.round(skor, 4)

                df_result = (
                    df_calc[["name", "type", "rating", "htm",
                              "jarak_km", "kategori", "popularitas", "Skor SAW"]]
                    .sort_values("Skor SAW", ascending=False)
                    .head(top_n)
                    .reset_index(drop=True)
                )
                df_result.index += 1
                df_result.index.name = "Peringkat"

                st.markdown("---")
                st.markdown("### Hasil Perangkingan Destinasi Wisata")
                st.markdown(
                    f"Menampilkan **Top {top_n}** dari **{len(df_calc)} destinasi** "
                    f"yang sesuai filter."
                )

                def highlight_rows(row):
                    if row.name == 1:
                        return ["background-color: #218517"] * len(row)
                    elif row.name == 2:
                        return ["background-color: #2B9E20"] * len(row)
                    elif row.name == 3:
                        return ["background-color: #45BF39"] * len(row)
                    return [""] * len(row)

                df_display = df_result.rename(columns={
                    "name"       : "Nama Destinasi",
                    "type"       : "Jenis Wisata",
                    "rating"     : "Rating",
                    "htm"        : "HTM (Rp)",
                    "jarak_km"   : "Jarak (km)",
                    "kategori"   : "Skor Kategori",
                    "popularitas": "Popularitas",
                })
                st.dataframe(
                    df_display.style.apply(highlight_rows, axis=1)
                    .format({
                        "HTM (Rp)"  : "Rp {:,.0f}",
                        "Jarak (km)": "{:.2f} km",
                        "Skor SAW"  : "{:.4f}",
                    }),
                    use_container_width=True,
                    height=500,
                )

                st.session_state["df_result"] = df_result
                st.session_state["df_calc"]   = df_calc

                # Top 3 Highlight Cards
                st.markdown("### Top 3 Rekomendasi Terbaik")
                top3  = df_result.head(3)
                cols3 = st.columns(3)
                medals = ["Peringkat 1", "Peringkat 2", "Peringkat 3"]
                colors = ["#6C6741", "#737777", "#685E4F"]
                for i, (_, row) in enumerate(top3.iterrows()):
                    with cols3[i]:
                        st.markdown(
                            f"<div style='background:{colors[i]};padding:16px;"
                            f"border-radius:12px;text-align:center'>"
                            f"<h3 style='margin:0'>{medals[i]}</h3>"
                            f"<b>{row['name']}</b><br>"
                            f"<small>{row['type']}</small><br><br>"
                            f"Rating: {row['rating']} &nbsp;|&nbsp; "
                            f"Rp {row['htm']:,.0f}<br>"
                            f"Jarak: {row['jarak_km']:.1f} km<br>"
                            f"<b>Skor SAW: {row['Skor SAW']:.4f}</b>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

#  HALAMAN 4 – VISUALISASI 
elif halaman == "Visualisasi":
    st.title("Visualisasi Data Analitik")

    # Grafik 1: Distribusi Jenis Wisata
    st.markdown("### 1. Distribusi Jenis Wisata")
    type_counts = df_raw["type"].value_counts()

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    colors_bar = plt.cm.Blues_r(np.linspace(0.3, 0.9, len(type_counts)))
    bars = ax1.barh(type_counts.index, type_counts.values, color=colors_bar)
    ax1.bar_label(bars, fmt="%d", padding=3, fontsize=9)
    ax1.set_xlabel("Jumlah Destinasi", fontsize=11)
    ax1.set_title("Distribusi Destinasi Wisata Yogyakarta per Jenis", fontsize=13, fontweight="bold")
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

    # Grafik 2: Rata-rata Rating per Kategori (Bar Chart)
    st.markdown("### 2. Rata-rata Rating per Kategori Wisata")
    avg_rating = df_raw.groupby("type")["rating"].mean().sort_values(ascending=False)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    colors_avg = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(avg_rating)))
    bars2 = ax2.barh(avg_rating.index, avg_rating.values, color=colors_avg)
    ax2.bar_label(bars2, fmt="%.2f", padding=3, fontsize=9)
    ax2.set_xlabel("Rata-rata Rating", fontsize=11)
    ax2.set_title("Rata-rata Rating per Kategori (Dasar Skor C4)", fontsize=13, fontweight="bold")
    ax2.set_xlim(0, 5.5)
    ax2.invert_yaxis()
    ax2.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Grafik 3: Scatter Jarak vs Rating
    st.markdown("### 3. Hubungan Jarak dari Pusat Kota vs Rating")
    df_scatter = df_raw.copy()
    jenis_list = df_raw["type"].value_counts().head(6).index.tolist()
    df_scatter = df_scatter[df_scatter["type"].isin(jenis_list)]

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    colors_sc = plt.cm.tab10(np.linspace(0, 1, len(jenis_list)))
    for i, jenis in enumerate(jenis_list):
        sub = df_scatter[df_scatter["type"] == jenis]
        ax3.scatter(sub["jarak_km"], sub["rating"], label=jenis,
                    color=colors_sc[i], alpha=0.65, s=50,
                    edgecolors="white", linewidths=0.4)

    ax3.set_xlabel("Jarak dari Pusat Kota (km)", fontsize=11)
    ax3.set_ylabel("Rating Wisatawan", fontsize=11)
    ax3.set_title("Scatter: Jarak vs Rating per Jenis Wisata", fontsize=13, fontweight="bold")
    ax3.legend(title="Jenis Wisata", fontsize=8, title_fontsize=9, bbox_to_anchor=(1.01, 1))
    ax3.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # Grafik 4: Popularitas
    st.markdown("### 4. Popularitas Destinasi")
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    popularitas_counts = df_raw["popularitas"].value_counts().sort_index()
    ax4.bar(popularitas_counts.index, popularitas_counts.values,
            color="#3b82f6", edgecolor="white", alpha=0.85)
    ax4.set_xlabel("Skor Popularitas (1=Kurang Populer, 5=Populer)", fontsize=11)
    ax4.set_ylabel("Jumlah Destinasi", fontsize=11)
    ax4.set_title("Popularitas (C5) - 437 Destinasi",
                  fontsize=13, fontweight="bold")
    ax4.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

    # Grafik 5: Top 10 Skor SAW (jika sudah dihitung)
    if "df_result" in st.session_state:
        st.markdown("### 5. Top 10 Destinasi - Skor SAW")
        top10 = st.session_state["df_result"].head(10)
        colors_saw = plt.cm.YlOrRd_r(np.linspace(0.2, 0.9, len(top10)))
        fig5, ax5 = plt.subplots(figsize=(10, 5))
        bars = ax5.barh(top10["name"], top10["Skor SAW"], color=colors_saw)
        ax5.bar_label(bars, fmt="%.4f", padding=3, fontsize=9)
        ax5.set_xlabel("Skor SAW", fontsize=11)
        ax5.set_title("Top 10 Destinasi Wisata Berdasarkan Skor SAW",
                      fontsize=13, fontweight="bold")
        ax5.invert_yaxis()
        ax5.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()
    else:
        st.info("Jalankan perhitungan SAW di halaman Hitung SPK terlebih dahulu untuk melihat grafik skor SAW.")
