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



  const shareTutorial = async (tutorial) => {
  if (!tutorial) return;
  const shareText = `${tutorial.title || "No Title"}\n\n${tutorial.text || "No Content"}`;
  try {
    if (navigator.share) {
      await navigator.share({
        title: tutorial.title || "Tutorial",
        text: shareText,
      });
    } else {
      await navigator.clipboard.writeText(shareText);
      alert("Tutorial copied to clipboard");
    }
  } catch (err) {
    console.log("Share cancelled", err);
  }
};

  return (
    <>
      <div className={styles.viewTots}>
        <THeader />
        {loading ? (
          <div className={styles.loader}></div>
        ) : tutorial ? (
          <>
            <div className={styles.tutorials}>
            <h1 className={styles.tots_header}>{tutorial.title}</h1>
            <p className={styles.tots_text}>{tutorial.text}</p>

           <button
  className={styles.shareBtn}
  onClick={() => shareTutorial(tutorial)}
>
  Share
</button>
            </div>
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