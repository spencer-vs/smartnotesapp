import React from "react"
import { createContext, useState, useEffect } from "react";
import api from "../api/axios";


export const AuthContext = createContext();
export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState({
    access: null,
    refresh: null,
    user: null,
    isAuthenticated: false,
    loading: true,
  });
  // 🔹 Load token on app start
  useEffect(() => {
    const access = localStorage.getItem("access");
    const refresh = localStorage.getItem("refresh");
    if (access && refresh) {
      api.defaults.headers.Authorization = `Bearer ${access}`;
      api.get("/auth/user/")
        .then(res => {
          setAuth({
            access,
            refresh,
            user: res.data,
            isAuthenticated: true,
            loading: false,
          });

        })
        .catch(() => logout());
    } else {
      setAuth(prev => ({ ...prev, loading: false }));
    }
  }, []);
  // 🔹 Login
  const login = async (data) => {
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("token", data.access);
    api.defaults.headers.Authorization = `Bearer ${data.access}`;
    const res = await api.get("/auth/user/");
    setAuth({
      access: data.access,
      refresh: data.refresh,
      user: res.data,
      isAuthenticated: true,
      loading: false,
    });
  };
  // 🔹 Logout
  const logout = () => {
    localStorage.clear();
    delete api.defaults.headers.Authorization;
    setAuth({
      access: null,
      refresh: null,
      user: null,
      isAuthenticated: false,
      loading: false,
    });
  };
  return (
    <AuthContext.Provider value={{ auth, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};