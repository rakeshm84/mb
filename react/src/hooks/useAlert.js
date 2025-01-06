import { useState } from "react";

const useAlert = () => {
  const [errorState, setErrorState] = useState({
    type: "success",
    show: false,
    message: "",
  });

  const showAlert = (type, message) => {
    setErrorState((prevState) => ({
      ...prevState,
      type,
      message,
      show: true,
      id: new Date().getTime(),
    }));
  };

  return { errorState, showAlert };
};

export default useAlert;
