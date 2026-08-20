import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../api/axios";
import styles from "./QuizDetail.module.css";
import NHeader from "../Home/NHeader";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import Footer from "../ui/Footer";


function SavedQuizDetail() {

    const { quiz_id } = useParams();

    const [quiz, setQuiz] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [retaking, setRetaking] = useState(false);
    const navigate = useNavigate();


    useEffect(() => {

        const fetchQuizReview = async () => {

            try {

                const response = await api.get(
                    `notes/quizzes/${quiz_id}/review/`
                );

                setQuiz(response.data);

            } catch (error) {

                console.error(
                    "Error fetching quiz review:",
                    error
                );

                setError(
                    error.response?.data?.error ||
                    "Unable to load quiz review."
                );

            } finally {

                setLoading(false);

            }

        };


        fetchQuizReview();

    }, [quiz_id]);


   const handleRetake = async () => {

    const confirmed = window.confirm(
        "Are you sure you want to retake this quiz?\n\n" +
        "A new quiz will be generated using the same source, " +
        "difficulty, and question type. Your previous quiz will remain saved."
    );

    if (!confirmed) {
        return;
    }

    try {

        setRetaking(true);

        const response = await api.post(
            `notes/quizzes/${quiz_id}/retake/`
        );

        const newQuiz = response.data;

        console.log(
            "NEW RETAKE QUIZ:",
            newQuiz
        );

        // Store it using the exact structure
        // expected by Quiz.jsx
        sessionStorage.setItem(
            "activeQuiz",
            JSON.stringify({
                sourceType: newQuiz.source_type,
                sourceId: newQuiz.source_id,
                quiz: newQuiz,
                answers: {},
            })
        );

        // Navigate to the existing Quiz route
        navigate(
            `/quiz/${newQuiz.source_type}/${newQuiz.source_id}`
        );

    } catch (error) {

        console.error(
            "Quiz retake error:",
            error
        );

        console.error(
            "Backend response:",
            error.response?.data
        );

        const message =
            error.response?.data?.error ||
            "Unable to generate quiz. Please try again.";

        toast.error(message);

    } finally {

        setRetaking(false);

    }
};


    if (loading) {

        return (
            
            <div className={styles.container}>

                <NHeader />

                <div className={styles.loader}></div>

            </div>
        );

    }


    if (error) {
        
        return (
            <div className={styles.container}>

                <NHeader />

                <div className={styles.errorMessage}>
                    {error}
                </div>

            </div>
        );

    }


    if (!quiz) {
        return null;
    }


    return (
        <div>
        <div className={styles.container}>

            <NHeader />


            <main className={styles.quizContent}>

                <h1 className={styles.header}>
                    Saved Quiz
                </h1>


                {/* =========================
                    QUIZ INFORMATION
                ========================= */}

                <section className={styles.quizInfoCard}>

                    <h2>
                        Quiz Information
                    </h2>


                    <div className={styles.infoGrid}>

                        <div className={styles.infoItem}>

                            <span>
                                Difficulty
                            </span>

                            <strong>
                                {quiz.difficulty}
                            </strong>

                        </div>


                        <div className={styles.infoItem}>

                            <span>
                                Question Type
                            </span>

                            <strong>
                                {quiz.question_type ===
                                "multiple_choice"
                                    ? "Multiple Choice"
                                    : "True / False"}
                            </strong>

                        </div>


                        <div className={styles.infoItem}>

                            <span>
                                Questions
                            </span>

                            <strong>
                                {quiz.total_questions}
                            </strong>

                        </div>


                        <div className={styles.infoItem}>

                            <span>
                                Score
                            </span>

                            <strong>
                                {quiz.score} /{" "}
                                {quiz.total_questions}
                            </strong>

                        </div>


                        <div className={styles.infoItem}>

                            <span>
                                Percentage
                            </span>

                            <strong
                                className={
                                    styles.score
                                }
                            >
                                {quiz.percentage}%
                            </strong>

                        </div>


                        <div className={styles.infoItem}>

                            <span>
                                Completed
                            </span>

                            <strong>
                                {quiz.completed_at
                                    ? new Date(
                                        quiz.completed_at
                                    ).toLocaleDateString()
                                    : "Not available"}
                            </strong>

                        </div>

                    </div>

                </section>



                {/* =========================
                    REVIEW
                ========================= */}

                <h2 className={styles.reviewHeading}>
                    Quiz Review
                </h2>


                <div className={styles.reviewContainer}>

                    {quiz.questions.map(
                        (question, index) => (

                            <section
                                key={question.question_id}
                                className={
                                    styles.questionCard
                                }
                            >

                                {/* Question Header */}

                                <div
                                    className={
                                        styles.questionHeader
                                    }
                                >

                                    <h3>
                                        Question{" "}
                                        {index + 1}
                                    </h3>


                                    <span
                                        className={
                                            question.is_correct
                                                ? styles.correct
                                                : styles.incorrect
                                        }
                                    >

                                        {question.is_correct
                                            ? "✓ Correct"
                                            : "✗ Incorrect"}

                                    </span>

                                </div>


                                {/* Question */}

                                <div
                                    className={
                                        styles.questionSection
                                    }
                                >

                                    <span>
                                        Question
                                    </span>

                                    <p>
                                        {question.question}
                                    </p>

                                </div>


                                {/* Your Answer */}

                                <div
                                    className={
                                        styles.answerSection
                                    }
                                >

                                    <span>
                                        Your Answer
                                    </span>

                                    <p
                                        className={
                                            question.is_correct
                                                ? styles.correctAnswer
                                                : styles.wrongAnswer
                                        }
                                    >

                                        {question.selected_answer
                                            ? `${question.selected_answer} — ${question.selected_answer_text}`
                                            : "No answer provided"}

                                    </p>

                                </div>


                                {/* Correct Answer */}

                                <div
                                    className={
                                        styles.answerSection
                                    }
                                >

                                    <span>
                                        Correct Answer
                                    </span>

                                    <p
                                        className={
                                            styles.correctAnswer
                                        }
                                    >

                                        {question.correct_answer}
                                        {" — "}
                                        {question.correct_answer_text}

                                    </p>

                                </div>


                                {/* Explanation */}

                                <div
                                    className={
                                        styles.explanation
                                    }
                                >

                                    <span>
                                        Explanation
                                    </span>

                                    <p>
                                        {question.explanation ||
                                            "No explanation provided."}
                                    </p>

                                </div>

                            </section>

                        )
                    )}

                </div>


                <div className={styles.backButtonContainer}>

                    <button
                        onClick={handleRetake}
                        className={styles.retakeButton}
                        disabled={retaking}
                    >

                        {retaking
                            ? "Generating Quiz..."
                            : "Retake Quiz"}

                    </button>


                    <Link
                        to="/quizzes"
                        className={styles.backButton}
                    >
                        Back 
                    </Link>

                </div>


            </main>

        </div>
         <Footer />
        </div>
         

    );

}


export default SavedQuizDetail;