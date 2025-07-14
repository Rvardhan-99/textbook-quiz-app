import streamlit as st
import spacy
import random
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Extract keywords and phrases
def extract_keywords(text):
    doc = nlp(text)
    # Extract nouns, proper nouns, and noun phrases
    keywords = []
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and len(token.text) > 2:
            keywords.append(token.text)
    for chunk in doc.noun_chunks:
        if len(chunk.text.split()) > 1 and len(chunk.text) > 4:
            keywords.append(chunk.text)
    return list(set(keywords))[:10]  # Unique, max 10

# Find related terms for a keyword
def find_related_terms(keyword, doc):
    related = []
    for sent in doc.sents:
        if keyword.lower() in sent.text.lower():
            for token in sent:
                if token.pos_ in ["NOUN", "PROPN", "VERB"] and token.text.lower() != keyword.lower():
                    related.append(token.text)
    return list(set(related))[:3]

# Generate random questions and options
def generate_questions(text):
    doc = nlp(text)
    keywords = extract_keywords(text)
    random.shuffle(keywords)
    keywords = keywords[:min(5, len(keywords))]  # Limit to 5 questions
    questions = []

    question_types = [
        {
            "template": "What is meant by '{keyword}' in the text?",
            "correct_gen": lambda k, sent: f"It refers to {sent or 'a key concept in the text'}.",
            "incorrect_gen": lambda k, others: [
                f"It is similar to {random.choice(others) if others else 'another term'}.",
                "It is an unrelated concept.",
                f"It opposes {random.choice(others) if others else 'the main topic'}."
            ]
        },
        {
            "template": "What role does '{keyword}' play in the text?",
            "correct_gen": lambda k, sent: f"It is central to {sent or 'the process described'}.",
            "incorrect_gen": lambda k, others: [
                f"It is a minor detail compared to {random.choice(others) if others else 'other terms'}.",
                "It has no significant role.",
                f"It is a synonym for {random.choice(others) if others else 'another term'}."
            ]
        },
        {
            "template": "How is '{keyword}' related to another concept in the text?",
            "correct_gen": lambda k, sent: f"It is connected to {random.choice(find_related_terms(k, doc)) if find_related_terms(k, doc) else 'the main topic'}.",
            "incorrect_gen": lambda k, others: [
                f"It is unrelated to {random.choice(others) if others else 'other concepts'}.",
                "It is the opposite of the main topic.",
                f"It is a type of {random.choice(others) if others else 'another concept'}."
            ]
        }
    ]

    for keyword in keywords:
        q_type = random.choice(question_types)
        # Find sentence containing the keyword for context
        context = ""
        for sent in doc.sents:
            if keyword.lower() in sent.text.lower():
                context = re.sub(rf'\b{keyword}\b', 'the concept', sent.text, flags=re.IGNORECASE)
                break
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
