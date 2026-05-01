// import axios from "axios"


// const api = axios.create({
//   baseURL: `${import.meta.env.VITE_API_URL}/api`,
// })

// //console.log("API URL:", import.meta.env.VITE_API_URL)

// api.interceptors.request.use((config) =>
// {
//     const token = localStorage.getItem("access");
//    // console.log("Sending token:", token);
//     if (token
//         && !config.url.includes("auth/register")
//         && !config.url.includes("auth/token")
//     ) {
//         config.headers.Authorization = `Bearer ${token}`;
//     }
//     return config;
// },
//     (error) => Promise.reject(error)
// );
// export default api





import axios from "axios";
const api = axios.create({
  baseURL: "https://smartnoteapi.onrender.com/api/",
});
api.interceptors.response.use(
  res => res,
  async err => {
    const originalRequest = err.config;
    if (err.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refresh = localStorage.getItem("refresh");
      const response = await axios.post(
        "https://smartnoteapi.onrender.com/api/auth/token/refresh/",
        { refresh }
      );
      localStorage.setItem("access", response.data.access);
      originalRequest.headers.Authorization =
        `Bearer ${response.data.access}`;
      return api(originalRequest);
    }
    return Promise.reject(err);
  }
);
export default api;