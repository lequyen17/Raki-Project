import React from "react";
import "./Input.css";

const Input = ({
  label,
  name,
  type = "text",
  value,
  onChange,
  placeholder = "",
  required,
  error = "",
}) => {
  return (
    <div className="input-group">
      {label && <label htmlFor={name}>{label}</label>}
      {error && <span className="error-text">{error}</span>}

      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required} // CHỖ NÀY: Truyền biến required xuống thẻ input HTML
        className={`custom-input ${error ? "input-error" : ""}`}
      />
    </div>
  );
};

export default Input;
