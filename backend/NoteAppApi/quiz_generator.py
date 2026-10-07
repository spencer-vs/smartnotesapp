import os
import json
import requests
from .models import Quiz, QuizQuestion
from django.db import transaction
import traceback
from groq import Groq, RateLimitError
import time


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
    Generate quiz questions from Lecture or Tutorial content
    using Groq GPT-OSS 20B.

    The complete source text is sent in one request.
    No manual truncation or chunking is performed.

    Returns:
        dict containing generated questions
        or None if generation fails.
    """

    try:

        # -----------------------------------
        # Validate difficulty
        # -----------------------------------

        if difficulty not in DIFFICULTY_QUESTION_COUNT:

            print(
                "❌ Invalid quiz difficulty:",
                difficulty
            )

            return None


        # -----------------------------------
        # Validate question type
        # -----------------------------------

        if question_type not in QUESTION_TYPES:

            print(
                "❌ Invalid question type:",
                question_type
            )

            return None


        # -----------------------------------
        # Validate source text
        # -----------------------------------

        if not source_text or not source_text.strip():

            print(
                "❌ No source text provided for quiz generation"
            )

            return None


        # -----------------------------------
        # Clean source text
        # -----------------------------------

        source_text = source_text.strip()


        # -----------------------------------
        # Determine number of questions
        # -----------------------------------

        number_of_questions = (
            DIFFICULTY_QUESTION_COUNT[difficulty]
        )


        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()


        if not api_key:

            print("❌ GROQ_API_KEY is missing")

            return None


        # -----------------------------------
        # Create Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )


        # -----------------------------------
        # Question type instructions
        # -----------------------------------

        if question_type == "multiple_choice":

            question_format = """
Each question must contain exactly four options:

A
B
C
D

There must be exactly ONE correct answer.

All four option texts must be:

- non-empty
- meaningful
- different from each other
- plausible within the source material
"""

        else:

            question_format = """
Each question must contain exactly two options:

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
        # Maximum generation attempts
        # -----------------------------------

        max_attempts = 2


        # -----------------------------------
        # Generate quiz
        # -----------------------------------

        for attempt in range(1, max_attempts + 1):

            print(
                f"🧠 Quiz generation attempt "
                f"{attempt}/{max_attempts}"
            )


            # -----------------------------------
            # Prompt
            # -----------------------------------

            prompt = f"""
You are the SmartNotes Quiz Generator.

Create an educational quiz using ONLY the
source material provided below.

Do NOT introduce facts that are not contained
in the source material.

DIFFICULTY:
{difficulty}

{difficulty_instructions[difficulty]}

QUESTION TYPE:
{question_type}

EXACT NUMBER OF QUESTIONS:
{number_of_questions}

You MUST generate exactly {number_of_questions}
questions.

{question_format}

IMPORTANT RULES:

1. Generate exactly {number_of_questions} questions.

2. Every question must be answerable using
   the supplied source material.

3. Do not invent information.

4. Avoid duplicate or nearly identical questions.

5. Each question must have exactly one
   correct answer.

6. Make incorrect answers plausible.

7. Every question must contain:
   - non-empty question text
   - valid options
   - a valid correct answer
   - a non-empty explanation

8. Every option must contain meaningful text.

9. For multiple-choice questions, all four
   options must contain different answer texts.

10. For true/false questions:
    A must be exactly "True".
    B must be exactly "False".

11. The explanation must briefly explain why
    the correct answer is correct.

12. Questions should test the requested
    difficulty level.

13. Do not repeat the same concept unnecessarily.

14. Use only information contained in the
    source material.

15. Return the quiz using the requested
    JSON structure.

SOURCE MATERIAL:

{source_text}
"""


            # -----------------------------------
            # Groq request
            # -----------------------------------

            try:

                completion = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.3,

                    max_tokens=7000,

                    response_format={
                        "type": "json_object"
                    }

                )


            except Exception as e:

                print(
                    "❌ Groq quiz request failed:",
                    repr(e)
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            # -----------------------------------
            # Log token usage
            # -----------------------------------

            if completion.usage:

                print("Quiz generation usage:")

                print(
                    "Input tokens:",
                    completion.usage.prompt_tokens
                )

                print(
                    "Output tokens:",
                    completion.usage.completion_tokens
                )

                print(
                    "Total tokens:",
                    completion.usage.total_tokens
                )


            # -----------------------------------
            # Extract AI response
            # -----------------------------------

            try:

                content = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

            except Exception as e:

                print(
                    "❌ Unable to extract Groq quiz response:",
                    repr(e)
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            if not content:

                print(
                    "❌ Groq returned an empty quiz response"
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            # -----------------------------------
            # Parse JSON
            # -----------------------------------

            try:

                quiz_data = json.loads(content)

            except json.JSONDecodeError as e:

                print(
                    "❌ Quiz JSON parsing error:",
                    repr(e)
                )

                print(
                    "AI CONTENT:",
                    content
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            # -----------------------------------
            # Validate response structure
            # -----------------------------------

            if not isinstance(
                quiz_data,
                dict
            ):

                print(
                    "❌ Quiz response is not a dictionary"
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            questions = quiz_data.get(
                "questions"
            )


            if not isinstance(
                questions,
                list
            ):

                print(
                    "❌ Quiz questions are missing or invalid"
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            # -----------------------------------
            # Validate question count
            # -----------------------------------

            if len(questions) != number_of_questions:

                print(
                    f"❌ Expected "
                    f"{number_of_questions} questions "
                    f"but received "
                    f"{len(questions)}"
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Wrong question count."
                    )

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                return None


            # -----------------------------------
            # Validate individual questions
            # -----------------------------------

            valid_quiz = True


            for index, question in enumerate(
                questions,
                start=1
            ):

                # -----------------------------------
                # Validate question object
                # -----------------------------------

                if not isinstance(
                    question,
                    dict
                ):

                    print(
                        f"❌ Question {index} is invalid"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Validate required fields
                # -----------------------------------

                required_fields = [
                    "question",
                    "options",
                    "correct_answer",
                    "explanation",
                ]


                for field in required_fields:

                    if field not in question:

                        print(
                            f"❌ Question {index} "
                            f"missing field: {field}"
                        )

                        valid_quiz = False
                        break


                if not valid_quiz:
                    break


                # -----------------------------------
                # Validate question text
                # -----------------------------------

                question_text = question["question"]


                if not isinstance(
                    question_text,
                    str
                ):

                    print(
                        f"❌ Question {index}: "
                        "question text must be a string"
                    )

                    valid_quiz = False
                    break


                if not question_text.strip():

                    print(
                        f"❌ Question {index}: "
                        "question text is empty"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Validate explanation
                # -----------------------------------

                explanation = question["explanation"]


                if not isinstance(
                    explanation,
                    str
                ):

                    print(
                        f"❌ Question {index}: "
                        "explanation must be a string"
                    )

                    valid_quiz = False
                    break


                if not explanation.strip():

                    print(
                        f"❌ Question {index}: "
                        "explanation is empty"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Validate options
                # -----------------------------------

                options = question["options"]


                if not isinstance(
                    options,
                    dict
                ):

                    print(
                        f"❌ Question {index}: "
                        "options are invalid"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Expected option structure
                # -----------------------------------

                if question_type == "multiple_choice":

                    expected_options = {
                        "A",
                        "B",
                        "C",
                        "D",
                    }

                else:

                    expected_options = {
                        "A",
                        "B",
                    }


                if set(options.keys()) != expected_options:

                    print(
                        f"❌ Question {index}: "
                        f"expected options "
                        f"{sorted(expected_options)} "
                        f"but received "
                        f"{sorted(options.keys())}"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # True / False validation
                # -----------------------------------

                if question_type == "true_false":

                    if options["A"] != "True":

                        print(
                            f"❌ Question {index}: "
                            "option A must be True"
                        )

                        valid_quiz = False
                        break


                    if options["B"] != "False":

                        print(
                            f"❌ Question {index}: "
                            "option B must be False"
                        )

                        valid_quiz = False
                        break


                # -----------------------------------
                # Validate option values
                # -----------------------------------

                option_values = []


                for option_key in expected_options:

                    option_value = options.get(
                        option_key
                    )


                    if not isinstance(
                        option_value,
                        str
                    ):

                        print(
                            f"❌ Question {index}: "
                            f"option {option_key} "
                            "must be a string"
                        )

                        valid_quiz = False
                        break


                    option_value = option_value.strip()


                    if not option_value:

                        print(
                            f"❌ Question {index}: "
                            f"option {option_key} is empty"
                        )

                        valid_quiz = False
                        break


                    option_values.append(
                        option_value
                    )


                if not valid_quiz:
                    break


                # -----------------------------------
                # Validate duplicate options
                # -----------------------------------

                normalized_options = [
                    option.lower()
                    for option in option_values
                ]


                if len(normalized_options) != len(
                    set(normalized_options)
                ):

                    print(
                        f"❌ Question {index}: "
                        "duplicate option values detected"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Validate correct answer
                # -----------------------------------

                correct_answer = question[
                    "correct_answer"
                ]


                if not isinstance(
                    correct_answer,
                    str
                ):

                    print(
                        f"❌ Question {index}: "
                        "correct_answer must be a string"
                    )

                    valid_quiz = False
                    break


                correct_answer = (
                    correct_answer
                    .strip()
                    .upper()
                )


                if correct_answer not in expected_options:

                    print(
                        f"❌ Question {index}: "
                        "invalid correct answer"
                    )

                    valid_quiz = False
                    break


                # -----------------------------------
                # Normalize correct answer
                # -----------------------------------

                question[
                    "correct_answer"
                ] = correct_answer


            # -----------------------------------
            # Retry invalid quiz
            # -----------------------------------

            if not valid_quiz:

                if attempt < max_attempts:

                    print(
                        "🔄 Quiz validation failed."
                    )

                    print(
                        "🔄 Retrying quiz generation..."
                    )

                    time.sleep(2)

                    continue

                print(
                    "❌ Maximum quiz generation attempts reached"
                )

                return None


            # -----------------------------------
            # Success
            # -----------------------------------

            print(
                "✅ Quiz generated successfully"
            )

            print(
                f"✅ Generated exactly "
                f"{len(questions)} questions"
            )

            return quiz_data


        # -----------------------------------
        # All attempts failed
        # -----------------------------------

        print(
            "❌ Quiz generation failed after "
            f"{max_attempts} attempts"
        )

        return None


    except Exception as e:

        print(
            "❌ Unexpected quiz generation error:",
            repr(e)
        )

        traceback.print_exc()

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