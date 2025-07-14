```python
import streamlit as st

# Simple keyword extraction
def extract_keywords(text):
    words = text.split()
    keywords = [word for word in words if len(word) > 3 and word.lower() not in ['the', 'is', 'are', 'and', 'or']]
    return list(set(keywords))[:10]  # Get unique keywords, max 10

# Generate multiple-choice questions
def generate_questions(keywords):
    questions = []
    for keyword in keywords:
        question = {
            'question': f'What is the significance of "{keyword}" in the context of the text?',
            'options': [
                'It is a key concept related to the topic.',
                'It is a minor detail in the text.',
                'It is an unrelated term.',
                'It is a synonym for another term.'
            ],
            'correct_answer': 'It is a key concept related to the topic.'
        }
        questions.append(question)
    return questions

# Main Streamlit app
def main():
    st.title("Textbook Quiz Generator")
    
    # Initialize session state variables
    if 'questions' not in st.session_state:
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.show_score = False
        st.session_state.textbook_content = ""

    # Text input for textbook content
    textbook_content = st.text_area(
        "Paste your textbook content here:",
        value=st.session_state.textbook_content,
        height=150
    )

    # Update session state with new input
    if textbook_content != st.session_state.textbook_content:
        st.session_state.textbook_content = textbook_content
        st.session_state.questions = []
        st.session_state.current_question_index = 0
        st.session_state.score = 0
        st.session_state.show_score = False

    # Generate Quiz button
    if st.button("Generate Quiz", disabled=not textbook_content):
        if textbook_content:
            keywords = extract_keywords(textbook_content)
            st.session_state.questions = generate_questions(keywords)
            st.session_state.current_question_index = 0
            st.session_state.score = 0
            st.session_state.show_score = False

    # Display quiz
    if st.session_state.questions and not st.session_state.show_score:
        question = st.session_state.questions[st.session_state.current_question_index]
        st.subheader(f"Question {st.session_state.current_question_index + 1} of {len(st.session_state.questions)}")
        st.write(question['question'])
        
        # Display radio buttons for options
        selected_option = st.radio("Select an answer:", question['options'], key=f"question_{st.session_state.current_question_index}")
        
        # Submit answer button
        if st.button("Submit Answer"):
            if selected_option == question['correct_answer']:
                st.session_state.score += 1
            next_question = st.session_state.current_question_index + 1
            if next_question < len(st.session_state.questions):
                st.session_state.current_question_index = next_question
            else:
                st.session_state.show_score = True
            st.rerun()  # Refresh to show next question or score

    # Display final score
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
```
