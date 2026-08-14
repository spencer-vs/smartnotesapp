import axios from "axios";

const api = axios.create({
    baseURL: "https://smartnoteapi.onrender.com/api/",
});


/* Handle expired access tokens and subscription errors */
api.interceptors.response.use(
    res => res,

    async err => {
        const originalRequest = err.config;

        /* --------------------------------
           401 — Access token expired
        -------------------------------- */
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

        /* --------------------------------
           403 — Subscription / Permission
        -------------------------------- */

        if (err.response?.status === 403) {

            console.log(
                "Subscription/permission error:",
                err.response.data
            );

            // Keep the original error intact so
            // individual components can display
            // the backend message.
            return Promise.reject(err);
        }

        return Promise.reject(err);
    }
);

export default api;





