import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";

function CardDetail() {
  const { id } = useParams(); // Lấy ID từ URL
  const navigate = useNavigate();
  const [card, setCard] = useState(null);
  const [loading, setLoading] = useState(true);
  return (
    <div className="card-detail-container" style={{ padding: "20px" }}>
      <button onClick={() => navigate(-1)}> &larr; Quay lại</button>

      <hr />

      <div className="card-detail-actions">
        <button onClick={() => alert("Chỉnh sửa")}>Edit Card</button>
        <button onClick={() => alert("Xóa")} style={{ color: "red" }}>
          Delete
        </button>
      </div>
    </div>
  );
}

export default CardDetail;
