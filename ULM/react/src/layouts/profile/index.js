// @mui material components
import Grid from "@mui/material/Grid";
import Divider from "@mui/material/Divider";

// @mui icons
import FacebookIcon from "@mui/icons-material/Facebook";
import TwitterIcon from "@mui/icons-material/Twitter";
import InstagramIcon from "@mui/icons-material/Instagram";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ProfileInfoCard from "examples/Cards/InfoCards/ProfileInfoCard";
import ProfilesList from "examples/Lists/ProfilesList";
import DefaultProjectCard from "examples/Cards/ProjectCards/DefaultProjectCard";

// Overview page components
import Header from "layouts/profile/components/Header";
import PlatformSettings from "layouts/profile/components/PlatformSettings";

// Data
import profilesListData from "layouts/profile/data/profilesListData";
import AlertMessage from "components/UI/AlertMessage";
import useAlert from "hooks/useAlert";

import useAuth from "hooks/useAuth";
import EditProfile from "./EditProfile";
import React, { useState } from "react";
import moment from "moment";

function Overview() {
  const { user } = useAuth();
  const [editMode, setEditMode] = useState(false);

  const handleEditProfile = () => {
    setEditMode((prevMode) => !prevMode);
  };
  const { errorState, showAlert } = useAlert();

  return (
    <React.Fragment>
      <DashboardLayout>
        <DashboardNavbar />
        <MDBox mb={2} />
        <Header user={user}>
          <MDBox mt={5} mb={3}>
            <Grid container spacing={1}>
              {/* <Grid item xs={12} md={6} xl={4}>
                <PlatformSettings />
              </Grid> */}
              <Grid item xs={12} md={6} xl={4} sx={{ display: "flex" }}>
                <Divider orientation="vertical" sx={{ ml: -2, mr: 1 }} />
                <ProfileInfoCard
                  title="profile information"
                  description={user?.desc || ""}
                  info={{
                    fullName:
                      user.first_name == ""
                        ? user.username
                        : user.first_name + " " + user.last_name,
                    mobile: user.phone,
                    email: user.email,
                    location: user.address,
                    birthDate: moment(user.date_of_birth).format("Do MMM YYYY"),
                  }}
                  // social={[
                  //   {
                  //     link: "https://www.facebook.com/",
                  //     icon: <FacebookIcon />,
                  //     color: "facebook",
                  //   },
                  //   {
                  //     link: "https://twitter.com/",
                  //     icon: <TwitterIcon />,
                  //     color: "twitter",
                  //   },
                  //   {
                  //     link: "https://www.instagram.com/",
                  //     icon: <InstagramIcon />,
                  //     color: "instagram",
                  //   },
                  // ]}
                  action={{ onClick: handleEditProfile, tooltip: "Edit Profile" }}
                  shadow={false}
                />
                <Divider orientation="vertical" sx={{ mx: 0 }} />
              </Grid>
              {editMode && (
                <Grid item xs={12} xl={8}>
                  <EditProfile setEditMode={setEditMode} showAlert={showAlert} />
                </Grid>
              )}
            </Grid>
          </MDBox>
        </Header>
        {/* <Footer /> */}
      </DashboardLayout>
      <AlertMessage {...errorState} />
    </React.Fragment>
  );
}

export default Overview;
