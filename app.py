import streamlit as st
import os
import time
from google import genai

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# TÙY BIẾN GIAO DIỆN (NỀN VÀ FONT CHỮ SƯ PHẠM)
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&family=Merriweather:wght@700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer:after {display:none;}

    .header-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 50%, #f8fafc 100%);
        padding: 22px 26px;
        border-radius: 16px;
        border: 1px solid #bfdbfe;
        border-left: 8px solid #1d4ed8;
        box-shadow: 0 6px 18px rgba(30, 64, 175, 0.08);
        margin-bottom: 22px;
    }

    .main-title {
        font-family: 'Merriweather', serif;
        font-size: 26px;
        font-weight: 900;
        color: #1e3a8a;
        margin: 0;
        padding-bottom: 6px;
    }

    .sub-title {
        color: #1e293b;
        font-size: 14.5px;
        font-weight: 700;
        margin-top: 4px;
    }

    .section-title {
        font-family: 'Be Vietnam Pro', sans-serif;
        color: #0f172a;
        font-size: 19px;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    .section-desc {
        color: #334155;
        font-size: 14.5px;
        font-weight: 600;
        margin-bottom: 12px;
    }

    div.stButton > button {
        background-color: #ffffff;
        color: #1e40af;
        border: 1.5px solid #93c5fd;
        border-radius: 20px;
        padding: 6px 15px;
        font-size: 13.5px;
        font-weight: 700;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #eff6ff;
        border-color: #2563eb;
        color: #1d4ed8;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Advanced settings -> Secrets trên Streamlit Cloud.")

# 2. Tiêu đề ứng dụng
header_html = """
<div class="header-box">
    <h1 class="main-title">🧭 Trợ Lý Cố Vấn Hướng Nghiệp AI - Cô Tâm</h1>
    <div class="sub-title">Trường THPT Phan Đăng Lưu • Đồng hành khai vấn & kiến tạo tương lai cùng học sinh</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# Khởi tạo lịch sử trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Chào em! Cô là cô giáo Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp tại Trường THPT Phan Đăng Lưu.\n\nCô rất vui được đồng hành cùng em. Thay vì vội vã chọn ngay một nghề, cô trò mình sẽ từng bước bóc tách những trăn trở để tìm ra con đường tự tin nhất.\n\nEm đang gặp khó khăn hay băn khoăn điều gì về chọn khối thi, ngành nghề hay thấu hiểu bản thân?"
        }
    ]

# 3. Phân chia các Tab chức năng
tab1, tab2, tab3 = st.tabs(["💬 Khung Cố Vấn Khai Vấn", "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", "📜 Sổ Tay & Lộ Trình 30 Ngày"])

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN (AI CHATBOT)
# ==========================================
with tab1:
    st.markdown('<div class="section-title">💡 Trò chuyện trực tiếp cùng Cô Tâm</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Em đang băn khoăn về chọn khối thi, chọn ngành, mâu thuẫn giữa sở thích và năng lực, hay áp lực từ gia
