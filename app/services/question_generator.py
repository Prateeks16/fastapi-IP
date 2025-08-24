def generate_resume_based_questions(resume_text: str) -> list[dict]:
    # Dummy logic; replace with your HF model output later
    base = [
        {"question_text": "Walk me through your most impactful project.", "category": "projects", "difficulty": "medium"},
        {"question_text": "What was a tough technical challenge you solved recently?", "category": "experience", "difficulty": "medium"},
        {"question_text": "Which skills from your resume are you strongest at?", "category": "skills", "difficulty": "easy"},
        {"question_text": "Tell me about a time you optimized performance.", "category": "experience", "difficulty": "hard"},
        {"question_text": "How do you stay updated with industry trends?", "category": "general", "difficulty": "easy"},
    ]
    # You can parse resume_text to tweak categories later
    return base
