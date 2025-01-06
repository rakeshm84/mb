import axios from "axios";
import useAuth from "hooks/useAuth";

const useAPI = () => {
  const { BASE_URL, getAccessToken, refreshAccessToken, logout } = useAuth();

  const api = axios.create({
    baseURL: BASE_URL,
  });

  // Add an interceptor to attach the access token to requests
  api.interceptors.request.use(
    async (config) => {
      const accessToken = getAccessToken();
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Add an interceptor to handle token expiration
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const newAccessToken = await refreshAccessToken();
          axios.defaults.headers.common["Authorization"] = `Bearer ${newAccessToken}`;
          return api(originalRequest);
        } catch (refreshError) {
          logout();
          return Promise.reject(refreshError);
        }
      }
      return Promise.reject(error);
    }
  );

  return { api };
};

export default useAPI;
