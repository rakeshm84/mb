import axios from "axios";
import useLanguageSwitcher from "hooks/useLanguageSwitcher";
import useConstants from "constants";
import { useMaterialUIController } from "context";

const useAuth = () => {
  const { switchLanguage } = useLanguageSwitcher();
  const { API_URL } = useConstants();
  const [controller, dispatch] = useMaterialUIController();
  const { setContextRenderCount } = controller;

  const BASE_URL = API_URL;
  // const BASE_URL = "http://mike.mbapi.local:8000/api";

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
    sessionStorage.removeItem("user");
    switchLanguage("en");
    setContextRenderCount(0);
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
