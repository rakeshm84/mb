import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import axios from "axios";
import useAuth from "hooks/useAuth";
import useConstants from "constants";

const AuthMiddleware = ({ children }) => {
  const { AUTH_URL, AUTH_API_URL } = useConstants();
  const [isAuthenticated, setIsAuthenticated] = useState(null); // Track authentication status
  const location = useLocation();
  const { user, saveUser, BASE_URL } = useAuth();

  // Helper functions to manage tokens
  const getAccessToken = () => localStorage.getItem("accessToken");
  const getRefreshToken = () => localStorage.getItem("refreshToken");
  const saveTokens = (accessToken, refreshToken) => {
    localStorage.setItem("accessToken", accessToken);
    localStorage.setItem("refreshToken", refreshToken);
  };
  const clearTokens = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
  };

  // Validate and refresh token if necessary
  const validateToken = async () => {
    const accessToken = getAccessToken();

    if (!accessToken) {
      setIsAuthenticated(false);
      return;
    }

    try {
      // Validate the access token
      await axios.post(`${AUTH_API_URL}/authentication/verify/`, { token: accessToken });
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        // Token is invalid or expired, attempt to refresh
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          try {
            const response = await axios.post(`${AUTH_API_URL}/authentication/refresh/`, {
              refresh: refreshToken,
            });
            saveTokens(response.data.access, refreshToken);
            setIsAuthenticated(true);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            clearTokens();
            setIsAuthenticated(false);
          }
        } else {
          // No refresh token available, redirect to login
          setIsAuthenticated(false);
        }
      } else {
        setIsAuthenticated(false);
      }
    }
  };

  useEffect(() => {
    const validateUserAsync = async () => {
      if (isAuthenticated) {
        const accessToken = getAccessToken();
        await validateUser(accessToken);
      }
    };
    validateUserAsync();
  }, [isAuthenticated]);

  const validateUser = async (accessToken) => {
    if (!user) {
      const response = await axios.get(`${AUTH_API_URL}/authentication/user/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      saveUser(response.data);
    }
  };

  const setAuthTokens = async () => {
    const accessToken = getAccessToken();

    if (!accessToken) {
      const auth_response = await axios.get(`${AUTH_API_URL}/get-authentication/`, {
        withCredentials: true,
      });

      if (auth_response) {
        saveTokens(auth_response.data.auth_token, auth_response.data.refresh_token);
      }
    }
  };

  // Run token validation on mount
  useEffect(() => {
    const validateAuthentication = async () => {
      await setAuthTokens();
      await validateToken();
    };
    validateAuthentication();
  }, []);

  // Handle authentication state
  if (isAuthenticated === null) {
    return <div>Loading...</div>; // Optionally show a loading spinner
  }

  if (!isAuthenticated) {
    window.location.assign(`${AUTH_URL}/sign-in`);
  }

  return children;
};

AuthMiddleware.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AuthMiddleware;
