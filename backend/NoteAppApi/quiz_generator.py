import os
import json
import requests
from .models import Quiz, QuizQuestion
from django.db import transaction


GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"


DIFFICULTY_QUESTION_COUNT = {
    "easy": 5,
    "mixed": 10,
    "hard": 20,
}


QUESTION_TYPES = {
    "multiple_choice",
    "true_false",
}


def generate_quiz(source_text, difficulty, question_type):
    """
    Generate quiz questions from Lecture or Tutorial content.

    Returns:
        dict containing generated questions
        or None if generation fails.
    """

    try:
        # -----------------------------------
        # Validate difficulty
        # -----------------------------------

        if difficulty not in DIFFICULTY_QUESTION_COUNT:
            print("❌ Invalid quiz difficulty:", difficulty)
            return None

        # -----------------------------------
        # Validate question type
        # -----------------------------------

        if question_type not in QUESTION_TYPES:
            print("❌ Invalid question type:", question_type)
            return None

        # -----------------------------------
        # Validate source text
        # -----------------------------------

        if not source_text or not source_text.strip():
            print("❌ No source text provided for quiz generation")
            return None

        # -----------------------------------
        # Determine number of questions
        # -----------------------------------

        number_of_questions = DIFFICULTY_QUESTION_COUNT[difficulty]

        # -----------------------------------
        # Limit source content
        # -----------------------------------

        source_text = source_text.strip()[:10000]

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv("GROQ_API_KEY", "").strip()

        if not api_key:
            print("❌ GROQ_API_KEY is missing")
            return None

        # -----------------------------------
        # Question type instructions
        # -----------------------------------

        if question_type == "multiple_choice":

            question_format = """
Each question must have exactly four options:

A
B
C
D

There must be exactly ONE correct answer.
"""

        else:

            question_format = """
Each question must have exactly two options:

A = True
B = False

There must be exactly ONE correct answer.
"""

        # -----------------------------------
        # Difficulty instructions
        # -----------------------------------

        difficulty_instructions = {
            "easy": """
Create straightforward questions that test
basic understanding, recognition, and recall
of the material.
""",

            "mixed": """
Create questions with a mixture of recall,
understanding, and moderate reasoning.
""",

            "hard": """
Create challenging questions that require
deeper understanding, comparison, interpretation,
and application of concepts contained in the material.
"""
        }

        # -----------------------------------
        # Prompt
        # -----------------------------------

        prompt = f"""
You are the SmartNotes Quiz Generator.

Create an educational quiz using ONLY the
source material provided below.

DO NOT introduce facts that are not contained
in the source material.

DIFFICULTY:
{difficulty}

{difficulty_instructions[difficulty]}

QUESTION TYPE:
{question_type}

NUMBER OF QUESTIONS:
{number_of_questions}

{question_format}

IMPORTANT RULES:

1. Generate exactly {number_of_questions} questions.

2. Every question must be answerable from
   the supplied source material.

3. Do not invent information.

4. Avoid duplicate or nearly identical questions.

5. Each question must have exactly one
   correct answer.

6. Make incorrect answers plausible.

7. Include a short explanation for the
   correct answer.

8. Return ONLY valid JSON.

9. Do not include Markdown.

10. Do not include ```json or ```.

RETURN THIS EXACT JSON STRUCTURE:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Explanation"
        }}
    ]
}}

For True/False questions use:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{
                "A": "True",
                "B": "False"
            }},
            "correct_answer": "A",
            "explanation": "Explanation"
        }}
    ]
}}

SOURCE MATERIAL:

{source_text}
"""

        # -----------------------------------
        # Request to Groq
        # -----------------------------------

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.3,
            "max_tokens": 5000,
        }

        print("🧠 Generating quiz...")
        print("Difficulty:", difficulty)
        print("Question type:", question_type)
        print("Number of questions:", number_of_questions)
        print("Source length:", len(source_text))

        response = requests.post(
            GROQ_URL,
            json=payload,
            headers=headers,
            timeout=120,
        )

        print("QUIZ STATUS CODE:", response.status_code)
        print("QUIZ RAW RESPONSE:", response.text)

        if response.status_code != 200:
            print("❌ Groq quiz generation failed")
            return None

        # -----------------------------------
        # Extract AI response
        # -----------------------------------

        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        # -----------------------------------
        # Remove accidental Markdown fences
        # -----------------------------------

        if content.startswith("```json"):
            content = content[7:]

        elif content.startswith("```"):
            content = content[3:]

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

        # -----------------------------------
        # Parse JSON
        # -----------------------------------

        try:
            quiz_data = json.loads(content)

        except json.JSONDecodeError as e:
            print("❌ Quiz JSON parsing error:", repr(e))
            print("AI CONTENT:", content)
            return None

        # -----------------------------------
        # Validate structure
        # -----------------------------------

        if not isinstance(quiz_data, dict):
            print("❌ Quiz response is not a dictionary")
            return None

        questions = quiz_data.get("questions")

        if not isinstance(questions, list):
            print("❌ Quiz questions are missing or invalid")
            return None

        # -----------------------------------
        # Validate question count
        # -----------------------------------

        if len(questions) != number_of_questions:
            print(
                f"❌ Expected {number_of_questions} questions "
                f"but received {len(questions)}"
            )
            return None

        # -----------------------------------
        # Validate individual questions
        # -----------------------------------

        for index, question in enumerate(questions, start=1):

            if not isinstance(question, dict):
                print(f"❌ Question {index} is invalid")
                return None

            required_fields = [
                "question",
                "options",
                "correct_answer",
                "explanation",
            ]

            for field in required_fields:

                if field not in question:
                    print(
                        f"❌ Question {index} missing field: {field}"
                    )
                    return None

            options = question["options"]

            if not isinstance(options, dict):
                print(f"❌ Question {index} options are invalid")
                return None

            # Multiple choice
            if question_type == "multiple_choice":

                expected_options = {"A", "B", "C", "D"}

                if set(options.keys()) != expected_options:
                    print(
                        f"❌ Question {index} must contain "
                        "A, B, C and D"
                    )
                    return None

            # True / False
            else:

                expected_options = {"A", "B"}

                if set(options.keys()) != expected_options:
                    print(
                        f"❌ Question {index} must contain "
                        "A and B"
                    )
                    return None

                if options["A"] != "True":
                    print(
                        f"❌ Question {index}: "
                        "option A must be True"
                    )
                    return None

                if options["B"] != "False":
                    print(
                        f"❌ Question {index}: "
                        "option B must be False"
                    )
                    return None

            # Validate correct answer
            correct_answer = question["correct_answer"]

            if correct_answer not in options:
                print(
                    f"❌ Question {index} has an invalid "
                    "correct answer"
                )
                return None

        print("✅ Quiz generated successfully")

        return quiz_data

    except requests.exceptions.Timeout:
        print("❌ Groq quiz request timed out")
        return None

    except requests.exceptions.RequestException as e:
        print("❌ Groq HTTP error:", repr(e))
        return None

    except Exception as e:
        print("❌ Unexpected quiz generation error:", repr(e))
        return None
    
    
    


@transaction.atomic
def save_generated_quiz(
    user,
    difficulty,
    question_type,
    quiz_data,
    lecture=None,
    tutorial=None,
):
    """
    Save a validated AI-generated quiz and its questions.

    A quiz must belong to either a Lecture or a Tutorial,
    but never both.
    """

    try:
        # -----------------------------------
        # Validate source
        # -----------------------------------

        if lecture is None and tutorial is None:
            print("❌ Quiz must have a Lecture or Tutorial source")
            return None

        if lecture is not None and tutorial is not None:
            print("❌ Quiz cannot belong to both Lecture and Tutorial")
            return None

        # -----------------------------------
        # Validate quiz data
        # -----------------------------------

        if not quiz_data or "questions" not in quiz_data:
            print("❌ Invalid quiz data")
            return None

        questions = quiz_data["questions"]

        if not questions:
            print("❌ Quiz contains no questions")
            return None

        # -----------------------------------
        # Determine question count
        # -----------------------------------

        number_of_questions = DIFFICULTY_QUESTION_COUNT.get(
            difficulty
        )

        if not number_of_questions:
            print("❌ Invalid difficulty")
            return None

        if len(questions) != number_of_questions:
            print(
                f"❌ Expected {number_of_questions} questions "
                f"but received {len(questions)}"
            )
            return None

        # -----------------------------------
        # Create Quiz
        # -----------------------------------

        quiz = Quiz.objects.create(
            user=user,
            lecture=lecture,
            tutorial=tutorial,
            difficulty=difficulty,
            question_type=question_type,
            number_of_questions=number_of_questions,
        )

        # -----------------------------------
        # Create Questions
        # -----------------------------------

        for index, question_data in enumerate(
            questions,
            start=1
        ):
            options = question_data["options"]

            QuizQuestion.objects.create(
                quiz=quiz,
                question=question_data["question"],
                option_a=options.get("A"),
                option_b=options.get("B"),
                option_c=options.get("C"),
                option_d=options.get("D"),
                correct_answer=question_data["correct_answer"],
                explanation=question_data["explanation"],
                order=index,
            )

        print(
            f"✅ Quiz saved successfully. "
            f"Quiz ID: {quiz.id}"
        )

        return quiz

    except Exception as e:
        print(
            "❌ Error saving generated quiz:",
            repr(e)
        )
        return None