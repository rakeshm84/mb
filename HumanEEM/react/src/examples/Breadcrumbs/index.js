import { Link } from "@mui/material";
import MDTypography from "../../components/MDTypography";
import { Link as RouterLink } from "react-router-dom";
import { Fragment } from "react";
import PropTypes from "prop-types";

const BreadCrumbs = ({ pagesList, mb = 2 }) => {
  return (
    <MDTypography aria-label="breadcrumb" mx={2} mb={mb} fontWeight="regular">
      {pagesList.map((page, index) => (
        <Fragment key={index}>
          {page.link != "" ? (
            <Link
              component={RouterLink}
              underline="none"
              to={page.route}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}
            >
              {page.icon} {t(`lang.${page.lang_attr}`)}
            </Link>
          ) : (
            <span>{page.name}</span>
          )}
          {pagesList.length != index + 1 && " / "}
        </Fragment>
      ))}
    </MDTypography>
  );
};

BreadCrumbs.propTypes = {
  pagesList: PropTypes.array,
  mb: PropTypes.number,
};

export default BreadCrumbs;
