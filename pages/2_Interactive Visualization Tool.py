import pandas as pd
import pygwalker as pyg
import streamlit as st
from pygwalker.api.streamlit import StreamlitRenderer

# Basic Streamlit configuration
st.set_page_config(
    page_title="Interactive Visualization Tool",
    layout="wide",
    page_icon="📈",
)

st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .title {
        font-size: 2.5em;
        color: #4a4a4a;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        font-size: 1.5em;
        color: #4a4a4a;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main">', unsafe_allow_html=True)
st.markdown('<div class="title">📊 Interactive Visualization Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Welcome! This tool allows you to explore your data interactively using various visualizations. \
    Upload your dataset and start analyzing!</div>', unsafe_allow_html=True)

if st.session_state.get('df') is not None:
    df = st.session_state.df
    pyg_app = StreamlitRenderer(df)
    pyg_app.explorer()
else:
    st.info("Please upload a dataset on the main page to begin using the interactive visualization tool.")

st.markdown('</div>', unsafe_allow_html=True)