import axios from "axios";
import useLanguageSwitcher from "hooks/useLanguageSwitcher";

const useAuth = () => {
  const { switchLanguage } = useLanguageSwitcher();

  const BASE_URL = process.env.REACT_APP_API_URL; // Your Django backend URL
  // const BASE_URL = "http://127.0.0.1:8000/api"; // Your Django backend URL
  // const BASE_URL = "http://john.mbapi.local:8000/api"; // Your Django backend URL

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${BASE_URL}/authentication/`, { username, password });
      saveTokens(response.data);
      saveUser(response.data.user);
      switchLanguage(response.data.user.lang);
      return response.data;
    } catch (error) {
      console.error("Login failed", error);
      throw error;
    }
  };

  const saveTokens = (tokens) => {
    localStorage.setItem("accessToken", tokens.access);
    localStorage.setItem("refreshToken", tokens.refresh);
  };

  const user =
    sessionStorage.getItem("user") !== "undefined" && sessionStorage.getItem("user") !== "null"
      ? JSON.parse(sessionStorage.getItem("user"))
      : {};

  const saveUser = (user) => {
    sessionStorage.setItem("user", JSON.stringify(user));
  };

  const getAccessToken = () => localStorage.getItem("accessToken");
  const getRefreshToken = () => localStorage.getItem("refreshToken");

  const refreshAccessToken = async () => {
    try {
      const response = await axios.post(`${BASE_URL}/authentication/refresh/`, {
        refresh: getRefreshToken(),
      });
      saveTokens({ access: response.data.access, refresh: getRefreshToken() });
      return response.data.access;
    } catch (error) {
      console.error("Token refresh failed", error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    switchLanguage("en");
  };

  return {
    BASE_URL,
    login,
    saveTokens,
    saveUser,
    getAccessToken,
    getRefreshToken,
    refreshAccessToken,
    logout,
    user,
  };
};

export default useAuth;
