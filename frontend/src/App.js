import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import Decks from './pages/Decks';
import Header from './components/header';
import Footer from './components/footer';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider> {/* Bọc ngoài cùng để "phủ sóng" dữ liệu cho toàn App */}
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<Decks />} />
          <Route path="/decks" element={<Decks />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;
