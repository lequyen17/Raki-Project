import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import Button from "../Button/Button";
import "./DictionaryModal.css";

const DictionaryModal = ({ word, isOpen, onClose, onSelect }) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isOpen || !word) return;
    
    const fetchDictionary = async () => {
      setLoading(true);
      setError("");
      setResults([]);
      
      try {
        const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${encodeURIComponent(word)}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            setError(t("dictionary.not_found"));
          } else {
            setError(t("dictionary.error_fetch"));
          }
          setLoading(false);
          return;
        }

        const data = await response.json();
        const extractedResults = [];

        data.forEach((entry) => {
          entry.meanings.forEach((meaning) => {
            meaning.definitions.forEach((def) => {
              extractedResults.push({
                partOfSpeech: meaning.partOfSpeech,
                definition: def.definition,
                example: def.example,
              });
            });
          });
        });

        setResults(extractedResults);
      } catch (err) {
        setError(t("dictionary.error_fetch"));
      } finally {
        setLoading(false);
      }
    };

    fetchDictionary();
  }, [word, isOpen, t]);

  if (!isOpen) return null;

  return (
    <div className="dictionary-modal-overlay" onClick={onClose}>
      <div className="dictionary-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="dictionary-modal-title">
          {t("dictionary.title")} <span className="dictionary-word">"{word}"</span>
        </h2>
        
        <div className="dictionary-modal-content">
          {loading && <p className="dictionary-loading">{t("common.loading")}</p>}
          {error && <p className="dictionary-error">{error}</p>}
          
          {!loading && !error && results.length === 0 && (
            <p className="dictionary-error">{t("dictionary.no_results")}</p>
          )}

          {!loading && !error && results.length > 0 && (
            <ul className="dictionary-results">
              {results.map((res, index) => (
                <li key={index} className="dictionary-result-item">
                  <div className="dictionary-result-text">
                    <span className="dictionary-pos">[{res.partOfSpeech}]</span>
                    <span className="dictionary-def">{res.definition}</span>
                    {res.example && (
                      <div className="dictionary-example">
                        <strong>{t("dictionary.example")}:</strong> "{res.example}"
                      </div>
                    )}
                  </div>
                  <div className="dictionary-result-actions">
                    <Button
                      size="sm"
                      color="blue"
                      onClick={() => onSelect(res.definition)}
                    >
                      {t("dictionary.apply_definition")}
                    </Button>
                    {res.example && (
                      <Button
                        size="sm"
                        color="green"
                        variant="outline"
                        onClick={() => onSelect(res.example)}
                      >
                        {t("dictionary.apply_example")}
                      </Button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="dictionary-modal-actions">
          <Button onClick={onClose} variant="outline" color="red">
            {t("common.cancel")}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DictionaryModal;
