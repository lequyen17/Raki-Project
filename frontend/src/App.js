import "./App.css";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login/Login";
import Register from "./pages/Register/Register";
import Profile from "./pages/Profile/Profile";
import Decks from "./pages/Decks/Decks";
import Cards from "./pages/Cards/Cards";
import AddCard from "./pages/AddCard/AddCard";
import Study from "./pages/Study/Study";
import CardDetail from "./pages/CardDetail/CardDetail";
import Header from "./components/Common/Header/Header";
import Footer from "./components/Common/Footer/Footer";
import Setting from "./pages/Setting/Setting";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <Router>
      <AuthProvider>
        {" "}
        {/* Bọc ngoài cùng để "phủ sóng" dữ liệu cho toàn App */}
        <Toaster position="top-center" reverseOrder={false} />
        <Header />
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/decks" element={<Decks />} />
          <Route path="/decks/:deckId/cards" element={<Cards />} />
          <Route path="/decks/:deckId/add-card" element={<AddCard />} />
          <Route path="/decks/:deckId/study" element={<Study />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Setting />} />
          <Route path="/cards/:cardId" element={<CardDetail />} />
        </Routes>
        <Footer />
      </AuthProvider>
    </Router>
  );
}

export default App;
