import React, { useEffect, useState, useContext } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";
import styles from "./Callback.module.css";

const PaymentCallback = () => {
const [searchParams] = useSearchParams();
const navigate = useNavigate();
const { refreshUser } = useContext(AuthContext);


const [status, setStatus] = useState("verifying");
const [message, setMessage] = useState("");

useEffect(() => {
    const verifyPayment = async () => {
        const reference = searchParams.get("reference");

        if (!reference) {
            setStatus("error");
            setMessage("Payment reference was not found.");
            return;
        }

        try {
            const response = await api.get(
                `payment/verify/${reference}/`
            );

            console.log(
                "Payment verification:",
                response.data
            );

            await refreshUser();

            setStatus("success");

            setMessage(
                "Payment successful! Your subscription is now active."
            );

        } catch (error) {
            console.error(
                "Payment verification failed:",
                error
            );

            setStatus("error");

            setMessage(
                error.response?.data?.detail ||
                "We could not verify your payment."
            );
        }
    };

    verifyPayment();
}, [searchParams, refreshUser]);

return (
    <div className={styles.container}>

        {status === "verifying" && (
            <div className={styles.card}>

                <div className={styles.spinner}></div>

                <h2>Verifying Your Payment</h2>

                <p>
                    Please wait while we confirm your payment.
                </p>

                <span className={styles.subText}>
                    This may take a few moments.
                </span>

            </div>
        )}


        {status === "success" && (
            <div className={`${styles.card} ${styles.success}`}>

                <div className={styles.icon}>
                    ✓
                </div>

                <h2>Payment Successful!</h2>

                <p>
                    {message}
                </p>

                <div className={styles.details}>
                    Your SmartNotes premium subscription
                    is now active.
                </div>

                <button
                    className={styles.primaryButton}
                    onClick={() => navigate("/profile")}
                >
                    View Profile
                </button>

            </div>
        )}


        {status === "error" && (
            <div className={`${styles.card} ${styles.error}`}>

                <div className={styles.errorIcon}>
                    !
                </div>

                <h2>Payment Verification Failed</h2>

                <p>
                    {message}
                </p>

                <div className={styles.details}>
                    If you completed the payment, please
                    try again or contact support.
                </div>

                <button
                    className={styles.primaryButton}
                    onClick={() => navigate("/pricing")}
                >
                    Return to Pricing
                </button>

            </div>
        )}

    </div>
);

};

export default PaymentCallback;
