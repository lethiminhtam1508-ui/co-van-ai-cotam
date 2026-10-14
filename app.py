import os
import time
import streamlit as st
from google import genai
from google.genai import types

# Cấu hình trang
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# Tùy biến CSS: Đổi font chữ và làm gọn khối thu âm bên phải
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
    /* Tối ưu kích thước nút audio input cho vừa vặn */
    div[data-testid="stAudioInput"] {
        margin-top: 0px;
        padding-top: 0px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
client = genai.Client(api_key=api_key) if api_key else None

if not client:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Streamlit Secrets.")

# 2. Khung tiêu đề chính có màu nền nổi bật
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
    st.markdown("### 💡 **Trò chuyện trực tiếp cùng Cô Tâm**")
    st.markdown("**Em có thể gõ chữ hoặc bấm nút Micro ở góc phải để tâm sự cùng cô nhé!**")

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

    # BỐ TRÍ Ô CHAT VÀ NÚT MICRO NẰM NGANG NHAU (GÓC PHẢI)
    col_input, col_voice = st.columns([0.72, 0.28])
    with col_input:
        user_msg = st.chat_input("Nhập băn khoăn của em tại đây...")
    with col_voice:
        recorded_voice = st.audio_input("Nói (Micro)", label_visibility="collapsed")

    prompt_to_run = None
    audio_bytes_data = None

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
                    except Exception:
                        prompt_to_run = "Em vừa gửi một đoạn ghi âm tâm sự nhưng âm thanh nghe chưa rõ."

            if prompt_to_run:
                st.session_state.messages.append({"role": "user", "content": f"🎙️ {prompt_to_run}" if audio_bytes_data else prompt_to_run})
                with st.chat_message("user"):
                    st.markdown(f"🎙️ *{prompt_to_run}*" if audio_bytes_data else prompt_to_run)

                with st.chat_message("assistant"):
                    with st.spinner("Cô Tâm đang suy ngẫm câu trả lời cho em..."):
                        recent_msgs = st.session_state.messages[-4:]
                        history_str = "\n".join([f"{item['role']}: {item['content']}" for item in recent_msgs])
                        full_context = f"{system_prompt}\n\nLỊCH SỬ ĐỐI THOẠI:\n{history_str}\n\nHọc sinh vừa nói: {prompt_to_run}\n\nCô Tâm phản hồi:"

                        answer = None
                        last_err = ""
                        for m_name in ["gemini-3.5-flash-lite", "gemini-3.8-flash"]:
                            for attempt in range(2):
                                try:
                                    resp = client.models.generate_content(
                                        model=m_name,
                                        contents=full_context,
                                    )
                                    answer = resp.text
                                    break
                                except Exception as e:
                                    last_err = str(e)
                                    if "503" in last_err:
                                        time.sleep(1.5)
                                        continue
                                    break
                            if answer:
                                break

                        if not answer:
                            answer = f"Hệ thống máy chủ đang bận xử lý ({last_err}). Em vui lòng thử bấm gửi lại nhé!"

                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})

# ==========================================
# TAB 2: TRẮC NGHIỆM TỐ CHẤT
# ==========================================
with tab2:
    st.markdown("### 🧩 **Khám phá Tố chất & Phong cách Làm việc**")
    st.markdown("**Trả lời 4 câu hỏi trắc nghiệm tình huống dưới đây để nhận diện bức tranh tổng quan về bản thân:**")

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

        q4 = st.radio(
            "4. Khi gặp một thất bại (ví dụ: điểm thi thử không như mong đợi), phản ứng đầu tiên của em là gì?",
            [
                "A. Quyết tâm học bù ngay lập tức để lấy lại phong độ ở lần sau.",
                "B. Tìm bạn bè hoặc thầy cô để tâm sự và tìm kiếm sự động viên.",
                "C. Khép mình lại, cảm thấy tự ti và lo lắng một thời gian.",
                "D. Ngồi rà soát lại từng lỗi sai trong bài thi để tìm nguyên nhân cụ thể."
            ]
        )

        submitted = st.form_submit_button("Tổng hợp kết quả & Gửi sang Cô Tâm tư vấn")

    if submitted:
        st.success("✅ Đã ghi nhận câu trả lời của em!")
        st.info(
            f"**Tóm tắt dữ liệu tố chất:**\n"
            f"- Phong cách hành động: {q1.split('.')[0]}\n"
            f"- Xu hướng sở thích: {q2.split('.')[0]}\n"
            f"- Xu hướng ra quyết định: {q3.split('.')[0]}\n"
            f"- Phản ứng trước biến cố: {q4.split('.')[0]}\n\n"
            "👉 Hãy quay lại **Tab Khung Cố Vấn** và gõ câu hỏi vào ô chat để nhận phản hồi chi tiết từ Cô Tâm nhé!"
        )

# ==========================================
# TAB 3: SỔ TAY HƯỚNG NGHIỆP
# ==========================================
with tab3:
    st.markdown("### 📖 **Triết Lý Khai Vấn & Công Thức Thành Công**")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("""
        ### 🌟 Công thức Vàng: $E + R = O$
        * **$E$ (Event - Sự kiện):** Những điều xảy ra khách quan ngoài tầm kiểm soát của em (đề thi, hoàn cảnh gia đình, xu hướng thị trường thay đổi).
        * **$R$ (Response - Phản ứng):** Thái độ, tư duy và hành động chủ động của em trước sự việc.
        * **$O$ (Outcome - Kết quả):** Tương lai thực tế mà em nhận được.
        
        > *"Chúng ta không thể thay đổi hướng gió ($E$), nhưng hoàn toàn có thể điều chỉnh cánh buồm ($R$) để cập bến mong muốn ($O$)."*
        """)

    with col_r:
        st.markdown("""
        ### 🪜 Lộ trình Bậc thang 30 ngày chuyển hóa
        * **Tuần 1 (Thấu hiểu bản thân):** Hoàn thành bài trắc nghiệm DISC & Holland, viết ra 3 điểm mạnh nhất và 2 điểm chưa tự tin.
        * **Tuần 2 (Khảo sát thực tế nghề nghiệp):** Phỏng vấn hoặc tìm hiểu sâu về 2 nghề em đang quan tâm (công việc hàng ngày, yêu cầu tuyển dụng).
        * **Tuần 3 (Rèn luyện Kỹ năng bù trừ):** Tập trung cải thiện 1 kỹ năng bổ trợ còn thiếu (kỹ năng thuyết trình, kỹ năng quản lý thời gian).
        * **Tuần 4 (Xác lập cam kết hành động):** Viết bản cam kết mục tiêu học tập năm học và kế hoạch rèn luyện gửi cho cô chủ nhiệm/cố vấn.
        """)
