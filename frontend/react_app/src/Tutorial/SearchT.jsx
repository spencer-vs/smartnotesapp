import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import styles from "./SearchT.module.css"

function SearchT() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const navigate = useNavigate();
  const handleSearch = async (text) => {
    setQuery(text);
    if (!text.trim()) {
      setResults([]);
      return;
    }
    try {
      const res = await api.get(`notes/search_tutorials/?q=${text}`);
      setResults(res.data);
    } catch (err) {
      console.error("Tutorial search error:", err.response?.data || err.message);
    }
  };
  return (
    <div className={styles.search_con}>
      <input
        type="text"
        placeholder="Search Tutorial"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        className={styles.search_input}
      />
      {results.map(tutorial => (
        <div key={tutorial.id} onClick={() => navigate(`/viewtutorials/${tutorial.id}/`)} className={styles.search_result}>
          <p>{tutorial.youtube_title} {tutorial.tutorial_text.slice(0, 50)}...</p>
          {/* <p></p> */}
        </div>
      ))}
    </div>
  );
}
export default SearchT;