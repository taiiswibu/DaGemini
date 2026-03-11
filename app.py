import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from typing import Any, Optional

from scr.agents.pandas_agent import DataAnalysisAgent
from scr.models.llms import load_llm
from scr.utils.utils import BaseLogger

# Load environment variables
load_dotenv()
logger = BaseLogger()

def execute_plot_code(code: str, df: pd.DataFrame, fig_size: tuple = (10, 6)) -> Optional[plt.Figure]:
    """Thực thi code vẽ biểu đồ một cách an toàn."""
    try:
        plt.figure(figsize=fig_size)
        local_vars = {"plt": plt, "df": df}
        compiled_code = compile(code, "<string>", "exec")
        exec(compiled_code, globals(), local_vars)
        return plt.gcf()
    except Exception as e:
        st.error(f"Lỗi vẽ biểu đồ: {e}")
        return None

def clean_llm_output(raw_output: Any) -> str:
    """Lọc text từ response của Gemini."""
    if isinstance(raw_output, str):
        return raw_output
    if isinstance(raw_output, list):
        cleaned_text = ""
        for item in raw_output:
            if isinstance(item, dict) and 'text' in item:
                cleaned_text += item['text']
            elif isinstance(item, str):
                cleaned_text += item
        return cleaned_text
    return str(raw_output)

def main():
    # 1. Cấu hình trang (Phải đặt ở đầu tiên)
    st.set_page_config(page_title="Gemini Data Analyst", page_icon="✨", layout="wide")

    # Custom CSS cho giao diện mượt mà hơn
    st.markdown("""
        <style>
        .stChatFloatingInputContainer { padding-bottom: 20px; }
        .block-container { padding-top: 2rem; padding-bottom: 5rem; }
        </style>
        """, unsafe_allow_html=True)

    st.title("✨ Gemini Data Agent")
    st.caption("Chat với dữ liệu CSV của ông bằng sức mạnh của Gemini 2.5")

    # 2. Khởi tạo Session State (Giữ dữ liệu không bị mất khi đổi tab)
    if "messages" not in st.session_state:
        # Lời chào mặc định của AI
        st.session_state.messages = [
            {"role": "assistant", "content": "Chào Tài! Hãy tải file CSV lên sidebar bên trái, tui sẽ giúp ông phân tích nó nhé. 📊"}
        ]
    if "df" not in st.session_state:
        st.session_state.df = None
    if "agent" not in st.session_state:
        st.session_state.agent = None

    # Khởi tạo model
    llm = load_llm("gemini-2.5-flash")

    # 3. Sidebar: Quản lý File và Cài đặt
    with st.sidebar:
        st.header("📂 Dữ liệu của ông")
        uploaded_file = st.file_uploader("Tải file CSV lên đây", type="csv")
        
        # Xử lý file upload an toàn
        if uploaded_file is not None:
            # Chỉ đọc lại file nếu đây là file mới (tránh load lại khi đổi tab)
            if "uploaded_filename" not in st.session_state or st.session_state.uploaded_filename != uploaded_file.name:
                st.session_state.df = pd.read_csv(uploaded_file)
                st.session_state.uploaded_filename = uploaded_file.name
                # Tạo lại agent với data mới
                daagent = DataAnalysisAgent(df=st.session_state.df, llm=llm, verbose=True)
                st.session_state.agent = daagent.create_agent()
                st.success(f"Đã nạp file: {uploaded_file.name}")
        
        st.divider()
        if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
            st.session_state.messages = [
                {"role": "assistant", "content": "Đã dọn dẹp bộ nhớ. Ông muốn hỏi gì tiếp?"}
            ]
            st.rerun()

        if st.session_state.df is not None:
            st.expander("Xem trước dữ liệu (5 dòng đầu)").dataframe(st.session_state.df.head())

    # 4. Hiển thị lịch sử Chat (Giao diện giống Gemini)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="✨" if msg["role"] == "assistant" else "🧑‍💻"):
            st.markdown(msg["content"])
            # Nếu tin nhắn có lưu biểu đồ, in nó ra (xử lý logic lưu hình ở dưới)
            if "fig" in msg:
                st.pyplot(msg["fig"])
            if "code" in msg:
                with st.expander("Xem code thực thi"):
                    st.code(msg["code"])

    # 5. Khung nhập liệu Chat Input (Nằm cố định ở dưới cùng)
    if prompt := st.chat_input("Nhập câu hỏi phân tích dữ liệu... (VD: Vẽ biểu đồ cột...)"):
        
        # Thêm câu hỏi của user vào UI và State
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        # Kiểm tra xem có data chưa
        if st.session_state.df is None or st.session_state.agent is None:
            error_msg = "Ông phải tải file CSV lên sidebar trước thì tui mới phân tích được chứ!"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant", avatar="✨"):
                st.warning(error_msg)
            st.stop()

        # Gemini xử lý
        with st.chat_message("assistant", avatar="✨"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    agent = st.session_state.agent
                    response = agent.invoke({"input": prompt})
                    
                    clean_output = clean_llm_output(response["output"])
                    
                    # Biến tạm để lưu dữ liệu vào state
                    msg_data = {"role": "assistant", "content": clean_output}
                    
                    st.markdown(clean_output)

                    # Xử lý nếu có code vẽ biểu đồ trong các bước trung gian
                    if response.get("intermediate_steps"):
                        tool_input = response["intermediate_steps"][-1][0].tool_input
                        action = tool_input.get("query", tool_input) if isinstance(tool_input, dict) else str(tool_input)

                        if "plt" in action or "plot" in action:
                            fig = execute_plot_code(action, st.session_state.df, fig_size=(10, 6))
                            if fig:
                                st.pyplot(fig)
                                msg_data["fig"] = fig # Lưu hình vào state
                            
                            with st.expander("Xem code thực thi"):
                                st.code(action)
                            msg_data["code"] = action # Lưu code vào state

                    # Lưu toàn bộ response của AI vào session state
                    st.session_state.messages.append(msg_data)

                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    main()