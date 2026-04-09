import React, { useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api/api';

const Profile = () => {
    const navigate = useNavigate();
    const { currentUser, logout, setCurrentUser } = useContext(AuthContext);
    const [profileData, setProfileData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [editData, setEditData] = useState({});

    const fetchProfileData = useCallback(async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            if (!token) {
                navigate('/login');
                return;
            }

            const res = await api.get('/api/user/profile/');
            setProfileData(res.data);
            setEditData({
                email: res.data.email,
                first_name: res.data.first_name,
                last_name: res.data.last_name,
                phone: res.data.phone,
            });
            setError('');
        } catch (err) {
            console.error('Error fetching profile:', err);
            setError('Không thể tải thông tin hồ sơ');
            if (err.response?.status === 401) {
                logout();
            }
        } finally {
            setLoading(false);
        }
    }, [navigate, logout]);

    useEffect(() => {
        if (!currentUser) {
            navigate('/login');
            return;
        }

        fetchProfileData();
    }, [currentUser, navigate, fetchProfileData]);

    const handleEditChange = (e) => {
        const { name, value } = e.target;
        setEditData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSaveProfile = async () => {
        try {
            setIsSaving(true);
            setError('');

            const res = await api.put('/api/user/profile/update/', editData);
            
            if (res.data.success) {
                setProfileData(res.data.user);
                setCurrentUser(res.data.user);
                setIsEditing(false);
                console.log('Profile updated successfully');
            }
        } catch (err) {
            console.error('Error updating profile:', err);
            if (err.response?.data?.error) {
                setError(err.response.data.error);
            } else {
                setError('Không thể cập nhật hồ sơ');
            }
        } finally {
            setIsSaving(false);
        }
    };

    const handleCancel = () => {
        setIsEditing(false);
        setError('');
        setEditData({
            email: profileData.email,
            first_name: profileData.first_name,
            last_name: profileData.last_name,
            phone: profileData.phone,
        });
    };

    if (loading) {
        return <div style={styles.container}><p>Đang tải...</p></div>;
    }

    if (!profileData) {
        return <div style={styles.container}><p>Không tìm thấy thông tin hồ sơ</p></div>;
    }

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h1 style={styles.title}>Hồ Sơ Cá Nhân</h1>

                {error && <div style={styles.errorBox}>{error}</div>}

                {!isEditing ? (
                    <>
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>Thông Tin Cá Nhân</h2>
                            <div style={styles.infoGrid}>
                                <div style={styles.infoRow}>
                                    <span style={styles.label}>Tên đăng nhập:</span>
                                    <span style={styles.value}>{profileData.username}</span>
                                </div>
                                <div style={styles.infoRow}>
                                    <span style={styles.label}>Email:</span>
                                    <span style={styles.value}>{profileData.email}</span>
                                </div>
                                <div style={styles.infoRow}>
                                    <span style={styles.label}>Tên đầu:</span>
                                    <span style={styles.value}>{profileData.first_name || 'Chưa cập nhật'}</span>
                                </div>
                                <div style={styles.infoRow}>
                                    <span style={styles.label}>Họ:</span>
                                    <span style={styles.value}>{profileData.last_name || 'Chưa cập nhật'}</span>
                                </div>
                                <div style={styles.infoRow}>
                                    <span style={styles.label}>Số điện thoại:</span>
                                    <span style={styles.value}>{profileData.phone || 'Chưa cập nhật'}</span>
                                </div>
                            </div>
                        </div>

                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>Thống Kê Học Tập</h2>
                            <div style={styles.statsGrid}>
                                <div style={styles.statCard}>
                                    <div style={styles.statNumber}>{profileData.total_cards}</div>
                                    <div style={styles.statLabel}>Thẻ Đang Sở Hữu</div>
                                </div>
                                <div style={styles.statCard}>
                                    <div style={styles.statNumber}>{profileData.total_learned_cards}</div>
                                    <div style={styles.statLabel}>Thẻ Đã Học</div>
                                </div>
                                <div style={styles.statCard}>
                                    <div style={styles.statNumber}>{profileData.streak}</div>
                                    <div style={styles.statLabel}>Chuỗi Học Liên Tục (Ngày)</div>
                                </div>
                            </div>
                        </div>

                        <div style={styles.buttonGroup}>
                            <button 
                                onClick={() => navigate('/')}
                                style={{...styles.button, backgroundColor: '#2196F3'}}
                            >
                                Quay Lại Trang Chủ
                            </button>
                            <button 
                                onClick={() => setIsEditing(true)}
                                style={{...styles.button, backgroundColor: '#4CAF50'}}
                            >
                                Chỉnh Sửa Hồ Sơ
                            </button>
                            <button 
                                onClick={logout}
                                style={{...styles.button, backgroundColor: '#f44336'}}
                            >
                                Đăng Xuất
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        <div style={styles.section}>
                            <h2 style={styles.sectionTitle}>Chỉnh Sửa Thông Tin</h2>
                            <div style={styles.formGroup}>
                                <label style={styles.formLabel}>Email:</label>
                                <input
                                    type="email"
                                    name="email"
                                    value={editData.email}
                                    onChange={handleEditChange}
                                    style={styles.formInput}
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.formLabel}>Tên đầu:</label>
                                <input
                                    type="text"
                                    name="first_name"
                                    value={editData.first_name}
                                    onChange={handleEditChange}
                                    style={styles.formInput}
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.formLabel}>Họ:</label>
                                <input
                                    type="text"
                                    name="last_name"
                                    value={editData.last_name}
                                    onChange={handleEditChange}
                                    style={styles.formInput}
                                />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.formLabel}>Số điện thoại:</label>
                                <input
                                    type="tel"
                                    name="phone"
                                    value={editData.phone}
                                    onChange={handleEditChange}
                                    style={styles.formInput}
                                />
                            </div>
                        </div>

                        <div style={styles.buttonGroup}>
                            <button 
                                onClick={handleSaveProfile}
                                disabled={isSaving}
                                style={{
                                    ...styles.button,
                                    backgroundColor: '#4CAF50',
                                    opacity: isSaving ? 0.7 : 1,
                                    cursor: isSaving ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {isSaving ? 'Đang lưu...' : 'Lưu Thay Đổi'}
                            </button>
                            <button 
                                onClick={handleCancel}
                                disabled={isSaving}
                                style={{
                                    ...styles.button,
                                    backgroundColor: '#9E9E9E',
                                    opacity: isSaving ? 0.7 : 1,
                                    cursor: isSaving ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Hủy
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: {
        minHeight: 'calc(100vh - 200px)',
        padding: '40px 20px',
        backgroundColor: '#f4f7f6',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    },
    card: {
        width: '100%',
        maxWidth: '800px',
        padding: '40px',
        backgroundColor: '#fff',
        borderRadius: '10px',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
    },
    title: {
        textAlign: 'center',
        marginBottom: '30px',
        color: '#333',
        fontSize: '28px',
        fontWeight: 'bold',
    },
    section: {
        marginBottom: '30px',
    },
    sectionTitle: {
        fontSize: '18px',
        fontWeight: 'bold',
        color: '#2c3e50',
        marginBottom: '15px',
        paddingBottom: '10px',
        borderBottom: '2px solid #e0e0e0',
    },
    infoGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '15px',
    },
    infoRow: {
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
    },
    label: {
        fontSize: '12px',
        color: '#7f8c8d',
        fontWeight: 'bold',
        textTransform: 'uppercase',
    },
    value: {
        fontSize: '16px',
        color: '#2c3e50',
        fontWeight: '500',
        padding: '8px 12px',
        backgroundColor: '#f8f9fa',
        borderRadius: '5px',
        border: '1px solid #e0e0e0',
    },
    formGroup: {
        marginBottom: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
    },
    formLabel: {
        fontSize: '14px',
        color: '#2c3e50',
        fontWeight: '600',
    },
    formInput: {
        padding: '12px',
        borderRadius: '5px',
        border: '1px solid #ddd',
        fontSize: '16px',
        boxSizing: 'border-box',
        fontFamily: 'inherit',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: '15px',
    },
    statCard: {
        backgroundColor: '#f0f4f8',
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        border: '2px solid #e0e0e0',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
        cursor: 'pointer',
    },
    statNumber: {
        fontSize: '32px',
        fontWeight: 'bold',
        color: '#2196F3',
        marginBottom: '10px',
    },
    statLabel: {
        fontSize: '14px',
        color: '#7f8c8d',
        fontWeight: '600',
    },
    buttonGroup: {
        display: 'flex',
        gap: '10px',
        justifyContent: 'center',
        marginTop: '30px',
        paddingTop: '20px',
        borderTop: '2px solid #e0e0e0',
        flexWrap: 'wrap',
    },
    button: {
        padding: '12px 30px',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontSize: '16px',
        fontWeight: 'bold',
        transition: 'opacity 0.3s ease',
    },
    errorBox: {
        backgroundColor: '#ffebee',
        color: '#c62828',
        padding: '12px 16px',
        borderRadius: '5px',
        marginBottom: '20px',
        textAlign: 'center',
        border: '1px solid #ef5350',
    },
};

export default Profile;
