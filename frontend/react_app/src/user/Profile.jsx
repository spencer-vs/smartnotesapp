import React from "react";
import { useEffect, useState } from "react";
import api from "../api/axios";
import styles from "./Profile.module.css";
import { Link } from "react-router-dom";
function Profile() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const response = await api.get("auth/user/");
                setProfile(response.data);
            } catch (error) {
                console.error("Error fetching profile:", error);
                setError("Unable to load your profile.");
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, []);

    if (loading) {
        return (
            <div className={styles.container}>
                {loading && (
                        <div className={styles.loader}></div>
                )}
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.container}>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div className={styles.container}>
           <div className={styles.container}>

    <h1 className={styles.header}>My Profile</h1>

    <section className={styles.profileCard}>
        <h2>Account Information</h2>

        <div className={styles.infoGrid}>

            <div className={styles.infoItem}>
                <span>Username</span>
                <strong>{profile.username}</strong>
            </div>

            <div className={styles.infoItem}>
                <span>Email</span>
                <strong>{profile.email || "Not provided"}</strong>
            </div>

            <div className={styles.infoItem}>
                <span>Phone</span>
                <strong>{profile.phone || "Not provided"}</strong>
            </div>


            <div className={styles.infoItem}>
                <span>Address</span>
                <strong>{profile.address || "Not provided"}</strong>
            </div>

        </div>
    </section>


    <section className={styles.subscriptionCard}>

        <h2>Subscription</h2>

        <div className={styles.subscriptionHeader}>
            <div>
                <span>Current Plan</span>
                <h3>{profile.subscription.plan_name}</h3>
            </div>

            <span className={`${styles.status} ${ styles[profile.subscription.status] }`}>
              {profile.subscription.status_name}
            </span>
        </div>

        <div className={styles.subscriptionInfo}>

            <div>
                <span>Days Remaining</span>
                <strong>
                    {profile.subscription.days_left}
                </strong>
            </div>

            <div>
                <span>
                    {profile.subscription.is_trial
                        ? "Trial Ends"
                        : "Next Billing"}
                </span>

                <strong>
                    {new Date(
                        profile.subscription.renewal_date
                    ).toLocaleDateString()}
                </strong>
            </div>

        </div>

        {profile.subscription.premium ? (
            <p>
                You currently have access to SmartNotes premium
                features.
            </p>
        ) : (
            <p>
                Your trial has ended. Upgrade to continue using
                SmartNotes AI features.
            </p>
        )}

        <Link to='/pricing' className={styles.upgradeButton}>
            {profile.subscription.premium
                ? "Upgrade Plan"
                : "Upgrade to Premium"}
        </Link>

    </section>

    </div>

           

    
            
    </div>
    );
}

export default Profile;