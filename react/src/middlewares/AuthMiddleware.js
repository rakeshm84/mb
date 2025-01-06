import React, { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import PropTypes from "prop-types";
import axios from "axios";
import useAuth from "hooks/useAuth";

const BASE_URL = "http://127.0.0.1:8000/api"; // Your Django backend URL

const AuthMiddleware = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // Track authentication status
  const location = useLocation();
  const { user, saveUser } = useAuth();

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
      await axios.post(`${BASE_URL}/authentication/verify/`, { token: accessToken });
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response && error.response.status === 401) {
        // Token is invalid or expired, attempt to refresh
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          try {
            const response = await axios.post(`${BASE_URL}/authentication/refresh/`, {
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
    if (isAuthenticated) {
      const accessToken = getAccessToken();
      validateUser(accessToken);
    }
  }, [isAuthenticated]);

  const validateUser = async (accessToken) => {
    if (!user) {
      const response = await axios.get(`${BASE_URL}/authentication/user/`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      saveUser(response.data);
    }
  };

  // Run token validation on mount
  useEffect(() => {
    validateToken();
  }, []);

  // Handle authentication state
  if (isAuthenticated === null) {
    return <div>Loading...</div>; // Optionally show a loading spinner
  }

  if (!isAuthenticated) {
    return <Navigate to="/authentication/sign-in" state={{ from: location }} />;
  }

  return children;
};

AuthMiddleware.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AuthMiddleware;
