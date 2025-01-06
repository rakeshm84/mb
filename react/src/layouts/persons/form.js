import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";

import { useForm } from "react-hook-form";
import { useParams, useNavigate } from "react-router-dom";
import useAPI from "hooks/useAPI";
import { useState, useEffect } from "react";
import { AdapterMoment } from "@mui/x-date-pickers/AdapterMoment";
import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import moment from "moment";
import useConstants from "constants";
import { useRef } from "react";
import TinyMCE from "components/TinyMCE";

function Tenant() {
  const { sql_date_format } = useConstants();
  const [userData, setUserData] = useState({});
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const navigate = useNavigate();
  const { api } = useAPI();
  const { id } = useParams();
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setError,
    setValue,
  } = useForm();

  const editorRef = useRef(null);

  const onFormSubmit = async (data) => {
    if (id) {
      var url = `/person/${id}/edit`;
    } else {
      var url = `/person/register`;
    }
    const formattedDob = data.date_of_birth
      ? moment(data.date_of_birth).format(sql_date_format)
      : null;

    var desc = "";
    if (editorRef.current) {
      desc = editorRef.current.getContent();
    }
    const Data = {
      ...data,
      date_of_birth: formattedDob,
      desc: desc,
    };
    try {
      var response = await api.post(url, Data);
      if (response.status == 201 || response.status == 200) {
        sessionStorage.setItem("alert", response.data.message);
        navigate("/persons");
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

  const fetchUser = async (id) => {
    setLoading(true);
    try {
      const response = await api.get(`/person/${id}/edit`);
      setUserData(response.data);
      setValue("first_name", response.data?.user?.first_name || "");
      setValue("last_name", response.data?.user?.last_name || "");
      setValue("email", response.data?.user?.email || "");
      setValue("phone_number", response.data?.profile?.phone_number || "");
      setValue("address", response.data?.profile?.address || "");
      const dateOfBirth = moment(response.data.profile.date_of_birth || null);
      setValue("date_of_birth", dateOfBirth);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      fetchUser(id);
      setEditMode(true);
    }
  }, [id]);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  {editMode ? t("lang.edit_person") : t("lang.add_new_person")}
                </MDTypography>
              </MDBox>
              <MDBox pt={4} pb={3} px={3}>
                <MDBox component="form" role="form" onSubmit={handleSubmit(onFormSubmit)}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <MDBox mb={1}>
                        <MDInput
                          {...register("first_name", {
                            required: t("lang.validations.required", {
                              field: t("lang.user.first_name"),
                            }),
                          })}
                          type="text"
                          label={t("lang.user.first_name")}
                          fullWidth
                          value={watch("first_name") || ""}
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
                            value: userData?.last_name,
                            required: t("lang.validations.required", {
                              field: t("lang.user.last_name"),
                            }),
                          })}
                          type="text"
                          label={t("lang.user.last_name")}
                          value={watch("last_name") || ""}
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
                            value: userData?.email,
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
                          value={watch("email") || ""}
                          error={!!errors.email}
                        />
                        {errors.email && (
                          <MDTypography variant="caption" color="error">
                            {errors.email.message}
                          </MDTypography>
                        )}
                      </MDBox>
                    </Grid>
                    {!id && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <MDInput
                            {...register("username", {
                              required: t("lang.validations.required", {
                                field: t("lang.user_name"),
                              }),
                            })}
                            type="text"
                            label={t("lang.user_name")}
                            fullWidth
                            value={watch("username") || ""}
                            error={!!errors.username}
                          />
                          {errors.username && (
                            <MDTypography variant="caption" color="error">
                              {errors.username.message}
                            </MDTypography>
                          )}
                        </MDBox>
                      </Grid>
                    )}
                    {!id && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <MDInput
                            {...register("password", {
                              required: t("lang.validations.password.required"),
                              minLength: {
                                value: 8,
                                message: t("lang.validations.password.min_length"),
                              },
                              maxLength: {
                                value: 20,
                                message: t("lang.validations.password.max_length"),
                              },
                              validate: {
                                containsUppercase: (value) =>
                                  /[A-Z]/.test(value) ||
                                  t("lang.validations.password.contains_uppercase"),
                                containsLowercase: (value) =>
                                  /[a-z]/.test(value) ||
                                  t("lang.validations.password.contains_lowercase"),
                                containsDigit: (value) =>
                                  /\d/.test(value) || t("lang.validations.password.contains_digit"),
                                containsSpecialChar: (value) =>
                                  /[@$!%*?&]/.test(value) ||
                                  t("lang.validations.password.contains_special_char"),
                              },
                            })}
                            type="password"
                            label={t("lang.password")}
                            fullWidth
                            value={watch("password") || ""}
                            error={!!errors.password}
                          />
                          {errors.password && (
                            <MDTypography variant="caption" color="error">
                              {errors.password.message}
                            </MDTypography>
                          )}
                        </MDBox>
                      </Grid>
                    )}

                    {!id && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <MDInput
                            {...register("confirm_password", {
                              required: t("lang.validations.confirm_password.required"),
                              validate: (value) =>
                                value === watch("password") ||
                                t("lang.validations.confirm_password.mismatch"),
                            })}
                            type="password"
                            label={t("lang.confirm_password")}
                            fullWidth
                            value={watch("confirm_password") || ""}
                            error={!!errors.confirm_password}
                          />
                          {errors.confirm_password && (
                            <MDTypography variant="caption" color="error">
                              {errors.confirm_password.message}
                            </MDTypography>
                          )}
                        </MDBox>
                      </Grid>
                    )}
                    {editMode && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <MDInput
                            {...register("phone_number")}
                            type="text"
                            label={t("lang.phone_number")}
                            fullWidth
                            value={watch("phone_number") || ""}
                          />
                        </MDBox>
                      </Grid>
                    )}
                    {editMode && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <MDInput
                            {...register("address")}
                            type="text"
                            label={t("lang.address")}
                            fullWidth
                            value={watch("address") || ""}
                          />
                        </MDBox>
                      </Grid>
                    )}
                    {editMode && (
                      <Grid item xs={6}>
                        <MDBox mb={1}>
                          <LocalizationProvider dateAdapter={AdapterMoment}>
                            <DatePicker
                              name="date_of_birth"
                              label={t("lang.date_of_birth")}
                              {...register("date_of_birth")}
                              value={watch("date_of_birth") || null}
                              onChange={(newValue) => setValue("date_of_birth", newValue)}
                              slotProps={{ textField: { fullWidth: true } }}
                              renderInput={(params) => <MDInput {...params} fullWidth />}
                            />
                          </LocalizationProvider>
                        </MDBox>
                      </Grid>
                    )}
                    {editMode && (
                      <Grid item xs={12}>
                        <MDBox mb={1}>
                          <MDTypography variant="button">{t("lang.description")}</MDTypography>
                          <TinyMCE
                            onInit={(_evt, editor) => (editorRef.current = editor)}
                            initialValue={userData?.profile?.desc || ""}
                          />
                        </MDBox>
                      </Grid>
                    )}
                    <Grid item xs={12}>
                      <MDBox mb={1}>
                        <MDButton type="submit" variant="gradient" color="info">
                          {editMode ? t("lang.actions.update") : t("lang.actions.submit")}
                        </MDButton>
                      </MDBox>
                    </Grid>
                  </Grid>
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}

export default Tenant;
