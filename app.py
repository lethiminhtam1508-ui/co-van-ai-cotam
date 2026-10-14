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

# TÙY BIẾN GIAO DIỆN (NỀN, FONT CHỮ & ẨN THANH CHÂN TRANG ĐỂ TRÁNH CHE KHUẤT)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&family=Merriweather:wght@700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    /* Ẩn thanh header và footer mặc định của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    footer:after {display:none;}

    /* Khung Header Banner màu nền nổi bật */
    .header-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 50%, #f8fafc 100%);
        padding: 20px 24px;
        border-radius: 14px;
        border: 1px solid #bfdbfe;
        border-left: 8px solid #1d4ed8;
        box-shadow: 0 4px 14px rgba(30, 64, 175, 0.08);
        margin-bottom: 18px;
    }

    .main-title {
        font-family: 'Merriweather', serif;
        font-size: 24px;
        font-weight: 900;
        color: #1e3a8a;
        margin: 0;
        padding-bottom: 4px;
    }

    .sub-title {
        color: #1e293b;
        font-size: 14px;
        font-weight: 700;
        margin-top: 4px;
    }

    .section-title {
        font-family: 'Be Vietnam Pro', sans-serif;
        color: #0f172a;
        font-size: 18px;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 6px;
    }

    .section-desc {
        color: #334155;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    div.stButton > button {
        background-color: #ffffff;
        color: #1e40af;
        border: 1.5px solid #93c5fd;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 13px;
        font-weight: 700;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #eff6ff;
        border-color: #2563eb;
        color: #1d4ed8;
    }
</style>
""", unsafe_allow_html=True)

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Advanced settings -> Secrets trên Streamlit Cloud.")

# 2. Tiêu đề ứng dụng
st.markdown("""
<div class="header-box">
    <h1 class="main-title">🧭 Trợ Lý Cố Vấn Hướng Nghiệp AI - Cô Tâm</h1>
    <div class="sub-title">Trường THPT Phan Đăng Lưu • Đồng hành khai vấn & kiến tạo tương lai cùng học sinh</div>
</div>
""", unsafe_allow_html=True)

# Khởi tạo lịch sử trò chuyện
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

# 3. Phân chia các Tab chức năng
tab1, tab2, tab3 = st.tabs(["💬 Khung Cố Vấn Khai Vấn", "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", "📜 Sổ Tay & Lộ Trình 30 Ngày"])

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN (AI CHATBOT)
# ==========================================
with tab1:
    st.markdown('<div class="section-title">💡 Trò chuyện trực tiếp cùng Cô Tâm</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Em đang băn khoăn về chọn khối thi, chọn ngành, mâu thuẫn giữa sở thích và năng lực, hay áp lực từ gia đình? Hãy chia sẻ cùng cô nhé!</div>', unsafe_allow_html=True)

    # Gợi ý tình huống nhanh
    st.markdown("**Gợi ý tình huống nhanh:**")
    col_a, col_b, col_c = st.columns(3)
    quick_prompt = None
    if col_a.button("IT & Tố chất Hướng nội (S)"):
        quick_prompt = "Em muốn học ngành Công nghệ Thông tin nhưng tính em rất hướng nội và ngại giao tiếp, kết quả trắc nghiệm ra nhóm Trầm tĩnh (S). Liệu em có theo được không cô?"
    if col_b.button("Sư phạm hay Kinh doanh?"):
        quick_prompt = "Gia đình muốn em thi Sư phạm cho ổn định, nhưng em lại thích kinh doanh khởi nghiệp. Em đang rất khó xử không biết chọn thế nào ạ?"
    if col_c.button("Học lực khá, chưa rõ đam mê?"):
        quick_prompt = "Em đang học lớp 11, học lực ở mức khá nhưng chưa thực sự thấy mình nổi trội môn nào hay đam mê ngành gì cụ thể. Cô giúp em với ạ!"

    # Hiển thị toàn bộ lịch sử tin nhắn
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Ô nhập tin nhắn
    user_chat = st.chat_input("Nhập băn khoăn của em về chọn ngành, chọn khối thi...")
    prompt_to_send = user_chat or quick_prompt

    if prompt_to_send:
        st.session_state.messages.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        with st.chat_message("assistant"):
            if not client:
                st.error("Chưa kết nối được với AI (Thiếu API Key). Vui lòng cấu hình Secrets trên Streamlit Cloud.")
            else:
                with st.spinner("Cô Tâm đang suy ngẫm câu trả lời cho em..."):
                    system_prompt = """
                    Bạn là cô giáo Lê Thị Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp (HĐTN, HN) tại Trường THPT Phan Đăng Lưu, Huế.
                    Bạn là người CÔ ĐỒNG HÀNH & CHUYÊN GIA KHAI VẤN (COACHING) CHỈ CHUYÊN SÂU VỀ HƯỚNG NGHIỆP VÀ TÂM LÝ LỨA TUỔI HỌC ĐƯỜNG.

                    GIỚI HẠN PHẠM VI NGHIÊM NGẶT (SCOPE BOUNDARY):
                    - BẠN CHỈ TƯ VẤN: Chọn ngành, chọn khối thi, thấu hiểu tính cách/sở thích (DISC, Holland), giải tỏa áp lực học tập/gia đình, phương pháp học tập chung và kế hoạch hành động 30 ngày (E + R = O).
                    - TUYỆT ĐỐI TỪ CHỐI: Giải bài tập cụ thể của các môn học (như giải bài tập Toán, Lý, Hóa, Văn, tích vô hướng, đạo hàm...), viết văn hộ, giải bài tập về nhà, hoặc các chủ đề phiếm ngoài học đường.
                    - KHI HỌC SINH HỎI NGOÀI PHẠM VI: Hãy mỉm cười từ chối một cách duyên dáng, chuẩn mực sư
