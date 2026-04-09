import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Header from './components/header';
import Footer from './components/footer';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider> {/* Bọc ngoài cùng để "phủ sóng" dữ liệu cho toàn App */}
      <Router>
        <Header />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;
