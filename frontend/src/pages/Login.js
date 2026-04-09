import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';
import { setAuthToken } from '../api/api';
import { AuthContext } from '../context/AuthContext';

const Login = () => {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { setCurrentUser } = useContext(AuthContext);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const res = await api.post('/api/login/', formData);
            const token = res.data.access;
            localStorage.setItem('access_token', token);
            setAuthToken(token);
            setCurrentUser(res.data.user);
            if (res.data.user.is_staff) {
                window.location.href = 'http://127.0.0.1:8000/admin/';
            } else {
                navigate('/');
            }
        } catch (err) {
            if (err.response && (err.response.status === 400 || err.response.status === 401)) {
                setError('Invalid username or password.');
            } else {
                setError('System error. Please try again later.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.wrapper}>
            <form onSubmit={handleSubmit} style={styles.card}>
                <h2 style={styles.title}>Login</h2>
                
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
                    {loading ? 'Please wait...' : 'Sign In'}
                </button>
            </form>
        </div>
    );
};

// Page styles
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