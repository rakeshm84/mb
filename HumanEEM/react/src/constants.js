// constants.js

const useConstants = () => {
  const per_page = 10;
  const sql_date_format = "YYYY-MM-DD";

  // const AUTH_URL = "http://localhost:3000";
  // const AUTH_API_URL = "http://127.0.0.1:8000/api";
  // const ADMIN_API_URL = "http://127.0.0.1:8001/api";
  // const HUMAN_API_URL = "http://127.0.0.1:8002/api";

  const AUTH_URL = "https://user.niyud.co.il";
  const AUTH_API_URL = "https://user.niyud.co.il/api";
  const ADMIN_API_URL = "/api";
  const HUMAN_API_URL = "https://human.niyud.co.il/api";

  const ADMIN_URL = "";
  return {
    per_page,
    sql_date_format,
    AUTH_API_URL,
    ADMIN_URL,
    AUTH_URL,
    ADMIN_API_URL,
    HUMAN_API_URL,
  };
};

export default useConstants;
