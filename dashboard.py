import streamlit as st  # type: ignore[import-not-found]
import pandas as pd  # type: ignore[import-not-found]
import plotly.graph_objects as go  # type: ignore[import-not-found]
import plotly.express as px  # type: ignore[import-not-found]

st.set_page_config(page_title="Sephora Dashboard", layout="wide")

st.title("Sephora Products and Skincare Reviews")

@st.cache_data
def load_data():
    path = r"C:\Users\giana\AI For Business\w11\Sephora.csv"
    df = pd.read_csv(path)
    df['price_usd'] = pd.to_numeric(df['price_usd'], errors='coerce')
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    if 'reviews' in df.columns:
        df['reviews'] = pd.to_numeric(df['reviews'], errors='coerce').fillna(0)
    if 'out_of_stock' in df.columns:
        df['out_of_stock'] = pd.to_numeric(df['out_of_stock'], errors='coerce').fillna(0)
    return df

df = load_data()

# ---------- Navigasi ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Ringkasan (Home)",
    "Kategori (Combo)",
    "Rating per Harga (Bar)",
    "Top Brand (Bubble)",
    "Preview Data",
])

# ---------- Helper: buat grafik ----------
def make_combo_fig():
    cat = (
        df.groupby('primary_category')
        .agg(jumlah_produk=('product_id', 'count'), rata_rata_harga=('price_usd', 'mean'))
        .reset_index()
        .sort_values('jumlah_produk', ascending=False)
    )

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=cat['primary_category'],
        y=cat['jumlah_produk'],
        name='Jumlah Produk',
        marker_color='#636EFA',
        text=cat['jumlah_produk'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Jumlah Produk: %{y}<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=cat['primary_category'],
        y=cat['rata_rata_harga'],
        name='Rata-rata Harga',
        mode='lines+markers',
        yaxis='y2',
        line=dict(color='#EF553B', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x}</b><br>Rata-rata Harga: $%{y:.2f}<extra></extra>',
    ))

    fig.update_layout(
        title='Jumlah Produk (Bar) dan Rata-rata Harga (Line) per Kategori Utama',
        xaxis=dict(title='Kategori Utama', tickangle=-45),
        yaxis=dict(
            title='Jumlah Produk',
            tickfont=dict(color='#636EFA'),
        ),
        yaxis2=dict(
            title='Rata-rata Harga ($)',
            tickfont=dict(color='#EF553B'),
            overlaying='y',
            side='right',
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.08, xanchor='right', x=1),
        barmode='group',
        height=500,
    )
    return fig

def make_rating_fig():
    work = df.copy()

    def price_bucket(p):
        if pd.isna(p):
            return None
        if p <= 25:
            return '$0–25'
        if p <= 50:
            return '$25–50'
        if p <= 100:
            return '$50–100'
        return '$100+'

    work['price_bucket'] = work['price_usd'].apply(price_bucket)
    bucket_order = ['$0–25', '$25–50', '$50–100', '$100+']

    line = (
        work.dropna(subset=['price_bucket', 'rating'])
        .groupby('price_bucket')['rating']
        .mean()
        .reindex(bucket_order)
        .reset_index()
    )

    fig2 = px.bar(
        line,
        x='price_bucket',
        y='rating',
        labels={'price_bucket': 'Kelompok Harga', 'rating': 'Rata-rata Rating'},
        title='Rata-rata Rating Berdasarkan Kelompok Harga',
    )
    fig2.update_traces(marker_color='#00CC96')
    fig2.update_yaxes(range=[0, 5])
    fig2.update_layout(height=500)
    return fig2

def make_bubble_fig():
    brand_agg = (
        df.groupby('brand_name')
        .agg(jumlah_produk=('product_id', 'count'), rata_rata_harga=('price_usd', 'mean'))
        .reset_index()
        .sort_values('jumlah_produk', ascending=False)
    )

    top_n = 15
    bubble_df = brand_agg.head(top_n)

    fig3 = px.scatter(
        bubble_df,
        x='jumlah_produk',
        y='rata_rata_harga',
        size='jumlah_produk',
        color='brand_name',
        hover_name='brand_name',
        hover_data={'jumlah_produk': True, 'rata_rata_harga': ':.2f', 'brand_name': False},
        labels={
            'jumlah_produk': 'Jumlah Produk',
            'rata_rata_harga': 'Rata-rata Harga ($)',
            'brand_name': 'Brand',
        },
        title=f'Top {top_n} Brand Berdasarkan Jumlah Produk (Bubble, Ukuran = Jumlah Produk)',
        size_max=40,
    )
    fig3.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='white')))
    fig3.update_layout(height=500)
    return fig3

# ---------- Tab 1: Ringkasan (Home) - tampilkan semua ----------
with tab1:
    st.subheader("Ringkasan Utama")
    total = len(df)
    avg_price = df['price_usd'].mean()
    avg_rating = df['rating'].mean()
    oos = int(df['out_of_stock'].sum()) if 'out_of_stock' in df.columns else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Produk", f"{total:,}")
    k2.metric("Rata-rata Harga", f"${avg_price:,.2f}")
    k3.metric("Rata-rata Rating", f"{avg_rating:.2f}")
    k4.metric("Out of Stock", f"{oos:,}")

    st.markdown("---")
    st.subheader("Grafik Lengkap")
    st.plotly_chart(make_combo_fig(), use_container_width=True, key="home_combo")

    cA, cB = st.columns(2)
    with cA:
        st.plotly_chart(make_rating_fig(), use_container_width=True, key="home_rating")
    with cB:
        st.plotly_chart(make_bubble_fig(), use_container_width=True, key="home_bubble")

    st.markdown("---")
    st.subheader("Sample Data Preview")
    preview_cols = ['product_id', 'loves_count', 'rating', 'reviews', 'price_usd', 'primary_category', 'secondary_category', 'tertiary_category']
    st.dataframe(df[preview_cols].head(5), use_container_width=True)
    st.caption(f"Total baris data: {len(df):,} | Kolom: {len(df.columns)}")

# ---------- Tab 2: Combo Chart ----------
with tab2:
    st.subheader("Jumlah Produk & Rata-rata Harga per Kategori")
    st.plotly_chart(make_combo_fig(), use_container_width=True, key="tab2_combo")

# ---------- Tab 3: Bar Chart Rating per Harga ----------
with tab3:
    st.subheader("Rata-rata Rating per Kelompok Harga")
    st.plotly_chart(make_rating_fig(), use_container_width=True, key="tab3_rating")

# ---------- Tab 4: Bubble Chart Brand ----------
with tab4:
    st.subheader("Top Brand Berdasarkan Jumlah Produk")
    st.plotly_chart(make_bubble_fig(), use_container_width=True, key="tab4_bubble")

# ---------- Tab 5: Data Preview ----------
with tab5:
    st.subheader("Sample Data Preview")
    preview_cols = ['product_id', 'loves_count', 'rating', 'reviews', 'price_usd', 'primary_category', 'secondary_category', 'tertiary_category']
    st.dataframe(df[preview_cols].head(5), use_container_width=True)
    st.caption(f"Total baris data: {len(df):,} | Kolom: {len(df.columns)}")
