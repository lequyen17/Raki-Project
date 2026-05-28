import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import api from "../../api/api";
import { tokenizeTemplate } from "../../utils/cardParser";
import { mapApiError } from "../../utils/errorMapper";
import Button from "../../components/Common/Button/Button";
import "./CardDetail.css";

const CardDetail = () => {
  const { t } = useTranslation();
  const { cardId } = useParams();
  const navigate = useNavigate();

  const [card, setCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [editFields, setEditFields] = useState([]);

  useEffect(() => {
    fetchCardDetail();
  }, [cardId]);

  const fetchCardDetail = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/api/cards/${cardId}/`);
      setCard(res.data);
      setEditFields(res.data.field_values || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "common.error")
          : "Error loading card details",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleEditChange = (fieldName, value) => {
    setEditFields((prev) =>
      prev.map((field) =>
        field.name === fieldName ? { ...field, value } : field,
      ),
    );
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const res = await api.put(`/api/cards/${cardId}/`, {
        field_values: editFields,
      });
      setCard(res.data);
      setIsEditing(false);
      toast.success(t("common.save_success"));
    } catch (err) {
      toast.error(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "common.error")
          : "Error saving card",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(t("common.delete_confirm"))) {
      return;
    }
    try {
      setLoading(true);
      await api.delete(`/api/cards/${cardId}/`);
      toast.success(t("common.delete_success"));
      navigate(-1);
    } catch (err) {
      toast.error(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "common.error")
          : "Error deleting card",
      );
      setLoading(false);
    }
  };

  if (loading && !card) {
    return <div className="card-detail-loading">{t("common.loading")}</div>;
  }

  if (error) {
    return (
      <div className="card-detail-error">
        <p>{error}</p>
        <Button onClick={() => navigate(-1)}>{t("common.back")}</Button>
      </div>
    );
  }

  if (!card) return null;

  // Use the edited fields for previewing if in edit mode, otherwise use saved fields
  const displayFieldsList = isEditing ? editFields : card.field_values;
  
  const displayFields = (displayFieldsList || []).reduce((acc, curr) => {
    acc[curr.name] = curr.value;
    return acc;
  }, {});

  const frontHTML = tokenizeTemplate(
    card.template.front,
    displayFields,
    card.cloze_index || 0,
    false,
    {},
    card.template.back,
  );

  let rawBackTemplate = card.template.back;
  if (rawBackTemplate.includes("{{FrontSide}}")) {
    rawBackTemplate = rawBackTemplate.replace(
      /\{\{FrontSide\}\}/g,
      card.template.front,
    );
  }

  const backHTML = tokenizeTemplate(
    rawBackTemplate,
    displayFields,
    card.cloze_index || 0,
    true,
    {}, // no typed answers for preview
  );

  return (
    <div className="card-detail-page">
      <div className="card-detail-header">
        <Button color="gray" onClick={() => navigate(-1)}>
          {t("common.back")}
        </Button>
        <h1 className="card-detail-title">Card {card.id}</h1>
        <div className="card-detail-actions">
          {!isEditing ? (
            <>
              <Button color="blue" onClick={() => setIsEditing(true)}>
                {t("common.edit")}
              </Button>
              <Button color="red" onClick={handleDelete}>
                {t("common.delete")}
              </Button>
            </>
          ) : (
            <>
              <Button color="green" onClick={handleSave} disabled={loading}>
                {t("common.save")}
              </Button>
              <Button color="gray" onClick={() => setIsEditing(false)}>
                {t("common.cancel")}
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="card-detail-content">
        {isEditing && (
          <div className="card-edit-fields">
            <h3>{t("common.edit")}</h3>
            {(editFields || []).map((field) => (
              <div key={field.name} className="card-edit-field-group">
                <label className="card-edit-field-label">{field.name}</label>
                <textarea
                  className="card-edit-field-input"
                  value={field.value}
                  onChange={(e) => handleEditChange(field.name, e.target.value)}
                  rows={3}
                />
              </div>
            ))}
          </div>
        )}

        <div className="card-preview-section">
          <div className="card-preview-container">
            <h3>{t("cards.front")}</h3>
            <div className="card-preview study-card">
              <div
                className="study-card-section study-front"
                dangerouslySetInnerHTML={{ __html: frontHTML }}
              />
            </div>
          </div>
          <div className="card-preview-container">
            <h3>{t("cards.back")}</h3>
            <div className="card-preview study-card">
              <div
                className="study-card-section study-back"
                dangerouslySetInnerHTML={{ __html: backHTML }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CardDetail;
