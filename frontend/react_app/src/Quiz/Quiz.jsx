import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import styles from "./Quiz.module.css";
import NHeader from "../Home/NHeader";
import { toast } from "react-toastify";
import Footer from "../ui/Footer";

function Quiz() {

    const { sourceType, sourceId } = useParams();

    const navigate = useNavigate();


    const [difficulty, setDifficulty] = useState("easy");

    const [questionType, setQuestionType] = useState(
        "multiple_choice"
    );

    const [loading, setLoading] = useState(false);

    const [quiz, setQuiz] = useState(null);
    const [answers, setAnswers] = useState({});
    const [submitting, setSubmitting] = useState(false);



    useEffect(() => {

    const savedQuiz = sessionStorage.getItem(
        "activeQuiz"
    );

    if (!savedQuiz) {
        return;
    }

    try {

        const parsedQuiz = JSON.parse(savedQuiz);

        const belongsToCurrentSource =
            parsedQuiz.sourceType === sourceType &&
            String(parsedQuiz.sourceId) === String(sourceId);

        if (belongsToCurrentSource && parsedQuiz.quiz) {

            console.log(
                "Restoring active quiz:",
                parsedQuiz.quiz.id
            );

            setQuiz(parsedQuiz.quiz);

            setAnswers(
                parsedQuiz.answers || {}
            );

        } else {

            sessionStorage.removeItem(
                "activeQuiz"
            );

        }

    } catch (error) {

        console.error(
            "Unable to restore quiz:",
            error
        );

        sessionStorage.removeItem(
            "activeQuiz"
        );

    }

}, [sourceType, sourceId]);


    const handleAnswerSelect = (questionId, answer) => {

    setAnswers((previousAnswers) => {

        const updatedAnswers = {
            ...previousAnswers,
            [questionId]: answer,
        };

        const savedQuiz =
            sessionStorage.getItem("activeQuiz");

        if (savedQuiz) {

            try {

                const parsedQuiz =
                    JSON.parse(savedQuiz);

                parsedQuiz.answers =
                    updatedAnswers;

                sessionStorage.setItem(
                    "activeQuiz",
                    JSON.stringify(parsedQuiz)
                );

            } catch (error) {

                console.error(
                    "Unable to save quiz answers:",
                    error
                );

            }

        }

        return updatedAnswers;

    });

};


    const handleGenerateQuiz = async () => {

        try {

            setLoading(true);

            const data = {

                difficulty: difficulty,

                question_type: questionType,

            };


            if (sourceType === "lecture") {

                data.lecture_id = sourceId;

            } else if (sourceType === "tutorial") {

                data.tutorial_id = sourceId;

            } else {

                toast.error("Invalid quiz source.");

                return;
            }


            const response = await api.post(
                "notes/quizzes/generate/",
                data
            );


            const generatedQuiz = response.data;

            setQuiz(generatedQuiz);

            sessionStorage.setItem(
                "activeQuiz",
                JSON.stringify({
                    sourceType,
                    sourceId,
                    quiz: generatedQuiz,
                    answers: {},
                })
            );

            toast.success(
                "Quiz generated successfully!"
            );

            
        } catch (error) {

            console.error(
                "Quiz generation error:",
                error
            );


            const message =
                error.response?.data?.error ||
                "Unable to generate quiz. Please try again.";


            toast.error(message);

        } finally {

            setLoading(false);

        }

    };



    const handleSubmitQuiz = async () => {

    if (!quiz) {
        return;
    }

    // Make sure every question has been answered
    if (
        Object.keys(answers).length !==
        quiz.number_of_questions
    ) {

        toast.warning(
            "Please answer all questions before submitting."
        );

        return;
    }

    try {

        setSubmitting(true);

        const response = await api.post(
            `notes/quizzes/${quiz.id}/submit/`,
            {
                answers: answers,
            }
        );

        console.log(
            "QUIZ SUBMISSION:",
            response.data
        );

        toast.success(
            "Quiz submitted successfully!"
        );

        sessionStorage.removeItem(
                "activeQuiz"
            );

        navigate("/quizzes");

    } catch (error) {

        console.error(
            "Quiz submission error:",
            error
        );

        const message =
            error.response?.data?.error ||
            "Unable to submit quiz. Please try again.";

        toast.error(message);

    } finally {

        setSubmitting(false);

    }
};

    return (
        <div>

        <div className={styles.container}>

            <NHeader />


            <main className={styles.quizContent}>

                {!quiz ? (

                    /* =========================
                       QUIZ CONFIGURATION
                    ========================= */

                    <section className={styles.quizCard}>

                        <h1>
                            Create Your Quiz
                        </h1>


                        <p className={styles.description}>
                            Choose your difficulty and question
                            type to generate a quiz from this{" "}
                            {sourceType}.
                        </p>


                        {/* =========================
                            DIFFICULTY
                        ========================= */}

                        <div className={styles.section}>

                            <h2>
                                Difficulty
                            </h2>


                            <div className={styles.options}>

                                <button
                                    type="button"
                                    className={
                                        difficulty === "easy"
                                            ? styles.selectedOption
                                            : styles.option
                                    }
                                    onClick={() =>
                                        setDifficulty("easy")
                                    }
                                >

                                    <strong>
                                        Easy
                                    </strong>

                                    <span>
                                        5 Questions
                                    </span>

                                </button>


                                <button
                                    type="button"
                                    className={
                                        difficulty === "mixed"
                                            ? styles.selectedOption
                                            : styles.option
                                    }
                                    onClick={() =>
                                        setDifficulty("mixed")
                                    }
                                >

                                    <strong>
                                        Mixed
                                    </strong>

                                    <span>
                                        10 Questions
                                    </span>

                                </button>


                                <button
                                    type="button"
                                    className={
                                        difficulty === "hard"
                                            ? styles.selectedOption
                                            : styles.option
                                    }
                                    onClick={() =>
                                        setDifficulty("hard")
                                    }
                                >

                                    <strong>
                                        Hard
                                    </strong>

                                    <span>
                                        20 Questions
                                    </span>

                                </button>

                            </div>

                        </div>


                        {/* =========================
                            QUESTION TYPE
                        ========================= */}

                        <div className={styles.section}>

                            <h2>
                                Question Type
                            </h2>


                            <div className={styles.options}>

                                <button
                                    type="button"
                                    className={
                                        questionType ===
                                        "multiple_choice"
                                            ? styles.selectedOption
                                            : styles.option
                                    }
                                    onClick={() =>
                                        setQuestionType(
                                            "multiple_choice"
                                        )
                                    }
                                >

                                    <strong>
                                        Multiple Choice
                                    </strong>

                                    <span>
                                        Choose from four option
                                    </span>

                                </button>


                                <button
                                    type="button"
                                    className={
                                        questionType ===
                                        "true_false"
                                            ? styles.selectedOption
                                            : styles.option
                                    }
                                    onClick={() =>
                                        setQuestionType(
                                            "true_false"
                                        )
                                    }
                                >

                                    <strong>
                                        True / False
                                    </strong>

                                    <span>
                                        Choose True or False
                                    </span>

                                </button>

                            </div>

                        </div>


                        {/* =========================
                            GENERATE BUTTON
                        ========================= */}

                        <button
                            className={styles.quizButton}
                            onClick={handleGenerateQuiz}
                            disabled={loading}
                        >

                            {loading
                                ? "Generating Quiz..."
                                : "Quiz"}

                        </button>

                    </section>

                ) : (

                    /* =========================
                       QUIZ QUESTIONS
                    ========================= */

                    <section className={styles.questionsContainer}>

                        <div className={styles.quizHeader}>

                            <h1>
                                Your Quiz
                            </h1>

                            <p>
                                {quiz.number_of_questions} Questions
                            </p>

                        </div>


                        {quiz.questions.map((question) => (

                            <div
                                key={question.id}
                                className={styles.questionCard}
                            >

                                <div
                                    className={
                                        styles.questionNumber
                                    }
                                >
                                    Question {question.order}
                                </div>


                                <h2>
                                    {question.question}
                                </h2>


                                <div
                                    className={
                                        styles.answerOptions
                                    }
                                >

                                    {Object.entries(
                                        question.options
                                    ).map(
                                        ([letter, text]) => (

                                            <button
                                                key={letter}
                                                type="button"
                                                className={
                                                    answers[question.id] === letter
                                                        ? styles.selectedAnswer
                                                        : styles.answerOption
                                                }
                                                onClick={() =>
                                                    handleAnswerSelect(
                                                        question.id,
                                                        letter
                                                    )
                                                }
                                            >

                                                <span
                                                    className={
                                                        styles.optionLetter
                                                    }
                                                >
                                                    {letter}
                                                </span>

                                                <span>
                                                    {text}
                                                </span>

                                            </button>

                                        )
                                    )}

                                </div>

                            </div>

                        ))}


                            <button
                                className={styles.submitButton}
                                onClick={handleSubmitQuiz}
                                disabled={submitting}
                            >
                                {submitting
                                    ? "Submitting..."
                                    : "Submit Quiz"}
                            </button>

                    </section>

                )}

            </main>

        </div>
        <Footer />
        </div>
    );
}

export default Quiz;