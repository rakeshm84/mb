import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";

import MDButton from "components/MDButton";
import { Link } from "react-router-dom";
import useAPI from "hooks/useAPI";
import { useEffect, useState } from "react";
import dummy from "assets/images/dummy-user.jpg";
import MDAvatar from "components/MDAvatar";
import MDBadge from "components/MDBadge";
import PropTypes from "prop-types";
import moment from "moment";
import AlertMessage from "components/UI/AlertMessage";
import useAlert from "hooks/useAlert";

const columns = [
  { Header: "username", accessor: "username", width: "45%", align: "left" },
  { Header: "db name", accessor: "db_name", align: "left" },
  { Header: "status", accessor: "status", align: "center" },
  { Header: "created", accessor: "created", align: "center" },
  { Header: "action", accessor: "action", align: "center" },
];

var rows = [];

const Person = ({ image, name, email }) => (
  <MDBox display="flex" alignItems="center" lineHeight={1}>
    <MDAvatar src={image} name={name} size="sm" />
    <MDBox ml={2} lineHeight={1}>
      <MDTypography display="block" variant="button" fontWeight="medium">
        {name}
      </MDTypography>
      <MDTypography variant="caption">{email}</MDTypography>
    </MDBox>
  </MDBox>
);

const Job = ({ title, description }) => (
  <MDBox lineHeight={1} textAlign="left">
    <MDTypography display="block" variant="caption" color="text" fontWeight="medium">
      {title}
    </MDTypography>
    <MDTypography variant="caption">{description}</MDTypography>
  </MDBox>
);

Person.propTypes = {
  image: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  email: PropTypes.string.isRequired,
};

Job.propTypes = {
  title: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
};

function Tenants() {
  const { errorState, showAlert } = useAlert();
  const { api } = useAPI();
  const [loading, setLoading] = useState(false);

  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 10,
    total: 0,
  });

  const [searchBy, setSearchBy] = useState("");
  const [sorting, setSorting] = useState([]);
  const serverSide = true;

  const formatDataForTable = (data) => {
    return data.map((item) => ({
      username: (
        <Person
          image={dummy}
          name={item.user_data.first_name + " " + item.user_data.last_name}
          email={item.user_data.email}
        />
      ),
      db_name: <Job title={item.db_name} description={item.slug} />,
      status: (
        <MDBox ml={-1}>
          <MDBadge
            badgeContent={item.status == 1 ? "active" : "inactive"}
            color={item.status == 1 ? "success" : "dark"}
            variant="gradient"
            size="sm"
          />
        </MDBox>
      ),
      created: (
        <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
          {moment(item.created_at).format("D/M/Y H:mm:ss")}
        </MDTypography>
      ),
      action: (
        <Link to={`/person/${item.entity_id}/edit`}>
          <MDTypography variant="caption" color="text" fontWeight="medium">
            Edit
          </MDTypography>
        </Link>
      ),
    }));
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/persons/`, {
        params: {
          page: pagination.pageIndex + 1,
          page_size: pagination.pageSize,
          searchBy,
          sorting: JSON.stringify(sorting),
          serverSide: serverSide,
        },
      });
      if (response.status == 200) {
        if (serverSide) {
          if (response.data.results.length === 0) {
            setData([]);
            setPagination((prev) => ({
              ...prev,
              total: 0,
            }));
          } else {
            setData(response.data.results);
            setPagination((prev) => ({
              ...prev,
              total: response.data.count,
            }));
          }
        } else {
          if (response.data.length === 0) {
            setData([]);
          } else {
            setData(response.data);
          }
        }
      }
      // setTableData(response.data.persons);
    } catch (error) {
      setError(error.message);
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSorting = (sort) => {
    const sortArr = [];
    sortArr.push({
      field: sort[0].id,
      direction: sort[0].desc == false ? "asc" : "desc",
    });
    setSorting(sortArr);
  };

  useEffect(() => {
    fetchData(); // Initial data fetch
  }, [pagination.pageIndex, pagination.pageSize, searchBy, sorting]);

  const alert = sessionStorage.getItem("alert");
  useEffect(() => {
    if (alert) {
      showAlert("success", alert);
      sessionStorage.removeItem("alert");
    }
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error fetching data: {error}</div>;

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
                  {t("lang.persons")}
                </MDTypography>
                <Link to="/person">
                  <MDButton variant="outlined" color="white" size="small">
                    {t("lang.actions.add_new")}
                  </MDButton>
                </Link>
              </MDBox>
              <MDBox pt={3}>
                {/* {rows.length > 0 && (
                  <DataTable
                    table={{ columns, rows }}
                    isSorted={true}
                    entriesPerPage={true}
                    canSearch={true}
                    showTotalEntries={true}
                    noEndBorder
                  />
                )} */}
                <DataTable
                  table={{ columns, rows: formatDataForTable(data) }}
                  isSorted={true}
                  showTotalEntries={true}
                  noEndBorder
                  canSearch={true}
                  onSearchChange={setSearchBy}
                  pagination={pagination}
                  setPagination={setPagination}
                  sorting={sorting}
                  handleSorting={handleSorting}
                  serverSide={serverSide}
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      {/* <Footer /> */}
      <AlertMessage {...errorState} />
    </DashboardLayout>
  );
}

export default Tenants;
