import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Projects from "layouts/dashboard/components/Projects";

function AdminDashboard() {
  return (
    <DashboardLayout>
      <DashboardNavbar />
      {/* <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={8}>
            <Projects />
          </Grid>
        </Grid>
      </MDBox> */}
    </DashboardLayout>
  );
}

export default AdminDashboard;
