import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
from io import BytesIO

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet



st.set_page_config(
    page_title="Career Recommendation AI",
    page_icon="🎯",
    layout="wide"
)



st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.stButton>button {
    background: linear-gradient(90deg, #6a11cb, #2575fc);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: scale(1.03);
    opacity: 0.95;
}

.card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 18px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

</style>
""", unsafe_allow_html=True)



model = SentenceTransformer('all-MiniLM-L6-v2')



career_data = {
    "AI / Machine Learning Engineer": {
        "skills": "Python Machine Learning Deep Learning TensorFlow PyTorch NLP Data Science",
        "roadmap": [
            "Python Temelleri",
            "NumPy & Pandas",
            "Makine Öğrenmesi",
            "Deep Learning",
            "TensorFlow / PyTorch",
            "MLOps & Deployment"
        ]
    },

    "Data Scientist": {
        "skills": "Python Pandas NumPy Statistics Visualization Machine Learning",
        "roadmap": [
            "Python",
            "Pandas & NumPy",
            "Veri Analizi",
            "İstatistik",
            "Veri Görselleştirme",
            "Machine Learning"
        ]
    },

    "Game Developer": {
        "skills": "Unity C# Game Design Physics OOP",
        "roadmap": [
            "C#",
            "Unity",
            "Game Physics",
            "Animation Systems",
            "Game Optimization",
            "Multiplayer Systems"
        ]
    },

    "Software Engineer": {
        "skills": "Algorithms Data Structures OOP Software Design Problem Solving",
        "roadmap": [
            "Algorithms",
            "Data Structures",
            "OOP",
            "System Design",
            "Testing",
            "Software Architecture"
        ]
    },

    "VR / AR Developer": {
        "skills": "Unity VR AR C# 3D Simulation Interaction Design",
        "roadmap": [
            "Unity",
            "C#",
            "3D Development",
            "XR Interaction Toolkit",
            "VR Optimization",
            "Immersive Experience Design"
        ]
    }
}



def extract_text_from_pdf(uploaded_file):
    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:
        text += page.extract_text()

    return text



def create_pdf_report(results):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    title = Paragraph(
        "AI Career Recommendation Report",
        styles['Title']
    )

    story.append(title)
    story.append(Spacer(1, 20))

    for career, score in results:

        text = f"""
        <b>{career}</b><br/>
        Uyum Skoru: %{score:.2f}
        """

        paragraph = Paragraph(text, styles['BodyText'])

        story.append(paragraph)
        story.append(Spacer(1, 12))

    doc.build(story)

    buffer.seek(0)

    return buffer



st.markdown("""
<div style="
padding: 40px;
border-radius: 25px;
background: linear-gradient(90deg,#1e3c72,#7b2ff7);
text-align:center;
color:white;
margin-bottom:30px;
">

<h1 style="font-size:55px;">🎯 Career Recommendation AI</h1>

<h4>
Semantic NLP & Embedding Based Career Recommendation System
</h4>

</div>
""", unsafe_allow_html=True)

st.write("""
Bu uygulama, kullanıcının yazdığı yetenek ve ilgi alanlarını NLP embedding modeliyle analiz eder ve en uygun kariyer alanlarını benzerlik skoruna göre önerir.
""")



col1, col2 = st.columns([2, 2])

with col1:

    st.subheader("📝 Profil Bilgilerini Gir")

    uploaded_file = st.file_uploader(
        "CV PDF dosyanı yükle",
        type=["pdf"]
    )

    user_input = st.text_area(
        "Yeteneklerini, ilgi alanlarını veya proje deneyimlerini yaz:",
        height=180,
        placeholder="Örnek: Python, Streamlit, machine learning, Unity, C#, cybersecurity..."
    )

    top_n = st.slider(
        "Kaç kariyer önerisi gösterilsin?",
        1,
        5,
        3
    )

with col2:

    st.subheader("💡 Örnek Girdi")

    st.info("""
Python ile projeler geliştiriyorum. Streamlit, makine öğrenmesi,
veri analizi ve yapay zeka alanlarına ilgim var.
Ayrıca Unity ve C# ile VR tabanlı simülasyon projeleri üzerinde çalışıyorum.
""")



pdf_text = ""

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)

combined_text = user_input + " " + pdf_text



if st.button("🚀 Kariyer Önerisi Oluştur"):

    if combined_text.strip() == "":
        st.warning("Lütfen bir metin gir veya CV yükle.")
        st.stop()

    user_embedding = model.encode([combined_text])

    scores = []

    detected_skills = []

    for career, info in career_data.items():

        career_embedding = model.encode([info["skills"]])

        similarity = cosine_similarity(
            user_embedding,
            career_embedding
        )[0][0]

        scores.append((career, similarity * 100))

        for skill in info["skills"].split():
            if skill.lower() in combined_text.lower():
                detected_skills.append(skill)

    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )

    top_results = scores[:top_n]

   
    st.markdown("---")

    st.subheader("🔎 Tespit Edilen Teknik Yetenekler")

    unique_skills = sorted(set(detected_skills))

    if unique_skills:
        st.write(" | ".join(unique_skills))
    else:
        st.write("Belirgin teknik yetenek tespit edilemedi.")

  

    st.markdown("---")

    st.subheader("🎯 En Uygun Kariyer Önerileri")

    for career, score in top_results:

        st.markdown(
            f"""
            <div class="card">

            <h2>{career}</h2>

            <h4 style="color:#2563eb;">
            Uyumluluk Skoru: %{score:.2f}
            </h4>

            <p>
            <b>Öne Çıkan Yetenekler:</b>
            {career_data[career]["skills"]}
            </p>

            <p>
            <b>Açıklama:</b>
            Bu alan, girdiğin yetenek ve ilgi alanlarıyla
            semantik olarak yüksek benzerlik göstermektedir.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("🗺️ Öğrenme Yol Haritası")

        for i, step in enumerate(career_data[career]["roadmap"], start=1):
            st.write(f"{i}. {step}")

   

    st.markdown("---")

    st.subheader("📊 Kariyer Uyum Skorları")

    df = pd.DataFrame(
        top_results,
        columns=["Kariyer Alanı", "Uyumluluk Skoru"]
    )

    fig = px.bar(
        df,
        x="Uyumluluk Skoru",
        y="Kariyer Alanı",
        orientation="h",
        text="Uyumluluk Skoru"
    )

    fig.update_layout(height=500)

    st.plotly_chart(fig, use_container_width=True)


    pdf_buffer = create_pdf_report(top_results)

    st.download_button(
        label="📄 AI Kariyer Raporunu İndir",
        data=pdf_buffer,
        file_name="career_report.pdf",
        mime="application/pdf"
    )


st.markdown("---")

st.caption(
    "Developed with Streamlit, SentenceTransformers and Scikit-learn | "
    "NLP Embedding Based Career Recommendation System"
)
