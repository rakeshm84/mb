import { useState, useEffect, useMemo } from "react";

// react-router components
import { Routes, Route, Navigate, useLocation } from "react-router-dom";

// @mui material components
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Material Dashboard 2 React themes
import theme from "assets/theme";
import themeRTL from "assets/theme/theme-rtl";

// Material Dashboard 2 React Dark Mode themes
import themeDark from "assets/theme-dark";
import themeDarkRTL from "assets/theme-dark/theme-rtl";

// RTL plugins
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";

// Material Dashboard 2 React routes
import { routes, admin_routes, human_tenant_routes } from "routes";

// Material Dashboard 2 React contexts
import { useMaterialUIController } from "context";

// Images
import brandWhite from "assets/images/logo-ct.png";
import brandDark from "assets/images/logo-ct-dark.png";

import AuthMiddleware from "middlewares/AuthMiddleware";
import NoAuthMiddleware from "middlewares/NoAuthMiddleware";
import useAuth from "hooks/useAuth";

export default function App() {
  const { user } = useAuth();
  const [controller, dispatch] = useMaterialUIController();
  const { direction, darkMode } = controller;
  const [rtlCache, setRtlCache] = useState(null);
  const { pathname } = useLocation();

  // Cache for the rtl
  useMemo(() => {
    const cacheRtl = createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });

    setRtlCache(cacheRtl);
  }, []);

  // Setting the dir attribute for the body element
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Setting page scroll to 0 when changing the route
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  const signInRoutes = ["/authentication/sign-in", "/authentication/sign-up"];

  const getRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) {
        return getRoutes(route.collapse);
      }

      if (route.route) {
        if (signInRoutes.includes(route.route)) {
          return (
            <Route
              exact
              path={route.route}
              element={<NoAuthMiddleware>{route.component}</NoAuthMiddleware>}
              key={route.key}
            />
          );
        } else {
          return (
            <Route
              exact
              path={route.route}
              element={<AuthMiddleware>{route.component}</AuthMiddleware>}
              key={route.key}
            />
          );
        }
      }

      return null;
    });

  return direction === "rtl" ? (
    <CacheProvider value={rtlCache}>
      <ThemeProvider theme={darkMode ? themeDarkRTL : themeRTL}>
        <CssBaseline />
        <Routes>{getRoutes([...routes])}</Routes>
      </ThemeProvider>
    </CacheProvider>
  ) : (
    <ThemeProvider theme={darkMode ? themeDark : theme}>
      <CssBaseline />
      <Routes>{getRoutes([...routes])}</Routes>
    </ThemeProvider>
  );
}
