import React, { useState, useEffect  } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import styles from "./SearchT.module.css"

function SearchT() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const navigate = useNavigate();



   useEffect(() => {
    const timer = setTimeout(async () => {

        if (!query.trim()) {
            setResults([]);
            return;
        }

        try {
            const res = await api.get(
                `notes/search_tutorials/?q=${encodeURIComponent(query)}`
            );

            setResults(res.data);

        } catch (err) {
            console.error(
                "Tutorial search error:",
                err.response?.data || err.message
            );
        }

    }, 400); // Wait 400 ms after typing stops

    return () => clearTimeout(timer);

    }, [query]);





  return (
    <div className={styles.search_con}>
      <input
       type="text"
       placeholder="Search Tutorial"
       value={query}
       onChange={(e) => setQuery(e.target.value)}
       className={styles.search_input}
    />
    {results.map((tutorial) => (
    <div
        key={tutorial.id}
        className={styles.search_result}
        onClick={() => navigate(`/viewtutorials/${tutorial.id}`)}
    >
        <h4>{tutorial.youtube_title}</h4>

        <p>
            {(tutorial.youtube_text || "").slice(0, 80)}
            {tutorial.youtube_text?.length > 80 ? "..." : ""}
        </p>
    </div>
    ))} 
    </div>
    );
}
export default SearchT;