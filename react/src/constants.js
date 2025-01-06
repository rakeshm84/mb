// constants.js

const useConstants = () => {
  const per_page = 10;
  const sql_date_format = "YYYY-MM-DD";

  return {
    per_page,
    sql_date_format,
  };
};

export default useConstants;
