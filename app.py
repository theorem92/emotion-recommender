from dotenv import load_dotenv
import os
import streamlit as st
from vertexai.generative_models import GenerativeModel, Part
import vertexai

# .env 파일 불러오기
load_dotenv()

# 환경변수 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
vertexai.init(project=os.getenv("PROJECT_ID"), location=os.getenv("LOCATION"))

# Streamlit 페이지 설정
st.set_page_config(page_title="감성 콘텐츠 추천", layout="centered")

# --- 🎨 스타일 적용 (회색 배경 제거) ---
st.markdown("""
    <style>
    .stApp {
        font-family: "Pretendard", sans-serif;
        padding: 2rem;
    }
    .stTextArea textarea {
        border-radius: 0.75rem;
        padding: 1rem;
        border: 1px solid #CBD5E1;
    }
    .stButton > button {
        background-color: #3182F6;
        color: white;
        font-weight: 600;
        font-size: 16px;
        padding: 0.8rem 1.4rem;
        border-radius: 0.75rem;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background-color: #1E62D0;
    }
    .stFileUploader {
        background-color: white;
        border: 2px dashed #CBD5E1;
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 타이틀 영역 ---
st.markdown("## 📮 소소한 일상으로 부터의 편지")
st.markdown("짧은 일상을 올려주시면 AI가 어울리는 콘텐츠를 추천해드려요 💌")

# --- 입력영역 ---
uploaded_file = st.file_uploader("사진 또는 영상을 업로드하세요", type=["jpg", "jpeg", "png", "mp4"])
user_text = st.text_area("어떤 내용이 담겨있는 영상인가요?", placeholder="예) 오늘은 강아지랑 공원에서 산책했어요.", height=150)

# --- 버튼 배치 ---
st.markdown("### ")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    submit = st.button("💌 추천받기", use_container_width=True)

# --- 처리 로직 ---
if submit:
    if not uploaded_file:
        st.warning("🖼️ 사진이나 영상을 업로드해 주세요. 그렇지 않으면 좋은 콘텐츠를 추천드리기 어려워요.")
    elif not user_text.strip():
        st.warning("✏️ 영상/사진에 대한 간단한 설명을 입력해 주세요.")
    else:
        file_path = f"temp_{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 업로드된 파일 보여주기
        st.markdown("---")
        if uploaded_file.type.startswith("image/"):
            st.image(file_path, caption="업로드한 이미지", use_container_width=True)
            mime_type = uploaded_file.type
        elif uploaded_file.type == "video/mp4":
            st.video(file_path, format="video/mp4")
            mime_type = "video/mp4"
        else:
            st.error("지원하지 않는 파일 형식입니다.")
            os.remove(file_path)
            st.stop()

        st.info("✨ 분석 중입니다... 잠시만 기다려주세요.")

        try:
            model = GenerativeModel("gemini-2.0-flash")
            with open(file_path, "rb") as f:
                file_data = f.read()
            file_part = Part.from_data(data=file_data, mime_type=mime_type)

            prompt = f"""
이 정보를 바탕으로 따뜻한 감성 편지를 써주세요.

- 내용은 업로드된 사진과 영상을 먼저 풍부하게 묘사해주시고,
- 여기에 어울리는 실제 도서 1권과 현재 영화관에서 상영 중인 영화 1편을 추천해주세요.
- 도서명과 영화명, 저자와 감독 등의 정보는 반드시 실제 존재하는 정보로 제공해주세요.
- 추천 문구는 총 2~3문단 정도, 존댓말로 작성해주세요.

[고객 입력 설명]: {user_text}
"""

            response = model.generate_content([file_part, prompt])
            st.success("💌 편지가 도착했어요!")
            st.markdown("---")
            st.markdown(response.text)
            st.markdown("---")

        except Exception as e:
            st.error(f"Gemini 분석 중 오류가 발생했습니다: {e}")

        os.remove(file_path)
