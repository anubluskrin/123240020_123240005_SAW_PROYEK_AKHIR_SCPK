import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SPK Wisata Jogja - Metode SAW",
    layout="wide",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLE
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
#  LOAD & PREPARE DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("tourism_jogja.csv")

    # C3: Skor Fasilitas – diturunkan dari jenis wisata
    fasilitas_map = {
        "Buatan": 5, "Wisata Air": 4, "Pantai": 4,
        "Alam": 3, "Budaya Dan Sejarah": 3, "Agrowisata": 3,
        "Museum": 3, "Desa Wisata": 2, "Religi": 2,
        "Kuliner": 2, "Pendidikan": 2, "Seni": 1, "Minat Khusus": 1
    }
    df["fasilitas"] = df["type"].map(fasilitas_map).fillna(2).astype(int)

    # C4: Skor Aksesibilitas (1-5) – seed deterministik per place_id
    rng = np.random.default_rng(seed=42)
    df["aksesibilitas"] = rng.integers(2, 6, size=len(df))

    # C5: Skor Popularitas – normalisasi berbasis rating
    df["popularitas"] = (
        pd.cut(df["rating"], bins=[0, 3.9, 4.2, 4.5, 4.7, 5.0],
               labels=[1, 2, 3, 4, 5]).astype(float)
    ).fillna(3).astype(int)

    return df

df_raw = load_data()

# ─────────────────────────────────────────────
#  KRITERIA DEFINITION
# ─────────────────────────────────────────────
KRITERIA = {
    "C1": {"label": "Rating Wisatawan",  "col": "rating",       "tipe": "benefit"},
    "C2": {"label": "Harga Tiket (HTM)", "col": "htm",          "tipe": "cost"},
    "C3": {"label": "Fasilitas",         "col": "fasilitas",    "tipe": "benefit"},
    "C4": {"label": "Aksesibilitas",     "col": "aksesibilitas","tipe": "benefit"},
    "C5": {"label": "Popularitas",       "col": "popularitas",  "tipe": "benefit"},
}

# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
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

# ══════════════════════════════════════════════════════════════════
#  HALAMAN 1 – BERANDA
# ══════════════════════════════════════════════════════════════════
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
        "User dapat menyesuaikan bobot kriteria sesuai preferensi pribadi."
    )

    st.markdown("### Kriteria Penilaian")
    df_kriteria = pd.DataFrame([
        {"Kode": k, "Kriteria": v["label"], "Tipe": v["tipe"].capitalize(),
         "Kolom Data": v["col"]}
        for k, v in KRITERIA.items()
    ])
    st.dataframe(df_kriteria, use_container_width=True, hide_index=True)

    st.markdown("### Alur Metode SAW")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.markdown("**1. Input Data**\n\nDataset 437 destinasi wisata Jogja")
    col_b.markdown("**2. Normalisasi**\n\nMatriks ternormalisasi (benefit/cost)")
    col_c.markdown("**3. Pembobotan**\n\nSkor = Jumlah(bobot x nilai ternormalisasi)")
    col_d.markdown("**4. Perangkingan**\n\nUrut dari skor tertinggi")

# ══════════════════════════════════════════════════════════════════
#  HALAMAN 2 – DATASET
# ══════════════════════════════════════════════════════════════════
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
                      "fasilitas", "aksesibilitas", "popularitas"]].rename(columns={
                "place_id": "ID", "name": "Nama Destinasi", "type": "Jenis",
                "rating": "Rating", "htm": "HTM (Rp)",
                "fasilitas": "Fasilitas", "aksesibilitas": "Aksesibilitas",
                "popularitas": "Popularitas"
            }),
            use_container_width=True,
            height=460,
        )

    st.markdown("---")
    st.markdown("### Statistik Deskriptif")
    st.dataframe(
        df_raw[["rating", "htm", "fasilitas", "aksesibilitas", "popularitas"]]
        .describe().round(2),
        use_container_width=True
    )

# ══════════════════════════════════════════════════════════════════
#  HALAMAN 3 – HITUNG SPK
# ══════════════════════════════════════════════════════════════════
elif halaman == "Hitung SPK":
    st.title("Perhitungan SPK - Metode SAW")

    # Panel Input Bobot
    st.markdown("### Input Bobot Kriteria")
    st.markdown("Atur bobot setiap kriteria (total harus = 100%). Bobot mencerminkan prioritas kamu.")

    col1, col2, col3, col4, col5 = st.columns(5)
    w1 = col1.slider("C1 - Rating",        0, 100, 30, 5, help="Bobot Rating Wisatawan")
    w2 = col2.slider("C2 - HTM",           0, 100, 25, 5, help="Bobot Harga Tiket")
    w3 = col3.slider("C3 - Fasilitas",     0, 100, 20, 5, help="Bobot Fasilitas")
    w4 = col4.slider("C4 - Aksesibilitas", 0, 100, 15, 5, help="Bobot Aksesibilitas")
    w5 = col5.slider("C5 - Popularitas",   0, 100, 10, 5, help="Bobot Popularitas")

    total_bobot = w1 + w2 + w3 + w4 + w5
    if total_bobot != 100:
        st.warning(f"Total bobot saat ini = **{total_bobot}** (harus tepat 100 agar valid)")
    else:
        st.success(f"Total bobot = {total_bobot} – Valid!")

    # Filter Jenis Wisata
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
                cols  = [v["col"] for v in KRITERIA.values()]
                tipes = [v["tipe"] for v in KRITERIA.values()]

                matriks = df_calc[cols].values.astype(float)

                # STEP 1: Tampilkan Matriks Keputusan
                with st.expander("STEP 1 - Matriks Keputusan (10 baris pertama)", expanded=True):
                    df_matriks = pd.DataFrame(
                        matriks[:10],
                        columns=[v["label"] for v in KRITERIA.values()],
                        index=df_calc["name"].iloc[:10]
                    ).round(4)
                    st.dataframe(df_matriks, use_container_width=True)

                # STEP 2: Normalisasi SAW
                norm = np.zeros_like(matriks)
                for j, tipe in enumerate(tipes):
                    col_vals = matriks[:, j]
                    if tipe == "benefit":
                        denom = col_vals.max()
                        norm[:, j] = col_vals / denom if denom != 0 else 0
                    else:  # cost
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

                # STEP 3: Pembobotan & Skor Akhir
                skor = np.dot(norm, bobot)
                df_calc["Skor SAW"] = np.round(skor, 4)
                df_result = (
                    df_calc[["name", "type", "rating", "htm",
                              "fasilitas", "aksesibilitas", "popularitas", "Skor SAW"]]
                    .sort_values("Skor SAW", ascending=False)
                    .head(top_n)
                    .reset_index(drop=True)
                )
                df_result.index += 1
                df_result.index.name = "Peringkat"

                with st.expander("STEP 3 - Bobot yang Digunakan"):
                    df_bobot = pd.DataFrame({
                        "Kriteria": [v["label"] for v in KRITERIA.values()],
                        "Tipe": [v["tipe"].capitalize() for v in KRITERIA.values()],
                        "Bobot": bobot,
                        "Bobot (%)": [f"{b*100:.0f}%" for b in bobot],
                    })
                    st.dataframe(df_bobot, use_container_width=True, hide_index=True)

                # STEP 4: Tabel Hasil Perangkingan
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
                    "name": "Nama Destinasi", "type": "Jenis Wisata",
                    "rating": "Rating", "htm": "HTM (Rp)",
                    "fasilitas": "Fasilitas", "aksesibilitas": "Aksesibilitas",
                    "popularitas": "Popularitas",
                })
                st.dataframe(
                    df_display.style.apply(highlight_rows, axis=1)
                    .format({"HTM (Rp)": "Rp {:,.0f}", "Skor SAW": "{:.4f}"}),
                    use_container_width=True,
                    height=500,
                )

                # Simpan ke session
                st.session_state["df_result"] = df_result
                st.session_state["df_calc"]   = df_calc

                # Highlight Top 3
                st.markdown("### Top 3 Rekomendasi Terbaik")
                top3 = df_result.head(3)
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
                            f"<b>Skor SAW: {row['Skor SAW']:.4f}</b>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

# ══════════════════════════════════════════════════════════════════
#  HALAMAN 4 – VISUALISASI
# ══════════════════════════════════════════════════════════════════
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


    # Grafik 2: Pie Chart Rating Rata-rata per Jenis Wisata
    st.markdown("### 2. Perbandingan Rating per Jenis Wisata (Pie Chart)")
    top_types = type_counts[type_counts >= 10].index.tolist()
    df_pie2 = df_raw[df_raw["type"].isin(top_types)]
    avg_rating_per_type = df_pie2.groupby("type")["rating"].mean().reindex(top_types)

    fig2, ax2 = plt.subplots(figsize=(9, 9))
    colors_pie2 = plt.cm.Set2(np.linspace(0, 1, len(top_types)))
    avg_vals = avg_rating_per_type.values
    labels_with_rating = [
        f"{t}\n(avg: {r:.2f})" for t, r in zip(avg_rating_per_type.index, avg_vals)
    ]
    wedges, texts, autotexts = ax2.pie(
        avg_vals,
        labels=labels_with_rating,
        autopct="%1.1f%%",
        colors=colors_pie2,
        startangle=140,
        pctdistance=0.75,
        wedgeprops=dict(edgecolor="white", linewidth=1.2),
    )
    for text in texts:
        text.set_fontsize(8.5)
    for autotext in autotexts:
        autotext.set_fontsize(7.5)
        autotext.set_color("white")
        autotext.set_fontweight("bold")
    ax2.set_title("Proporsi Rata-rata Rating per Jenis Wisata", fontsize=13, fontweight="bold", pad=20)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    # Grafik 3: Scatter HTM vs Rating
    st.markdown("### 3. Hubungan Harga Tiket vs Rating Wisatawan")
    df_scatter = df_raw[df_raw["htm"] <= 200_000].copy()
    jenis_list = df_raw["type"].value_counts().head(6).index.tolist()
    df_scatter = df_scatter[df_scatter["type"].isin(jenis_list)]

    fig3, ax3 = plt.subplots(figsize=(10, 5))
    colors_sc = plt.cm.tab10(np.linspace(0, 1, len(jenis_list)))
    for i, jenis in enumerate(jenis_list):
        sub = df_scatter[df_scatter["type"] == jenis]
        ax3.scatter(sub["htm"], sub["rating"], label=jenis,
                    color=colors_sc[i], alpha=0.65, s=50, edgecolors="white", linewidths=0.4)

    ax3.set_xlabel("Harga Tiket / HTM (Rp)", fontsize=11)
    ax3.set_ylabel("Rating Wisatawan", fontsize=11)
    ax3.set_title("Scatter: Harga Tiket vs Rating (HTM <= Rp 200.000)", fontsize=13, fontweight="bold")
    ax3.legend(title="Jenis Wisata", fontsize=8, title_fontsize=9, bbox_to_anchor=(1.01, 1))
    ax3.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"Rp {int(x):,}"))
    ax3.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

    # Grafik 4: Histogram Rating
    st.markdown("### 4. Distribusi Rating Seluruh Destinasi")
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    ax4.hist(df_raw["rating"], bins=20, color="#3b82f6", edgecolor="white", alpha=0.85)
    ax4.axvline(df_raw["rating"].mean(), color="#ef4444", linestyle="--",
                linewidth=2, label=f"Rata-rata: {df_raw['rating'].mean():.2f}")
    ax4.set_xlabel("Rating", fontsize=11)
    ax4.set_ylabel("Jumlah Destinasi", fontsize=11)
    ax4.set_title("Distribusi Rating Wisatawan - 437 Destinasi", fontsize=13, fontweight="bold")
    ax4.legend(fontsize=10)
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
        ax5.set_title("Top 10 Destinasi Wisata Berdasarkan Skor SAW", fontsize=13, fontweight="bold")
        ax5.invert_yaxis()
        ax5.spines[["top", "right"]].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig5)
        plt.close()
    else:
        st.info("Jalankan perhitungan SAW di halaman Hitung SPK terlebih dahulu untuk melihat grafik skor SAW.")
