import React, { useContext } from "react";
import { NavLink } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

import {
    FaFacebookF,
    FaXTwitter,
    FaEnvelope,
    FaYoutube
} from "react-icons/fa6";

import styles from "./footer.module.css";

// CHANGE THIS FILE NAME TO THE ACTUAL NAME OF YOUR LOGO
import logo from "../assets/img/smartnotes_logo.png";


const Footer = () => {

    const { auth } = useContext(AuthContext);


    return (

        <footer className={styles.container}>

            <div className={styles.footer}>

                {/* =========================
                    LEFT SECTION
                ========================= */}

                <div className={styles.brandSection}>

                    <div className={styles.logoContainer}>

                        <img
                            src={logo}
                            alt="SmartNotes Logo"
                            className={styles.logo}
                        />

                        <h2 className={styles.brandName}>
                            Smart<span>Notes</span>
                        </h2>

                    </div>


                    <div className={styles.brandDivider}></div>


                    <p className={styles.tagline}>
                        Your smart companion
                        <br />
                        for learning and productivity.
                    </p>

                </div>


                {/* =========================
                    SITE MAP
                ========================= */}

                <div className={styles.siteMap}>

                    <h3>
                        SITE MAP
                    </h3>


                    <ul>

                        <li>
                            <NavLink to="/">
                                <span>›</span>
                                Home
                            </NavLink>
                        </li>


                        <li>
                            <NavLink to="/about">
                                <span>›</span>
                                Developer
                            </NavLink>
                        </li>


                        {auth.isAuthenticated ? (

                            <>

                                <li>
                                    <NavLink to="/contact">
                                        <span>›</span>
                                        Contact
                                    </NavLink>
                                </li>

                            </>

                        ) : (

                            <>

                                <li>
                                    <NavLink to="/login">
                                        <span>›</span>
                                        Sign In
                                    </NavLink>
                                </li>


                                <li>
                                    <NavLink to="/signup">
                                        <span>›</span>
                                        Sign Up
                                    </NavLink>
                                </li>

                            </>

                        )}

                    </ul>

                </div>


                {/* =========================
                    RIGHT SECTION
                ========================= */}

                <div className={styles.rightSection}>

                    <div className={styles.rightDivider}></div>


                    <p className={styles.copyright}>
                        © {new Date().getFullYear()} SmartNotes.
                        All rights reserved.
                    </p>


                    <NavLink
                        to="/privacy-policy"
                        className={styles.privacy}
                    >
                        Privacy Policy
                    </NavLink>


                    {/* =========================
                        SOCIAL ICONS
                    ========================= */}

                    <div className={styles.socials}>

                        <a
                            href="#"
                            aria-label="Facebook"
                            className={styles.socialIcon}
                        >
                            <FaFacebookF />
                        </a>


                        <a
                            href="#"
                            aria-label="X"
                            className={styles.socialIcon}
                        >
                            <FaXTwitter />
                        </a>


                        <a
                            href="mailto:smartnotes@example.com"
                            aria-label="Email"
                            className={styles.socialIcon}
                        >
                            <FaEnvelope />
                        </a>


                        <a
                            href="#"
                            aria-label="YouTube"
                            className={styles.socialIcon}
                        >
                            <FaYoutube />
                        </a>

                    </div>

                </div>

            </div>

        </footer>
    );
};


export default Footer;