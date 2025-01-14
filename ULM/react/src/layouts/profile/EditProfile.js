import { useForm } from "react-hook-form";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import useAuth from "hooks/useAuth";
import PropTypes from "prop-types";
import useAPI from "hooks/useAPI";
import { useEffect } from "react";
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import moment from "moment";
import useConstants from "constants";
import React, { useRef } from "react";
import TinyMCE from "components/TinyMCE";
import TextareaAutosize from "@mui/material/TextareaAutosize";

function EditProfile({ setEditMode, showAlert }) {
  const { sql_date_format } = useConstants();
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setError,
    setValue,
  } = useForm();

  const { user, saveUser } = useAuth();

  const { api } = useAPI();

  const editorRef = useRef(null);

  const onFormSubmit = async (data) => {
    const formattedDob = data.date_of_birth
      ? moment(data.date_of_birth).format(sql_date_format)
      : null;
    var desc = "";
    if (editorRef.current) {
      desc = editorRef.current.getContent();
    }
    console.log("data", data);
    const Data = {
      ...data,
      date_of_birth: formattedDob,
      // desc: desc,
    };
    try {
      var response = await api.post(`/person/${user.id}/edit`, Data);
      if (response.status == 201 || response.status == 200) {
        setEditMode(false);
        saveUser(response.data.user);
        showAlert("success", response.data.message);
      }
    } catch (error) {
      if (error.response && error.response.data) {
        const backendErrors = error.response.data.errors;
        for (const field in backendErrors) {
          setError(field, { type: "manual", message: t(backendErrors[field]) });
        }
      }
    }
  };

  useEffect(() => {
    if (user?.dob) {
      setValue("date_of_birth", moment(user.dob));
    }
  }, []);
  return (
    <Grid container spacing={6}>
      <Grid item xs={12}>
        <MDBox component="form" role="form" onSubmit={handleSubmit(onFormSubmit)}>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <MDInput
                  {...register("first_name", {
                    value: user?.first_name || "",
                    required: t("lang.validations.required", {
                      field: t("lang.user.first_name"),
                    }),
                  })}
                  type="text"
                  label={t("lang.user.first_name")}
                  fullWidth
                  error={!!errors.first_name}
                />
                {errors.first_name && (
                  <MDTypography variant="caption" color="error">
                    {errors.first_name.message}
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <MDInput
                  {...register("last_name", {
                    value: user?.last_name || "",
                    required: t("lang.validations.required", {
                      field: t("lang.user.last_name"),
                    }),
                  })}
                  type="text"
                  label={t("lang.user.last_name")}
                  fullWidth
                  error={!!errors.last_name}
                />
                {errors.last_name && (
                  <MDTypography variant="caption" color="error">
                    {errors.last_name.message}
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <MDInput
                  {...register("email", {
                    value: user?.email || "",
                    required: t("lang.validations.required", {
                      field: t("lang.user.email"),
                    }),
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: t("lang.validations.email.invalid"),
                    },
                  })}
                  type="email"
                  label={t("lang.user.email")}
                  fullWidth
                  error={!!errors.email}
                />
                {errors.email && (
                  <MDTypography variant="caption" color="error">
                    {errors.email.message}
                  </MDTypography>
                )}
              </MDBox>
            </Grid>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <MDInput
                  {...register("phone_number", {
                    value: user?.phone || "",
                  })}
                  type="text"
                  label={t("lang.phone_number")}
                  fullWidth
                />
              </MDBox>
            </Grid>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <MDInput
                  {...register("address", {
                    value: user?.address || "",
                  })}
                  type="text"
                  label={t("lang.address")}
                  fullWidth
                />
              </MDBox>
            </Grid>
            <Grid item xs={6}>
              <MDBox mb={1}>
                <LocalizationProvider dateAdapter={AdapterMoment}>
                  <DatePicker
                    name="date_of_birth"
                    label={t("lang.date_of_birth")}
                    value={watch("date_of_birth") || null}
                    onChange={(newValue) => setValue("date_of_birth", newValue)}
                    slotProps={{ textField: { fullWidth: true } }}
                    renderInput={(params) => <MDInput {...params} />}
                  />
                </LocalizationProvider>
              </MDBox>
            </Grid>
            <Grid item xs={12}>
              <MDBox mb={1}>
                {/* <MDTypography variant="button">{t("lang.description")}</MDTypography> */}
                {/* <TinyMCE
                  onInit={(_evt, editor) => (editorRef.current = editor)}
                  initialValue={user?.desc || ""}
                  height={300}
                /> */}
                <MDInput
                  {...register("desc", {
                    value: user?.desc || "",
                  })}
                  multiline
                  rows={4}
                  type="text"
                  label={t("lang.description")}
                  fullWidth
                  error={!!errors.first_name}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12}>
              <MDBox mb={1}>
                <MDButton type="submit" variant="gradient" color="info" sx={{ float: "right" }}>
                  {t("lang.actions.update")}
                </MDButton>
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
      </Grid>
    </Grid>
  );
}

EditProfile.propTypes = {
  setEditMode: PropTypes.func.isRequired,
  showAlert: PropTypes.func.isRequired,
};

export default EditProfile;
