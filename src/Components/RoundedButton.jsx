import React from 'react';

const RoundedButton = ({ routeLink, label, style, onClick }) => {
  return (
    <button
      className="rounded-button"
      style={style}
      onClick={onClick || (() => window.location.href = routeLink)} // If onClick is provided, use it, else use routeLink
    >
      {label}
    </button>
  );
};

export default RoundedButton;
