import Icon from "@mui/material/Icon";
import Person from "./persons/form";
import Person_DT from "./persons";
import AdminDashboard from "./dashboard";

const admin_routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <AdminDashboard />,
    sidebar_item: true,
    lang_attr: "dashboard",
  },
  {
    type: "collapse",
    name: "Persons",
    key: "persons",
    icon: <Icon fontSize="small">group</Icon>,
    route: "/persons",
    component: <Person_DT />,
    sidebar_item: true,
    lang_attr: "persons",
  },
  {
    type: "collapse",
    name: "Person",
    key: "person",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/person",
    component: <Person />,
    lang_attr: "person",
  },
  {
    type: "collapse",
    name: "Edit Person",
    key: "edit_person",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/person/:id/edit",
    component: <Person />,
    lang_attr: "edit_person",
  },
];

export default admin_routes;
