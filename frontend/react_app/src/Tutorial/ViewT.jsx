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



  const shareTutorial = async () => {
  if (!tutorial) return;
  const shareText = `${tutorial.title || "No Title"}\n\n${tutorial.text || "No Content"}`;
  const file = new File(
    [shareText],
    `${(tutorial.title || "Tutorial").replace(/\s+/g, "_")}.txt`,
    { type: "text/plain" }
  );
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try {
      await navigator.share({
        title: tutorial.title,
        text: shareText,
        files: [file],
      });
    } catch {
      console.log("Share cancelled");
    }
  } else {
    const blobUrl = URL.createObjectURL(file);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = file.name;
    a.click();
    URL.revokeObjectURL(blobUrl);
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

            <button className={styles.shareBtn} onClick={shareTutorial}>
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