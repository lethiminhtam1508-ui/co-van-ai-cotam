import os
import time
import streamlit as st
import streamlit.components.v1 as components
from google import genai

# Cấu hình trang
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# TÙY BIẾN CSS GIAO DIỆN
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&family=Merriweather:wght@700;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }
    .stSubheader {
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 1. Khởi tạo Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
client = genai.Client(api_key=api_key) if api_key else None

if not client:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")

# 2. Tiêu đề ứng dụng
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 100%); 
                padding: 20px 24px; 
                border-radius: 14px; 
                border-left: 7px solid #1d4ed8; 
                margin-bottom: 20px; 
                box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
        <h2 style="color: #1e3a8a; margin: 0 0 6px 0; font-weight: 900; font-size: 24px;">
            🧭 Trợ Lý Cố Vấn Hướng Nghiệp AI - Cô Tâm
        </h2>
        <p style="color: #334155; margin: 0; font-weight: 700; font-size: 14.5px;">
            Trường THPT Phan Đăng Lưu • Đồng hành khai vấn & kiến tạo tương lai cùng học sinh
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# 3. Lịch sử trò chuyện
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Chào em! Cô là cô giáo Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp tại Trường THPT Phan Đăng Lưu.\n\n"
                "Cô rất vui được đồng hành cùng em. Thay vì vội vã chọn ngay một nghề, cô trò mình sẽ từng bước bóc tách những trăn trở để tìm ra con đường tự tin nhất.\n\n"
                "Em đang gặp khó khăn hay băn khoăn điều gì về chọn khối thi, ngành nghề hay thấu hiểu bản thân?"
            )
        }
    ]

# 4. Phân chia Tab
tab1, tab2, tab3 = st.tabs([
    "💬 Khung Cố Vấn Khai Vấn", 
    "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", 
    "📜 Sổ Tay & Lộ Trình 30 Ngày"
])

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN
# ==========================================
with tab1:
    st.markdown("### 💡 **Trò chuyện trực tiếp cùng Cô Tâm**")
    st.markdown("**Em có thể gõ câu hỏi hoặc bấm vào biểu tượng Micro 🎙️ trong ô nhập bên dưới để nói trực tiếp cùng cô nhé!**")

    st.markdown("**Gợi ý tình huống nhanh:**")
    c1, c2, c3 = st.columns(3)
    quick_text = None
    if c1.button("IT & Tố chất Hướng nội (S)"):
        quick_text = "Em muốn học ngành Công nghệ Thông tin nhưng tính em rất hướng nội và ngại giao tiếp, kết quả trắc nghiệm ra nhóm Trầm tĩnh (S). Liệu em có theo được không cô?"
    if c2.button("Sư phạm hay Kinh doanh?"):
        quick_text = "Gia đình muốn em thi Sư phạm cho ổn định, nhưng em lại thích kinh doanh khởi nghiệp. Em đang rất khó xử không biết chọn thế nào ạ?"
    if c3.button("Học lực khá, chưa rõ đam mê?"):
        quick_text = "Em đang học lớp 11, học lực ở mức khá nhưng chưa thực sự thấy mình nổi trội môn nào hay đam mê ngành gì cụ thể. Cô giúp em với ạ!"

    # Hiển thị lịch sử chat
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # THIẾT KẾ KHUNG NHẬP LIỆU PHONG CÁCH GEMINI (VIÊN THUỐC BO TRÒN + NÚT MICRO BÊN PHẢI)
    gemini_bar_html = """
    <div style="display: flex; justify-content: center; width: 100%; margin-top: 15px; margin-bottom: 5px;">
        <div style="display: flex; align-items: center; width: 100%; max-width: 850px; 
                    background-color: #f1f3f4; border-radius: 35px; padding: 6px 18px; 
                    box-shadow: 0 1px 4px rgba(0,0,0,0.08); border: 1px solid #e0e0e0;">
            <span style="font-size: 20px; color: #5f6368; margin-right: 12px; cursor: pointer; user-select: none;">＋</span>
            <input id="gemini-input" type="text" placeholder="Hỏi Cô Tâm..." 
                   style="flex: 1; border: none; background: transparent; font-size: 15px; 
                          outline: none; color: #202124; font-family: 'Be Vietnam Pro', sans-serif;" />
            <div style="display: flex; align-items: center; gap: 8px; margin-left: 10px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background-color: #1a73e8;"></span>
                <span style="font-size: 13.5px; font-weight: 600; color: #202124;">Flash</span>
                <span style="font-size: 12px; color: #5f6368; margin-right: 8px;">▾</span>
                <button id="mic-btn" title="Nói qua Micro" 
                        style="background: transparent; border: none; cursor: pointer; font-size: 18px; 
                               padding: 4px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    🎙️
                </button>
            </div>
        </div>
    </div>

    <script>
        const inputEl = document.getElementById('gemini-input');
        const micBtn = document.getElementById('mic-btn');
        let recognition = null;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.lang = 'vi-VN';
            recognition.interimResults = false;

            recognition.onstart = function() {
                micBtn.style.color = '#d93025';
                micBtn.style.transform = 'scale(1.2)';
            };

            recognition.onresult = function(e) {
                const text = e.results[0][0].transcript;
                inputEl.value = text;
                micBtn.style.color =
