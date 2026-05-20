import streamlit as st

st.set_page_config(
    page_title="AI Career Advisor",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Career Advisor")
st.write("Yeteneklerine göre kariyer alanı öneren, eksik becerilerini analiz eden ve sana öğrenme yolu çıkaran akıllı danışman.")

skills_input = st.text_input(
    "Yeteneklerini virgülle ayırarak yaz:",
    placeholder="Python, SQL, Unity, Machine Learning, Git, C#"
)

career_paths = {
    "AI Engineer": {
        "skills": ["python", "machine learning", "deep learning", "tensorflow", "pandas", "numpy", "opencv"],
        "description": "Yapay zeka modelleri geliştirir, veriyle çalışır ve makine öğrenimi çözümleri üretir.",
        "project": "Görüntü işleme tabanlı nesne tanıma veya NLP tabanlı metin sınıflandırma projesi geliştirebilirsin."
    },
    "Data Analyst": {
        "skills": ["python", "sql", "excel", "pandas", "power bi", "data visualization"],
        "description": "Verileri analiz eder, raporlar hazırlar ve karar destek süreçlerine katkı sağlar.",
        "project": "Kaggle veri setiyle satış analizi dashboard'u veya öğrenci başarı analizi yapabilirsin."
    },
    "Game Developer": {
        "skills": ["unity", "c#", "game design", "oop", "animation", "ui"],
        "description": "Unity veya benzeri oyun motorlarıyla oyun mekanikleri, sahneler ve etkileşimli sistemler geliştirir.",
        "project": "Unity ile küçük bir 3D kaçış oyunu veya VR fobi terapisi simülasyonu geliştirebilirsin."
    },
    "Cybersecurity Analyst": {
        "skills": ["python", "linux", "network", "cybersecurity", "cryptography", "log analysis"],
        "description": "Sistemleri saldırılara karşı analiz eder, güvenlik açıklarını inceler ve tehdit tespiti yapar.",
        "project": "Python ile log analizi yapan veya şüpheli girişleri tespit eden mini IDS projesi yapabilirsin."
    },
    "Backend Developer": {
        "skills": ["python", "flask", "sql", "api", "git", "database"],
        "description": "Sunucu tarafı uygulamalar, API sistemleri ve veri tabanı bağlantıları geliştirir.",
        "project": "Flask ile kullanıcı giriş sistemi veya REST API tabanlı görev takip uygulaması geliştirebilirsin."
    }
}

if st.button("Kariyer Önerisi Al"):

    if skills_input.strip() == "":
        st.warning("Lütfen en az birkaç yetenek gir.")
    else:
        user_skills = [skill.strip().lower() for skill in skills_input.split(",")]

        results = {}

        for career, data in career_paths.items():
            required_skills = set(data["skills"])
            matched_skills = set(user_skills) & required_skills
            missing_skills = required_skills - set(user_skills)

            match_rate = round((len(matched_skills) / len(required_skills)) * 100)

            results[career] = {
                "matched": matched_skills,
                "missing": missing_skills,
                "match_rate": match_rate
            }

        best_career = max(results, key=lambda career: results[career]["match_rate"])
        best_result = results[best_career]

        st.success(f"En uygun kariyer alanın: {best_career}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Uyum Oranı", f"%{best_result['match_rate']}")

        with col2:
            st.metric("Eşleşen Beceri", len(best_result["matched"]))

        with col3:
            st.metric("Eksik Beceri", len(best_result["missing"]))

        st.progress(best_result["match_rate"] / 100)

        st.subheader("📌 Kariyer Açıklaması")
        st.write(career_paths[best_career]["description"])

        left, right = st.columns(2)

        with left:
            st.subheader("✅ Eşleşen Yeteneklerin")
            if best_result["matched"]:
                for skill in best_result["matched"]:
                    st.write(f"- {skill}")
            else:
                st.write("Henüz doğrudan eşleşen yetenek bulunamadı.")

        with right:
            st.subheader("📚 Geliştirmen Gereken Yetenekler")
            for skill in best_result["missing"]:
                st.write(f"- {skill}")

        st.subheader("🧭 Önerilen Öğrenme Yolu")

        for index, skill in enumerate(best_result["missing"], start=1):
            st.write(f"{index}. {skill} öğren")

        st.subheader("💡 Sana Uygun Proje Önerisi")
        st.info(career_paths[best_career]["project"])

        st.subheader("📊 Tüm Kariyer Alanları Uyum Skoru")

        for career, result in results.items():
            st.write(f"**{career}** - %{result['match_rate']}")
            st.progress(result["match_rate"] / 100)