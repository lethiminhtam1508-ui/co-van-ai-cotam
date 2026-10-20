import streamlit as st
import os
import time
import pandas as pd
from datetime import datetime
from google import genai
from google.genai import types

# Cấu hình giao diện Streamlit
st.set_page_config(
    page_title="Cố Vấn Hướng Nghiệp AI - Cô Tâm",
    page_icon="🧭",
    layout="wide"
)

# Đường dẫn file lưu trữ dữ liệu
DATA_FILE = "lich_su_tu_van.csv"

def init_data_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=["Thoi_Gian", "Loai_Hoat_Dong", "Noi_Dung_Hoi", "Phan_Hoi_AI_Ket_Qua"])
        df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")

def save_interaction(loai_hoat_dong, noi_dung, phan_hoi):
    init_data_file()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{
        "Thoi_Gian": now_str,
        "Loai_Hoat_Dong": loai_hoat_dong,
        "Noi_Dung_Hoi": noi_dung,
        "Phan_Hoi_AI_Ket_Qua": phan_hoi
    }])
    new_row.to_csv(DATA_FILE, mode="a", header=False, index=False, encoding="utf-8-sig")

init_data_file()

# 1. Khởi tạo kết nối Gemini API
api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    st.warning("⚠️ Chưa tìm thấy GEMINI_API_KEY trong Advanced settings -> Secrets trên Streamlit Cloud.")

# 2. Tiêu đề ứng dụng
st.markdown("""
<div style="background: linear-gradient(135deg, #e0f2fe 0%, #ede9fe 100%); 
            padding: 20px 24px; 
            border-radius: 14px; 
            border-left: 7px solid #1d4ed8; 
            margin-bottom: 22px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
    <h2 style="color: #1e3a8a; margin: 0 0 6px 0; font-weight: 900; font-size: 25px;">
        🧭 Trợ Lý Cố Vấn Hướng Nghiệp AI - Cô Tâm
    </h2>
    <p style="color: #334155; margin: 0; font-weight: 700; font-size: 14.5px;">
        Trường THPT Phan Đăng Lưu | Đồng hành khai vấn & kiến tạo tương lai cùng học sinh
    </p>
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

# ==========================================
# KHU VỰC QUẢN TRỊ DÀNH RIÊNG CHO CÔ GIÁO (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("🔐 Dành Cho Giáo Viên")
    admin_password = st.text_input("Nhập mật khẩu quản trị để xem dữ liệu HS:", type="password")
    
    if admin_password == "cotam2026":
        st.success("✅ Đã xác thực quyền giáo viên!")
        if os.path.exists(DATA_FILE):
            df_history = pd.read_csv(DATA_FILE)
            st.metric("Tổng lượt tương tác/câu hỏi", len(df_history))
            st.dataframe(df_history, use_container_width=True)
            
            csv_data = df_history.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
            st.download_button(
                label="📥 Tải dữ liệu về máy (Excel/CSV)",
                data=csv_data,
                file_name="lich_su_hoc_sinh_hoi_co_tam.csv",
                mime="text/csv"
            )
        else:
            st.info("Chưa có câu hỏi nào được ghi nhận.")
    elif admin_password:
        st.error("Mật khẩu chưa đúng!")

# 3. Phân chia các Tab chức năng
tab1, tab2, tab3 = st.tabs([
    "💬 Khung Cố Vấn Khai Vấn", 
    "📊 Trắc Nghiệm Tố Chất (DISC & Holland)", 
    "📜 Sổ Tay & Lộ Trình 30 Ngày"
])

goi_y = ""

# ==========================================
# TAB 1: KHUNG CỐ VẤN KHAI VẤN (AI CHATBOT)
# ==========================================
with tab1:
    st.subheader("Trò chuyện trực tiếp cùng Cô Tâm")
    st.write("Em đang băn khoăn về chọn khối thi, chọn ngành, mâu thuẫn giữa sở thích và năng lực, hay áp lực từ gia đình? Hãy chia sẻ với cô nhé!")

    st.markdown("**Gợi ý tình huống nhanh:**")
    col_a, col_b, col_c = st.columns(3)
    if col_a.button("Em muốn học IT nhưng tính hướng nội, sợ giao tiếp?"):
        goi_y = "Em muốn học ngành Công nghệ Thông tin nhưng tính em rất hướng nội và ngại giao tiếp, kết quả trắc nghiệm ra nhóm Trầm tĩnh (S). Liệu em có theo được không cô?"
    if col_b.button("Bố mẹ muốn em thi Sư phạm, em lại thích Kinh doanh?"):
        goi_y = "Gia đình muốn em thi Sư phạm cho ổn định, nhưng em lại thích kinh doanh khởi nghiệp. Em đang rất khó xử không biết chọn thế nào ạ?"
    if col_c.button("Em học lực khá, chưa biết mình thích ngành gì?"):
        goi_y = "Em đang học lớp 11, học lực ở mức khá nhưng chưa thực sự thấy mình nổi trội môn nào hay đam mê ngành gì cụ thể. Cô giúp em với ạ!"

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
        tom_tat = (
            f"Phong cách hành động: {q1.split('.')[0]} | "
            f"Xu hướng sở thích: {q2.split('.')[0]} | "
            f"Ra quyết định: {q3.split('.')[0]} | "
            f"Phản ứng biến cố: {q4.split('.')[0]}"
        )
        st.info(
            f"**Tóm tắt dữ liệu tố chất:**\n"
            f"- Phong cách hành động: {q1.split('.')[0]}\n"
            f"- Xu hướng sở thích: {q2.split('.')[0]}\n"
            f"- Xu hướng ra quyết định: {q3.split('.')[0]}\n"
            f"- Phản ứng trước biến cố: {q4.split('.')[0]}\n\n"
            "👉 Hãy quay lại **Tab Khung Cố Vấn** và gõ câu hỏi vào ô chat phía dưới để nhận phản hồi chi tiết từ Cô Tâm nhé!"
        )
        save_interaction("Trắc nghiệm DISC & Holland", "Học sinh nộp kết quả test", tom_tat)

# ==========================================
# TAB 3: SỔ TAY HƯỚNG NGHIỆP & LỘ TRÌNH 30 NGÀY
# ==========================================
with tab3:
    st.subheader("Triết Lý Khai Vấn & Công Thức Thành Công")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
        ### 🌟 Công thức Vàng: $E + R = O$
        - **$E$ (Event - Sự kiện):** Những điều xảy ra khách quan ngoài tầm kiểm soát của em (đề thi, hoàn cảnh gia đình, xu hướng thị trường thay đổi).
        - **$R$ (Response - Phản ứng):** Thái độ, tư duy và hành động chủ động của em trước sự việc.
        - **$O$ (Outcome - Kết quả):** Tương lai thực tế mà em nhận được.
        
        > *"Chúng ta không thể thay đổi hướng gió ($E$), nhưng hoàn toàn có thể điều chỉnh cánh buồm ($R$) để cập bến mong muốn ($O$)."*
        """)
    with col_r:
        st.markdown("""
        ### 🪜 Lộ trình Bậc thang 30 ngày chuyển hóa
        - **Tuần 1 (Thấu hiểu bản thân):** Hoàn thành bài trắc nghiệm DISC & Holland, viết ra 3 điểm mạnh nhất và 2 điểm chưa tự tin.
        - **Tuần 2 (Khảo sát thực tế nghề nghiệp):** Phỏng vấn hoặc tìm hiểu sâu về 2 nghề em đang quan tâm (công việc hàng ngày, yêu cầu tuyển dụng).
        - **Tuần 3 (Rèn luyện Kỹ năng bù trừ):** Tập trung cải thiện 1 kỹ năng bổ trợ còn thiếu (kỹ năng thuyết trình, kỹ năng quản lý thời gian).
        - **Tuần 4 (Xác lập cam kết hành động):** Viết bản cam kết mục tiêu học tập năm học và kế hoạch rèn luyện gửi cho cô chủ nhiệm/cố vấn.
        """)

# ==========================================
# Ô NHẬP LIỆU GHIM DƯỚI ĐÁY TRÌNH DUYỆT
# ==========================================
user_input = st.chat_input("Nhập băn khoăn của em về chọn ngành, chọn khối thi...")
prompt_to_send = user_input or (goi_y if goi_y and ("last_quick" not in st.session_state or st.session_state.last_quick != goi_y) else None)

if prompt_to_send:
    if goi_y:
        st.session_state.last_quick = goi_y

    st.session_state.messages.append({"role": "user", "content": prompt_to_send})

    if not client:
        st.error("Chưa kết nối được với AI (Thiếu API Key). Vui lòng cấu hình Secrets trên Streamlit Cloud.")
    else:
        system_prompt = """
        Bạn là cô giáo Lê Thị Minh Tâm, phụ trách Hoạt động Trải nghiệm, Hướng nghiệp (HĐTN, HN) tại Trường THPT Phan Đăng Lưu, Huế.
        Bạn là người CÔ ĐỒNG HÀNH & CHUYÊN GIA KHAI VẤN (COACHING) CHỈ CHUYÊN SÂU VỀ HƯỚNG NGHIỆP VÀ TÂM LÝ LỨA TUỔI HỌC ĐƯỜNG.

        GIỚI HẠN PHẠM VI NGHIÊM NGẶT (SCOPE BOUNDARY):
        - BẠN CHỈ TƯ VẤN: Chọn ngành, chọn khối thi, thấu hiểu tính cách/sở thích (DISC, Holland), giải tỏa áp lực học tập/gia đình, phương pháp học tập chung và kế hoạch hành động 30 ngày (E + R = O).
        - TUYỆT ĐỐI TỪ CHỐI: Giải bài tập cụ thể của các môn học (như giải bài tập Toán, Lý, Hóa, Văn, tích vô hướng, đạo hàm...), viết văn hộ, giải bài tập về nhà, hoặc các chủ đề phiếm ngoài học đường.
        - KHI HỌC SINH HỎI NGOÀI PHẠM VI: Hãy mỉm cười từ chối một cách duyên dáng, chuẩn mực sư phạm. Nhắc em rằng đây là không gian dành riêng cho Hướng nghiệp và Khám phá bản thân; khuyên em nên hỏi thầy cô bộ môn trên lớp hoặc tự tư duy làm bài, sau đó khéo léo hỏi lại xem em có cần cô hỗ trợ gì về mục tiêu nghề nghiệp hay phương pháp phân bổ thời gian học môn đó không.

        NGUYÊN TẮC KHAI VẤN:
        1. Tuyệt đối không liệt kê tiêu đề "Bước 1, Bước 2, Bước 3, Bước 4".
        2. Độ dài: Ngắn gọn, ấm áp (khoảng 2-3 đoạn ngắn, dưới 200 từ).
        3. Thấu cảm cảm xúc -> Đưa ra góc nhìn sâu sắc -> Luôn kết thúc bằng 1 đến 2 câu hỏi gợi mở để học sinh tự soi chiếu.
        4. Xưng hô: "cô" - "em". Ngôn từ mực thước sư phạm xứ Huế, tình cảm, tinh tế.
        """

        conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])
        full_context = f"{system_prompt}\n\nLỊCH SỬ ĐỐI THOẠI:\n{conversation_history}\n\nHọc sinh vừa nói: {prompt_to_send}\n\nCô Tâm phản hồi:"

        candidate_models = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]
        reply = None
        last_error = ""

        for model_name in candidate_models:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_context,
                    )
                    reply = response.text
                    break
                except Exception as e:
                    last_error = str(e)
                    if "503" in last_error:
                        time.sleep(1.5)
                        continue
                    break
            if reply:
                break

        if not reply:
            reply = f"Hệ thống máy chủ đang bận xử lý một chút ({last_error}). Em vui lòng thử bấm gửi lại nhé!"

        st.session_state.messages.append({"role": "assistant", "content": reply})
        save_interaction("Tư vấn trực tiếp Chatbot", prompt_to_send, reply)
        st.rerun()
