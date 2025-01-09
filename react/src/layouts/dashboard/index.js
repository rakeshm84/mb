import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";
import HumanDashboard from "includes/human/dashboard";
import AdminDashboard from "includes/admin/dashboard";
import useAuth from "hooks/useAuth";

function Dashboard() {
  const { user } = useAuth();

  return <>{user?.is_human_tenant ? <HumanDashboard /> : <AdminDashboard />}</>;
}

export default Dashboard;
