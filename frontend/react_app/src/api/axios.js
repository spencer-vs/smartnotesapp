import axios from "axios";

const api = axios.create({
    baseURL: "https://smartnoteapi.onrender.com/api/",
});


/* Attach access token to every request */
api.interceptors.request.use(
    config => {
        const access = localStorage.getItem("access");

          console.log(
            "API REQUEST:",
            config.url,
            "Has token:",
            !!access
        );

        if (access) {
            config.headers.Authorization = `Bearer ${access}`;
        }

        return config;
    },
    error => Promise.reject(error)
);


/* Handle expired access tokens */
api.interceptors.response.use(
    res => res,

    async err => {
        const originalRequest = err.config;

        if (
            err.response?.status === 401 &&
            !originalRequest._retry
        ) {
            originalRequest._retry = true;

            try {
                const refresh = localStorage.getItem("refresh");

                if (!refresh) {
                    return Promise.reject(err);
                }

                const response = await axios.post(
                    "https://smartnoteapi.onrender.com/api/auth/token/refresh/",
                    { refresh }
                );

                localStorage.setItem(
                    "access",
                    response.data.access
                );

                originalRequest.headers.Authorization =
                    `Bearer ${response.data.access}`;

                return api(originalRequest);

            } catch (refreshError) {
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(err);
    }
);

export default api;





// import axios from "axios";
// const api = axios.create({
//   baseURL: "https://smartnoteapi.onrender.com/api/",
// });
// api.interceptors.response.use(
//   res => res,
//   async err => {
//     const originalRequest = err.config;
//     if (err.response?.status === 401 && !originalRequest._retry) {
//       originalRequest._retry = true;
//       const refresh = localStorage.getItem("refresh");
//       const response = await axios.post(
//         "https://smartnoteapi.onrender.com/api/auth/token/refresh/",
//         { refresh }
//       );
//       localStorage.setItem("access", response.data.access);
//       originalRequest.headers.Authorization =
//         `Bearer ${response.data.access}`;
//       return api(originalRequest);
//     }
//     return Promise.reject(err);
//   }
// );
// export default api;