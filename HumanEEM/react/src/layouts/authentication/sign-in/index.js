import { useState } from "react";

// react-router-dom components
import { Link, useNavigate, useLocation } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Switch from "@mui/material/Switch";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";

// @mui icons
import FacebookIcon from "@mui/icons-material/Facebook";
import GitHubIcon from "@mui/icons-material/GitHub";
import GoogleIcon from "@mui/icons-material/Google";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

// Authentication layout components
import BasicLayout from "layouts/authentication/components/BasicLayout";

// Images
import bgImage from "assets/images/bg-sign-in-basic.jpeg";

import useAuth from "hooks/useAuth";
import AlertMessage from "components/UI/AlertMessage";
import useAlert from "hooks/useAlert";
import useConstants from "constants";
import axios from "axios";

function Basic() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [user, setuser] = useState(false);

  const { login } = useAuth();
  const { ADMIN_URL, AUTH_API_URL } = useConstants();

  const navigate = useNavigate();
  const location = useLocation();

  const [rememberMe, setRememberMe] = useState(false);
  const { errorState, showAlert } = useAlert();

  const handleSetRememberMe = () => setRememberMe(!rememberMe);

  const handleSubmit = async (e) => {
    try {
      // const response = await login(username, password);
      const cookieRes = await axios.get(`${AUTH_API_URL}/get-authentication/`, {
        withCredentials: true,
      });
      console.log(cookieRes);

      if (cookieRes) {
        setuser(true);
        // if (res.Status === 200) {
        //   window.location.replace(ADMIN_URL);
        // } else {
        //   // showAlert("error", "Something Went Wrong.");
        // }
        // window.location.replace("http://localhost:3001/dashboard");
        // if (res) {
        //   const cookieRes = await axios.get(`${AUTH_API_URL}/get-authentication/`, {
        //     withCredentials: true,
        //   });
        //   // Handle the cookie response
        //   console.log(cookieRes.data);
        // }
      }
    } catch (error) {
      // console.error("An error occurred:", error);
      // const data = error.response.data;
      // showAlert("error", data.detail);
    }
  };

  handleSubmit();
  return (
    <BasicLayout image={bgImage}>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="info"
          mx={2}
          mt={-3}
          p={2}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            {t("")}
          </MDTypography>
          <Grid container spacing={3} justifyContent="center" sx={{ mt: 1, mb: 2 }}>
            <Grid item xs={2}>
              <MDTypography component={MuiLink} href="#" variant="body1" color="white">
                <FacebookIcon color="inherit" />
              </MDTypography>
            </Grid>
            <Grid item xs={2}>
              <MDTypography component={MuiLink} href="#" variant="body1" color="white">
                <GitHubIcon color="inherit" />
              </MDTypography>
            </Grid>
            <Grid item xs={2}>
              <MDTypography component={MuiLink} href="#" variant="body1" color="white">
                <GoogleIcon color="inherit" />
              </MDTypography>
            </Grid>
          </Grid>
        </MDBox>
        <MDBox pt={4} pb={3} px={3}>
          <MDBox component="form" role="form" onSubmit={handleSubmit}>
            {user && (
              <>
                <h1>User logged In</h1>{" "}
              </>
            )}

            {user && (
              <>
                <h1>{JSON.stringify(cookieRes)}</h1>{" "}
              </>
            )}
          </MDBox>
        </MDBox>
      </Card>
      <AlertMessage {...errorState} />
    </BasicLayout>
  );
}

export default Basic;
