import React, { useState, useEffect } from "react";
import styles from "./ViewT.module.css";
import THeader from "./THeader";
import Footer from "../ui/Footer";
import { useParams } from "react-router-dom";
import api from "../api/axios";
const ViewT = () => {
  const { id } = useParams();
  const [tutorial, setTutorial] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    api.get(`notes/tutorial/${id}/`)
      .then(res => {
        console.log("Tutorial:", res.data);
        setTutorial(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.log(err);
        setLoading(false);
      });
  }, [id]);
  return (
    <>
      <div className={styles.viewTots}>
        <THeader />
        {loading ? (
          <p>Loading...</p>
        ) : tutorial ? (
          <>
            <h1>{tutorial.title}</h1>
            <p>{tutorial.text}</p>
          </>
        ) : (
          <p>No tutorial found</p>
        )}
      </div>
      <Footer />
    </>
  );
};
export default ViewT;