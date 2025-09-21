import streamlit as st
import nltk
import spacy
nltk.download('stopwords')
spacy.load('en_core_web_sm')

import pandas as pd
import base64, random
import time, datetime
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import pafy
import plotly.express as px
import youtube_dl

# ✅ Import our custom parser
from resume_utils import extract_resume_details


def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title


def get_table_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


connection = pymysql.connect(host='localhost', user='root', password='')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
        name, email, str(res_score), timestamp, str(no_of_pages),
        reco_field, cand_level, skills, recommended_skills, courses
    )
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon='./Logo/SRA_Logo.ico',
)


def run():
    st.title("Smart Resume Analyzer 🚀")
    st.sidebar.markdown("# Choose User")
    activities = ["Normal User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)

    img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250, 250))
    st.image(img)

    # Create DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)
    connection.select_db("sra")

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name VARCHAR(100) NOT NULL,
                     Email_ID VARCHAR(100) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(50) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills TEXT NOT NULL,
                     Recommended_skills TEXT NOT NULL,
                     Recommended_courses TEXT NOT NULL,
                     PRIMARY KEY (ID));
                    """

    cursor.execute(table_sql)

    if choice == 'Normal User':
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            # ✅ Use custom parser
            resume_data = extract_resume_details(save_image_path)

            if resume_data:
                resume_text = resume_data["raw_text"]

                st.header("**Resume Analysis**")
                st.success("Hello " + str(resume_data.get('name', 'Candidate')))
                st.subheader("**Your Basic info**")
                st.text('Name: ' + str(resume_data.get('name')))
                st.text('Email: ' + str(resume_data.get('email')))
                st.text('Contact: ' + str(resume_data.get('mobile_number')))
                st.text('Resume pages: ' + str(resume_data.get('no_of_pages')))

                # Candidate level
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown("<h4 style='color: #d73b5c;'>You are looking Fresher.</h4>", unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown("<h4 style='color: #1ed760;'>You are at intermediate level!</h4>", unsafe_allow_html=True)
                else:
                    cand_level = "Experienced"
                    st.markdown("<h4 style='color: #fba171;'>You are at experience level!</h4>", unsafe_allow_html=True)

                st.subheader("**Skills Recommendation💡**")
                keywords = st_tags(label='### Skills that you have',
                                   text='See our skills recommendation',
                                   value=resume_data['skills'], key='1')

                # Resume Score (modern sections)
                st.subheader("**Resume Score📝**")
                score_sections = ["Summary", "Core Competencies", "Experience", "Projects", "Certifications"]
                resume_score = sum([20 for section in score_sections if section.lower() in resume_text.lower()])

                my_bar = st.progress(0)
                for percent_complete in range(resume_score):
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)

                st.success('** Your Resume Writing Score: ' + str(resume_score) + '**')

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                insert_data(
                    resume_data.get('name', ''),
                    resume_data.get('email', ''),
                    str(resume_score),
                    timestamp,
                    str(resume_data.get('no_of_pages', 0)),
                    "",  # reco_field placeholder
                    cand_level,
                    str(resume_data.get('skills', [])),
                    "",  # recommended_skills placeholder
                    ""   # rec_course placeholder
                )

                st.balloons()

    else:  # Admin side
        st.success('Welcome to Admin Side')
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'machine_learning_hub' and ad_password == 'mlhub123':
                st.success("Welcome Admin")
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's👨‍💻 Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)

                labels = df['Predicted Field'].unique()
                values = df['Predicted Field'].value_counts()
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                labels = df['User Level'].unique()
                values = df['User Level'].value_counts()
                st.subheader("📈 **Pie-Chart for User Levels**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart for User Levels")
                st.plotly_chart(fig)
            else:
                st.error("Wrong ID & Password Provided")


run()
