/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import MDBadge from "components/MDBadge";

// Images
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/team-4.jpg";
import useAPI from "hooks/useAPI";
import { useEffect, useState } from "react";

export default function data() {
  const [loading, setLoading] = useState(false);
  const [tableData, setTableData] = useState({});
  const { api } = useAPI();
  const fetchData = async (searchQuery) => {
    setLoading(true);
    try {
      const response = await api.get(`/persons/`, {
        params: { search: searchQuery },
      });
      setTableData(response.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(""); // Initial data fetch
  }, []);

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

  const rows = [];

  if (tableData) {
    tableData.forEach((row) => {
      var temp = {
        username: <Person image={team2} name={row.name} email="" />,
        db_name: <Job title={row.db_name} description="" />,
        status: (
          <MDBox ml={-1}>
            <MDBadge
              badgeContent={row.status == 1 ? "active" : "inactive"}
              color={row.status == 1 ? "success" : "dark"}
              variant="gradient"
              size="sm"
            />
          </MDBox>
        ),
        created: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {row.created_at}
          </MDTypography>
        ),
        action: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            Edit
          </MDTypography>
        ),
      };

      rows.push(temp);
    });
  }

  return {
    columns: [
      { Header: "username", accessor: "name", width: "45%", align: "left" },
      { Header: "db_name", accessor: "db_name", align: "left" },
      { Header: "status", accessor: "status", align: "center" },
      { Header: "created", accessor: "created", align: "center" },
      { Header: "action", accessor: "action", align: "center" },
    ],
    rows,
  };
}
