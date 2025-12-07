import React, { useState } from 'react';
import './App.css';
import Dashboard from './components/Dashboard';
import CallList from './components/CallList';
import Analytics from './components/Analytics';
import Settings from './components/Settings';

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');

    const renderContent = () => {
        switch (activeTab) {
            case 'dashboard':
                return <Dashboard />;
            case 'calls':
                return <CallList />;
            case 'analytics':
                return <Analytics />;
            case 'settings':
                return <Settings />;
            default:
                return <Dashboard />;
        }
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>🤖 AI Call Center</h1>
                <nav className="nav-tabs">
                    <button
                        className={activeTab === 'dashboard' ? 'active' : ''}
                        onClick={() => setActiveTab('dashboard')}
                    >
                        Dashboard
                    </button>
                    <button
                        className={activeTab === 'calls' ? 'active' : ''}
                        onClick={() => setActiveTab('calls')}
                    >
                        Calls
                    </button>
                    <button
                        className={activeTab === 'analytics' ? 'active' : ''}
                        onClick={() => setActiveTab('analytics')}
                    >
                        Analytics
                    </button>
                    <button
                        className={activeTab === 'settings' ? 'active' : ''}
                        onClick={() => setActiveTab('settings')}
                    >
                        Settings
                    </button>
                </nav>
            </header>
            <main className="App-main">
                {renderContent()}
            </main>
        </div>
    );
}

export default App;
