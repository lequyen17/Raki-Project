import React from "react";
import { useTranslation } from "react-i18next";
import "./CoinPrice.css";

export const formatCoin = (value) =>
  new Intl.NumberFormat().format(Math.abs(Number(value) || 0));

const CoinPrice = ({
  amount,
  variant = "chip",
  showUnit = true,
  label,
  freeLabel,
}) => {
  const { t } = useTranslation();
  const value = Number(amount) || 0;

  if (value <= 0) {
    return (
      <span className={`coin-price coin-price--free coin-price--${variant}`}>
        {freeLabel || t("community.free")}
      </span>
    );
  }

  return (
    <span className={`coin-price coin-price--premium coin-price--${variant}`}>
      <span className="coin-price-icon" aria-hidden="true">🪙</span>
      <span className="coin-price-amount">{formatCoin(value)}</span>
      {showUnit && (
        <span className="coin-price-unit">{t("wallet.coin_unit")}</span>
      )}
      {label && <span className="coin-price-label">{label}</span>}
    </span>
  );
};

export default CoinPrice;
