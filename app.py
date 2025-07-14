import streamlit as st
import random
import re

# Extract keywords from text
def extract_keywords(text):
    # Split text into words and filter
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {'the', 'is', 'are', 'and', 'or', 'in', 'to', 'of', 'by', 'from', 'with'}
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    # Extract phrases (simple approach: look for consecutive capitalized words or common phrases)
    phrases = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b', text)  # e.g., "Calvin Cycle"
    return list(set(keywords + phrases))[:10]  # Unique, max 10

# Find context for a keyword (sentence containing it)
def find_context(keyword, text):
    sentences = re.split(r'[.!?]', text)
    for sent in sentences:
        if keyword.lower() in sent.lower():
            return sent.strip()
    return ""

# Generate random questions and options
def generate_questions(text):
    keywords = extract_keywords(text)
    random.shuffle(keywords)
    keywords = keywords[:min(5, len(keywords))]  # Limit to 5 questions
    questions = []

    question_types = [
        {
            "template": "What does '{keyword}' refer to in the text?",
            "correct_gen": lambda k, ctx: f"It refers to {ctx or 'a main concept'}.",
            "incorrect_gen": lambda k, others: [
                f"It is similar to {random.choice(others) if others else 'another term'}.",
                "It is an unrelated term.",
                f"It contrasts with {random.choice(others) if others else 'the main topic'}."
            ]
        },
        {
            "template": "What is the purpose of '{keyword}' in the context?",
           ns
            "correct_gen": lambda k, ctx: f"It is used in {ctx or 'the process described'}.",
            "incorrect_gen": lambda k, others: [
                f"It is a minor detail unlike {random.choice(others) if others else 'other terms'}.",
                "It serves no purpose.",
                f"It is a type of {random.choice(others) if others else 'another concept'}."
            ]
        },
        {
            "template": "How does '{keyword}' relate to another idea in the text?",
            "correct_gen": lambda k, ctx: f"It is linked to {random.choice(others) if others else 'the main topic'} in the text.",
            "incorrect_gen": lambda k, others: [
                f"It is unrelated to {random.choice(others) if others else 'other ideas'}.",
                "It opposes the main idea.",
                f"It is a synonym for {random.choice(others) if others else 'another term'}."
            ]
        }
    ]

    for keyword in keywords:
        q_type = random.choice(question_types)
        context = find_context(keyword, text)
        question_text = q_type["template"].format(keyword=keyword)
        correct_answer = q_type["correct_gen"](keyword, context)
        other_keywords = [kw for kw in keywords if kw != keyword]
        incorrect_options = q_type["incorrect_gen"](keyword, other_keywords)
        options = [correct_answer] + incorrect_options
        random.shuffle(options)

        questions.append({
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer
        })

    return questions

# Main Streamlit app
def main():
    st.title("Dynamic Textbook Quiz Generator")

    # Initialize session state
    if 'questions' not in st.session_state:
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.show_score = False
        st.session_state.textbook_content = ""

    # Text input
    textbook_content = st.text_area(
        "Paste your textbook content here:",
        value=st.session_state.textbook_content,
        height=150
    )

    # Update session state when text changes
    if textbook_content != st.session_state.textbook_content:
        st.session_state.textbook_content = textbook_content
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.show_score = False

    # Generate Quiz button
    if st.button("Generate Quiz", disabled=not textbook_content):
        if textbook_content:
            st.session_state.questions = generate_questions(textbook_content)
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.show_score = False

    # Display quiz
    if st.session_state.questions and not st.session_state.show_score:
        question = st.session_state.questions[st.session_state.current_question_index]
        st.subheader(f"Question {st.session_state.current_question_index + 1} of {len(st.session_state.questions)}")
        st.write(question['question'])
        
        # Display options
        selected_option = st.radio("Select an answer:", question['options'], key=f"q_{st.session_state.current_question_index}")
        
        # Submit answer
        if st.button("Submit Answer"):
            if selected_option == question['correct_answer']:
                st.session_state.score += 1
            st.session_state.current_question_index += 1
            if st.session_state.current_question_index >= len(st.session_state.questions):
                st.session_state.show_score = True
            st.rerun()

    # Show score
    if st.session_state.show_score:
        st.subheader("Quiz Completed!")
        st.write(f"Your score: {st.session_state.score} out of {len(st.session_state.questions)}")
        if st.button("Start New Quiz"):
            st.session_state.questions = []
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.show_score = False
            st.session_state.textbook_content = ""
            st.rerun()

if __name__ == "__main__":
    main()
