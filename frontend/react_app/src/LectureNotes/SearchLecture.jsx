import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";


function SearchLectures() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const navigate = useNavigate();
 
  useEffect(() => {
  const delay = setTimeout(() => {
    if (query.trim()) {
      handleSearch(query);
    }
  }, 500);
  return () => clearTimeout(delay);
}, [query]);
 
 
  const handleSearch = async (text) => {
    setQuery(text);
    if (!text.trim()) {
      setResults([]);
      return;
    }
    try {
      const res = await api.get(`/notes/search_lectures/?q=${text}`);
      setResults(res.data);
    } catch (err) {
      console.error("Lecture search error:", err.response?.data || err.message);
    }
  };
  return (
    <div>
      {/* 🔥 You can switch this to type="date" */}
      <input
        type="text"
        placeholder="Search lectures or date (YYYY-MM-DD)"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
      />
      {results.map(lecture => (
        <div
          key={lecture.id}
          onClick={() => navigate(`/viewlecture/${lecture.id}`)}
        >
          {/* <p>{lecture.created_at}</p> */}
          <p>{lecture.created_at}  {lecture.lecture.slice(0, 80)}...</p>
        </div>
      ))}
    </div>
  );
}
export default SearchLectures;