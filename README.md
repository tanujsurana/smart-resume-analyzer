# Smart Resume Analyzer 🚀

An AI-powered resume analysis app built with **Streamlit**, **spaCy**, and **pdfminer.six**.  
It extracts user details from resumes, identifies skills, assigns a score, and provides recommendations.  

## ✨ Features
- Extracts **Name, Email, Phone, Skills, Page Count**
- Resume Scoring based on key sections (Summary, Experience, Projects, Certifications)
- User & Admin modes
- Skill & Course recommendations
- Interactive analytics with Plotly

## 🛠️ Tech Stack
- Python, Streamlit
- spaCy (NLP), Regex
- pdfminer.six (PDF parsing)
- MySQL (Database)
- Plotly (Charts)

## 🚀 Run Locally
```bash
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
streamlit run app.py
