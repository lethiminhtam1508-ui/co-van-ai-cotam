import streamlit as st
import os
from google import genai
from google.genai import types

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Advanced settings -> Secrets trên Streamlit Cloud.")

# 2. Tiêu đề ứng dụng
st.title("🧭 Trợ Lý Cố Vấn Hướng Nghiệp AI - Cô Tâm")
st.caption("Đồng hành cùng học sinh THPT Phan Đăng Lưu trên Hành trình Kiến tạo Tương lai | Phương pháp Khai vấn Sư phạm")

# 3. Phân chia các Tab chức năng
tab1, tab2, tab3 = st.tabs(["💬 Khung Cố Vấn Khai Vấn", "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", "📜 Sổ Tay & Lộ Trình 30 Ngày"])

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN (AI CHATBOT)
# ==========================================
with tab1:
    st.subheader("Trò chuyện trực tiếp cùng Cô Tâm")
    st.write("Em đang băn khoăn về chọn khối thi, chọn ngành, mâu thuẫn giữa sở thích và năng lực, hay áp lực từ gia đình? Hãy chia sẻ với cô nhé!")

    # Gợi ý câu hỏi nhanh
    st.markdown("**Gợi ý câu hỏi nhanh:**")
    col_a, col_b, col_c = st.columns(3)
    goi_y = ""
    if col_a.button("Em muốn làm IT nhưng tính lại hướng nội, sợ giao tiếp?"):
        goi_y = "Em muốn học ngành Công nghệ Thông tin nhưng tính em rất hướng nội và ngại giao tiếp, kết quả trắc nghiệm ra nhóm Trầm tĩnh (S). Liệu em có làm được không cô?"
    if col_b.button("Bố mẹ muốn em thi Sư phạm nhưng em thích Kinh doanh?"):
        goi_y = "Gia đình muốn em thi khối ngành Sư phạm cho ổn định, nhưng em lại đam mê kinh doanh và khởi nghiệp. Em đang rất bối rối không biết nên chọn thế nào?"
    if col_c.button("Em học lực khá, chưa biết mình thực sự thích ngành gì?"):
        goi_y = "Em đang học lớp 11, học lực ở mức khá nhưng chưa thực sự thấy mình nổi trội môn nào hay đam mê ngành gì cụ thể. Cô giúp em định hướng với ạ!"

    # Lưu lịch sử chat
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Chào em! Cô là cô giáo Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp tại Trường THPT Phan Đăng Lưu.\n\n"
                    "Cô luôn tin rằng mỗi học sinh đều sở hữu những thế mạnh và tố chất riêng biệt. "
                    "Dù em đang phân vân chọn khối thi, chọn ngành hay gặp khó khăn trong việc thấu hiểu bản thân, cô luôn sẵn sàng lắng nghe.\n\n"
                    "Em đang trăn trở điều gì nhất lúc này?"
                )
            }
        ]

    # Hiển thị lịch sử chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Xử lý khi có câu hỏi mới
    user_input = st.chat_input("Nhập băn khoăn của em về ngành nghề, chọn khối, định hướng tương lai...")
    prompt_to_send = user_input or (goi_y if goi_y and ("last_quick" not in st.session_state or st.session_state.last_quick != goi_y) else None)

    if prompt_to_send:
        if goi_y:
            st.session_state.last_quick = goi_y

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
                    Bạn đóng vai một chuyên gia khai vấn và người cô đồng hành tận tâm, ấm áp, sâu sắc và khoa học.

                    QUY TRÌNH KHAI VẤN BẮT BUỘC (Tuân thủ đúng 4 bước trong mọi câu trả lời tư vấn):
                    - Bước 1: Thấu cảm & Giải tỏa tâm lý: Thấu hiểu nỗi lo lắng, bối rối của học sinh cấp 3 trước ngưỡng cửa chọn trường/chọn nghề. Khẳng định cảm xúc đó là hoàn toàn tự nhiên.
                    - Bước 2: Bóc tách nghịch lý tố chất (Giao thoa DISC & Holland): Phân tích xem mâu thuẫn của học sinh nằm ở đâu (ví dụ: nhóm S thích công nghệ, nhóm A muốn theo kinh tế...).
                    - Bước 3: Đề xuất Kỹ năng bù trừ (Compensatory Skills): Chỉ ra rằng tố chất không phải là định mệnh; hoàn toàn có thể rèn luyện các kỹ năng bổ trợ để khắc phục điểm yếu và tối ưu thế mạnh.
                    - Bước 4: Lộ trình hành động vi mô 30 ngày (Công thức E + R = O):
                      + Giải thích ngắn gọn: Event (Sự kiện) + Response (Phản ứng của em) = Outcome (Kết quả).
                      + Đưa ra 3-4 hành động cụ thể, làm được ngay trong 30 ngày tới.

                    Phong cách giao tiếp: Xưng "cô" và gọi "em". Giọng văn sư phạm mực thước, gần gũi, khích lệ và giàu năng lượng tích cực.
                    """

                    full_context = f"{system_prompt}\n\nHọc sinh chia sẻ: {prompt_to_send}"
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.0-flash",
                            contents=full_context,
                        )
                        reply = response.text
                        st.markdown(reply)
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.error(f"Đã xảy ra lỗi khi kết nối với AI: {e}")

# ==========================================
# TAB 2: TRẮC NGHIỆM TỐ CHẤT (DISC & HOLLAND)
# ==========================================
with tab2:
    st.subheader("Khám phá Tố chất & Phong cách Làm việc")
    st.write("Trả lời 4 câu hỏi trắc nghiệm tình huống dưới đây để nhận diện bức tranh tổng quan về bản thân:")

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
            "👉 Hãy quay lại **Tab Khung Cố Vấn** và gõ: *'Cô ơi, em vừa làm trắc nghiệm với kết quả [A/B/C/D], nhờ cô phân tích giúp em lộ trình phù hợp!'* để nhận phản hồi chi tiết từ Cô Tâm nhé!"
        )

# ==========================================
# TAB 3: SỔ TAY HƯỚNG NGHIỆP & LỘ TRÌNH 30 NGÀY
# ==========================================
with tab3:
    st.subheader("Triết Lý Khai Vấn & Công Thức Thành Công")

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
