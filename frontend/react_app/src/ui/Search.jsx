import React from "react"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "../api/axios"
import styles from "./Search.module.css"
import Header from "./Header"
import Footer from "./Footer"



function SearchNotes() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState([])
  const navigate = useNavigate()
  
  
  const handleSearch = async (text) => {
    setQuery(text)
    if (!text) {
      setResults([])
      return
    }
    const res = await api.get(`/notes/search/?q=${text}`)
    setResults(res.data)
  }
  return (
    <>
    {/* <Header /> */}
    
    <div className={styles.searchPage}>

    <div className={styles.searcBox}>
      <input
        className={styles.searchInput}
        placeholder="Search your notes..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
      />
      <div className={styles.searchResults}>
        {results.map(note => (
          <div
            key={note.id}
            className={styles.searchNote}
            onClick={() => navigate(`/notes/${note.id}/update`)}
          >
            <h4>{note.title}</h4>
            <p>{note.content.slice(0, 80)}...</p>
          </div>
        ))}
      </div>
      </div>
    </div>

    <Footer />
    </>
  )
}

export default SearchNotes