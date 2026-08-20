import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";
import styles from "./Quizzes.module.css";
import NHeader from "../Home/NHeader";
import Footer from "../ui/Footer";

function Quizzes() {
    const [quizzes, setQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchSavedQuizzes = async () => {
            try {
                const response = await api.get(
                    "notes/quizzes/"
                );

                setQuizzes(response.data.quizzes || []);

            } catch (error) {
                console.error(
                    "Error fetching saved quizzes:",
                    error
                );

                setError(
                    error.response?.data?.error ||
                    "Unable to load your saved quizzes."
                );

            } finally {
                setLoading(false);
            }
        };

        fetchSavedQuizzes();
    }, []);


    const formatDifficulty = (difficulty) => {
        if (!difficulty) return "";

        return (
            difficulty.charAt(0).toUpperCase() +
            difficulty.slice(1)
        );
    };


    const formatQuestionType = (type) => {
        if (type === "multiple_choice") {
            return "Multiple Choice";
        }

        if (type === "true_false") {
            return "True / False";
        }

        return type;
    };


    const formatDate = (date) => {
        if (!date) {
            return "Not available";
        }

        return new Date(date).toLocaleDateString(
            undefined,
            {
                year: "numeric",
                month: "short",
                day: "numeric",
            }
        );
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


    return (
        <div>
        <div className={styles.container}>

            <NHeader />

            <main className={styles.quizContent}>

                <h1 className={styles.header}>
                    Saved Quizzes
                </h1>


                {quizzes.length === 0 ? (

                    <section className={styles.emptyCard}>

                        <h2>
                            No Saved Quizzes
                        </h2>

                        <p>
                            You haven't completed any quizzes
                            yet. Generate a quiz from one of
                            your lectures or tutorials to get
                            started.
                        </p>

                    </section>

                ) : (

                    <div className={styles.quizList}>

                        {quizzes.map((quiz) => (

                            <Link
                                key={quiz.id}
                                to={`/saved_quizzes/${quiz.id}`}
                                className={styles.quizCard}
                            >

                                <div
                                    className={
                                        styles.quizCardHeader
                                    }
                                >

                                    <div>

                                        <span
                                            className={
                                                styles.sourceType
                                            }
                                        >
                                            {quiz.source_type ===
                                            "lecture"
                                                ? "Lecture"
                                                : "Tutorial"}
                                        </span>

                                        <h2>
                                            {quiz.source_title}
                                        </h2>

                                    </div>


                                    <span
                                        className={
                                            styles.percentage
                                        }
                                    >
                                        {quiz.percentage}%
                                    </span>

                                </div>


                                <div
                                    className={
                                        styles.quizInfo
                                    }
                                >

                                    <div
                                        className={
                                            styles.infoItem
                                        }
                                    >

                                        <span>
                                            Difficulty
                                        </span>

                                        <strong>
                                            {formatDifficulty(
                                                quiz.difficulty
                                            )}
                                        </strong>

                                    </div>


                                    <div
                                        className={
                                            styles.infoItem
                                        }
                                    >

                                        <span>
                                            Type
                                        </span>

                                        <strong>
                                            {formatQuestionType(
                                                quiz.question_type
                                            )}
                                        </strong>

                                    </div>


                                    <div
                                        className={
                                            styles.infoItem
                                        }
                                    >

                                        <span>
                                            Score
                                        </span>

                                        <strong>
                                            {quiz.score} /{" "}
                                            {quiz.number_of_questions}
                                        </strong>

                                    </div>


                                    <div
                                        className={
                                            styles.infoItem
                                        }
                                    >

                                        <span>
                                            Completed
                                        </span>

                                        <strong>
                                            {formatDate(
                                                quiz.completed_at
                                            )}
                                        </strong>

                                    </div>

                                </div>


                                <div
                                    className={
                                        styles.quizCardFooter
                                    }
                                >

                                    <span>
                                        View Quiz & Review
                                    </span>

                                    <span
                                        className={
                                            styles.arrow
                                        }
                                    >
                                        →
                                    </span>

                                </div>

                            </Link>

                        ))}

                    </div>

                )}

            </main>
        
        </div>
        <Footer />
        </div>
    );
}

export default Quizzes;