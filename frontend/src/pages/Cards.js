import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/api';
import './CardsUI.css';

const Cards = () => {
  const navigate = useNavigate();
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState('');
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modals state
  const [showAddNoteModal, setShowAddNoteModal] = useState(false);
  const [showCreateNoteTypeModal, setShowCreateNoteTypeModal] = useState(false);

  // NoteTypes state for Add Note Modal
  const [noteTypes, setNoteTypes] = useState([]);
  const [selectedNoteTypeId, setSelectedNoteTypeId] = useState('');
  const [noteValues, setNoteValues] = useState({});

  const fetchCards = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await api.get(`/api/user/decks/${deckId}/cards/`);
      setDeckName(res.data?.deck_name || '');
      setCards(res.data?.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
        return;
      }
      setError(err.response?.data?.error || 'Khong the tai danh sach card.');
    } finally {
      setLoading(false);
    }
  };

  const fetchNoteTypes = async () => {
    try {
      const res = await api.get('/api/user/note-types/');
      setNoteTypes(res.data.results || []);
      if (res.data.results && res.data.results.length > 0) {
        setSelectedNoteTypeId(res.data.results[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch note types", err);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchCards();
    fetchNoteTypes();
  }, [deckId, navigate]);

  // ADD NOTE LOGIC
  const handleNoteValueChange = (defId, val) => {
    setNoteValues(prev => ({ ...prev, [defId]: val }));
  };

  const submitAddNote = async () => {
    try {
      await api.post(`/api/user/decks/${deckId}/notes/`, {
        note_type_id: selectedNoteTypeId,
        values: noteValues
      });
      setShowAddNoteModal(false);
      setNoteValues({});
      fetchCards();
    } catch (err) {
      alert("Failed to add note: " + (err.response?.data?.error || err.message));
    }
  };

  const selectedNoteType = noteTypes.find(nt => String(nt.id) === String(selectedNoteTypeId));

  // CREATE NOTETYPE LOGIC
  const [newNoteTypeName, setNewNoteTypeName] = useState('');
  const [newDefinitions, setNewDefinitions] = useState([{ id: Date.now(), value: '' }]);
  const [newTemplates, setNewTemplates] = useState([]);
  const [step, setStep] = useState(1);
  const [step1Error, setStep1Error] = useState('');

  const [tmplName, setTmplName] = useState('');
  const [tmplFront, setTmplFront] = useState('');
  const [tmplBack, setTmplBack] = useState('');

  const handleAddDefinition = () => {
    setNewDefinitions([...newDefinitions, { id: Date.now() + Math.random(), value: '' }]);
  };

  const handleDefChange = (id, val) => {
    setNewDefinitions(newDefinitions.map(def => def.id === id ? { ...def, value: val } : def));
  };

  const handleRemoveDefinition = (id) => {
    setNewDefinitions(newDefinitions.filter(def => def.id !== id));
  };

  const validDefs = newDefinitions.map(d => d.value.trim()).filter(Boolean);

  const handleNextStep1 = () => {
    setStep1Error('');
    if (!newNoteTypeName.trim()) {
      setStep1Error('NoteType Name không được để trống.');
      return;
    }
    if (newDefinitions.length === 0) {
      setStep1Error('Phải có ít nhất một field.');
      return;
    }
    if (newDefinitions.some(def => def.value.trim() === '')) {
      setStep1Error('Không được để field name trống.');
      return;
    }
    setStep(2);
  };
  const handleAddTemplate = () => {
    if (tmplName && tmplFront && tmplBack) {
      setNewTemplates([...newTemplates, { name: tmplName, front: tmplFront, back: tmplBack }]);
      setTmplName('');
      setTmplFront('');
      setTmplBack('');
    }
  };

  const submitCreateNoteType = async () => {
    try {
      await api.post('/api/user/note-types/', {
        name: newNoteTypeName,
        definitions: validDefs,
        templates: newTemplates
      });
      setShowCreateNoteTypeModal(false);
      setNewNoteTypeName('');
      setNewDefinitions([{ id: Date.now(), value: '' }]);
      setNewTemplates([]);
      setStep(1);
      setStep1Error('');
      fetchNoteTypes();
    } catch (err) {
      alert("Failed to create note type");
    }
  };

  return (
    <div className="decks-page">
      <div className="decks-container">
        <div className="deck-detail-actions" style={{ marginBottom: '16px', display: 'flex', gap: '16px' }}>
          <button type="button" className="deck-action-btn" onClick={() => navigate('/decks')}>
            Back To Decks
          </button>
          <button type="button" className="deck-action-btn" onClick={() => setShowAddNoteModal(true)} style={{ background: '#10b981', color: 'white' }}>
            + Add Card
          </button>
        </div>

        <h1 className="decks-title">Cards In Deck {deckName ? `- ${deckName}` : ''}</h1>

        {loading && <p className="decks-state">Dang tai danh sach card...</p>}
        {error && <p className="decks-error">{error}</p>}

        {!loading && !error && (
          <>
            {cards.length === 0 ? (
              <p className="decks-state">Deck nay chua co card nao.</p>
            ) : (
              <div className="deck-tree-list">
                {cards.map((card) => (
                  <div key={card.id} className="deck-tree-node">
                    <div className="deck-tree-row deck-tree-row--root">
                      <div className="deck-row-main">
                        <span className="deck-row-name">Card #{card.id} (Note Type/Tmpl id: {card.template_id})</span>
                        <span className="deck-row-count">
                          rep {card.repetition} | int {card.interval} | ease {card.easiness}
                        </span>
                        <span className="deck-row-count">
                          next: {card.next_review ? new Date(card.next_review).toLocaleString() : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      {/* MODAL: ADD NOTE */}
      {showAddNoteModal && (
        <div className="add-card-modal-overlay">
          <div className="add-card-modal">
            <div className="modal-header">
              <h2 className="modal-title">Add New Card</h2>
              <button className="close-btn" onClick={() => setShowAddNoteModal(false)}>&times;</button>
            </div>

            <div className="form-group horizontal-flex">
              <div style={{ flex: 1 }}>
                <label className="form-label">Note Type</label>
                <select
                  className="form-select"
                  value={selectedNoteTypeId}
                  onChange={e => setSelectedNoteTypeId(e.target.value)}
                >
                  {noteTypes.map(nt => (
                    <option key={nt.id} value={nt.id}>{nt.name} {nt.user_id ? '(Custom)' : '(System)'}</option>
                  ))}
                </select>
              </div>
              <button
                className="btn-secondary btn-list"
                style={{ marginTop: '25px' }}
                onClick={() => {
                  setShowAddNoteModal(false);
                  setStep1Error('');
                  setShowCreateNoteTypeModal(true);
                }}
              >
                + Create NoteType
              </button>
            </div>

            <hr style={{ borderColor: '#334155', margin: '24px 0' }} />

            {selectedNoteType && selectedNoteType.definitions.map(def => (
              <div key={def.id} className="form-group">
                <label className="form-label">{def.name}</label>
                <textarea
                  className="form-textarea"
                  value={noteValues[def.id] || ''}
                  onChange={e => handleNoteValueChange(def.id, e.target.value)}
                  placeholder={`Enter ${def.name}...`}
                />
              </div>
            ))}

            <div style={{ textAlign: 'right', marginTop: '24px' }}>
              <button className="btn-primary" onClick={submitAddNote}>Generates Cards</button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: CREATE NOTE TYPE */}
      {showCreateNoteTypeModal && (
        <div className="add-card-modal-overlay">
          <div className="add-card-modal">
            <div className="modal-header">
              <h2 className="modal-title">Create Custom NoteType</h2>
              <button className="close-btn" onClick={() => {
                setShowCreateNoteTypeModal(false);
                setStep1Error('');
              }}>&times;</button>
            </div>

            {step === 1 && (
              <>
                <div className="form-group">
                  <label className="form-label">NoteType Name</label>
                  <input
                    className="form-input"
                    value={newNoteTypeName}
                    onChange={e => setNewNoteTypeName(e.target.value)}
                    placeholder="e.g. Japanese Vocabulary"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Definitions (Fields)</label>

                  <div className="field-list" style={{ marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {newDefinitions.map((def) => (
                      <div key={def.id} style={{ display: 'flex', gap: '8px' }}>
                        <input
                          className="form-input"
                          value={def.value}
                          onChange={e => handleDefChange(def.id, e.target.value)}
                          placeholder="Field name "
                          style={{ flex: 1 }}
                        />
                        <button
                          type="button"
                          className="btn-remove"
                          style={{ position: 'static', width: 'auto', padding: '0 12px', borderRadius: '6px', fontSize: '1.2rem', backgroundColor: '#ef4444', color: 'white', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                          onClick={() => handleRemoveDefinition(def.id)}
                          title="Delete field"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z" />
                            <path fillRule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z" />
                          </svg>
                        </button>
                      </div>
                    ))}
                  </div>

                  <button type="button" className="btn-secondary" onClick={handleAddDefinition}>+ Add Field</button>
                </div>

                {step1Error && (
                  <div style={{ color: '#ef4444', marginBottom: '16px', fontWeight: '500' }}>
                    {step1Error}
                  </div>
                )}

                <div style={{ textAlign: 'right', marginTop: '24px' }}>
                  <button
                    className="btn-primary"
                    onClick={handleNextStep1}
                  >
                    Next: Design Templates &rarr;
                  </button>
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <div className="form-group">
                  <label className="form-label">Available Fields to use in Templates (Kéo & thả thẻ vào khung nội dung bên dưới):</label>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '8px' }}>
                    {validDefs.map((def, idx) => (
                      <span 
                        key={idx} 
                        draggable={true}
                        onDragStart={(e) => {
                          e.dataTransfer.setData('text/plain', `{{${def}}}`);
                        }}
                        style={{ 
                          cursor: 'grab', 
                          userSelect: 'none',
                          padding: '6px 12px',
                          backgroundColor: '#3b82f6',
                          color: 'white',
                          borderRadius: '16px',
                          fontSize: '0.9rem',
                          fontWeight: '500',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          transition: 'transform 0.2s'
                        }}
                        title="Kéo & thả tôi xuống Dường Design bên dưới"
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style={{ opacity: 0.8 }}>
                          <circle cx="9" cy="5" r="1.5"></circle>
                          <circle cx="15" cy="5" r="1.5"></circle>
                          <circle cx="9" cy="12" r="1.5"></circle>
                          <circle cx="15" cy="12" r="1.5"></circle>
                          <circle cx="9" cy="19" r="1.5"></circle>
                          <circle cx="15" cy="19" r="1.5"></circle>
                        </svg>
                        {def}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="template-box">
                  <div className="form-group">
                    <label className="form-label">Card Template Name</label>
                    <input className="form-input" value={tmplName} onChange={e => setTmplName(e.target.value)} placeholder="e.g. Recognition Card" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Front Design</label>
                    <textarea className="form-textarea" value={tmplFront} onChange={e => setTmplFront(e.target.value)} placeholder={`e.g. {{${validDefs[0] || 'Front'}}}`} />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Back Design</label>
                    <textarea className="form-textarea" value={tmplBack} onChange={e => setTmplBack(e.target.value)} placeholder="Use {{Field}} syntax" />
                  </div>
                  <button className="btn-secondary" onClick={handleAddTemplate} disabled={!tmplName || !tmplFront || !tmplBack}>
                    + Add This Template
                  </button>
                </div>

                {newTemplates.length > 0 && (
                  <div className="form-group">
                    <label className="form-label">Templates Created ({newTemplates.length}): </label>
                    <div className="field-list">
                      {newTemplates.map((t, idx) => (
                        <div key={idx} className="field-item">
                          <span className="field-name">{t.name}</span>
                          <button className="btn-remove" onClick={() => setNewTemplates(newTemplates.filter((_, i) => i !== idx))}>&times;</button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
                  <button className="btn-secondary" onClick={() => setStep(1)}>&larr; Back to Fields</button>
                  <button className="btn-primary" disabled={newTemplates.length === 0} onClick={submitCreateNoteType}>
                    Finish & Create NoteType
                  </button>
                </div>
              </>
            )}

          </div>
        </div>
      )}

    </div>
  );
};

export default Cards;
