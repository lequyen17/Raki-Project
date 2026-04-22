import React from "react";

// Tính tổng đệ quy total_cards của node và tất cả deck con
const sumTotalCards = (node) => {
  const own = node.total_cards || 0;
  return node.children.reduce((acc, child) => acc + sumTotalCards(child), own);
};

const DeckLeft = ({
  searchText,
  setSearchText,
  handleOpenCreateModal,
  loading,
  error,
  moveError,
  treeDecks,
  expandedIds,
  toggleExpanded,
  dropTargetId,
  setDropTargetId,
  draggingDeckId,
  handleDragStart,
  handleDragEnd,
  handleDropOnDeck,
  selectedDeckId,
  handleSelectDeck,
}) => {
  const renderNode = (node, depth) => {
    const currentDepth = depth ?? 0;

    const hasChildren = node.children.length > 0;
    const isExpanded = expandedIds.has(node.id);

    return (
      <div key={node.id} className="deck-tree-node">
        <div
          className={`deck-tree-row ${
            currentDepth === 0 ? "deck-tree-row--root" : "deck-tree-row--child"
          } ${dropTargetId === node.id ? "deck-tree-row--drop" : ""}`}
          style={{ marginLeft: `${currentDepth * 24}px` }}
          draggable
          onDragStart={(e) => handleDragStart(e, node.id)}
          onDragEnd={handleDragEnd}
          onDragOver={(e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = "move";
            setDropTargetId(node.id);
          }}
          onDragLeave={() => setDropTargetId(null)}
          onDrop={(e) => {
            e.preventDefault();
            e.stopPropagation();
            handleDropOnDeck(node.id);
          }}
        >
          <button
            type="button"
            className="deck-expand-btn"
            onClick={() => hasChildren && toggleExpanded(node.id)}
          >
            {hasChildren ? (isExpanded ? "v" : ">") : "-"}
          </button>

          <div className="deck-drag-handle">::</div>

          <div className="deck-row-main">
            <button
              type="button"
              className={`deck-row-name ${
                selectedDeckId === node.id ? "deck-row-name--selected" : ""
              }`}
              onClick={() => handleSelectDeck(node.id)}
            >
              {node.name}
            </button>

            <span className="deck-row-count">{sumTotalCards(node)} cards</span>

            <button
              type="button"
              className="deck-view-btn"
              onClick={() => handleSelectDeck(node.id)}
            >
              View
            </button>
          </div>
        </div>

        {hasChildren &&
          isExpanded &&
          node.children.map((child) => renderNode(child, currentDepth + 1))}
      </div>
    );
  };

  return (
    <div className="decks-container">
      <h1 className="decks-title">My Decks</h1>

      <div className="decks-toolbar">
        <input
          type="text"
          className="decks-search"
          placeholder="Search deck..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <button
          type="button"
          className="decks-add-btn"
          onClick={handleOpenCreateModal}
        >
          Add New Deck
        </button>
      </div>

      {loading && <p className="decks-state">Dang tai danh sach deck...</p>}
      {error && <p className="decks-error">{error}</p>}
      {moveError && <p className="decks-error">{moveError}</p>}

      {!loading && !error && (
        <>
          {treeDecks.length === 0 ? (
            <p className="decks-state">Khong tim thay deck phu hop.</p>
          ) : (
            <div className="deck-tree-list">
              {treeDecks.map((node) => renderNode(node))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default DeckLeft;
