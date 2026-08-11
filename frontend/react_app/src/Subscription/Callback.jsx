import React, { useEffect, useState, useContext } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { AuthContext } from "../context/AuthContext";

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
                const response = await api.get(`payment/verify/${reference}/`)

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
    }, [searchParams]);

    return (
        <div>
            {status === "verifying" && (
                <div>
                    <h2>Verifying your payment...</h2>
                    <p>Please wait while we confirm your payment.</p>
                </div>
            )}

            {status === "success" && (
                <div>
                    <h2>Payment Successful!</h2>
                    <p>{message}</p>

                    <button
                        onClick={() => navigate("/profile")}
                    >
                        View Profile
                    </button>
                </div>
            )}

            {status === "error" && (
                <div>
                    <h2>Payment Verification Failed</h2>
                    <p>{message}</p>

                    <button
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