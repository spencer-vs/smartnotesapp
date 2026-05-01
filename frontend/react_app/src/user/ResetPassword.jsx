import React, { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import styles from "Resetassword.module.css"


const ResetPassword = () => {
  const { uid, token } = useParams();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!password || !confirmPassword) {
      alert("Fill all fields");
      return;
    }
    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }
    try {
      setLoading(true);
      await api.post(`auth/reset-password/${uid}/${token}/`, {
        password,
      });
      alert("Password reset successful");
      navigate("/signin");
    } catch (err) {
      console.log(err);
      alert("Invalid or expired link");
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className={styles.new_con}>
      <h2>Reset Password</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.new_pass}
        />
        <input
          type="password"
          placeholder="Confirm password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className={styles.new_pass}
        />
        <button type="submit" disabled={loading} className={styles.new_btn}>
          {loading ? "Resetting..." : "Reset Password"}
        </button>
      </form>
    </div>
  );
};
export default ResetPassword;