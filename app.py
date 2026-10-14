import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Cấu hình trang web
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# Tùy biến CSS: Đổi font chữ và in đậm tiêu đề phụ
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800;900&display=swap');
    html, body, [class*="css"] {
        font-family: 'Be Vietnam Pro', sans-serif;
    }
    .stSubheader {
        font-weight: 800 !important;
        color: #1e3a8a !important;
    }
</style>
""", unsafe_allow_html=True)

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
client = genai.Client(api_key=api_key) if api_key else None

if not client:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")

# 2. Khung tiêu đề chính có màu nền nổi bật
header_html = """
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
"""
st.markdown(header_html, unsafe_allow_html=True)

# 3. Khởi tạo lịch sử cuộc trò chuyện
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

# 4. Các Tab chức năng
tab1, tab2, tab3 = st.tabs([
    "💬 Khung Cố Vấn Khai Vấn", 
    "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", 
    "📜 Sổ Tay & Lộ Trình 30 Ngày"
])

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN
# ==========================================
with tab1:
    st.subheader("💡 Trò chuyện trực tiếp cùng Cô Tâm")
    st.markdown("**Em có thể gõ phím hoặc bấm nút Micro 🎙️ phía dưới để nói trực tiếp cùng cô nhé!**")

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

    # Khung thu âm giọng nói (Micro)
    st.write("---")
    recorded_voice = st.audio_input("🎙️ Bấm nút micro để nói (học sinh chia sẻ trực tiếp bằng giọng nói):")
    
    # Ô nhập văn bản truyền thống
    user_msg = st.chat_input("Hoặc nhập băn khoăn của em bằng văn bản tại đây...")

    prompt_to_run = None
    audio_bytes_data = None

    # Ưu tiên nhận diện giọng nói nếu học sinh vừa thu âm
    if recorded_voice is not None:
        raw_audio = recorded_voice.read()
        audio_id = hash(raw_audio)
        if "last_audio_id" not in st.session_state or st.session_state.last_audio_id != audio_id:
            st.session_state.last_audio_id = audio_id
            audio_bytes_data = raw_audio
    elif user_msg:
        prompt_to_run = user_msg
    elif quick_text:
        prompt_to_run = quick_text

    # Xử lý khi có câu hỏi (bằng giọng nói hoặc chữ viết)
    if audio_bytes_data is not None or prompt_to_run:
        if not client:
            st.error("Chưa kết nối được với AI (Thiếu API Key).")
        else:
            system_prompt = (
                "Bạn là cô giáo Lê Thị Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp (HĐTN, HN) tại Trường THPT Phan Đăng Lưu, Huế. "
                "Bạn là người CÔ ĐỒNG HÀNH & CHUYÊN GIA KHAI VẤN (COACHING) CHỈ CHUYÊN SÂU VỀ HƯỚNG NGHIỆP VÀ TÂM LÝ LỨA TUỔI HỌC ĐƯỜNG.\n\n"
                "GIỚI HẠN PHẠM VI NGHIÊM NGẶT:\n"
                "- BẠN CHỈ TƯ VẤN: Chọn ngành, chọn khối thi, thấu hiểu tính cách/sở thích (DISC, Holland), giải tỏa áp lực học tập/gia đình, phương pháp học tập chung và kế hoạch hành động 30 ngày (E + R = O).\n"
                "- TUYỆT ĐỐI TỪ CHỐI: Giải bài tập cụ thể của các môn học (như giải bài tập Toán, Lý, Hóa, Văn, tích vô hướng, đạo hàm...), viết văn hộ, giải bài tập về nhà, hoặc các chủ đề phiếm ngoài học đường.\n"
                "- KHI HỌC SINH HỎI NGOÀI PHẠM VI: Hãy mỉm cười từ chối một cách duyên dáng, chuẩn mực sư phạm. Nhắc em rằng đây là không gian dành riêng cho Hướng nghiệp và Khám phá bản thân; khuyên em nên trao đổi với thầy cô bộ môn, sau đó khéo léo hỏi lại xem em có cần cô hỗ trợ gì về mục tiêu nghề nghiệp hay quản lý thời gian không.\n\n"
                "NGUYÊN TẮC KHAI VẤN:\n"
                "1. Tuyệt đối không liệt kê tiêu đề Bước 1, Bước 2, Bước 3, Bước 4.\n"
                "2. Độ dài: Ngắn gọn, ấm áp (khoảng 2-3 đoạn ngắn, dưới 200 từ).\n"
                "3. Thấu cảm cảm xúc -> Đưa ra góc nhìn sâu sắc -> Luôn kết thúc bằng 1 đến 2 câu hỏi gợi mở để học sinh tự soi chiếu và trả lời.\n"
                "4. Xưng hô: cô - em. Ngôn từ mực thước sư phạm xứ Huế, tình cảm, tinh tế."
            )

            # Nếu là giọng nói: Nhận diện giọng nói sang chữ trước
            if audio_bytes_data is not None:
                with st.spinner("Đang lắng nghe giọng nói của em..."):
                    try:
                        trans_resp = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=[
                                "Hãy ghi lại chính xác từng lời tiếng Việt mà học sinh vừa nói trong đoạn âm thanh này. Chỉ xuất ra nội dung lời nói, không giải thích gì thêm:",
                                types.Part.from_bytes(data=audio_bytes_data, mime_type="audio/wav")
                            ]
                        )
                        prompt_to_run = trans_resp.text.strip()
                    except Exception as ex:
                        prompt_to_run = "Em vừa gửi một đoạn ghi âm tâm sự nhưng âm thanh nghe chưa rõ."

            if prompt_to_run:
                st.session_state
