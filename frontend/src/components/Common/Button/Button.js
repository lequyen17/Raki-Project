import React from "react";
import "./Button.css";

const Button = ({
  children,
  type = "button",
  onClick,
  color = "blue",
  variant = "solid",
  size = "md",
  fullWidth = false,

  isLoading = false,
  disabled = false,

  ...props
}) => {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={isLoading || disabled}
      className={`
        btn-custom
        btn-${variant}
        btn-${color}
        btn-${size}
        ${fullWidth ? "btn-full" : ""}
      `}
      {...props}
    >
      {isLoading ? (
        <div className="btn-content">
          <span className="btn-spinner"></span>
          <span>Loading...</span>
        </div>
      ) : (
        <span className="btn-content">{children}</span>
      )}
    </button>
  );
};

export default Button;
