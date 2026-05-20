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


@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


model = load_model()


career_data = [
    {
        "role": "AI / Machine Learning Engineer",
        "description": "Python, machine learning, deep learning, TensorFlow, PyTorch, data analysis, model training, artificial intelligence, neural networks",
        "skills": "Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, Data Science"
    },
    {
        "role": "Data Scientist",
        "description": "data analysis, statistics, pandas, numpy, visualization, machine learning, predictive modeling, business intelligence",
        "skills": "Python, Pandas, NumPy, Statistics, Visualization, Machine Learning"
    },
    {
        "role": "Backend Developer",
        "description": "server side development, APIs, databases, authentication, Flask, Django, Node.js, SQL, REST API, backend systems",
        "skills": "Python, Flask, Django, SQL, REST API, Authentication"
    },
    {
        "role": "Frontend Developer",
        "description": "user interface, web design, React, JavaScript, HTML, CSS, responsive design, frontend development",
        "skills": "HTML, CSS, JavaScript, React, UI Design"
    },
    {
        "role": "Cybersecurity Specialist",
        "description": "network security, ethical hacking, penetration testing, cryptography, authentication, vulnerability analysis, secure systems",
        "skills": "Cybersecurity, Network Security, Cryptography, Penetration Testing"
    },
    {
        "role": "Game Developer",
        "description": "Unity, C#, game mechanics, 2D games, 3D games, player movement, physics, game design, interactive systems",
        "skills": "Unity, C#, Game Design, Physics, OOP"
    },
    {
        "role": "VR / AR Developer",
        "description": "virtual reality, augmented reality, Unity, immersive environments, simulation, interaction design, therapy simulation, 3D development",
        "skills": "Unity, VR, AR, C#, 3D Simulation, Interaction Design"
    },
    {
        "role": "Software Engineer",
        "description": "software development, algorithms, data structures, object oriented programming, problem solving, system design, clean code",
        "skills": "Algorithms, Data Structures, OOP, Software Design, Problem Solving"
    }
]


roadmaps = {
    "AI / Machine Learning Engineer": [
        "Python Temelleri",
        "NumPy & Pandas",
        "Makine Öğrenmesi",
        "Deep Learning",
        "TensorFlow / PyTorch",
        "MLOps & Deployment"
    ],
    "Data Scientist": [
        "Python",
        "Pandas & NumPy",
        "Veri Analizi",
        "İstatistik",
        "Veri Görselleştirme",
        "Machine Learning"
    ],
    "Backend Developer": [
        "Python / Node.js",
        "REST API",
        "Flask / Django",
        "Authentication",
        "Database Yönetimi",
        "Deployment"
    ],
    "Frontend Developer": [
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "Responsive Design",
        "Frontend Optimization"
    ],
    "Cybersecurity Specialist": [
        "Networking",
        "Linux",
        "Cryptography",
        "Web Security",
        "Penetration Testing",
        "Ethical Hacking"
    ],
    "Game Developer": [
        "C#",
        "Unity",
        "Game Physics",
        "Animation Systems",
        "Game Optimization",
        "Multiplayer Systems"
    ],
    "VR / AR Developer": [
        "Unity",
        "C#",
        "3D Development",
        "XR Interaction Toolkit",
        "VR Optimization",
        "Immersive Experience Design"
    ],
    "Software Engineer": [
        "Algorithms",
        "Data Structures",
        "OOP",
        "System Design",
        "Testing",
        "Software Architecture"
    ]
}


career_df = pd.DataFrame(career_data)
career_embeddings = model.encode(career_df["description"].tolist())


skill_keywords = [
    "Python", "Java", "C#", "C++", "JavaScript", "HTML", "CSS",
    "React", "Node.js", "Flask", "Django", "SQL", "PostgreSQL",
    "MongoDB", "Streamlit", "Machine Learning", "Deep Learning",
    "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
    "Data Analysis", "Data Science", "NLP", "Computer Vision",
    "Cybersecurity", "Cryptography", "Penetration Testing",
    "Unity", "Game Development", "VR", "AR", "Git", "GitHub",
    "Docker", "Kubernetes", "API", "REST API", "OOP", "Algorithms",
    "Data Structures"
]


def extract_skills(text):
    found_skills = []
    lower_text = text.lower()

    for skill in skill_keywords:
        if skill.lower() in lower_text:
            found_skills.append(skill)

    return sorted(set(found_skills))


def generate_pdf_report(detected_skills, results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("AI Career Recommendation Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    skill_text = ", ".join(detected_skills) if detected_skills else "No specific skills detected."

    elements.append(
        Paragraph(f"<b>Detected Skills:</b> {skill_text}", styles["BodyText"])
    )
    elements.append(Spacer(1, 20))

    for _, row in results.iterrows():
        score = round(row["similarity_score"] * 100, 2)
        roadmap = roadmaps.get(row["role"], [])
        roadmap_text = "<br/>".join([f"• {step}" for step in roadmap])

        elements.append(Paragraph(f"<b>{row['role']}</b>", styles["Heading2"]))
        elements.append(Paragraph(f"Compatibility Score: %{score}", styles["BodyText"]))
        elements.append(Spacer(1, 10))
        elements.append(
            Paragraph(
                f"<b>Learning Roadmap:</b><br/>{roadmap_text}",
                styles["BodyText"]
            )
        )
        elements.append(Spacer(1, 25))

    doc.build(elements)
    buffer.seek(0)

    return buffer


st.markdown("""
<style>
.hero {
    padding: 45px;
    border-radius: 25px;
    background: linear-gradient(135deg, #1e3a8a, #7c3aed);
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.card {
    padding: 24px;
    border-radius: 18px;
    background-color: #f8fafc;
    color: #0f172a;
    margin-bottom: 18px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.12);
}

.score {
    font-size: 20px;
    font-weight: bold;
    color: #2563eb;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <h1>🎯 Career Recommendation AI</h1>
    <p>Semantic NLP & Embedding Based Career Recommendation System</p>
</div>
""", unsafe_allow_html=True)


st.write(
    "Bu uygulama, kullanıcının yazdığı yetenek ve ilgi alanlarını NLP embedding modeliyle analiz eder "
    "ve en uygun kariyer alanlarını benzerlik skoruna göre önerir."
)


col1, col2 = st.columns([1, 1])


with col1:
    st.subheader("📝 Profil Bilgilerini Gir")

    uploaded_file = st.file_uploader(
        "CV PDF dosyanı yükle",
        type=["pdf"]
    )

    user_input = st.text_area(
        "Yeteneklerini, ilgi alanlarını veya proje deneyimlerini yaz:",
        height=220,
        placeholder="Örnek: Python, Streamlit, machine learning, Unity, C#, cybersecurity, data analysis..."
    )

    top_n = st.slider(
        "Kaç kariyer önerisi gösterilsin?",
        1,
        5,
        3
    )

    analyze_button = st.button("🚀 Kariyer Önerisi Oluştur")


with col2:
    st.subheader("💡 Örnek Girdi")

    st.info(
        "Python ile projeler geliştiriyorum. Streamlit, makine öğrenmesi, "
        "veri analizi ve yapay zeka alanlarına ilgim var. Ayrıca Unity ve C# "
        "ile VR tabanlı simülasyon projeleri üzerinde çalışıyorum."
    )


if analyze_button:

    extracted_text = ""

    if uploaded_file is not None:

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        reader = PdfReader(tmp_path)

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + " "

        st.success("CV başarıyla analiz edildi.")

        with st.expander("📄 CV'den Çıkarılan Metni Göster"):
            st.write(extracted_text[:2000])

    final_input = user_input + " " + extracted_text

    if final_input.strip() == "":
        st.warning("Lütfen analiz için metin gir veya CV yükle.")

    else:
        detected_skills = extract_skills(final_input)

        if detected_skills:
            st.subheader("🔍 Tespit Edilen Teknik Yetenekler")
            st.write(" | ".join(detected_skills))

        user_embedding = model.encode([final_input])
        similarities = cosine_similarity(user_embedding, career_embeddings)[0]

        career_df["similarity_score"] = similarities

        results = career_df.sort_values(
            by="similarity_score",
            ascending=False
        ).head(top_n)

        st.markdown("---")
        st.subheader("🎯 En Uygun Kariyer Önerileri")

        for _, row in results.iterrows():
            score_percent = round(row["similarity_score"] * 100, 2)

            st.markdown(f"""
            <div class="card">
                <h3>{row["role"]}</h3>
                <p class="score">Uyumluluk Skoru: %{score_percent}</p>
                <p><b>Öne Çıkan Yetenekler:</b> {row["skills"]}</p>
                <p><b>Açıklama:</b> Bu alan, girdiğin yetenek ve ilgi alanlarıyla semantik olarak yüksek benzerlik göstermektedir.</p>
            </div>
            """, unsafe_allow_html=True)

            roadmap = roadmaps.get(row["role"], [])

            if roadmap:
                st.markdown("### 🛣️ Öğrenme Yol Haritası")

                for step_no, step in enumerate(roadmap, start=1):
                    st.write(f"{step_no}. {step}")

        st.subheader("📊 Kariyer Uyum Skorları")

        chart_data = results[["role", "similarity_score"]].copy()
        chart_data["similarity_score"] = chart_data["similarity_score"] * 100

        fig = px.bar(
            chart_data,
            x="similarity_score",
            y="role",
            orientation="h",
            text=chart_data["similarity_score"].round(2),
            labels={
                "similarity_score": "Uyumluluk Skoru (%)",
                "role": "Kariyer Alanı"
            }
        )

        fig.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="inside"
        )

        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        pdf_buffer = generate_pdf_report(
            detected_skills,
            results
        )

        st.download_button(
            label="📄 AI Kariyer Raporunu İndir",
            data=pdf_buffer,
            file_name="career_report.pdf",
            mime="application/pdf"
        )


st.markdown("---")

st.caption(
    "Developed with Streamlit, Sentence Transformers and Scikit-learn | "
    "NLP Embedding Based Career Recommendation System"
)
