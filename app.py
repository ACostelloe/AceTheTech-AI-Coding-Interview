import streamlit as st
import openai
import time
import datetime
import os
import pandas as pd


from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load secrets from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.yourdomain.com")  # Default example
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))  # Default to 587

def generate_coding_question(new=False):
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key is missing. Please set it as an environment variable."
    
    client = openai.Client(api_key=OPENAI_API_KEY)
    prompt = "Generate a unique coding challenge for a candidate to solve."
    if new:
        prompt = "Generate a completely new and different coding challenge."
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI coding interviewer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def evaluate_code(user_code, question):
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key is missing. Please set it as an environment variable."
    
    client = openai.Client(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI coding interviewer evaluating a candidate's code for efficiency and correctness. Provide detailed feedback, including time complexity analysis and potential optimizations."},
            {"role": "user", "content": f"Here is the candidate's code:\n{user_code}\nThey were asked to solve: {question}\nHow well does it solve the problem? Explain the correct approach and provide insights on improvements."}
        ]
    )
    return response.choices[0].message.content

def send_email_with_results(email, pdf_path):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        return "Error: Email sender credentials are missing. Please set them as environment variables."
    
    subject = "Your AI Coding Interview Results"
    body = "Please find attached your coding interview results."
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with open(pdf_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename=results.pdf")
        msg.attach(part)
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def generate_pdf(question, user_code, feedback):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "AI Coding Interview Results", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, f"Question: {question}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"Your Code:\n{user_code}")
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"AI Feedback:\n{feedback}")
    pdf_path = "coding_interview_results.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Store user job and question history
if 'job_stats' not in st.session_state:
    st.session_state['job_stats'] = pd.DataFrame(columns=['Job Role', 'Interview Question'])

st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🚀 AI-Powered Coding Interview Simulator</h1>", unsafe_allow_html=True)
st.subheader("Practice real coding challenges and get AI-driven feedback in real-time!")

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.datetime.now()
    st.session_state['question'] = generate_coding_question()

st.write("### Coding Challenge")
st.write(st.session_state['question'])

user_code = st.text_area("Write your solution here:", height=200)
email = st.text_input("Enter your email to receive results:")

if st.button("Submit & Get Results via Email"):
    if user_code.strip() and email.strip():
        feedback = evaluate_code(user_code, st.session_state['question'])
        pdf_path = generate_pdf(st.session_state['question'], user_code, feedback)
        send_email_with_results(email, pdf_path)
        st.success("Your results have been emailed to you!")
    else:
        st.warning("Please enter both your code and email before submitting.")
