import React, { useState, useEffect } from 'react';
import { getCalls } from '../services/api';

function CallList() {
    const [calls, setCalls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedCall, setSelectedCall] = useState(null);

    useEffect(() => {
        fetchCalls();
    }, []);

    const fetchCalls = async () => {
        try {
            const data = await getCalls();
            setCalls(data);
            setLoading(false);
        } catch (err) {
            console.error('Failed to load calls:', err);
            setLoading(false);
        }
    };

    const formatDuration = (seconds) => {
        if (!seconds) return 'N/A';
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString();
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            'completed': 'success',
            'in_progress': 'warning',
            'failed': 'danger'
        };
        return statusMap[status] || 'info';
    };

    if (loading) return <div className="loading">Loading calls...</div>;

    return (
        <div className="call-list">
            <h2>Call History</h2>

            <div className="card">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Caller</th>
                            <th>Start Time</th>
                            <th>Duration</th>
                            <th>Intent</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {calls.map((call) => (
                            <tr key={call.id}>
                                <td>{call.id}</td>
                                <td>{call.caller_number || 'Unknown'}</td>
                                <td>{formatDate(call.start_time)}</td>
                                <td>{formatDuration(call.duration)}</td>
                                <td>{call.intent || 'N/A'}</td>
                                <td>
                                    <span className={`badge ${getStatusBadge(call.status)}`}>
                                        {call.status}
                                    </span>
                                </td>
                                <td>
                                    <button onClick={() => setSelectedCall(call)}>View</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {selectedCall && (
                <div className="modal-overlay" onClick={() => setSelectedCall(null)}>
                    <div className="modal" onClick={(e) => e.stopPropagation()}>
                        <h2>Call Details - #{selectedCall.id}</h2>
                        <div className="call-details">
                            <p><strong>Caller:</strong> {selectedCall.caller_number}</p>
                            <p><strong>Start Time:</strong> {formatDate(selectedCall.start_time)}</p>
                            <p><strong>End Time:</strong> {formatDate(selectedCall.end_time)}</p>
                            <p><strong>Duration:</strong> {formatDuration(selectedCall.duration)}</p>
                            <p><strong>Intent:</strong> {selectedCall.intent || 'N/A'}</p>
                            <p><strong>Status:</strong> {selectedCall.status}</p>
                            <p><strong>Resolution:</strong> {selectedCall.resolution_status || 'N/A'}</p>

                            {selectedCall.transcript && (
                                <div className="transcript">
                                    <h3>Transcript</h3>
                                    <pre>{selectedCall.transcript}</pre>
                                </div>
                            )}
                        </div>
                        <button onClick={() => setSelectedCall(null)}>Close</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default CallList;
