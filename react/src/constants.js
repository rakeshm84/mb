// constants.js

const getApiUrl = () => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const domain = `${protocol}//${hostname}`;

  if (hostname === "localhost") {
    // Development environment
    return "http://127.0.0.1:8000/api";
  } else {
    // Production environment
    return domain + "/api";
  }
};

const useConstants = () => {
  const per_page = 10;
  const sql_date_format = "YYYY-MM-DD";
  const API_URL = getApiUrl();

  return {
    per_page,
    sql_date_format,
    API_URL,
  };
};

export default useConstants;
