import { useMemo, useEffect, useState } from "react";

// prop-types is a library for typechecking of props
import PropTypes from "prop-types";

// react-table components
import { useTable, usePagination, useGlobalFilter, useAsyncDebounce, useSortBy } from "react-table";

// @mui material components
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableContainer from "@mui/material/TableContainer";
import TableRow from "@mui/material/TableRow";
import Icon from "@mui/material/Icon";
import Autocomplete from "@mui/material/Autocomplete";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDPagination from "components/MDPagination";

// Material Dashboard 2 React example components
import DataTableHeadCell from "examples/Tables/DataTable/DataTableHeadCell";
import DataTableBodyCell from "examples/Tables/DataTable/DataTableBodyCell";

function DataTable({
  entriesPerPage,
  canSearch,
  showTotalEntries,
  table,
  pagination,
  isSorted,
  noEndBorder,
  onSearchChange,
  setPagination,
  handleSorting,
  sorting,
  serverSide,
}) {
  const defaultValue = entriesPerPage.defaultValue ? entriesPerPage.defaultValue : 10;
  const entries = entriesPerPage.entries
    ? entriesPerPage.entries.map((el) => el.toString())
    : ["5", "10", "15", "20", "25"];
  const columns = useMemo(() => table.columns, [table]);
  const data = useMemo(() => table.rows, [table]);
  const TIME_IN_MS = 200;

  const tableInstance = useTable(
    serverSide
      ? {
          columns,
          data,
          initialState: { pageIndex: pagination.pageIndex, pageSize: pagination.pageSize, sorting },
          manualPagination: true,
          manualSorting: true,
          sortDescFirst: false,
          onSortChange: handleSorting,
          pageCount: Math.ceil(pagination.total / pagination.pageSize),
        }
      : {
          columns,
          data,
          initialState: { pageIndex: 0 },
        },
    useGlobalFilter,
    useSortBy,
    usePagination
  );

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    rows,
    page,
    pageOptions,
    canPreviousPage,
    canNextPage,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    setGlobalFilter,
    state: { pageIndex, pageSize, globalFilter },
  } = tableInstance;

  const [search, setSearch] = useState(globalFilter);

  const onSearch = useAsyncDebounce((value) => {
    if (serverSide) {
      onSearchChange(value);
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    } else {
      setGlobalFilter(value);
    }
  }, TIME_IN_MS);

  useEffect(() => {
    if (serverSide) {
      setPageSize(pagination.pageSize);
    } else {
      setPageSize(defaultValue || 10);
    }
  }, [serverSide, pagination.pageSize, defaultValue]);

  const setEntriesPerPage = (value) => {
    setPageSize(value);
    if (serverSide) {
      setPagination((prev) => ({ ...prev, pageSize: value, pageIndex: 0 }));
    }
  };

  const renderPagination = pageOptions.map((option) => (
    <MDPagination
      item
      key={option}
      onClick={
        serverSide
          ? () => setPagination((prev) => ({ ...prev, pageIndex: Number(option) }))
          : () => gotoPage(Number(option))
      }
      active={pageIndex === option}
    >
      {option + 1}
    </MDPagination>
  ));

  let handleInputPagination;
  if (serverSide) {
    handleInputPagination = ({ target: { value } }) => {
      let newPageIndex = Number(value) - 1;
      if (newPageIndex < 0 || newPageIndex >= pageOptions.length) {
        newPageIndex = 0;
      }
      gotoPage(newPageIndex);
      setPagination((prev) => ({ ...prev, pageIndex: newPageIndex }));
    };
  } else {
    handleInputPagination = ({ target: { value } }) =>
      value > pageOptions.length || value < 0 ? gotoPage(0) : gotoPage(Number(value));
  }

  let handleInputPaginationValue;
  if (serverSide) {
    handleInputPaginationValue = ({ target: { value } }) => {
      const newPageIndex = Number(value) - 1;

      if (newPageIndex >= 0 && newPageIndex < pageOptions.length) {
        // gotoPage(newPageIndex);
        setPagination((prev) => ({ ...prev, pageIndex: newPageIndex }));
      }
    };
  } else {
    handleInputPaginationValue = ({ target: value }) => gotoPage(Number(value.value - 1));
  }

  const customizedPageOptions = pageOptions.map((option) => option + 1);

  const setSortedValue = (column) => {
    let sortedValue;

    if (isSorted && column.isSorted) {
      sortedValue = column.isSortedDesc ? "desc" : "asc";
    } else if (isSorted) {
      sortedValue = "none";
    } else {
      sortedValue = false;
    }

    return sortedValue;
  };

  let entriesStart;
  let entriesEnd;

  if (serverSide) {
    entriesStart = pageIndex * pageSize + 1;
    entriesEnd = (pageIndex + 1) * pageSize;

    if (entriesEnd > pagination.total) {
      entriesEnd = pagination.total;
    }
  } else {
    entriesStart = pageIndex === 0 ? pageIndex + 1 : pageIndex * pageSize + 1;
    entriesEnd;
    if (pageIndex === 0) {
      entriesEnd = pageSize;
    } else if (pageIndex === pageOptions.length - 1) {
      entriesEnd = rows.length;
    } else {
      entriesEnd = pageSize * (pageIndex + 1);
    }
  }

  return (
    <TableContainer sx={{ boxShadow: "none" }}>
      {entriesPerPage || canSearch ? (
        <MDBox display="flex" justifyContent="space-between" alignItems="center" p={3}>
          {entriesPerPage && (
            <MDBox display="flex" alignItems="center">
              <Autocomplete
                disableClearable
                value={pageSize.toString()}
                options={entries}
                onChange={(event, newValue) => {
                  setEntriesPerPage(parseInt(newValue, 10));
                }}
                size="small"
                sx={{ width: "5rem" }}
                renderInput={(params) => <MDInput {...params} />}
              />
              <MDTypography variant="caption" color="secondary">
                &nbsp;&nbsp;entries per page
              </MDTypography>
            </MDBox>
          )}
          {canSearch && (
            <MDBox width="12rem" ml="auto">
              <MDInput
                placeholder="Search..."
                size="small"
                fullWidth
                value={search}
                onChange={({ currentTarget }) => {
                  if (!serverSide) {
                    setSearch(search);
                  }
                  onSearch(currentTarget.value);
                }}
              />
            </MDBox>
          )}
        </MDBox>
      ) : null}
      <Table {...getTableProps()}>
        <MDBox component="thead">
          {headerGroups.map((headerGroup, key) => (
            <TableRow key={key} {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column, idx) => (
                <DataTableHeadCell
                  key={idx}
                  {...column.getHeaderProps(isSorted && column.getSortByToggleProps())}
                  width={column.width ? column.width : "auto"}
                  align={column.align ? column.align : "left"}
                  sorted={setSortedValue(column)}
                  sorting={sorting}
                  onSorting={handleSorting}
                  columnName={column.id}
                  serverSide={serverSide}
                >
                  {column.render("Header")}
                </DataTableHeadCell>
              ))}
            </TableRow>
          ))}
        </MDBox>
        <TableBody {...getTableBodyProps()}>
          {page.map((row, key) => {
            prepareRow(row);
            return (
              <TableRow key={key} {...row.getRowProps()}>
                {row.cells.map((cell, idx) => (
                  <DataTableBodyCell
                    key={idx}
                    noBorder={noEndBorder && rows.length - 1 === key}
                    align={cell.column.align ? cell.column.align : "left"}
                    {...cell.getCellProps()}
                  >
                    {cell.render("Cell")}
                  </DataTableBodyCell>
                ))}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>

      <MDBox
        display="flex"
        flexDirection={{ xs: "column", sm: "row" }}
        justifyContent="space-between"
        alignItems={{ xs: "flex-start", sm: "center" }}
        p={!showTotalEntries && pageOptions.length === 1 ? 0 : 3}
      >
        {showTotalEntries && (
          <MDBox mb={{ xs: 3, sm: 0 }}>
            <MDTypography variant="button" color="secondary" fontWeight="regular">
              Showing {entriesStart} to {entriesEnd} of{" "}
              {serverSide ? pagination.total : rows.length} entries
            </MDTypography>
          </MDBox>
        )}
        {pageOptions.length > 1 && (
          <MDPagination
            variant={pagination.variant ? pagination.variant : "gradient"}
            color={pagination.color ? pagination.color : "info"}
          >
            {canPreviousPage && (
              <MDPagination item onClick={() => previousPage()}>
                <Icon sx={{ fontWeight: "bold" }}>chevron_left</Icon>
              </MDPagination>
            )}
            {renderPagination.length > 6 ? (
              <MDBox width="5rem" mx={1}>
                <MDInput
                  inputProps={{ type: "number", min: 1, max: customizedPageOptions.length }}
                  value={customizedPageOptions[pageIndex]}
                  onChange={(handleInputPagination, handleInputPaginationValue)}
                />
              </MDBox>
            ) : (
              renderPagination
            )}
            {canNextPage && (
              <MDPagination item onClick={() => nextPage()}>
                <Icon sx={{ fontWeight: "bold" }}>chevron_right</Icon>
              </MDPagination>
            )}
          </MDPagination>
        )}
      </MDBox>
    </TableContainer>
  );
}

// Setting default values for the props of DataTable
DataTable.defaultProps = {
  entriesPerPage: { defaultValue: 10, entries: [5, 10, 15, 20, 25] },
  canSearch: false,
  showTotalEntries: true,
  pagination: { variant: "gradient", color: "info" },
  isSorted: true,
  noEndBorder: false,
};

// Typechecking props for the DataTable
DataTable.propTypes = {
  entriesPerPage: PropTypes.oneOfType([
    PropTypes.shape({
      defaultValue: PropTypes.number,
      entries: PropTypes.arrayOf(PropTypes.number),
    }),
    PropTypes.bool,
  ]),
  canSearch: PropTypes.bool,
  showTotalEntries: PropTypes.bool,
  table: PropTypes.objectOf(PropTypes.array).isRequired,
  pagination: PropTypes.shape({
    variant: PropTypes.oneOf(["contained", "gradient"]),
    color: PropTypes.oneOf([
      "primary",
      "secondary",
      "info",
      "success",
      "warning",
      "error",
      "dark",
      "light",
    ]),
    total: PropTypes.number,
    pageSize: PropTypes.number,
    pageIndex: PropTypes.number,
  }),
  isSorted: PropTypes.bool,
  noEndBorder: PropTypes.bool,
  onSearchChange: PropTypes.func,
  setPagination: PropTypes.func,
  handleSorting: PropTypes.func,
  sorting: PropTypes.arrayOf(PropTypes.object),
  serverSide: PropTypes.bool,
};

export default DataTable;
