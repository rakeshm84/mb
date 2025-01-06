import { Alert, Slide, Snackbar } from "@mui/material";
import { useEffect, useState } from "react";
import PropTypes from "prop-types";

const AlertMessage = ({ type, show, message, id }) => {
  const vertical = "top";
  const horizontal = "center";

  const [showAlert, setShowAlert] = useState(show);

  useEffect(() => {
    setShowAlert(show);
  }, [id]);

  //Close MessageBar
  const handleCloseMessageBar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setShowAlert(false);
  };

  return (
    <Snackbar
      anchorOrigin={{ vertical, horizontal }}
      open={showAlert}
      onClose={handleCloseMessageBar}
      autoHideDuration={6000}
      TransitionComponent={Slide}
    >
      <Alert
        variant="filled"
        elevation={4}
        severity={type.toLowerCase()}
        onClose={handleCloseMessageBar}
        sx={{ width: "100%" }}
      >
        {message}
      </Alert>
    </Snackbar>
  );
};

AlertMessage.propTypes = {
  type: PropTypes.oneOf(["success", "info", "warning", "error"]).isRequired, // Alert type
  show: PropTypes.bool.isRequired, // Whether the alert should be shown
  message: PropTypes.string.isRequired, // The message to be displayed in the alert
  id: PropTypes.number.isRequired,
};

export default AlertMessage;
