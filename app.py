import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

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

career_df = pd.DataFrame(career_data)

career_embeddings = model.encode(career_df["description"].tolist())

st.markdown("""
<style>
.main {
    background-color: #0f172a;
}

.hero {
    padding: 35px;
    border-radius: 25px;
    background: linear-gradient(135deg, #1e3a8a, #7c3aed);
    color: white;
    text-align: center;
    margin-bottom: 30px;
}

.card {
    padding: 22px;
    border-radius: 18px;
    background-color: #f8fafc;
    color: #0f172a;
    margin-bottom: 15px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.12);
}

.score {
    font-size: 22px;
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

    user_input = st.text_area(
        "Yeteneklerini, ilgi alanlarını veya proje deneyimlerini yaz:",
        height=220,
        placeholder="Örnek: Python, Streamlit, machine learning, Unity, C#, cybersecurity, data analysis..."
    )

    top_n = st.slider("Kaç kariyer önerisi gösterilsin?", 1, 5, 3)

    analyze_button = st.button("🚀 Kariyer Önerisi Oluştur")

with col2:
    st.subheader("💡 Örnek Girdi")

    st.info(
        "Python ile projeler geliştiriyorum. Streamlit, makine öğrenmesi, "
        "veri analizi ve yapay zeka alanlarına ilgim var. Ayrıca Unity ve C# "
        "ile VR tabanlı simülasyon projeleri üzerinde çalışıyorum."
    )

if analyze_button:
    if user_input.strip() == "":
        st.warning("Lütfen analiz için bir metin gir.")
    else:
        user_embedding = model.encode([user_input])
        similarities = cosine_similarity(user_embedding, career_embeddings)[0]

        career_df["similarity_score"] = similarities
        results = career_df.sort_values(by="similarity_score", ascending=False).head(top_n)

        st.markdown("---")
        st.subheader("🎯 En Uygun Kariyer Önerileri")

        for index, row in results.iterrows():
            score_percent = round(row["similarity_score"] * 100, 2)

            st.markdown(f"""
            <div class="card">
                <h3>{row["role"]}</h3>
                <p class="score">Uyumluluk Skoru: %{score_percent}</p>
                <p><b>Öne Çıkan Yetenekler:</b> {row["skills"]}</p>
                <p><b>Açıklama:</b> Bu alan, girdiğin yetenek ve ilgi alanlarıyla semantik olarak yüksek benzerlik göstermektedir.</p>
            </div>
            """, unsafe_allow_html=True)

        st.subheader("📊 Skor Tablosu")
        chart_data = results[["role", "similarity_score"]].copy()
        chart_data["similarity_score"] = chart_data["similarity_score"] * 100
        st.bar_chart(chart_data.set_index("role"))

st.markdown("---")

st.caption(
    "Developed with Streamlit, Sentence Transformers and Scikit-learn | "
    "NLP Embedding Based Career Recommendation System"
)
