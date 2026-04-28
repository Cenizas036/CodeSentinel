import React, { useState, useCallback } from 'react';
import './Analyzer.css';

const SAMPLE_CODE = `# sample_code.py — Test file for CodeSentinel
import os
import pickle

# SECURITY: Hardcoded credentials
DATABASE_PASSWORD = "super_secret_123"
API_KEY = "sk-abc123def456"

def process_user_input(user_data):
    """Process raw user input — has multiple issues."""
    result = eval(user_data)
    os.system("echo " + user_data)
    obj = pickle.loads(user_data.encode())
    return result

def deeply_nested(a, b, c, d, e, f, g):
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
    return 0

class MassiveController:
    def action_1(self): pass
    def action_2(self): pass
    def action_3(self): pass
    def action_4(self): pass
    def action_5(self): pass
    def action_6(self): pass
    def action_7(self): pass
    def action_8(self): pass
    def action_9(self): pass
    def action_10(self): pass
    def action_11(self): pass
    def action_12(self): pass
    def action_13(self): pass
    def action_14(self): pass
    def action_15(self): pass
    def action_16(self): pass
    def action_17(self): pass
    def action_18(self): pass
    def action_19(self): pass
    def action_20(self): pass
    def action_21(self): pass

def buggy_error_handling():
    try:
        x = 1 / 0
    except:
        pass
`;

const SEVERITY_CONFIG = {
  critical: { label: 'CRITICAL', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', icon: '🔴' },
  high:     { label: 'HIGH',     color: '#f97316', bg: 'rgba(249,115,22,0.1)', icon: '🟠' },
  medium:   { label: 'MEDIUM',   color: '#eab308', bg: 'rgba(234,179,8,0.1)', icon: '🟡' },
  low:      { label: 'LOW',      color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', icon: '🔵' },
  info:     { label: 'INFO',     color: '#94a3b8', bg: 'rgba(148,163,184,0.1)', icon: '⚪' },
};

const Analyzer = () => {
  const [code, setCode] = useState(SAMPLE_CODE);
  const [language, setLanguage] = useState('python');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('issues');

  const handleAnalyze = useCallback(async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const apiBase = window.location.hostname === 'localhost'
        ? 'http://127.0.0.1:5000'
        : '';
      const res = await fetch(`${apiBase}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.error || 'API request failed');
      }

      const data = await res.json();
      setResults(data);
      setActiveTab('issues');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [code, language]);

  const getGradeColor = (grade) => {
    const map = { A: '#10b981', B: '#22d3ee', C: '#eab308', D: '#f97316', F: '#ef4444' };
    return map[grade] || '#94a3b8';
  };

  return (
    <section className="analyzer" id="analyzer">
      <div className="container">
        {/* Header */}
        <div className="analyzer__header">
          <span className="tech-label text-emerald">Live Analysis Engine</span>
          <h2 className="analyzer__title font-serif">Analyze Your Code</h2>
          <p className="analyzer__subtitle text-muted">
            Paste your code below and let CodeSentinel scan for security vulnerabilities, quality issues, and architectural problems in real-time.
          </p>
        </div>

        {/* Editor + Controls */}
        <div className="analyzer__workspace">
          <div className="analyzer__editor-panel">
            <div className="analyzer__editor-toolbar">
              <div className="analyzer__editor-dots">
                <span style={{ background: 'rgba(255,80,80,0.7)' }}></span>
                <span style={{ background: 'rgba(255,200,50,0.7)' }}></span>
                <span style={{ background: 'rgba(80,200,120,0.7)' }}></span>
              </div>
              <select
                className="analyzer__lang-select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
              </select>
            </div>

            <textarea
              className="analyzer__textarea font-mono"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="Paste your code here..."
              spellCheck={false}
            />

            <div className="analyzer__editor-footer">
              <span className="tech-label" style={{ color: 'rgba(235,235,235,0.3)' }}>
                {code.split('\n').length} lines • {language}
              </span>
              <button
                className="btn-pill btn-emerald analyzer__run-btn"
                onClick={handleAnalyze}
                disabled={loading || !code.trim()}
              >
                {loading ? (
                  <>
                    <span className="analyzer__spinner"></span>
                    Analyzing...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                    </svg>
                    Analyze Code
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Panel */}
          {error && (
            <div className="analyzer__error">
              <strong>Error:</strong> {error}
              <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', opacity: 0.6 }}>
                Make sure the API server is running: <code>python api.py</code>
              </p>
            </div>
          )}

          {results && (
            <div className="analyzer__results">
              {/* Summary Cards */}
              <div className="analyzer__summary-grid">
                <div className="analyzer__summary-card">
                  <span className="analyzer__summary-value font-mono" style={{ color: getGradeColor(results.metrics.grade) }}>
                    {results.metrics.grade}
                  </span>
                  <span className="tech-label" style={{ color: 'rgba(235,235,235,0.4)' }}>Grade</span>
                </div>
                <div className="analyzer__summary-card">
                  <span className="analyzer__summary-value font-mono text-emerald">
                    {results.metrics.overall_score}
                  </span>
                  <span className="tech-label" style={{ color: 'rgba(235,235,235,0.4)' }}>Score /100</span>
                </div>
                <div className="analyzer__summary-card">
                  <span className="analyzer__summary-value font-mono" style={{ color: results.summary.total_issues > 5 ? '#f97316' : '#10b981' }}>
                    {results.summary.total_issues}
                  </span>
                  <span className="tech-label" style={{ color: 'rgba(235,235,235,0.4)' }}>Issues</span>
                </div>
                <div className="analyzer__summary-card">
                  <span className="analyzer__summary-value font-mono" style={{ color: results.summary.critical > 0 ? '#ef4444' : '#10b981' }}>
                    {results.summary.critical}
                  </span>
                  <span className="tech-label" style={{ color: 'rgba(235,235,235,0.4)' }}>Critical</span>
                </div>
              </div>

              {/* Tabs */}
              <div className="analyzer__tabs">
                <button
                  className={`analyzer__tab ${activeTab === 'issues' ? 'analyzer__tab--active' : ''}`}
                  onClick={() => setActiveTab('issues')}
                >
                  Issues ({results.summary.total_issues})
                </button>
                <button
                  className={`analyzer__tab ${activeTab === 'metrics' ? 'analyzer__tab--active' : ''}`}
                  onClick={() => setActiveTab('metrics')}
                >
                  Quality Metrics
                </button>
              </div>

              {/* Issues Tab */}
              {activeTab === 'issues' && (
                <div className="analyzer__issues-list">
                  {results.issues.length === 0 ? (
                    <div className="analyzer__no-issues">
                      <span style={{ fontSize: '2rem' }}>✅</span>
                      <p>No issues found. Your code looks clean!</p>
                    </div>
                  ) : (
                    results.issues.map((issue, i) => {
                      const sev = SEVERITY_CONFIG[issue.severity] || SEVERITY_CONFIG.info;
                      return (
                        <div key={i} className="analyzer__issue" style={{ borderLeftColor: sev.color }}>
                          <div className="analyzer__issue-header">
                            <span className="analyzer__issue-badge" style={{ background: sev.bg, color: sev.color }}>
                              {sev.icon} {sev.label}
                            </span>
                            <span className="tech-label" style={{ color: 'rgba(235,235,235,0.3)' }}>
                              Line {issue.line} • {issue.category}
                            </span>
                          </div>
                          <p className="analyzer__issue-message">{issue.message}</p>
                        </div>
                      );
                    })
                  )}
                </div>
              )}

              {/* Metrics Tab */}
              {activeTab === 'metrics' && (
                <div className="analyzer__metrics-grid">
                  <MetricRow label="Overall Score" value={`${results.metrics.overall_score}/100`} accent />
                  <MetricRow label="Grade" value={results.metrics.grade} accent />
                  <MetricRow label="Functions" value={results.metrics.function_count} />
                  <MetricRow label="Classes" value={results.metrics.class_count} />
                  <MetricRow label="Avg Complexity" value={results.metrics.avg_cyclomatic_complexity} />
                  <MetricRow label="Maintainability" value={results.metrics.maintainability_index} />
                  <MetricRow label="Lines of Code" value={results.metrics.lines_of_code?.code} />
                  <MetricRow label="Comments" value={results.metrics.lines_of_code?.comments} />
                  <MetricRow label="Comment Ratio" value={`${(results.metrics.comment_ratio * 100).toFixed(1)}%`} />
                  <MetricRow label="Duplication" value={`${results.metrics.duplication_score?.duplication_percentage}%`} />
                  <MetricRow label="Naming Conformance" value={`${(results.metrics.naming_quality?.naming_conformance * 100).toFixed(1)}%`} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

const MetricRow = ({ label, value, accent }) => (
  <div className="analyzer__metric-row">
    <span className="analyzer__metric-label">{label}</span>
    <span className={`analyzer__metric-value font-mono ${accent ? 'text-emerald' : ''}`}>
      {value ?? '—'}
    </span>
  </div>
);

export default Analyzer;
