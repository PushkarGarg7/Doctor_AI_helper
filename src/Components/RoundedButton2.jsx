import React from 'react';
import '../Styles/RoundedButton2.css'; // External CSS file for styling

const RoundedButton2 = ({ label, onClick, disabled, style}) => {
  return (
    <button 
      className="rounded-button" 
      onClick={onClick} 
      disabled={disabled}
      style={style}
    >
      {label}
    </button>
  );
};

export default RoundedButton2;
