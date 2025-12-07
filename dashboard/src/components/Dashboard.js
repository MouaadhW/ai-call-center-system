import React, { useState, useEffect } from 'react';
import { getAnalytics } from '../services/api';

function Dashboard() {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchAnalytics();
        const interval = setInterval(fetchAnalytics, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const fetchAnalytics = async () => {
        try {
            const data = await getAnalytics();
            setAnalytics(data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load analytics');
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Loading dashboard...</div>;
    if (error) return <div className="error">{error}</div>;
    if (!analytics) return null;

    return (
        <div className="dashboard">
            <h2>Dashboard Overview</h2>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Calls</h3>
                    <p className="value">{analytics.total_calls || 0}</p>
                    <p className="label">All time</p>
                </div>

                <div className="stat-card">
                    <h3>Answered Calls</h3>
                    <p className="value">{analytics.answered_calls || 0}</p>
                    <p className="label">
                        {analytics.total_calls > 0
                            ? ((analytics.answered_calls / analytics.total_calls) * 100).toFixed(1)
                            : 0}% answer rate
                    </p>
                </div>

                <div className="stat-card">
                    <h3>Avg Duration</h3>
                    <p className="value">{analytics.avg_duration || 0}s</p>
                    <p className="label">Per call</p>
                </div>

                <div className="stat-card">
                    <h3>Recent Calls</h3>
                    <p className="value">{analytics.recent_calls_24h || 0}</p>
                    <p className="label">Last 24 hours</p>
                </div>
            </div>

            <div className="stats-grid">
                <div className="stat-card">
                    <h3>Total Tickets</h3>
                    <p className="value">{analytics.total_tickets || 0}</p>
                    <p className="label">{analytics.open_tickets || 0} open</p>
                </div>

                <div className="stat-card">
                    <h3>Resolved Tickets</h3>
                    <p className="value">{analytics.resolved_tickets || 0}</p>
                    <p className="label">
                        {analytics.total_tickets > 0
                            ? ((analytics.resolved_tickets / analytics.total_tickets) * 100).toFixed(1)
                            : 0}% resolution rate
                    </p>
                </div>
            </div>

            <div className="card">
                <h2>Call Intents</h2>
                {analytics.intents && Object.keys(analytics.intents).length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Intent</th>
                                <th>Count</th>
                                <th>Percentage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(analytics.intents).map(([intent, count]) => (
                                <tr key={intent}>
                                    <td>{intent}</td>
                                    <td>{count}</td>
                                    <td>{((count / analytics.total_calls) * 100).toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No intent data available</p>
                )}
            </div>

            <div className="card">
                <h2>Top Issues</h2>
                {analytics.top_issues && Object.keys(analytics.top_issues).length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th>Issue Type</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(analytics.top_issues).map(([issue, count]) => (
                                <tr key={issue}>
                                    <td>{issue}</td>
                                    <td>{count}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No issue data available</p>
                )}
            </div>
        </div>
    );
}

export default Dashboard;
