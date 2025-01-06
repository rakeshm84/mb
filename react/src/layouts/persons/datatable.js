import React, { useState, useEffect } from "react";
import DataTable from "react-data-table-component";
import useAPI from "hooks/useAPI";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import MDButton from "components/MDButton";
import MDInput from "components/MDInput";
import { Link } from "react-router-dom";
import moment from "moment";
import useConstants from "constants";
import Loader from "components/loader";
import AlertMessage from "components/UI/AlertMessage";
import useAlert from "hooks/useAlert";

const PersonsDT = () => {
  const { errorState, showAlert } = useAlert();
  const [data, setData] = useState([]);
  const { per_page } = useConstants();
  const [loading, setLoading] = useState(false);
  const [totalRows, setTotalRows] = useState(1);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(per_page);
  const [search, setSearch] = useState("");
  const { api } = useAPI();

  const fetchData = async (page, perPage, search, sortColumn = "", sortDirection = "asc") => {
    setLoading(true);
    const params = {
      start: (page - 1) * perPage, // Calculate the start index
      length: perPage, // Number of records per page
      search: { value: search, regex: false }, // Global search term
      order: [{ column: sortColumn, dir: sortDirection }], // Sort parameters
    };

    const response = await api.get(`/persons_dt`, { params });
    const result = response.data;
    setData(result.data);
    setTotalRows(result.recordsTotal);
    setLoading(false);
  };

  useEffect(() => {
    fetchData(page, perPage, search);
  }, [page, perPage, search]);

  const handlePageChange = (newPage) => setPage(newPage);

  const handlePerPageChange = (newPerPage) => {
    setPerPage(newPerPage);
    setPage(1); // Reset to the first page
  };

  const handleSearchChange = (event) => {
    setSearch(event.target.value);
    setPage(1); // Reset to the first page
  };

  const handleSort = (column, sortDirection) => {
    fetchData(1, perPage, "", column.columnKey, sortDirection);
  };

  const alert = sessionStorage.getItem("alert");
  useEffect(() => {
    if (alert) {
      showAlert("success", alert);
      sessionStorage.removeItem("alert");
    }
  }, [alert]);

  const columns = [
    {
      name: "NAME",
      columnKey: "first_name",
      selector: (row) => row.user_data.first_name + " " + row.user_data.last_name,
      sortable: true,
    },
    { name: "EMAIL", columnKey: "email", selector: (row) => row.user_data.email, sortable: true },
    { name: "DB NAME", columnKey: "db_name", selector: (row) => row.db_name, sortable: true },
    {
      name: "CREATED",
      columnKey: "date_joined",
      selector: (row) => moment(row.user_data.date_joined).format("D/M/Y H:mm:ss"),
      sortable: true,
    },
    {
      name: "ACTION",
      selector: (row) => {
        return (
          <Link to={`/person/${row.entity_id}/edit`}>
            <MDTypography variant="caption" color="text" fontWeight="medium">
              Edit
            </MDTypography>
          </Link>
        );
      },
      sortable: false,
    },
  ];

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
              <MDBox p={3}>
                <MDBox width="12rem" ml="auto">
                  <MDInput
                    placeholder="Search..."
                    size="small"
                    fullWidth
                    value={search}
                    onChange={handleSearchChange}
                  />
                </MDBox>
                <DataTable
                  columns={columns}
                  data={data}
                  progressPending={loading}
                  progressComponent={<Loader />}
                  pagination
                  paginationServer
                  paginationTotalRows={totalRows}
                  onChangeRowsPerPage={handlePerPageChange}
                  onChangePage={handlePageChange}
                  onSort={handleSort}
                  sortServer
                  paginationPerPage={perPage}
                  paginationRowsPerPageOptions={[5, 10, 25, 50, 100]}
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <AlertMessage {...errorState} />
    </DashboardLayout>
  );
};

export default PersonsDT;
