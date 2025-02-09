import streamlit as st
import openai
import time
import datetime
import os
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

# Ensure results storage
RESULTS_FILE = "user_results.csv"
if not os.path.exists(RESULTS_FILE):
    pd.DataFrame(columns=["Timestamp", "Email", "Question", "User Code", "AI Feedback"]).to_csv(RESULTS_FILE, index=False)

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

def save_results(email, question, user_code, feedback):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_data = pd.DataFrame([[timestamp, email, question, user_code, feedback]],
                             columns=["Timestamp", "Email", "Question", "User Code", "AI Feedback"])
    new_data.to_csv(RESULTS_FILE, mode='a', header=False, index=False)

def send_email_with_results(email, question, user_code, feedback):
    if not SENDER_EMAIL or not SENDER_PASSWORD or not SMTP_SERVER:
        return "Error: Email sender credentials are missing. Please set them as environment variables."
    
    subject = "Your AI Coding Interview Results"
    body = f"""
    Hello,

    Here are your coding interview results:

    🏆 **Question:**
    {question}

    🖥 **Your Code:**
    {user_code}

    🤖 **AI Feedback:**
    {feedback}

    Best of luck with your interviews!
    - AI Coding Interview Simulator
    """
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Streamlit UI
st.title("🚀 AI-Powered Coding Interview Simulator")
st.subheader("Practice real coding challenges and get AI-driven feedback in real-time!")

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.datetime.now()
    st.session_state['question'] = generate_coding_question()

# Check session duration
elapsed_time = datetime.datetime.now() - st.session_state['start_time']
remaining_time = max(0, 3600 - elapsed_time.seconds)  # 1 hour limit
st.write(f"⏳ Time Remaining: {remaining_time // 60} minutes {remaining_time % 60} seconds")

if remaining_time <= 0:
    st.error("Your session has expired! Please restart the application.")
    st.stop()

st.write("### Coding Challenge")
st.write(st.session_state['question'])

user_code = st.text_area("Write your solution here:", height=200)
email = st.text_input("Enter your email to receive results:")

if st.button("Submit & Get Results via Email"):
    if user_code.strip() and email.strip():
        feedback = evaluate_code(user_code, st.session_state['question'])
        save_results(email, st.session_state['question'], user_code, feedback)
        send_email_with_results(email, st.session_state['question'], user_code, feedback)
        st.success("Your results have been emailed to you!")
        
        # Display feedback in UI
        st.write("### AI Feedback 🧠")
        st.write(feedback)
        
        # Set flag to generate new question on next reload
        st.session_state['new_question'] = True
    else:
        st.warning("Please enter both your code and email before submitting.")

if st.button("🔄 Generate New Question") or st.session_state.get('new_question', False):
    st.session_state['question'] = generate_coding_question(new=True)
    st.session_state['new_question'] = False
    st.rerun()
