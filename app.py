from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from scr.agents.pandas_agent import DataAnalysisAgent
from scr.models.llms import load_llm
from scr.utils.utils import BaseLogger

# Load environment variables
load_dotenv()
logger = BaseLogger()

def execute_plot_code(code: str, df: pd.DataFrame, fig_size: tuple = (10, 6)) -> Optional[plt.Figure]:
    """Execute the plot code safely."""
    try:
        plt.figure(figsize=fig_size)
        local_vars = {"plt": plt, "df": df}
        compiled_code = compile(code, "<string>", "exec")
        exec(compiled_code, globals(), local_vars)
        return plt.gcf()
    except Exception as e:
        st.error(f"Error executing plot code: {e}")
        return None

def display_data(df: pd.DataFrame):
    st.write("### DataFrame Head:")
    st.write(df.head())

def initialize_agent(df: pd.DataFrame, llm: Any, verbose: bool) -> DataAnalysisAgent:
    daagent = DataAnalysisAgent(df=df, llm=llm, verbose=verbose)
    return daagent.create_agent()

def clean_llm_output(raw_output: Any) -> str:
    """Hàm 'máy lọc' để trích xuất text từ response lộn xộn của LLM."""
    if isinstance(raw_output, str):
        return raw_output
    
    if isinstance(raw_output, list):
        cleaned_text = ""
        for item in raw_output:
            # Nếu là dictionary chứa key 'text' (như log của ông gửi)
            if isinstance(item, dict) and 'text' in item:
                cleaned_text += item['text']
            # Nếu nó là chuỗi bình thường
            elif isinstance(item, str):
                cleaned_text += item
        return cleaned_text
        
    return str(raw_output)

def process_query(agent: Any, query: str):
    response = agent.invoke({"input": query})
    
    # Dùng máy lọc để lấy text sạch sẽ
    clean_output = clean_llm_output(response["output"])
    
    if response.get("intermediate_steps"):
        logger.info("### Intermediate steps ###")
        
        tool_input = response["intermediate_steps"][-1][0].tool_input
        action = tool_input.get("query", tool_input) if isinstance(tool_input, dict) else str(tool_input)

        if "plt" in action or "plot" in action:
            st.write(clean_output)
            fig = execute_plot_code(action, st.session_state.df, fig_size=(12, 8))
            if fig:
                st.pyplot(fig)
            st.markdown("**Executed the code:**")
            st.code(action)
            
            to_display_str = clean_output + "\n" + f"```python\n{action}\n```"
            st.session_state.history.append((query, to_display_str))
        else:
            st.write(clean_output)
            st.session_state.history.append((query, clean_output))
    else:
        logger.info("### No intermediate steps ###")
        st.write(clean_output)
        st.session_state.history.append((query, clean_output))

def display_chat_history():
    st.markdown("### Chat History:")
    for i, (q, r) in enumerate(st.session_state.history):
        st.markdown(f"**Query {i+1}:** {q}")
        st.markdown(f"**Response {i+1}:** {r}")
        st.markdown("---")

def main():
    st.set_page_config(page_title="Gemini Data Analysis", page_icon="📊", layout="centered")

    st.markdown("""
        <style>
        .main { padding: 20px; }
        .title { font-size: 2.5em; color: #4a4a4a; text-align: center; margin-bottom: 10px; }
        .subtitle { font-size: 1.5em; color: #4a4a4a; text-align: center; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True)

    llm = load_llm("gemini-2.5-flash")

    with st.sidebar:
        uploaded_file = st.file_uploader("Upload your CSV here:", type="csv")
        if st.button("Clear History"):
            st.session_state.history = []

    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">📊 Gemini Data Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Welcome! Upload your CSV file, enter your query, and let Gemini handle the rest.</div>', unsafe_allow_html=True)

    if "history" not in st.session_state:
        st.session_state.history = []

    if uploaded_file is not None:
        if "df" not in st.session_state or st.session_state.get("uploaded_filename") != uploaded_file.name:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.uploaded_filename = uploaded_file.name
            
        display_data(st.session_state.df)
        
        agent = initialize_agent(st.session_state.df, llm, verbose=True)
        query = st.text_input("Enter your query:")

        if st.button("Run Query") and query:
            with st.spinner("Gemini is analyzing..."):
                process_query(agent, query)

        st.divider()
        display_chat_history()

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()