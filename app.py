import streamlit as st
import openai
import time

def generate_coding_question():
    return "Write a function that finds the longest palindrome in a given string."

def evaluate_code(user_code):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI coding interviewer evaluating a candidate's code for efficiency and correctness."},
            {"role": "user", "content": f"Here is the candidate's code:\n{user_code}\nHow well does it solve the problem?"}
        ]
    )
    return response['choices'][0]['message']['content']

st.title("🚀 AI-Powered Coding Interview Simulator")
st.subheader("Practice real coding challenges and get AI-driven feedback in real-time!")

if 'question' not in st.session_state:
    st.session_state['question'] = generate_coding_question()

st.write("### Coding Challenge")
st.write(st.session_state['question'])

user_code = st.text_area("Write your solution here:", height=200)

if st.button("Submit Code"):
    if user_code.strip():
        st.write("Evaluating your solution... ⏳")
        time.sleep(2)  # Simulate evaluation delay
        feedback = evaluate_code(user_code)
        st.write("### AI Feedback 🧠")
        st.write(feedback)
    else:
        st.warning("Please enter some code before submitting.")
