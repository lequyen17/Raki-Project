import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";
import "./Study.css";

const Study = () => {
  const { deckId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [deckName, setDeckName] = useState("");
  const [cards, setCards] = useState([]);
  const [counts, setCounts] = useState({
    new: 0,
    learning: 0,
    review: 0,
    total: 0,
  });
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchStudyCards();
  }, [deckId]);

  const fetchStudyCards = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/api/user/decks/${deckId}/study/`);
      setDeckName(res.data.deck_name);
      setCounts(res.data.counts);
      setCards(res.data.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(err.response?.data?.error || "Không thể lấy dữ liệu thẻ học.");
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality) => {
    const currentCard = cards[currentIndex];
    if (!currentCard || submitting) return;

    try {
      setSubmitting(true);

      // 1. Gọi API lưu kết quả vào Database
      const res = await api.post(`/api/user/cards/${currentCard.id}/review/`, {
        quality,
      });

      // 2. Lấy interval và status mới từ Backend trả về
      const { interval, status: nextStatus } = res.data;

      // Tạo một bản sao của danh sách thẻ hiện tại
      let newCards = [...cards];

      // 3. LOGIC XỬ LÝ HÀNG ĐỢI (CÁCH B)
      if (interval === 0) {
        // Thẻ này chưa thuộc (Again/Hard/Good lần 1), cần học lại ngay hôm nay
        const cardToRepeat = {
          ...currentCard,
          status: nextStatus, // Cập nhật status mới (ví dụ từ Review -> Learning nếu bấm Again)
        };

        if (quality === "again") {
          // Hiện lại sau 5 thẻ nữa: chèn vào vị trí currentIndex + 6
          // (Dùng Math.min để không vượt quá độ dài mảng)
          const insertAt = Math.min(currentIndex + 6, newCards.length);
          newCards.splice(insertAt, 0, cardToRepeat);
          console.log("Đã chèn thẻ Again vào vị trí:", insertAt);
        } else {
          // Hard hoặc Good (lần 1): Đẩy xuống cuối danh sách của phiên học này
          newCards.push(cardToRepeat);
          console.log("Đã đẩy thẻ xuống cuối danh sách");
        }

        // Cập nhật lại state cards với mảng đã được chèn/đẩy
        setCards(newCards);

        // Vì thẻ chưa "xong", ta không trừ counts,
        // nhưng có thể cập nhật status hiển thị nếu muốn
      } else {
        // interval > 0: Thẻ đã "tốt nghiệp" khỏi phiên học hôm nay
        // Cập nhật số lượng thẻ còn lại trên giao diện
        const oldStatus = currentCard.status.toLowerCase();
        setCounts((prev) => ({
          ...prev,
          [oldStatus]: Math.max(0, prev[oldStatus] - 1),
          total: Math.max(0, prev.total - 1),
        }));
        console.log("Thẻ đã hoàn thành, hẹn gặp lại sau", interval, "ngày");
      }

      // 4. Chuyển sang thẻ tiếp theo trong mảng
      setShowAnswer(false);
      setCurrentIndex((prev) => prev + 1);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Đánh giá thất bại.");
    } finally {
      setSubmitting(false);
    }
  };

  const replaceTags = (templateStr, fieldValues) => {
    if (!templateStr) return "";
    return templateStr.replace(/\{\{([^{}]+)\}\}/g, (match, fieldName) => {
      const trimmed = fieldName.trim();
      return fieldValues[trimmed] !== undefined ? fieldValues[trimmed] : match;
    });
  };

  if (loading) {
    return <div className="study-loading">Đang chuẩn bị thẻ học...</div>;
  }

  if (error) {
    return (
      <div className="study-error">
        <p>{error}</p>
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          Quay lại
        </button>
      </div>
    );
  }

  const isFinished = currentIndex >= cards.length;
  const currentCard = cards[currentIndex];

  if (isFinished) {
    return (
      <div className="study-finished-container">
        <h2>Chúc mừng!</h2>
        <p>
          Bạn đã hoàn thành phiên học cho deck <strong>{deckName}</strong> hôm
          nay.
        </p>
        <button
          className="study-show-answer-btn"
          style={{ marginTop: "20px" }}
          onClick={() => navigate("/decks")}
        >
          Quay lại danh sách
        </button>
      </div>
    );
  }

  const frontHTML = replaceTags(
    currentCard.template.front,
    currentCard.field_values,
  );
  const backHTML = replaceTags(
    currentCard.template.back,
    currentCard.field_values,
  );

  return (
    <div className="study-container">
      <div className="study-header">
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          &larr; Theo dõi tiến độ
        </button>
        <div className="study-deck-name">{deckName}</div>
      </div>

      <div className="study-counts">
        <span className="count-new" title="New">
          N: {counts.new}
        </span>
        <span className="count-learning" title="Learning">
          L: {counts.learning}
        </span>
        <span className="count-review" title="Review">
          R: {counts.review}
        </span>
      </div>

      <div className="study-card-wrapper">
        <div className="study-card">
          <div
            className="study-card-section study-front"
            dangerouslySetInnerHTML={{ __html: frontHTML }}
          />

          {showAnswer && (
            <>
              <hr className="study-divider" />
              <div
                className="study-card-section study-back"
                dangerouslySetInnerHTML={{ __html: backHTML }}
              />
            </>
          )}
        </div>
      </div>

      <div className="study-controls">
        {!showAnswer ? (
          <button
            className="study-show-answer-btn"
            onClick={() => setShowAnswer(true)}
          >
            Hiển thị đáp án
          </button>
        ) : (
          <div className="study-rating-buttons">
            <button
              className="btn-again"
              disabled={submitting}
              onClick={() => handleReview("again")}
            >
              <span className="btn-label">Again</span>
              <span className="btn-hint">&lt;1m</span>
            </button>
            <button
              className="btn-hard"
              disabled={submitting}
              onClick={() => handleReview("hard")}
            >
              <span className="btn-label">Hard</span>
            </button>
            <button
              className="btn-good"
              disabled={submitting}
              onClick={() => handleReview("good")}
            >
              <span className="btn-label">Good</span>
            </button>
            <button
              className="btn-easy"
              disabled={submitting}
              onClick={() => handleReview("easy")}
            >
              <span className="btn-label">Easy</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Study;
