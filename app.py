import streamlit as st
import openai
import time
import datetime
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_coding_question():
    questions = [
        "Write a function that finds the longest palindrome in a given string.",
        "Implement a function to check if two strings are anagrams of each other.",
        "Write a function that returns the nth Fibonacci number using dynamic programming.",
        "Implement a function to find the lowest common ancestor in a binary tree.",
        "Write a function that sorts an array using the quicksort algorithm."
    ]
    return random.choice(questions)

def evaluate_code(user_code, question):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Error: OpenAI API key is missing. Please set it as an environment variable."
    
    client = openai.Client(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI coding interviewer evaluating a candidate's code for efficiency and correctness. Provide detailed feedback, including time complexity analysis and potential optimizations."},
            {"role": "user", "content": f"Here is the candidate's code:\n{user_code}\nThey were asked to solve: {question}\nHow well does it solve the problem? Explain the correct approach and provide insights on improvements."}
        ]
    )
    return response.choices[0].message.content

st.title("🚀 AI-Powered Coding Interview Simulator")
st.subheader("Practice real coding challenges and get AI-driven feedback in real-time!")

if 'start_time' not in st.session_state:
    st.session_state['start_time'] = datetime.datetime.now()
    st.session_state['question'] = generate_coding_question()

elapsed_time = datetime.datetime.now() - st.session_state['start_time']
remaining_time = max(0, 3600 - elapsed_time.seconds)  # 1 hour session limit
elapsed_minutes = elapsed_time.seconds // 60
elapsed_seconds = elapsed_time.seconds % 60
remaining_minutes = remaining_time // 60
remaining_seconds = remaining_time % 60

st.write(f"⏳ Time Elapsed: {elapsed_minutes} minutes {elapsed_seconds} seconds")
st.write(f"🕒 Time Remaining: {remaining_minutes} minutes {remaining_seconds} seconds")

if remaining_time <= 0:
    st.error("⏳ Your session has expired! Please start a new session to continue.")
    st.stop()

st.write("### Coding Challenge")
st.write(st.session_state['question'])

user_code = st.text_area("Write your solution here:", height=200)

if st.button("Submit Code"):
    if user_code.strip():
        st.write("Evaluating your solution... ⏳")
        time.sleep(2)  # Simulate evaluation delay
        feedback = evaluate_code(user_code, st.session_state['question'])
        st.write("### AI Feedback 🧠")
        st.write(feedback)
    else:
        st.warning("Please enter some code before submitting.")
