// constants.js

const useConstants = () => {
  const per_page = 10;
  const sql_date_format = "YYYY-MM-DD";

  // const AUTH_API_URL = "http://127.0.0.1:8000/api";

  const AUTH_API_URL = "https://user.niyud.co.il/api";
  const ADMIN_URL = "";
  return {
    per_page,
    sql_date_format,
    AUTH_API_URL,
    ADMIN_URL,
  };
};

export default useConstants;
