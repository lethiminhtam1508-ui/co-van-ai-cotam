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

# TÙY BIẾN GIAO DIỆN NỀN TIÊU ĐỀ VÀ CHỮ IN ĐẬM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&family=Merriweather:wght@700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }

    /* Khung Header Banner có màu nền nổi bật */
    .header-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 50%, #f8fafc 100%);
        padding: 24px 28px;
        border-radius: 16px;
        border: 1px solid #bfdbfe;
        border-left: 8px solid #1d4ed8;
        box-shadow: 0 8px 20px rgba(30, 64, 175, 0.08);
        margin-bottom: 24px;
    }

    .main-title {
        font-family: 'Merriweather', serif;
        font-size: 27px;
        font-weight: 900;
        color: #1e3a8a;
        margin: 0;
        padding-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .sub-title {
        color: #1e293b;
        font-size: 15px;
        font-weight: 700; /* In đậm tiêu đề phụ */
        margin-top: 6px;
        letter-spacing: 0.2px;
    }

    /* Các tiêu đề phụ trong các tab */
    .section-title {
        font-family: 'Be Vietnam Pro', sans-serif;
        color: #0f172a;
        font-size: 20px;
        font-weight: 800; /* In đậm rõ nét */
        margin-top: 14px;
        margin-bottom: 8px;
    }

    .section-desc {
        color: #334155;
        font-size: 14.5px;
        font-weight: 600; /* In đậm chữ chú thích */
        margin-bottom: 12px;
    }

    /* Nút câu hỏi nhanh */
    div.stButton > button {
        background-color: #ffffff;
        color: #1e40af;
        border: 1.5px solid #93c5fd;
        border-radius: 20px;
        padding: 7px 16px;
        font-size: 13.5px;
        font-weight: 700; /* Chữ trên nút in đậm */
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    div.stButton > button:hover {
        background-color: #eff6ff;
        border-color: #2563eb;
        color: #1d4ed8;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.12);
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

# 2. Tiêu đề ứng dụng (Đã áp dụng nền màu gradient & in đậm)
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

goi_y = ""

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN (AI CHATBOT)
# ==========================================
with tab1:
    st.markdown('<div class="section-title">💡 Trò chuyện trực tiếp cùng Cô Tâm</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Em đang băn khoăn về chọn khối thi, chọn ngành, mâu thuẫn giữa sở thích và năng lực, hay áp lực từ gia đình? Hãy chia sẻ cùng cô nhé!</div>', unsafe_allow_html=True)

    # Gợi ý tình huống nhanh
    st.markdown("**Gợi ý tình huống nhanh:**")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("IT & Tố chất Hướng nội (S)"):
        goi_y = "Em muốn học ngành Công nghệ Thông tin nhưng tính em rất hướng nội và ngại giao tiếp, kết quả trắc nghiệm ra nhóm Trầm tĩnh (S). Liệu em có theo được không cô?"
    if col_b.button("Sư phạm hay Kinh doanh?"):
        goi_y = "Gia đình muốn em thi Sư phạm cho ổn định, nhưng em lại thích kinh doanh khởi nghiệp. Em đang rất khó xử không biết chọn thế nào ạ?"
    if col_c.button("Học lực khá, chưa rõ đam mê?"):
        goi_y = "Em đang học lớp 11, học lực ở mức khá nhưng chưa thực sự thấy mình nổi trội môn nào hay đam mê ngành gì cụ thể. Cô giúp em với ạ!"

    # Hiển thị lịch sử tin nhắn
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ==========================================
# TAB 2: TRẮC NGHIỆM TỐ CHẤT (DISC & HOLLAND)
# ==========================================
with tab2:
    st.markdown('<div class="section-title">🧩 Khám phá Tố chất & Phong cách Làm việc</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Trả lời 4 câu hỏi trắc nghiệm tình huống dưới đây để nhận diện bức tranh tổng quan về bản thân:</div>', unsafe_allow_html=True)

    with st.form("quiz_form"):
        q1 = st.radio(
            "1. Khi tham gia một hoạt động trải nghiệm nhóm tại trường, em thường chủ động đảm nhận vai trò nào?",
            [
                "A. Trưởng nhóm, phân công nhiệm vụ và thúc đẩy tiến độ hoàn thành (Nhóm D - Thống trị / Quản lý).",
                "B. Người dẫn dắt không khí, thuyết trình và tạo sự gắn kết, vui vẻ (Nhóm I - Ảnh hưởng / Xã hội).",
                "C. Thành viên hỗ trợ chu đáo, luôn lắng nghe và giữ hòa khí cho cả nhóm (Nhóm S - Kiên định / Hòa nhã).",
                "D. Người lập kế hoạch chi tiết, kiểm tra số liệu và đảm bảo không có sai sót (Nhóm C - Tuân thủ / Kỹ thuật)."
            ]
        )

        q2 = st.radio(
            "2. Trong giờ tự học hoặc thời gian rảnh, hoạt động nào khiến em cảm thấy say mê nhất?",
            [
                "A. Lắp ráp, sửa chữa đồ dùng, làm thí nghiệm hoặc vận động thể chất (Holland R - Thực tế).",
                "B. Đọc tài liệu, tìm hiểu nguyên lý sâu xa của các hiện tượng, nghiên cứu logic (Holland I - Nghiên cứu).",
                "C. Viết lách, vẽ tranh, thiết kế, dựng video, sáng tạo nội dung (Holland A - Nghệ thuật).",
                "D. Trò chuyện tâm sự, giúp đỡ bạn bè giải tỏa khúc mắc, lắng nghe tâm tư (Holland S - Xã hội)."
            ]
        )

        q3 = st.radio(
            "3. Khi đứng trước một quyết định quan trọng (như chọn khối thi lớp 10 lên 11), em căn cứ vào điều gì nhất?",
            [
                "A. Mục tiêu nghề nghiệp tương lai mang lại thu nhập và vị thế cao.",
                "B. Điểm số các môn học thực tế và khả năng logic của bản thân.",
                "C. Cảm xúc, niềm đam mê cá nhân và mong muốn sống đúng với chính mình.",
                "D. Lời khuyên định hướng từ thầy cô giáo và sự an tâm của cha mẹ."
            ]
        )

        q4 = st
