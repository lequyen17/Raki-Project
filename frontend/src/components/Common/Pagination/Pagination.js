import React, { useEffect, useMemo, useState } from "react";
import MuiPagination from "@mui/material/Pagination";
import "./Pagination.css";

export const usePagination = (items, itemsPerPage = 10) => {
  const [page, setPage] = useState(1);

  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(items.length / itemsPerPage));
  }, [items, itemsPerPage]);

  const paginatedItems = useMemo(() => {
    const startIndex = (page - 1) * itemsPerPage;

    return items.slice(startIndex, startIndex + itemsPerPage);
  }, [items, page, itemsPerPage]);

  useEffect(() => {
    setPage(1);
  }, [items]);

  return {
    page,
    setPage,
    totalPages,
    paginatedItems,
  };
};

const Pagination = ({ page, totalPages, onPageChange }) => {
  if (totalPages <= 1) return null;

  return (
    <div className="pagination-wrapper">
      <MuiPagination
        count={totalPages}
        page={page}
        color="primary"
        shape="rounded"
        onChange={(event, value) => {
          onPageChange(value);
        }}
      />
    </div>
  );
};

export default Pagination;
