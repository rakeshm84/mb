import { useState, useEffect } from "react";

// react-router components
import { useLocation, Link, useNavigate } from "react-router-dom";

// prop-types is a library for typechecking of props.
import PropTypes from "prop-types";

// @material-ui core components
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import Icon from "@mui/material/Icon";
import MenuItem from "@mui/material/MenuItem";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDInput from "components/MDInput";

// Material Dashboard 2 React example components
import Breadcrumbs from "examples/Breadcrumbs";
import NotificationItem from "examples/Items/NotificationItem";

// Custom styles for DashboardNavbar
import {
  navbar,
  navbarContainer,
  navbarRow,
  navbarIconButton,
  navbarMobileMenu,
} from "examples/Navbars/DashboardNavbar/styles";

// Material Dashboard 2 React context
import {
  useMaterialUIController,
  setTransparentNavbar,
  setMiniSidenav,
  setOpenConfigurator,
  setDirection,
} from "context";

import TranslateIcon from "@mui/icons-material/Translate";
// import { routes, admin_routes, human_tenant_routes } from "../../../routes";
import { routes } from "../../../routes";
import useLanguageSwitcher from "../../../hooks/useLanguageSwitcher";
import useAuth from "hooks/useAuth";
import useAPI from "hooks/useAPI";

function DashboardNavbar({ absolute, light, isMini }) {
  const [navbarType, setNavbarType] = useState();
  const [controller, dispatch] = useMaterialUIController();
  const { miniSidenav, transparentNavbar, fixedNavbar, darkMode } = controller;
  const [openMenu, setOpenMenu] = useState(false);
  const [openLanguageMenu, setOpenLanguageMenu] = useState(false);
  const [openUserMenu, setOpenUserMenu] = useState(false);
  const route = useLocation().pathname.split("/").slice(1);
  const navigate = useNavigate();
  const { switchLanguage, getActiveLang } = useLanguageSwitcher();
  const { logout, user } = useAuth();
  const { api } = useAPI();

  const pages = routes;
  const all_routes = routes;
  const routeObject = all_routes.find((r) => r.key === route[0]);
  const PageHeader = () => {
    const pagesList = [routeObject];
    return <Breadcrumbs pagesList={pagesList} />;
  };

  useEffect(() => {
    // Setting the navbar type
    if (fixedNavbar) {
      setNavbarType("sticky");
    } else {
      setNavbarType("static");
    }

    // A function that sets the transparent state of the navbar.
    function handleTransparentNavbar() {
      setTransparentNavbar(dispatch, (fixedNavbar && window.scrollY === 0) || !fixedNavbar);
    }

    /** 
     The event listener that's calling the handleTransparentNavbar function when 
     scrolling the window.
    */
    window.addEventListener("scroll", handleTransparentNavbar);

    // Call the handleTransparentNavbar function to set the state with the initial value.
    handleTransparentNavbar();

    // Remove event listener on cleanup
    return () => window.removeEventListener("scroll", handleTransparentNavbar);
  }, [dispatch, fixedNavbar]);

  const handleMiniSidenav = () => setMiniSidenav(dispatch, !miniSidenav);
  const handleOpenMenu = (event) => setOpenMenu(event.currentTarget);
  const handleOpenUserMenu = (event) => setOpenUserMenu(event.currentTarget);
  const handleCloseMenu = () => setOpenMenu(false);
  const handleCloseUserMenu = () => setOpenUserMenu(false);
  const handleOpenLanguageMenu = (event) => setOpenLanguageMenu(event.currentTarget);
  const handleCloseLanguageMenu = () => setOpenLanguageMenu(false);

  // Change the language
  const handleLanguageChange = async (event) => {
    try {
      const selectedLanguage = event.target.value;
      if (getActiveLang() === selectedLanguage) return;
      var response = await api.post(`/set-language/`, { language: selectedLanguage });
      if (response.status == 200) {
        switchLanguage(selectedLanguage);
      } else {
        console.warn("Unexpected response from server:", response);
      }
    } catch (error) {
      console.error("Error changing language:", error.message);
    }
  };

  // Render the notifications menu
  const renderMenu = () => (
    <Menu
      anchorEl={openMenu}
      anchorReference={null}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "left",
      }}
      open={Boolean(openMenu)}
      onClose={handleCloseMenu}
      sx={{ mt: 2 }}
    >
      <NotificationItem icon={<Icon>email</Icon>} title="Check new messages" />
      <NotificationItem icon={<Icon>podcasts</Icon>} title="Manage Podcast sessions" />
      <NotificationItem icon={<Icon>shopping_cart</Icon>} title="Payment successfully completed" />
    </Menu>
  );

  // Render the user menu
  const renderUserMenu = () => (
    <Menu
      anchorEl={openUserMenu}
      anchorReference={null}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "left",
      }}
      open={Boolean(openUserMenu)}
      onClose={handleCloseUserMenu}
      sx={{ mt: 2 }}
    >
      <Link to="/profile">
        <NotificationItem icon={<Icon>person</Icon>} title={t("lang.profile")} />
      </Link>
      <NotificationItem
        icon={<Icon>logout</Icon>}
        title={t("lang.logout")}
        onClick={handleLogout}
      />
    </Menu>
  );

  const handleLogout = () => {
    logout();

    const redirectTo = "/sign-in";
    navigate(redirectTo);
  };

  // Render the language menu
  const renderLanguageMenu = () => (
    <Menu
      anchorEl={openLanguageMenu}
      anchorReference={null}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "left",
      }}
      open={Boolean(openLanguageMenu)}
      onClose={handleCloseLanguageMenu}
      sx={{ mt: 2 }}
    >
      <MenuItem onClick={() => handleLanguageChange({ target: { value: "en" } })}>English</MenuItem>
      <MenuItem onClick={() => handleLanguageChange({ target: { value: "he" } })}>עִברִית</MenuItem>
    </Menu>
  );

  // Styles for the navbar icons
  const iconsStyle = ({ palette: { dark, white, text }, functions: { rgba } }) => ({
    color: () => {
      let colorValue = light || darkMode ? white.main : dark.main;

      if (transparentNavbar && !light) {
        colorValue = darkMode ? rgba(text.main, 0.6) : text.main;
      }

      return colorValue;
    },
  });

  return (
    <AppBar
      position={absolute ? "absolute" : navbarType}
      color="inherit"
      sx={(theme) => navbar(theme, { transparentNavbar, absolute, light, darkMode })}
    >
      <Toolbar sx={(theme) => navbarContainer(theme)}>
        <MDBox color="inherit" mb={{ xs: 1, md: 0 }} sx={(theme) => navbarRow(theme, { isMini })}>
          <PageHeader />
        </MDBox>
        {isMini ? null : (
          <MDBox sx={(theme) => navbarRow(theme, { isMini })}>
            <MDBox pr={1}>
              <MDInput label="Search here" />
            </MDBox>
            <MDBox color={light ? "white" : "inherit"}>
              <IconButton
                size="small"
                disableRipple
                color="inherit"
                sx={navbarIconButton}
                aria-controls="language-menu"
                aria-haspopup="true"
                variant="contained"
                onClick={handleOpenLanguageMenu}
              >
                <TranslateIcon sx={iconsStyle} />
              </IconButton>
              {renderLanguageMenu()}
              <IconButton
                size="small"
                disableRipple
                color="inherit"
                sx={navbarIconButton}
                aria-controls="user-menu"
                aria-haspopup="true"
                variant="contained"
                onClick={handleOpenUserMenu}
              >
                <Icon sx={iconsStyle}>account_circle</Icon>
              </IconButton>
              {renderUserMenu()}
              <IconButton
                size="small"
                disableRipple
                color="inherit"
                sx={navbarMobileMenu}
                onClick={handleMiniSidenav}
              >
                <Icon sx={iconsStyle} fontSize="medium">
                  {miniSidenav ? "menu_open" : "menu"}
                </Icon>
              </IconButton>
              <IconButton
                size="small"
                disableRipple
                color="inherit"
                sx={navbarIconButton}
                aria-controls="notification-menu"
                aria-haspopup="true"
                variant="contained"
                onClick={handleOpenMenu}
              >
                <Icon sx={iconsStyle}>notifications</Icon>
              </IconButton>
              {renderMenu()}
            </MDBox>
          </MDBox>
        )}
      </Toolbar>
    </AppBar>
  );
}

// Setting default values for the props of DashboardNavbar
DashboardNavbar.defaultProps = {
  absolute: false,
  light: false,
  isMini: false,
};

// Typechecking props for the DashboardNavbar
DashboardNavbar.propTypes = {
  absolute: PropTypes.bool,
  light: PropTypes.bool,
  isMini: PropTypes.bool,
};

export default DashboardNavbar;
