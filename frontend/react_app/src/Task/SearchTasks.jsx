import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";
import styles from "./Search.module.css"

function SearchTasks() {
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
      const res = await api.get(`/notes/search_tasks/?q=${text}`);
      setResults(res.data);
    } catch (err) {
      console.error("Task search error:", err.response?.data || err.message);
    }
  };
  return (
    <div className={styles.search_con}>
      <input
        type="text"
        placeholder="Search task"
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        className={styles.search_input}
      />
      {results.map(task => (
        <div key={task.id} onClick={() => navigate(`/saved_task/${task.id}`)} className={styles.search_result}>
          <p>{task.todo_title} {task.todo_list.slice(0, 50)}...</p>
          {/* <p></p> */}
        </div>
      ))}
    </div>
  );
}
export default SearchTasks;