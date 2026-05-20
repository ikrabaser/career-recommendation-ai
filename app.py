import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pypdf import PdfReader

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


st.set_page_config(page_title="AI Kariyer Danışmanı", page_icon="🎯", layout="wide")


def html(kod):
    temiz_kod = " ".join(kod.split())
    st.markdown(temiz_kod, unsafe_allow_html=True)


def pdf_metni_cikar(yuklenen_dosya):
    reader = PdfReader(yuklenen_dosya)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "

    return text.lower()


def yetenekleri_cikar(text, skill_pool):
    bulunan_yetenekler = []

    for skill in skill_pool:
        if skill.lower() in text:
            bulunan_yetenekler.append(skill)

    return list(set(bulunan_yetenekler))


def yetenek_frekansi_hesapla(text, skill_pool):
    skill_scores = {}

    for skill in skill_pool:
        count = text.lower().count(skill.lower())
        if count > 0:
            skill_scores[skill] = count

    return skill_scores


def cv_uyum_skoru_hesapla(eslesen_yetenekler, gerekli_yetenekler):
    if len(gerekli_yetenekler) == 0:
        return 0

    score = (len(eslesen_yetenekler) / len(gerekli_yetenekler)) * 100
    return round(score)


def pdf_rapor_olustur(tahmin, guven, eslesen_yetenekler, eksik_yetenekler, cv_skoru):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    c = canvas.Canvas(temp_file.name, pagesize=letter)

    c.setFont("Helvetica-Bold", 22)
    c.drawString(50, 750, "AI Kariyer Danismani Raporu")

    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Onerilen Kariyer Alani: {tahmin}")
    c.drawString(50, 690, f"Model Guven Orani: {guven}%")
    c.drawString(50, 670, f"CV Uyum Skoru: {cv_skoru}/100")

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, 630, "Eslesen Yetenekler:")
    y = 610

    c.setFont("Helvetica", 12)
    for skill in eslesen_yetenekler:
        c.drawString(70, y, f"- {skill}")
        y -= 20

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y - 10, "Gelistirilmesi Gereken Yetenekler:")
    y -= 30

    c.setFont("Helvetica", 12)
    for skill in eksik_yetenekler:
        c.drawString(70, y, f"- {skill}")
        y -= 20

    c.save()
    return temp_file.name


st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(124,58,237,0.12), transparent 32%),
        radial-gradient(circle at top right, rgba(37,99,235,0.10), transparent 30%),
        #f6f7fb;
}

.block-container {
    max-width: 1240px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stSidebar"] {
    display: none;
}

.hero {
    background: linear-gradient(135deg, #0f172a 0%, #312e81 55%, #7c3aed 100%);
    padding: 58px;
    border-radius: 34px;
    color: white;
    box-shadow: 0 28px 80px rgba(49, 46, 129, 0.32);
    margin-bottom: 34px;
}

.badge {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.24);
    padding: 9px 16px;
    border-radius: 999px;
    font-size: 14px;
    margin-bottom: 20px;
}

.hero h1 {
    font-size: 56px !important;
    color: white !important;
    margin-bottom: 18px;
    line-height: 1.05;
}

.hero p {
    max-width: 800px;
    font-size: 18px;
    color: #e5e7eb;
}

.feature-pill {
    display: inline-block;
    background: rgba(255,255,255,0.13);
    border: 1px solid rgba(255,255,255,0.18);
    padding: 10px 14px;
    border-radius: 14px;
    font-size: 14px;
    margin-right: 8px;
    margin-top: 8px;
}

.card {
    background: rgba(255, 255, 255, 0.88);
    border: 1px solid rgba(124, 58, 237, 0.14);
    border-radius: 30px;
    padding: 32px;
    box-shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
    margin-bottom: 24px;
    backdrop-filter: blur(14px);
    transition: all 0.25s ease;
    outline: 1px solid rgba(255,255,255,0.65);
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 30px 90px rgba(79, 70, 229, 0.16);
    border-color: rgba(124, 58, 237, 0.28);
}

.panel-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8f7ff 100%);
    border: 1px solid rgba(124, 58, 237, 0.16);
    border-radius: 30px;
    padding: 30px;
    box-shadow: 0 24px 70px rgba(15, 23, 42, 0.10);
    margin-bottom: 24px;
}

.result-title {
    font-size: 40px;
    font-weight: 900;
    color: #111827;
    margin: 8px 0 8px 0;
}

.result-label {
    font-size: 13px;
    color: #64748b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .08em;
}

.stat-number {
    font-size: 30px;
    font-weight: 900;
    color: #312e81;
}

.stat-label {
    color: #64748b;
    font-weight: 700;
    font-size: 13px;
}

.skill-pill {
    display: inline-block;
    background: #eef2ff;
    color: #3730a3;
    padding: 9px 13px;
    border-radius: 999px;
    margin: 5px;
    font-weight: 700;
}

.missing-pill {
    display: inline-block;
    background: #fff1f2;
    color: #be123c;
    padding: 9px 13px;
    border-radius: 999px;
    margin: 5px;
    font-weight: 700;
}

.roadmap-item {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 16px;
    border-radius: 18px;
    margin-bottom: 12px;
    color: #374151;
}

.project-box {
    background: linear-gradient(135deg, #eef2ff, #f5f3ff);
    border: 1px solid #ddd6fe;
    padding: 22px;
    border-radius: 22px;
    color: #312e81;
    font-weight: 700;
}

.placeholder-box {
    background: linear-gradient(135deg, #f8fafc, #eef2ff);
    border: 1px dashed rgba(99,102,241,0.35);
    border-radius: 26px;
    padding: 32px;
    color: #475569;
}

.stTextInput label {
    display: none;
}

.stTextInput input {
    height: 54px;
    border-radius: 16px;
    border: 1px solid #d1d5db;
    padding: 0 16px;
    font-size: 16px;
}

.stButton button {
    height: 52px;
    border-radius: 16px;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white;
    border: none;
    font-weight: 800;
    padding: 0 24px;
    box-shadow: 0 16px 35px rgba(79,70,229,0.25);
}

.stButton button:hover {
    color: white;
    transform: translateY(-1px);
}

[data-testid="stFileUploader"] {
    background: rgba(248,250,252,0.9);
    border-radius: 20px;
    padding: 12px;
    border: 1px solid rgba(226,232,240,0.9);
}
</style>
""", unsafe_allow_html=True)


html("""
<div class="hero">
    <div class="badge">Yapay Zeka Destekli Kariyer Öneri Platformu</div>
    <h1>Teknoloji kariyer yolunu keşfet.</h1>
    <p>
        AI Kariyer Danışmanı teknik yeteneklerini analiz eder, CV içinden becerileri çıkarır,
        sana en uygun kariyer alanını tahmin eder ve kişiselleştirilmiş öğrenme yol haritası oluşturur.
    </p>
    <div>
        <span class="feature-pill">🤖 Makine Öğrenmesi Tahmini</span>
        <span class="feature-pill">📄 CV Beceri Çıkarımı</span>
        <span class="feature-pill">📊 Kariyer Analitiği</span>
        <span class="feature-pill">🧭 Öğrenme Yol Haritası</span>
    </div>
</div>
""")


training_data = [
    ("python machine learning deep learning tensorflow keras pandas numpy ai", "Yapay Zeka Mühendisi"),
    ("python pytorch computer vision opencv neural networks data science", "Yapay Zeka Mühendisi"),
    ("nlp transformers bert text classification python machine learning", "Yapay Zeka Mühendisi"),

    ("python sql excel power bi tableau pandas data analysis visualization", "Veri Analisti"),
    ("sql excel dashboard reporting statistics pandas business intelligence", "Veri Analisti"),
    ("data cleaning data visualization python matplotlib analysis", "Veri Analisti"),

    ("unity c# game design oop animation physics level design", "Oyun Geliştirici"),
    ("unity c# 3d game development player movement collision ui", "Oyun Geliştirici"),
    ("c# unity vr ar game mechanics scene management", "Oyun Geliştirici"),

    ("python linux network cybersecurity cryptography log analysis ids", "Siber Güvenlik Analisti"),
    ("penetration testing network security linux python firewall malware", "Siber Güvenlik Analisti"),
    ("cybersecurity threat detection incident response siem log monitoring", "Siber Güvenlik Analisti"),

    ("python flask django api database sql backend rest git", "Backend Geliştirici"),
    ("nodejs api server database authentication backend development", "Backend Geliştirici"),
    ("flask python rest api postgresql docker git backend", "Backend Geliştirici"),
]

df = pd.DataFrame(training_data, columns=["skills", "career"])

model = Pipeline([
    ("vectorizer", CountVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(df["skills"], df["career"])


career_details = {
    "Yapay Zeka Mühendisi": {
        "skills": ["python", "machine learning", "deep learning", "tensorflow", "pytorch", "opencv", "pandas", "numpy"],
        "description": "Yapay zeka modelleri geliştirir, veriler üzerinde model eğitir ve tahmin sistemleri oluşturur.",
        "project": "Görüntü işleme tabanlı nesne tanıma veya NLP tabanlı metin sınıflandırma projesi geliştirebilirsin."
    },
    "Veri Analisti": {
        "skills": ["python", "sql", "excel", "pandas", "power bi", "tableau", "statistics", "data visualization"],
        "description": "Verileri analiz eder, görselleştirir ve karar destek süreçleri için raporlar üretir.",
        "project": "Satış verisi analizi, öğrenci başarı dashboard'u veya finansal veri görselleştirme projesi yapabilirsin."
    },
    "Oyun Geliştirici": {
        "skills": ["unity", "c#", "game design", "oop", "animation", "physics", "ui", "vr"],
        "description": "Oyun motorlarıyla sahne, karakter, mekanik ve etkileşimli sistemler geliştirir.",
        "project": "Unity ile 3D mini oyun, VR fobi terapisi simülasyonu veya karakter kontrol sistemi geliştirebilirsin."
    },
    "Siber Güvenlik Analisti": {
        "skills": ["python", "linux", "network", "cybersecurity", "cryptography", "log analysis", "ids", "web security"],
        "description": "Sistemleri güvenlik açısından analiz eder, saldırı tespiti ve zafiyet incelemesi yapar.",
        "project": "Python ile log analizi yapan mini IDS veya basit web güvenlik tarayıcı sistemi geliştirebilirsin."
    },
    "Backend Geliştirici": {
        "skills": ["python", "flask", "django", "api", "database", "sql", "git", "docker"],
        "description": "Sunucu tarafı uygulamalar, API sistemleri ve veri tabanı bağlantıları geliştirir.",
        "project": "Flask/Django ile REST API tabanlı görev takip veya kullanıcı kimlik doğrulama sistemi yapabilirsin."
    }
}

all_skills = sorted(set(
    skill
    for details in career_details.values()
    for skill in details["skills"]
))

extra_skills = [
    "java", "c++", "javascript", "typescript",
    "go", "rust", "php", "swift", "kotlin",
    "opencv", "nlp", "computer vision", "transformers", "llm",
    "react", "next.js", "node.js", "fastapi",
    "html", "css", "mongodb", "postgresql",
    "kubernetes", "aws", "azure", "firebase",
    "unreal engine", "blender",
    "penetration testing", "wireshark", "metasploit", "network security"
]

all_skills.extend(extra_skills)
all_skills = sorted(list(set(all_skills)))


left_panel, right_panel = st.columns([1, 2], gap="large")

with left_panel:
    html("""
    <div class="panel-card">
        <div class="result-label">Giriş Paneli</div>
        <h2>CV yükle veya yetenek gir</h2>
        <p>CV dosyanı yükleyerek veya teknik yeteneklerini manuel yazarak kariyer analizi oluşturabilirsin.</p>
    </div>
    """)

    uploaded_cv = st.file_uploader("CV Yükle (PDF)", type=["pdf"])

    skills_input = st.text_input(
        "Yetenekler",
        placeholder="Python, SQL, Unity, Machine Learning, Git, C#"
    )

    cv_skills = []
    skill_scores = {}

    if uploaded_cv is not None:
        cv_text = pdf_metni_cikar(uploaded_cv)
        cv_skills = yetenekleri_cikar(cv_text, all_skills)
        skill_scores = yetenek_frekansi_hesapla(cv_text, all_skills)

        if cv_skills:
            st.success("CV içinden bulunan beceriler:")
            st.write(", ".join(cv_skills))

            if skill_scores:
                skill_score_df = pd.DataFrame(
                    skill_scores.items(),
                    columns=["Yetenek", "Geçme Sayısı"]
                ).sort_values(by="Geçme Sayısı", ascending=False)

                st.markdown("#### 🔥 CV İçindeki Öne Çıkan Beceriler")
                st.dataframe(skill_score_df.head(8), use_container_width=True)
        else:
            st.warning("CV içinde tanımlı yetenek listesinden eşleşme bulunamadı.")

    analyze_button = st.button("Kariyer Yolunu Analiz Et", use_container_width=True)


with right_panel:
    if not analyze_button:
        html("""
        <div class="placeholder-box">
            <div class="result-label">Kariyer Analiz Paneli</div>
            <h2>Analiz sonuçların burada görüntülenecek</h2>
            <p>
                CV yükle veya teknik yeteneklerini gir. Analiz sonrasında önerilen kariyer alanı,
                CV uyum skoru, eksik beceriler, öğrenme yol haritası ve proje önerileri burada yer alacak.
            </p>
        </div>
        """)
    else:
        combined_skills = skills_input

        if cv_skills:
            combined_skills += ", " + ", ".join(cv_skills)

        if combined_skills.strip() == "":
            st.warning("Lütfen birkaç yetenek gir veya CV yükle.")
        else:
            cleaned_input = combined_skills.lower().replace(",", " ")

            prediction = model.predict([cleaned_input])[0]
            probabilities = model.predict_proba([cleaned_input])[0]
            classes = model.classes_

            probability_table = pd.DataFrame({
                "Kariyer Alanı": classes,
                "Olasılık": probabilities
            }).sort_values(by="Olasılık", ascending=False)

            confidence = probability_table.iloc[0]["Olasılık"]
            confidence_percent = round(confidence * 100)

            required_skills = set(career_details[prediction]["skills"])
            user_skills = set(
                skill.strip().lower()
                for skill in combined_skills.split(",")
                if skill.strip()
            )

            matched_skills = required_skills & user_skills
            missing_skills = required_skills - user_skills
            cv_score = cv_uyum_skoru_hesapla(matched_skills, required_skills)

            coverage = round((len(matched_skills) / len(required_skills)) * 100)

            if cv_score < 30:
                readiness = "Başlangıç"
            elif cv_score < 60:
                readiness = "Gelişiyor"
            elif cv_score < 80:
                readiness = "İyi Seviye"
            else:
                readiness = "Hazır"

            learning_time = max(1, len(missing_skills) * 2)

            career_power = round(
                (len(matched_skills) * 15) +
                (confidence_percent * 0.5)
            )

            career_power = min(career_power, 100)

            matched_html = "".join(
                f"<span class='skill-pill'>{skill}</span>"
                for skill in matched_skills
            ) or "<p>Doğrudan eşleşen beceri bulunamadı.</p>"

            missing_html = "".join(
                f"<span class='missing-pill'>{skill}</span>"
                for skill in missing_skills
            )

            roadmap_html = ""
            for index, skill in enumerate(missing_skills, start=1):
                roadmap_html += f"""
                <div class="roadmap-item">
                    <b>Adım {index}</b><br>
                    <b>{skill}</b> öğren ve bununla ilgili küçük bir proje geliştir.
                </div>
                """

            if roadmap_html == "":
                roadmap_html = "<div class='roadmap-item'>Temel becerilerin bu kariyer alanı için güçlü görünüyor.</div>"

            pdf_path = pdf_rapor_olustur(
                prediction,
                confidence_percent,
                matched_skills,
                missing_skills,
                cv_score
            )

            html(f"""
            <div class="card">
                <div class="result-label">Önerilen Kariyer Alanı</div>
                <div class="result-title">{prediction}</div>
                <p>{career_details[prediction]["description"]}</p>
            </div>
            """)

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                html(f"""
                <div class="card">
                    <div class="stat-number">{confidence_percent}%</div>
                    <div class="stat-label">Model Güven Oranı</div>
                </div>
                """)

            with c2:
                html(f"""
                <div class="card">
                    <div class="stat-number">{len(matched_skills)}</div>
                    <div class="stat-label">Eşleşen Beceri</div>
                </div>
                """)

            with c3:
                html(f"""
                <div class="card">
                    <div class="stat-number">{len(missing_skills)}</div>
                    <div class="stat-label">Eksik Beceri</div>
                </div>
                """)

            with c4:
                html(f"""
                <div class="card">
                    <div class="stat-number">{cv_score}/100</div>
                    <div class="stat-label">CV Uyum Skoru</div>
                </div>
                """)

            c5, c6, c7, c8 = st.columns(4)

            with c5:
                html(f"""
                <div class="card">
                    <div class="stat-number">{coverage}%</div>
                    <div class="stat-label">Skill Coverage</div>
                </div>
                """)

            with c6:
                html(f"""
                <div class="card">
                    <div class="stat-number">{learning_time} Ay</div>
                    <div class="stat-label">Tahmini Öğrenme Süresi</div>
                </div>
                """)

            with c7:
                html(f"""
                <div class="card">
                    <div class="stat-number">{career_power}/100</div>
                    <div class="stat-label">Kariyer Güç Skoru</div>
                </div>
                """)

            with c8:
                html(f"""
                <div class="card">
                    <div class="stat-number">{readiness}</div>
                    <div class="stat-label">Hazırlık Seviyesi</div>
                </div>
                """)

            s1, s2 = st.columns(2)

            with s1:
                html(f"""
                <div class="card">
                    <h3>✅ Eşleşen Beceriler</h3>
                    {matched_html}
                </div>
                """)

            with s2:
                html(f"""
                <div class="card">
                    <h3>📚 Geliştirmen Gereken Beceriler</h3>
                    {missing_html}
                </div>
                """)

            html(f"""
            <div class="card">
                <h3>🧭 Kişiselleştirilmiş Öğrenme Yol Haritası</h3>
                {roadmap_html}
            </div>
            """)

            html(f"""
            <div class="card">
                <h3>💡 Portfolyo Proje Önerisi</h3>
                <div class="project-box">{career_details[prediction]["project"]}</div>
            </div>
            """)

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📄 Kariyer Raporunu İndir",
                    data=pdf_file,
                    file_name="kariyer_raporu.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            html("""
            <div class="card">
                <h3>📊 Kariyer Olasılık Analizi</h3>
            </div>
            """)

            fig = px.bar(
                probability_table,
                x="Kariyer Alanı",
                y="Olasılık",
                text=probability_table["Olasılık"].apply(lambda x: f"{x:.2f}"),
                color="Olasılık",
                color_continuous_scale=["#2563eb", "#7c3aed", "#a855f7"]
            )

            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(size=14, color="#111827"),
                coloraxis_showscale=False,
                xaxis_title="",
                yaxis_title="Olasılık"
            )

            fig.update_traces(
                marker_line_width=0,
                textposition="outside"
            )

            st.plotly_chart(fig, use_container_width=True)