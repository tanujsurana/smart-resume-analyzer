import re
import spacy
from pdfminer.high_level import extract_text

nlp = spacy.load("en_core_web_sm")

# Define a list of skills (expand as you wish)
SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Redux",
    "Node.js", "Express", "Tailwind", "Bootstrap", "SQL", "Docker",
    "AWS", "Firebase", "GitHub Actions", "CI/CD", "scikit-learn",
    "TensorFlow", "Keras", "RESTful APIs", "JWT", "Agile", "Scrum",
    "Unit Testing", "Integration Testing", "Accessibility", "WCAG",
    "Git", "Postman", "JIRA", "MongoDB", "FastAPI", "Kubernetes"
]

def extract_resume_details(file_path):
    """Extracts basic details and skills from a resume PDF"""
    text = extract_text(file_path)

    # Extract email
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    email = email.group(0) if email else None

    # Extract phone number
    phone = re.search(r'\+?\d[\d -]{8,}\d', text)
    phone = phone.group(0) if phone else None

    # Use spaCy for name detection
    doc = nlp(text)
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break

    # Extract skills
    found_skills = []
    for skill in SKILLS:
        if re.search(rf"\b{skill}\b", text, re.IGNORECASE):
            found_skills.append(skill)

    return {
        "name": name,
        "email": email,
        "mobile_number": phone,
        "skills": found_skills,
        "no_of_pages": text.count("\f") + 1,
        "raw_text": text
    }
