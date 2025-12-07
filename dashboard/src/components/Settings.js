import React from 'react';

function Settings() {
    return (
        <div className="settings">
            <h2>Settings</h2>

            <div className="card">
                <h3>System Configuration</h3>
                <div className="settings-group">
                    <label>
                        <strong>Company Name:</strong>
                        <input type="text" defaultValue="AI Call Center" />
                    </label>

                    <label>
                        <strong>Company Phone:</strong>
                        <input type="text" defaultValue="+1234567890" />
                    </label>

                    <label>
                        <strong>Business Hours:</strong>
                        <input type="text" defaultValue="Monday-Friday 9AM-5PM" />
                    </label>
                </div>
            </div>

            <div className="card">
                <h3>AI Configuration</h3>
                <div className="settings-group">
                    <label>
                        <strong>LLM Provider:</strong>
                        <select defaultValue="ollama">
                            <option value="ollama">Ollama</option>
                            <option value="openai">OpenAI</option>
                        </select>
                    </label>

                    <label>
                        <strong>LLM Model:</strong>
                        <input type="text" defaultValue="llama3.2:3b" />
                    </label>

                    <label>
                        <strong>Whisper Model:</strong>
                        <select defaultValue="base">
                            <option value="tiny">Tiny</option>
                            <option value="base">Base</option>
                            <option value="small">Small</option>
                            <option value="medium">Medium</option>
                            <option value="large">Large</option>
                        </select>
                    </label>
                </div>
            </div>

            <div className="card">
                <h3>Call Settings</h3>
                <div className="settings-group">
                    <label>
                        <strong>Max Call Duration (seconds):</strong>
                        <input type="number" defaultValue="600" />
                    </label>

                    <label>
                        <strong>Silence Timeout (seconds):</strong>
                        <input type="number" defaultValue="10" />
                    </label>

                    <label>
                        <input type="checkbox" defaultChecked />
                        <strong>Enable Call Recording</strong>
                    </label>

                    <label>
                        <input type="checkbox" defaultChecked />
                        <strong>Enable Analytics</strong>
                    </label>
                </div>
            </div>

            <div className="card">
                <h3>About</h3>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>System:</strong> AI Call Center</p>
                <p><strong>Status:</strong> <span className="badge success">Running</span></p>
            </div>

            <style jsx>{`
        .settings-group {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        
        .settings-group label {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        
        .settings-group input[type="text"],
        .settings-group input[type="number"],
        .settings-group select {
          padding: 0.5rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
        }
        
        .settings-group input[type="checkbox"] {
          width: auto;
          margin-right: 0.5rem;
        }
      `}</style>
        </div>
    );
}

export default Settings;
