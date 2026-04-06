import React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api/axios"
import styles from "../ui/Search.module.css"



function SearchLectures() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const navigate = useNavigate()
  
  
  const handleSearch = async (text) => {
    setQuery(text)
    if (!text.trim()) {
      setResults([])
      return
    }
   try {
    const res = await api.get(`/notes/search_tasks/?q=${text}`)
    setResults(res.data)
   } catch (err) {
    console.error("Search error:", err.response?.data || err.message)
   }
  }
  return (
    <>
   
    
    <div className={styles.searchPage}>

    <div className={styles.searcBox}>
      <input
        className={styles.searchInput}
        placeholder="Search your tasks..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
      />
      <div className={styles.searchResults}>
        {results.map(new_todo => (
          <div
            key={new_todo.id}
            className={styles.searchNote}
            onClick={() => navigate(`/saved_task/${task.id}`)}
          >
            <h1>{new_todo.todo_title.slice(0, 80)}</h1>
            <p>{new_todo.todo_list.slice(0, 80)}...</p>
          </div>
        ))}
      </div>
      </div>
    </div>

   
    </>
  )
}

export default SearchLectures