import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import { useEffect, useState } from 'react';
import { AuthProvider } from './context/AuthContext';

function App() {
  
  return (

    <AuthProvider> {/* Bọc ngoài cùng để "phủ sóng" dữ liệu cho toàn App */}
      <Router>
        
        <Routes>
          <Route path="/login" element={<Login />} />
          
          
        </Routes>
      </Router>
    </AuthProvider>

  );
}

export default App;
