import styles from "./Pricing.module.css";
import React from "react";
import { Link } from "react-router-dom";
import { useState } from "react";
import api from "../api/axios";


function Pricing() {

   const [loadingPlan, setLoadingPlan] = useState(null);

   const handleSubscribe = async (plan) => {
    try {
        setLoadingPlan(plan);

        const response = await api.post("payment/initialize_payment/",
            {
                plan: plan,
            }
        );

        const { authorization_url } = response.data;

        window.location.href = authorization_url;

    } catch (error) {
        console.error("Payment initialization failed:", error);

        const message =
            error.response?.data?.detail ||
            "Unable to initialize payment.";

        alert(message);

    } finally {
        setLoadingPlan(null);
    }
};  




    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h1>Choose Your Plan</h1>
                <p>
                    Get more from SmartNotes with premium AI features.
                </p>
            </div>

            <div className={styles.plans}>

                {/* Monthly */}
                <div className={styles.planCard}>
                    <h2>Monthly</h2>

                    <div className={styles.price}>
                        <span>₦</span>
                        <strong>3,000</strong>
                        <small>/month</small>
                    </div>

                    <p className={styles.description}>
                        Flexible monthly access to SmartNotes premium
                        features.
                    </p>

                    <ul>
                        <li>AI-powered notes</li>
                        <li>Lecture transcription</li>
                        <li>AI task generation</li>
                        <li>Semantic search</li>
                        <li>Premium SmartNotes features</li>
                    </ul>

            <button onClick={() => handleSubscribe("monthly")}>
                {loadingPlan === "monthly" ? "Loading..." : "Choose Monthly"}
            </button>
                </div>


                {/* Yearly */}
                <div className={`${styles.planCard} ${styles.featured}`}>
                    <div className={styles.badge}>
                        Best Value
                    </div>

                    <h2>Yearly</h2>

                    <div className={styles.price}>
                        <span>₦</span>
                        <strong>30,000</strong>
                        <small>/year</small>
                    </div>

                    <p className={styles.description}>
                        Save money with a full year of premium
                        SmartNotes access.
                    </p>

                    <ul>
                        <li>Everything in Monthly</li>
                        <li>12 months of premium access</li>
                        <li>Better value</li>
                        <li>Priority access to new features</li>
                    </ul>

            <button onClick={() => handleSubscribe("yearly")}>
               {loadingPlan === "yearly" ? "Loading..." : "Choose Yearly"}
            </button>
                </div>

            </div>
        </div>
    );
}

export default Pricing;