import React, { useState, useEffect } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import AlertMessage from "components/UI/AlertMessage";
import useAlert from "hooks/useAlert";

const Businesses = () => {
  const { errorState, showAlert } = useAlert();

  const alert = sessionStorage.getItem("alert");
  useEffect(() => {
    if (alert) {
      showAlert("success", alert);
      sessionStorage.removeItem("alert");
    }
  }, [alert]);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <MDTypography variant="h6" color="white">
                  {t("lang.businesses")}
                </MDTypography>
              </MDBox>
              <MDBox p={3}></MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <AlertMessage {...errorState} />
    </DashboardLayout>
  );
};

export default Businesses;
