import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/api';

const Register = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        confirm_password: '',
        email: '',
        first_name: '',
        last_name: '',
        phone: ''
    });
    const [errors, setErrors] = useState({});
    const [generalError, setGeneralError] = useState('');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const navigate = useNavigate();

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
        if (errors[name]) {
            setErrors({ ...errors, [name]: '' });
        }
        setGeneralError('');
    };

    const validateForm = () => {
        const newErrors = {};

        if (!formData.username.trim()) {
            newErrors.username = 'Username is required';
        } else if (formData.username.trim().length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        } else if (formData.username.trim().length > 150) {
            newErrors.username = 'Username must be 150 characters or less';
        }

        if (!formData.email.trim()) {
            newErrors.email = 'Email is required';
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
            newErrors.email = 'Invalid email address';
        }

        if (!formData.first_name.trim()) {
            newErrors.first_name = 'First name is required';
        } else if (formData.first_name.trim().length < 2) {
            newErrors.first_name = 'First name must be at least 2 characters';
        } else if (formData.first_name.trim().length > 150) {
            newErrors.first_name = 'First name must be 150 characters or less';
        }

        if (!formData.last_name.trim()) {
            newErrors.last_name = 'Last name is required';
        } else if (formData.last_name.trim().length < 2) {
            newErrors.last_name = 'Last name must be at least 2 characters';
        } else if (formData.last_name.trim().length > 150) {
            newErrors.last_name = 'Last name must be 150 characters or less';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 6) {
            newErrors.password = 'Password must be at least 6 characters';
        }

        if (!formData.confirm_password) {
            newErrors.confirm_password = 'Please confirm your password';
        } else if (formData.password !== formData.confirm_password) {
            newErrors.confirm_password = 'Password confirmation does not match';
        }

        if (formData.phone && formData.phone.length > 15) {
            newErrors.phone = 'Invalid phone number';
        }

        return newErrors;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setGeneralError('');
        setSuccess(false);

        const validationErrors = validateForm();
        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            return;
        }

        setLoading(true);

        try {
            const res = await api.post('/api/register/', {
                username: formData.username.trim(),
                password: formData.password,
                confirm_password: formData.confirm_password,
                email: formData.email.trim(),
                first_name: formData.first_name.trim(),
                last_name: formData.last_name.trim(),
                phone: formData.phone.trim()
            });

            setSuccess(true);
            setFormData({
                username: '',
                password: '',
                confirm_password: '',
                email: '',
                first_name: '',
                last_name: '',
                phone: ''
            });
            setErrors({});

            setTimeout(() => {
                navigate('/login');
            }, 1000);

        } catch (err) {
            if (err.response && err.response.data && err.response.data.error) {
                setGeneralError(err.response.data.error);
            } else {
                setGeneralError('System error. Please try again later.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.wrapper}>
            <form onSubmit={handleSubmit} style={styles.card}>
                <h2 style={styles.title}>Create Account</h2>

                {success && <div style={styles.success}>Registration successful! Redirecting to login...</div>}
                {generalError && <div style={styles.error}>{generalError}</div>}

                <div style={styles.inputGroup}>
                    <label>First Name *</label>
                    <input
                        name="first_name"
                        type="text"
                        style={{...styles.input, borderColor: errors.first_name ? '#c62828' : '#ddd'}}
                        value={formData.first_name}
                        onChange={handleChange}
                        placeholder="Enter first name"
                    />
                    {errors.first_name && <span style={styles.errorText}>{errors.first_name}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Last Name *</label>
                    <input
                        name="last_name"
                        type="text"
                        style={{...styles.input, borderColor: errors.last_name ? '#c62828' : '#ddd'}}
                        value={formData.last_name}
                        onChange={handleChange}
                        placeholder="Enter last name"
                    />
                    {errors.last_name && <span style={styles.errorText}>{errors.last_name}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Username *</label>
                    <input
                        name="username"
                        type="text"
                        style={{...styles.input, borderColor: errors.username ? '#c62828' : '#ddd'}}
                        value={formData.username}
                        onChange={handleChange}
                        placeholder="Enter username"
                    />
                    {errors.username && <span style={styles.errorText}>{errors.username}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Email *</label>
                    <input
                        name="email"
                        type="email"
                        style={{...styles.input, borderColor: errors.email ? '#c62828' : '#ddd'}}
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Enter email"
                    />
                    {errors.email && <span style={styles.errorText}>{errors.email}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Phone Number</label>
                    <input
                        name="phone"
                        type="tel"
                        style={{...styles.input, borderColor: errors.phone ? '#c62828' : '#ddd'}}
                        value={formData.phone}
                        onChange={handleChange}
                        placeholder="Enter phone (optional)"
                    />
                    {errors.phone && <span style={styles.errorText}>{errors.phone}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Password *</label>
                    <input
                        name="password"
                        type="password"
                        style={{...styles.input, borderColor: errors.password ? '#c62828' : '#ddd'}}
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Enter password (at least 6 characters)"
                    />
                    {errors.password && <span style={styles.errorText}>{errors.password}</span>}
                </div>

                <div style={styles.inputGroup}>
                    <label>Confirm Password *</label>
                    <input
                        name="confirm_password"
                        type="password"
                        style={{...styles.input, borderColor: errors.confirm_password ? '#c62828' : '#ddd'}}
                        value={formData.confirm_password}
                        onChange={handleChange}
                        placeholder="Confirm password"
                    />
                    {errors.confirm_password && <span style={styles.errorText}>{errors.confirm_password}</span>}
                </div>

                <button
                    type="submit"
                    style={{...styles.button, opacity: loading ? 0.7 : 1}}
                    disabled={loading}
                >
                    {loading ? 'Please wait...' : 'Register'}
                </button>

                <div style={styles.loginLink}>
                    Already have an account? <Link to="/login" style={styles.link}>Login here</Link>
                </div>
            </form>
        </div>
    );
};

const styles = {
    wrapper: {
        display: 'flex', justifyContent: 'center', alignItems: 'center',
        minHeight: 'calc(100vh - 100px)', backgroundColor: '#f4f7f6',
        padding: '20px'
    },
    card: {
        width: '100%', maxWidth: '500px', padding: '40px',
        backgroundColor: '#fff', borderRadius: '10px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
    },
    title: { textAlign: 'center', marginBottom: '30px', color: '#333' },
    inputGroup: { marginBottom: '20px' },
    input: {
        width: '100%', padding: '12px', marginTop: '5px',
        borderRadius: '5px', border: '1px solid #ddd', boxSizing: 'border-box',
        fontSize: '14px'
    },
    button: {
        width: '100%', padding: '12px', backgroundColor: '#4CAF50',
        color: 'white', border: 'none', borderRadius: '5px',
        cursor: 'pointer', fontSize: '16px', fontWeight: 'bold',
        marginTop: '10px'
    },
    error: {
        backgroundColor: '#ffebee', color: '#c62828',
        padding: '10px', borderRadius: '5px', marginBottom: '20px', textAlign: 'center'
    },
    success: {
        backgroundColor: '#e8f5e9', color: '#2e7d32',
        padding: '10px', borderRadius: '5px', marginBottom: '20px', textAlign: 'center'
    },
    errorText: {
        color: '#c62828', fontSize: '12px', marginTop: '5px', display: 'block'
    },
    loginLink: {
        textAlign: 'center', marginTop: '20px', color: '#666', fontSize: '14px'
    },
    link: {
        color: '#4CAF50', textDecoration: 'none', fontWeight: 'bold'
    }
};

export default Register;
