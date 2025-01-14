import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import PropTypes from "prop-types";
import axios from "axios";
import useAuth from "hooks/useAuth";

const NoAuthMiddleware = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // Track authentication status
  const { BASE_URL, getAccessToken } = useAuth();

  // Validate token
  const validateToken = async () => {
    const token = getAccessToken();

    if (!token) {
      setIsAuthenticated(false); // No token, allow rendering children
      return;
    }

    try {
      // Validate the access token
      await axios.post(`${BASE_URL}/authentication/verify/`, { token });
      setIsAuthenticated(true); // Token is valid, redirect to dashboard
    } catch (error) {
      setIsAuthenticated(false); // Token is invalid, allow rendering children
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

  if (isAuthenticated) {
    return <Navigate to="/dashboard" />; // Redirect to dashboard if authenticated
  }

  return children; // Render login components if not authenticated
};

NoAuthMiddleware.propTypes = {
  children: PropTypes.node.isRequired,
};

export default NoAuthMiddleware;
