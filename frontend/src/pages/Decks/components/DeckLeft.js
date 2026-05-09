import React, { useState, useEffect, useMemo } from "react";
import Button from "../../../components/Common/Button/Button.js";
import Input from "../../../components/Common/Input/Input.js";
import Pagination, {
  usePagination,
} from "../../../components/Common/Pagination/Pagination";

// Recursively sum total_cards for node and its children.
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

            <Button
              variant="outline"
              color="blue"
              size="sm"
              onClick={() => handleSelectDeck(node.id)}
            >
              View
            </Button>
          </div>
        </div>

        {hasChildren &&
          isExpanded &&
          node.children.map((child) => renderNode(child, currentDepth + 1))}
      </div>
    );
  };

  const {
    page,
    setPage,
    totalPages,
    paginatedItems: paginatedDecks,
  } = usePagination(treeDecks, 9);

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
        <Button
          type="button"
          color="blue"
          size="md"
          onClick={handleOpenCreateModal}
        >
          Add New Deck
        </Button>
      </div>

      {loading && <p className="decks-state">Loading decks...</p>}
      {error && <p className="decks-error">{error}</p>}
      {moveError && <p className="decks-error">{moveError}</p>}

      {!loading && !error && (
        <>
          {treeDecks.length === 0 ? (
            <p className="decks-state">No matching decks found.</p>
          ) : (
            <>
              <div className="deck-tree-list">
                {paginatedDecks.map((node) => renderNode(node))}
              </div>

              <Pagination
                page={page}
                totalPages={totalPages}
                onPageChange={setPage}
              />
            </>
          )}
        </>
      )}
    </div>
  );
};

export default DeckLeft;
