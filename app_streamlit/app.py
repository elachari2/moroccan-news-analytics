import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
import plotly.graph_objects as go

# Configuration
st.set_page_config(page_title="Morocco News Analytics", layout="wide", initial_sidebar_state="collapsed")

# CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&family=Inter:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    
    h1 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 20px;
        text-align: center;
        font-size: 3rem !important;
    }
    
    h2, h3 {
        font-family: 'Outfit', sans-serif;
        color: #e2e8f0;
    }

    /* Glassmorphism Metrics */
    div[data-testid="stMetric"] {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(56, 189, 248, 0.3);
        box-shadow: 0 10px 40px rgba(56, 189, 248, 0.1);
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif;
        color: #38bdf8;
        font-size: 2.5rem;
    }

    div[data-testid="stMetricLabel"] {
        color: #94a3b8;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Styled DataFrame Headers */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🇲🇦 Morocco News Analytics Hub</h1>", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def get_data():
    try:
        conn = psycopg2.connect(os.getenv("DB_URL", "postgresql://admin:adminpassword@postgres/news_dw"))
        query = "SELECT source, category, published_date, word_count, title FROM gold_news_analytics ORDER BY published_date DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df = df.drop_duplicates(subset=['title']).reset_index(drop=True)
            
            df = df[['published_date', 'source', 'title', 'category']]
            
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

df = get_data()

# Metrics
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Articles Analysés", len(df))
with col2:
    st.metric("Sources Actives", df['source'].nunique() if not df.empty else 0)
with col3:
    st.metric("Catégorie Dominante", df['category'].mode()[0] if not df.empty else "N/A")

st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)


c1, c2 = st.columns(2)

chart_config = {
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'font': {'color': '#e2e8f0', 'family': 'Inter'},
    'margin': dict(t=40, b=40, l=40, r=40)
}

with c1:
    st.markdown("<h3 style='text-align: center;'>Répartition par Source</h3>", unsafe_allow_html=True)
    if not df.empty:
        fig1 = px.pie(df, names='source', hole=0.6, color_discrete_sequence=['#38bdf8', '#818cf8', '#c084fc'])
        fig1.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#0f172a', width=2)))
        fig1.update_layout(**chart_config, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.markdown("<h3 style='text-align: center;'>Activité Temporelle</h3>", unsafe_allow_html=True)
    if not df.empty:
        trend = df.groupby('published_date').size().reset_index(name='count')
        fig2 = px.area(trend, x='published_date', y='count', color_discrete_sequence=['#38bdf8'])
        fig2.update_layout(**chart_config, xaxis_title="", yaxis_title="")
        fig2.update_xaxes(showgrid=False)
        fig2.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
st.markdown("<h3>Dernières Actualités en Direct</h3>", unsafe_allow_html=True)

if not df.empty:
    st.dataframe(
        df, 
        use_container_width=True,
        hide_index=True,
        column_config={
            "published_date": st.column_config.DatetimeColumn("Date de Publication", format="DD MMM YYYY, HH:mm"),
            "source": "Source",
            "title": "Titre de l'Article",
            "category": "Catégorie"
        }
    )
