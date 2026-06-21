import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import Button from "../../components/Common/Button/Button";
import toast from "react-hot-toast";
import "./Wallet.css";

const FILTERS = ["all", "topup", "buy_deck", "sell_deck"];

const FILTER_REASONS = {
  all: null,
  topup: ["TOPUP"],
  buy_deck: ["BUY_DECK"],
  sell_deck: ["SELL_DECK"],
};

const formatCoin = (value) =>
  new Intl.NumberFormat().format(Math.abs(Number(value) || 0));

const formatVnd = (value) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

const Wallet = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [coinBalance, setCoinBalance] = useState(0);
  const [allTransactions, setAllTransactions] = useState([]);
  const [activeFilter, setActiveFilter] = useState("all");

  const [showPaymentHistory, setShowPaymentHistory] = useState(false);
  const [paymentHistory, setPaymentHistory] = useState([]);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [paymentError, setPaymentError] = useState("");

  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [topUpAmount, setTopUpAmount] = useState("");
  const [topUpSubmitting, setTopUpSubmitting] = useState(false);

  const formatDate = useCallback(
    (dateString) => {
      if (!dateString) return "";
      return new Date(dateString).toLocaleString(
        i18n.language === "vi" ? "vi-VN" : "en-US",
        {
          year: "numeric",
          month: "short",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
        },
      );
    },
    [i18n.language],
  );

  const getReasonLabel = useCallback(
    (reason) => t(`wallet.reasons.${reason}`, { defaultValue: reason }),
    [t],
  );

  const filteredTransactions = useMemo(() => {
    const reasons = FILTER_REASONS[activeFilter];
    if (!reasons) return allTransactions;
    return allTransactions.filter((item) => reasons.includes(item.reason));
  }, [allTransactions, activeFilter]);

  const fetchPaymentHistory = useCallback(async () => {
    setPaymentLoading(true);
    setPaymentError("");
    try {
      const res = await api.get("/api/wallet/payment-history/");
      setPaymentHistory(res.data.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setPaymentError(t("wallet.error_load_payment"));
    } finally {
      setPaymentLoading(false);
    }
  }, [navigate, t]);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    const loadWallet = async () => {
      setLoading(true);
      setError("");
      try {
        const [walletRes, historyRes] = await Promise.all([
          api.get("/api/wallet/"),
          api.get("/api/wallet/coin-history/"),
        ]);
        setCoinBalance(walletRes.data.coin_balance ?? 0);
        setAllTransactions(historyRes.data.results || []);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem("access_token");
          navigate("/login");
          return;
        }
        setError(t("wallet.error_load"));
      } finally {
        setLoading(false);
      }
    };

    loadWallet();
  }, [navigate, t]);

  useEffect(() => {
    const vnp_ResponseCode = searchParams.get("vnp_ResponseCode");
    const vnp_TxnRef = searchParams.get("vnp_TxnRef");
    const vnp_SecureHash = searchParams.get("vnp_SecureHash");

    if (vnp_ResponseCode && vnp_TxnRef && vnp_SecureHash) {
      if (vnp_ResponseCode === "00") {
        const vnp_Amount = searchParams.get("vnp_Amount");
        const coinsReceived = vnp_Amount ? parseInt(vnp_Amount, 10) / 100 : 0;
        toast.success(t("wallet.top_up_success", { coins: formatCoin(coinsReceived) }));
        // Refresh wallet data after successful top‑up
        (async () => {
          try {
            const [walletRes, historyRes] = await Promise.all([
              api.get("/api/wallet/"),
              api.get("/api/wallet/coin-history/"),
            ]);
            setCoinBalance(walletRes.data.coin_balance ?? 0);
            setAllTransactions(historyRes.data.results || []);
          } catch (err) {
            console.error("Failed to refresh wallet after VNPay", err);
          }
        })();
      } else {
        toast.error(t("wallet.top_up_failed"));
      }
      // Clean query params to avoid duplicate toasts on refresh
      navigate("/wallet", { replace: true });
    }
  }, [searchParams, navigate]);

  const handleOpenPaymentHistory = async () => {
    setShowPaymentHistory(true);
    await fetchPaymentHistory();
  };

  const handleTopUpSubmit = async (e) => {
    e.preventDefault();
    const amountVal = parseInt(topUpAmount, 10);
    if (isNaN(amountVal) || amountVal < 10000) {
      toast.error(t("wallet.top_up_amount_invalid"));
      return;
    }

    setTopUpSubmitting(true);
    try {
      const redirectUrl = window.location.origin + "/app/wallet";
      const res = await api.post("/api/wallet/topup/vnpay/", {
        amount: amountVal,
        redirectUrl: redirectUrl
      });
      if (res.data.payUrl) {
        window.location.href = res.data.payUrl;
      } else {
        toast.error(t("wallet.top_up_error"));
      }
    } catch (err) {
      const errMsg = err.response?.data?.error || t("wallet.top_up_error");
      toast.error(errMsg);
    } finally {
      setTopUpSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="wallet-page">
        <div className="wallet-container wallet-loading">{t("wallet.loading")}</div>
      </div>
    );
  }

  return (
    <div className="wallet-page">
      <div className="wallet-container">
        <h1 className="wallet-title">{t("wallet.title")}</h1>

        {error && <div className="wallet-error">{error}</div>}

        <section className="wallet-balance-card" aria-label={t("wallet.current_balance")}>
          <div>
            <p className="wallet-balance-label">{t("wallet.current_balance")}</p>
            <p className="wallet-balance-amount">
              <span className="wallet-balance-icon" aria-hidden="true">
                🪙
              </span>
              <span>
                {formatCoin(coinBalance)} {t("wallet.coin_unit")}
              </span>
            </p>
          </div>

          <div className="wallet-balance-actions">
            <Button color="orange" size="lg" onClick={() => setShowTopUpModal(true)}>
              {t("wallet.top_up")}
            </Button>
          </div>
        </section>

        <section className="wallet-history-section">
          <div className="wallet-history-header">
            <h2 className="wallet-history-title">{t("wallet.transaction_history")}</h2>
            <Button
              color="blue"
              variant="outline"
              size="sm"
              onClick={handleOpenPaymentHistory}
            >
              {t("wallet.payment_history")}
            </Button>
          </div>

          <div className="wallet-filter-tabs" role="tablist" aria-label={t("wallet.filters")}>
            {FILTERS.map((filter) => (
              <button
                key={filter}
                type="button"
                role="tab"
                aria-selected={activeFilter === filter}
                className={`wallet-filter-tab${activeFilter === filter ? " active" : ""}`}
                onClick={() => setActiveFilter(filter)}
              >
                {t(`wallet.filter_${filter}`)}
              </button>
            ))}
          </div>

          {filteredTransactions.length === 0 ? (
            <div className="wallet-empty">{t("wallet.empty_history")}</div>
          ) : (
            <ul className="wallet-transaction-list">
              {filteredTransactions.map((item) => {
                const isCredit = item.amount >= 0;
                const sign = isCredit ? "+" : "-";

                return (
                  <li key={item.id} className="wallet-transaction-item">
                    <div className="wallet-transaction-main">
                      <div
                        className={`wallet-transaction-amount ${isCredit ? "credit" : "debit"}`}
                      >
                        {sign} {formatCoin(item.amount)} {t("wallet.coin_unit")}
                      </div>
                      <p className="wallet-transaction-desc">
                        {getReasonLabel(item.reason)}
                      </p>
                    </div>
                    <time className="wallet-transaction-date" dateTime={item.created_at}>
                      {formatDate(item.created_at)}
                    </time>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>

      {showTopUpModal && (
        <div
          className="wallet-modal-overlay"
          role="presentation"
          onClick={() => {
            if (!topUpSubmitting) {
              setShowTopUpModal(false);
              setTopUpAmount("");
            }
          }}
        >
          <div
            className="wallet-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="wallet-topup-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="wallet-modal-header">
              <h3 id="wallet-topup-title" className="wallet-modal-title">
                {t("wallet.top_up")}
              </h3>
              <button
                type="button"
                className="wallet-modal-close"
                aria-label={t("common.cancel")}
                disabled={topUpSubmitting}
                onClick={() => {
                  setShowTopUpModal(false);
                  setTopUpAmount("");
                }}
              >
                ×
              </button>
            </div>
            <form onSubmit={handleTopUpSubmit} className="wallet-modal-body">
              <div className="wallet-topup-form-group">
                <label htmlFor="topUpAmount" className="wallet-topup-label">
                  {t("wallet.top_up_amount")}
                </label>
                <input
                  type="number"
                  id="topUpAmount"
                  className="wallet-topup-input"
                  placeholder={t("wallet.top_up_amount_placeholder")}
                  value={topUpAmount}
                  onChange={(e) => setTopUpAmount(e.target.value)}
                  min="10000"
                  required
                  disabled={topUpSubmitting}
                />
              </div>
              
              <div className="wallet-topup-preview-card">
                <p className="wallet-topup-rate">{t("wallet.top_up_rate_info")}</p>
                <p className="wallet-topup-receive">
                  🪙 {t("wallet.top_up_coins_receive", {
                    coins: formatCoin(topUpAmount || 0),
                  })}
                </p>
              </div>

              <div className="wallet-modal-actions">
                <Button
                  color="gray"
                  type="button"
                  disabled={topUpSubmitting}
                  onClick={() => {
                    setShowTopUpModal(false);
                    setTopUpAmount("");
                  }}
                >
                  {t("common.cancel")}
                </Button>
                <Button
                  color="orange"
                  type="submit"
                  disabled={topUpSubmitting}
                >
                  {topUpSubmitting ? t("common.loading") : t("wallet.top_up_submit")}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showPaymentHistory && (
        <div
          className="wallet-modal-overlay"
          role="presentation"
          onClick={() => setShowPaymentHistory(false)}
        >
          <div
            className="wallet-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="wallet-payment-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="wallet-modal-header">
              <h3 id="wallet-payment-title" className="wallet-modal-title">
                {t("wallet.payment_history")}
              </h3>
              <button
                type="button"
                className="wallet-modal-close"
                aria-label={t("common.cancel")}
                onClick={() => setShowPaymentHistory(false)}
              >
                ×
              </button>
            </div>
            <div className="wallet-modal-body">
              {paymentLoading ? (
                <div className="wallet-loading">{t("wallet.loading_payment")}</div>
              ) : paymentError ? (
                <div className="wallet-error">{paymentError}</div>
              ) : paymentHistory.length === 0 ? (
                <div className="wallet-empty">{t("wallet.empty_payment")}</div>
              ) : (
                <ul className="wallet-payment-list">
                  {paymentHistory.map((item) => (
                    <li key={item.id} className="wallet-payment-item">
                      <div className="wallet-payment-amount">
                        {formatVnd(item.amount_vnd)}
                      </div>
                      <span className={`wallet-status-badge ${item.status}`}>
                        {t(`wallet.payment_status.${item.status}`, {
                          defaultValue: item.status,
                        })}
                      </span>
                      <div className="wallet-payment-coin">
                        + {formatCoin(item.coin_received)} {t("wallet.coin_unit")}
                      </div>
                      <time className="wallet-payment-date" dateTime={item.created_at}>
                        {formatDate(item.created_at)}
                      </time>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Wallet;
