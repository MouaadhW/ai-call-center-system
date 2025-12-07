import React, { useState, useEffect } from 'react';
import { getDailyAnalytics, getIntentAnalytics } from '../services/api';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'];

function Analytics() {
    const [dailyData, setDailyData] = useState([]);
    const [intentData, setIntentData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [days, setDays] = useState(7);

    useEffect(() => {
        fetchAnalytics();
    }, [days]);

    const fetchAnalytics = async () => {
        try {
            const [daily, intents] = await Promise.all([
                getDailyAnalytics(days),
                getIntentAnalytics()
            ]);
            setDailyData(daily);
            setIntentData(intents);
            setLoading(false);
        } catch (err) {
            console.error('Failed to load analytics:', err);
            setLoading(false);
        }
    };

    if (loading) return <div className="loading">Loading analytics...</div>;

    return (
        <div className="analytics">
            <h2>Analytics</h2>

            <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h3>Daily Call Volume</h3>
                    <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
                        <option value={7}>Last 7 days</option>
                        <option value={14}>Last 14 days</option>
                        <option value={30}>Last 30 days</option>
                    </select>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={dailyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="total_calls" stroke="#667eea" strokeWidth={2} name="Total Calls" />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            <div className="card">
                <h3>Average Call Duration (seconds)</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={dailyData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="avg_duration" fill="#764ba2" name="Avg Duration" />
                    </BarChart>
                </ResponsiveContainer>
            </div>

            <div className="card">
                <h3>Intent Distribution</h3>
                <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                        <Pie
                            data={intentData}
                            dataKey="count"
                            nameKey="intent"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            label
                        >
                            {intentData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip />
                        <Legend />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            <div className="card">
                <h3>Intent Statistics</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Intent</th>
                            <th>Count</th>
                            <th>Avg Duration</th>
                        </tr>
                    </thead>
                    <tbody>
                        {intentData.map((item) => (
                            <tr key={item.intent}>
                                <td>{item.intent}</td>
                                <td>{item.count}</td>
                                <td>{item.avg_duration}s</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Analytics;
