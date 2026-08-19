import axios from "axios";

const api = axios.create({
    baseURL: "https://smartnoteapi.onrender.com/api/",
});


/* =========================================
   HANDLE EXPIRED ACCESS TOKENS
========================================= */

api.interceptors.response.use(

    response => response,

    async error => {

        const originalRequest = error.config;


        /* =====================================
           401 — ACCESS TOKEN EXPIRED
        ===================================== */

        if (
            error.response?.status === 401 &&
            !originalRequest?._retry
        ) {

            const requestUrl =
                originalRequest?.url || "";


            /*
             * Never attempt token refresh for
             * authentication endpoints.
             */

            const isAuthRequest =
                requestUrl.includes(
                    "/auth/token/"
                ) ||
                requestUrl.includes(
                    "/auth/token/refresh/"
                );


            if (isAuthRequest) {

                return Promise.reject(error);

            }


            originalRequest._retry = true;


            try {

                const refresh =
                    localStorage.getItem("refresh");


                if (!refresh) {

                    return Promise.reject(error);

                }


                const response = await axios.post(
                    "https://smartnoteapi.onrender.com/api/auth/token/refresh/",
                    {
                        refresh
                    }
                );


                const newAccess =
                    response.data.access;


                localStorage.setItem(
                    "access",
                    newAccess
                );


                localStorage.setItem(
                    "token",
                    newAccess
                );


                /*
                 * Update Axios default header.
                 */

                api.defaults.headers.Authorization =
                    `Bearer ${newAccess}`;


                /*
                 * Update the original failed request.
                 */

                originalRequest.headers =
                    originalRequest.headers || {};


                originalRequest.headers.Authorization =
                    `Bearer ${newAccess}`;


                return api(originalRequest);


            } catch (refreshError) {

                console.error(
                    "Token refresh failed:",
                    refreshError
                );


                /*
                 * Remove invalid authentication
                 * credentials.
                 */

                localStorage.removeItem(
                    "access"
                );

                localStorage.removeItem(
                    "refresh"
                );

                localStorage.removeItem(
                    "token"
                );


                delete api.defaults.headers.Authorization;


                return Promise.reject(
                    refreshError
                );

            }

        }


        /* =====================================
           403 — SUBSCRIPTION / PERMISSION
        ===================================== */

        if (
            error.response?.status === 403
        ) {

            console.log(
                "Subscription/permission error:",
                error.response.data
            );

        }


        return Promise.reject(error);

    }
);


export default api;