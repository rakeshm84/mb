import Icon from "@mui/material/Icon";
import Businesses from "includes/human/businesses";
import HumanDashboard from "./dashboard";

const human_tenant_routes = [
  {
    type: "collapse",
    name: "Dashboard",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <HumanDashboard />,
    sidebar_item: true,
    lang_attr: "dashboard",
  },
  {
    type: "collapse",
    name: "Businesses",
    key: "businesses",
    icon: <Icon fontSize="small">business</Icon>,
    route: "/businesses",
    component: <Businesses />,
    sidebar_item: true,
    lang_attr: "businesses",
  },
];

export default human_tenant_routes;
