import React, { useState } from 'react';
import axios from 'axios';

const Login = () => {
    // 1. Quản lý trạng thái của các ô nhập
    const [formData, setFormData] = useState({
        username: '',
        password: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // 2. Hàm xử lý khi gõ phím
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
    e.preventDefault();
    const { username, password } = formData;
    try {
        await axios.post('http://127.0.0.1:8000/api/login/', 
            { username, password },
            { withCredentials: true } // Dòng này cực quan trọng để gửi/nhận Cookie
        );
        alert("Đã đăng nhập!");
        window.location.href = '/dashboard';
    } catch (err) {
        alert("Lỗi rồi!");
    }
};

    return (
        <div style={styles.wrapper}>
            <form onSubmit={handleSubmit} style={styles.card}>
                <h2 style={styles.title}>Anki Login</h2>
                
                {error && <div style={styles.error}>{error}</div>}

                <div style={styles.inputGroup}>
                    <label>Username</label>
                    <input
                        name="username"
                        type="text"
                        style={styles.input}
                        value={formData.username}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div style={styles.inputGroup}>
                    <label>Password</label>
                    <input
                        name="password"
                        type="password"
                        style={styles.input}
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                <button 
                    type="submit" 
                    style={{...styles.button, opacity: loading ? 0.7 : 1}}
                    disabled={loading}
                >
                    {loading ? 'Đang xử lý...' : 'Đăng nhập'}
                </button>
            </form>
        </div>
    );
};

// CSS nội bộ để bạn copy một phát là đẹp luôn
const styles = {
    wrapper: {
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        height: '100vh', backgroundColor: '#f4f7f6'
    },
    card: {
        width: '100%', maxWidth: '400px', padding: '40px',
        backgroundColor: '#fff', borderRadius: '10px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
    },
    title: { textAlign: 'center', marginBottom: '30px', color: '#333' },
    inputGroup: { marginBottom: '20px' },
    input: {
        width: '100%', padding: '12px', marginTop: '5px',
        borderRadius: '5px', border: '1px solid #ddd', boxSizing: 'border-box'
    },
    button: {
        width: '100%', padding: '12px', backgroundColor: '#4CAF50',
        color: 'white', border: 'none', borderRadius: '5px',
        cursor: 'pointer', fontSize: '16px', fontWeight: 'bold'
    },
    error: {
        backgroundColor: '#ffebee', color: '#c62828',
        padding: '10px', borderRadius: '5px', marginBottom: '20px', textAlign: 'center'
    }
};

export default Login;