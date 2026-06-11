// Bên code ReactJS cũ
import React from 'react';

export default function Intro() {
  return (
    <div style={{ width: '100%', height: 'calc(100vh - 80px)' }}> 
      {/* 80px là chiều cao của Header React */}
      <iframe 
        src="http://localhost:3000/intro" // Hoặc gọi qua proxy mạng Docker
        style={{ width: '100%', height: '100%', border: 'none' }}
        title="NextJS Intro Page"
      />
    </div>
  );
}