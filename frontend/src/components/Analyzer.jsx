import React, { useState, useCallback, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { listFiles, readFile, saveFile, createFile } from '../services/drive';
import './Analyzer.css';

const SAMPLE_CODES = {
  python: `# sample_code.py — Test file for CodeSentinel
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
`,
  javascript: `// app.js — JavaScript Sample with Issues
const API_KEY = "sk-live-abc123456789";
var password = "admin123";

function processUserInput(input) {
  // FIXME: This is dangerous
  var result = eval(input);
  document.getElementById("output").innerHTML = input;
  console.log("Processing:", input);

  if (input == null) {
    if (input == undefined) {
      alert("No input provided!");
    }
  }
  return result;
}

function fetchData(url) {
  try {
    var response = fetch(url);
  } catch (err) {
  }
}

document.write("<h1>Welcome</h1>");
`,
  typescript: `// service.ts — TypeScript Sample with Issues
const API_SECRET = "ts-secret-key-12345";

function processData(data: any): any {
  const result = eval(data as any);
  document.getElementById("output")!.innerHTML = data;
  console.log("Debug:", result);

  if (data == null) {
    return undefined;
  }

  // TODO: Add proper validation
  return result;
}

async function fetchAPI(url: string) {
  try {
    const res = await fetch(url);
  } catch (e) {
  }
}
`,
  java: `// UserService.java — Java Sample with Issues
import java.sql.*;
import java.io.*;

public class UserService {
    private static final String DB_PASSWORD = "root123";

    public void processInput(String userInput) throws Exception {
        // SQL Injection vulnerability
        Statement stmt = connection.createStatement();
        stmt.execute("SELECT * FROM users WHERE name = '" + userInput + "'");

        Runtime.getRuntime().exec(userInput);
        System.out.println("Processing: " + userInput);

        try {
            riskyOperation();
        } catch (Exception e) {
        }

        ObjectInputStream ois = new ObjectInputStream(
            new FileInputStream("data.ser"));
        Object obj = ois.readObject();
    }
}
`,
  c: `/* buffer.c — C Sample with Issues */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char password[] = "hardcoded_pass123";

void process_input(char *input) {
    char buffer[64];
    gets(input);
    strcpy(buffer, input);
    strcat(buffer, " processed");
    sprintf(buffer, "Result: %s", input);

    system(input);
    printf(input);

    char *data = malloc(1024);
    scanf("%s", buffer);
}
`,
  cpp: `// engine.cpp — C++ Sample with Issues
#include <iostream>
#include <cstring>
using namespace std;

string api_key = "cpp-secret-key-999";

class DataProcessor {
public:
    void process(const char* input) {
        char buffer[128];
        strcpy(buffer, input);
        strcat(buffer, "_processed");

        int* ptr = reinterpret_cast<int*>(buffer);
        const_cast<char*>(input);

        int* data = new int[100];
        system(input);

        goto cleanup;
    cleanup:
        delete[] data;
    }
};
`,
  go: `// server.go — Go Sample with Issues
package main

import (
    "fmt"
    "net/http"
    "os/exec"
)

var apiToken = "go-token-secret-abc"

func handleRequest(w http.ResponseWriter, r *http.Request) {
    input := r.URL.Query().Get("cmd")

    cmd := exec.Command("sh", "-c", input)
    output, _ := cmd.Output()
    fmt.Println("Executed:", string(output))

    http.ListenAndServe(":8080", nil)

    if input == "" {
        panic("empty input received")
    }
}
`,
  rust: `// processor.rs — Rust Sample with Issues
use std::mem;

static API_KEY: &str = "rust-secret-key-xyz";

fn process_data(input: &str) -> String {
    let result = unsafe {
        let ptr = input.as_ptr();
        std::mem::transmute::<*const u8, usize>(ptr)
    };

    let parsed: i32 = input.parse().unwrap();
    let value = Some(42).expect("Should have value");

    let data = input.to_string().clone();

    // TODO: Handle errors properly
    data
}
`,
  ruby: `# service.rb — Ruby Sample with Issues
DB_PASSWORD = "ruby_secret_pass"

def process_input(user_data)
  system("echo #{user_data}")
  result = eval(user_data)

  obj.send(user_data.to_sym)

  puts "Debug: #{result}"

  begin
    risky_operation
  rescue
  end

  open(user_data)
  result
end
`,
  php: `<?php
// api.php — PHP Sample with Issues
$db_password = "php_admin_pass";

function processInput($input) {
    $result = mysql_query("SELECT * FROM users WHERE id = " . $input);

    exec("ls " . $input);
    shell_exec($input);
    system("echo " . $input);

    $hash = md5($input);

    $name = $_GET['name'];
    $data = $_POST['data'];

    $obj = unserialize($input);
    extract($_POST);

    eval($input);
    echo $result;
}
?>
`,
  csharp: `// UserController.cs — C# Sample with Issues
using System.Data.SqlClient;
using System.Diagnostics;
using System.Runtime.Serialization.Formatters.Binary;

public class UserController {
    private string apiKey = "csharp-secret-key";

    public void ProcessInput(string userInput) {
        var cmd = new SqlCommand("SELECT * FROM Users WHERE Name = '" + userInput + "'");
        Process.Start("cmd", "/c " + userInput);
        var formatter = new BinaryFormatter();

        try {
            RiskyOperation();
        } catch (Exception ex) {
        }

        Console.WriteLine("Processing: " + userInput);
    }
}
`,
  swift: `// DataManager.swift — Swift Sample with Issues
import Foundation

let apiSecret = "swift-secret-key-123"

class DataManager {
    func processInput(_ input: String) {
        let task = Process()
        task.launchPath = "/bin/sh"
        task.arguments = ["-c", input]

        let ptr = UnsafePointer<Int>.allocate(capacity: 10)
        let mutablePtr = UnsafeMutablePointer<Int>.allocate(capacity: 10)

        print("Processing: \\(input)")
    }
}
`,
  kotlin: `// UserService.kt — Kotlin Sample with Issues
import java.sql.Statement

class UserService {
    val dbPassword = "kotlin_secret_123"

    fun processInput(userInput: String) {
        val stmt = connection.createStatement()
        stmt.execute("SELECT * FROM users WHERE name = '\$userInput'")

        Runtime.getRuntime().exec(userInput)
        println("Processing: \$userInput")

        try {
            riskyOperation()
        } catch (e: Exception) {
        }
    }
}
`,
  html: `<!-- index.html — HTML Sample with Issues -->
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    <!-- SECURITY: Loading script over HTTP -->
    <script src="http://example.com/insecure.js"></script>
</head>
<body>
    <h1>Welcome</h1>
    
    <!-- Inline event handler (XSS risk) -->
    <button onclick="eval(userInput)">Click Me</button>
    
    <!-- Deprecated tags -->
    <center>
        <font color="red">Warning: Invalid input</font>
    </center>
    
    <!-- iframe without sandbox -->
    <iframe src="https://untrusted.com/widget"></iframe>
</body>
</html>
`,
  css: `/* styles.css — CSS Sample with Issues */

/* Performance: using @import inside CSS is slow */
@import url("http://example.com/fonts.css");

/* Overusing !important */
.button {
    color: #fff !important;
    background-color: red !important;
}

/* Inefficient selector (too broad) */
* {
    margin: 0;
}
div span a {
    text-decoration: none;
}

/* Hardcoded, inaccessible color contrast */
.text-light {
    color: #ccc;
    background: #ddd;
}
`
};

const SEVERITY_CONFIG = {
  critical: { label: 'CRITICAL', color: '#ef4444', bg: 'rgba(239,68,68,0.1)', icon: '🔴' },
  high:     { label: 'HIGH',     color: '#f97316', bg: 'rgba(249,115,22,0.1)', icon: '🟠' },
  medium:   { label: 'MEDIUM',   color: '#eab308', bg: 'rgba(234,179,8,0.1)',  icon: '🟡' },
  low:      { label: 'LOW',      color: '#3b82f6', bg: 'rgba(59,130,246,0.1)', icon: '🔵' },
  info:     { label: 'INFO',     color: '#94a3b8', bg: 'rgba(148,163,184,0.1)', icon: '⚪' },
};

const OPT_TYPE_CONFIG = {
  security:    { label: 'Security', color: '#ef4444', icon: '🛡️' },
  quality:     { label: 'Quality',  color: '#eab308', icon: '✨' },
  performance: { label: 'Perf',     color: '#3b82f6', icon: '⚡' },
};

const LANGUAGES = [
  { value: 'python', label: 'Python', monaco: 'python' },
  { value: 'javascript', label: 'JavaScript', monaco: 'javascript' },
  { value: 'typescript', label: 'TypeScript', monaco: 'typescript' },
  { value: 'html', label: 'HTML', monaco: 'html' },
  { value: 'css', label: 'CSS', monaco: 'css' },
  { value: 'java', label: 'Java', monaco: 'java' },
  { value: 'c', label: 'C', monaco: 'c' },
  { value: 'cpp', label: 'C++', monaco: 'cpp' },
  { value: 'go', label: 'Go', monaco: 'go' },
  { value: 'rust', label: 'Rust', monaco: 'rust' },
  { value: 'ruby', label: 'Ruby', monaco: 'ruby' },
  { value: 'php', label: 'PHP', monaco: 'php' },
  { value: 'csharp', label: 'C#', monaco: 'csharp' },
  { value: 'swift', label: 'Swift', monaco: 'swift' },
  { value: 'kotlin', label: 'Kotlin', monaco: 'kotlin' },
];

const Analyzer = ({ user, onLoginClick }) => {
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState(SAMPLE_CODES['python']);
  const [activeFileId, setActiveFileId] = useState(null);
  const [driveFiles, setDriveFiles] = useState([]);
  const [loadingDrive, setLoadingDrive] = useState(false);
  const [results, setResults] = useState(null);
  const [optimizeResults, setOptimizeResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('issues');
  const [showDiff, setShowDiff] = useState(false);
  const editorRef = useRef(null);

  useEffect(() => {
    if (user && localStorage.getItem('googleOAuthToken')) {
      fetchDriveFiles();
    } else {
      setDriveFiles([]);
      setActiveFileId(null);
    }
  }, [user]);

  const fetchDriveFiles = async () => {
    setLoadingDrive(true);
    try {
      const files = await listFiles();
      setDriveFiles(files);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch Drive files. Token might be expired.');
    } finally {
      setLoadingDrive(false);
    }
  };

  const handleFileClick = async (file) => {
    try {
      setLoading(true);
      const content = await readFile(file.id);
      setCode(content);
      setActiveFileId(file.id);
      
      // Guess language by extension
      let lang = 'python';
      const name = file.name.toLowerCase();
      if (name.endsWith('.js')) lang = 'javascript';
      else if (name.endsWith('.ts')) lang = 'typescript';
      else if (name.endsWith('.html')) lang = 'html';
      else if (name.endsWith('.css')) lang = 'css';
      else if (name.endsWith('.java')) lang = 'java';
      else if (name.endsWith('.c')) lang = 'c';
      else if (name.endsWith('.cpp')) lang = 'cpp';
      else if (name.endsWith('.go')) lang = 'go';
      else if (name.endsWith('.rs')) lang = 'rust';
      else if (name.endsWith('.rb')) lang = 'ruby';
      else if (name.endsWith('.php')) lang = 'php';
      else if (name.endsWith('.cs')) lang = 'csharp';
      else if (name.endsWith('.swift')) lang = 'swift';
      else if (name.endsWith('.kt')) lang = 'kotlin';
      setLanguage(lang);
      
      setResults(null);
      setOptimizeResults(null);
    } catch (err) {
      setError('Failed to load file from Drive');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveToDrive = async () => {
    if (!user) return onLoginClick();
    setSaving(true);
    setError(null);
    try {
      if (activeFileId) {
        await saveFile(activeFileId, code);
      } else {
        const extMap = { python: '.py', javascript: '.js', typescript: '.ts', html: '.html', css: '.css', java: '.java', c: '.c', cpp: '.cpp', go: '.go', rust: '.rs', ruby: '.rb', php: '.php', csharp: '.cs', swift: '.swift', kotlin: '.kt' };
        const ext = extMap[language] || '.txt';
        const newFile = await createFile(`snippet_${Date.now()}${ext}`, code);
        setActiveFileId(newFile.id);
        fetchDriveFiles();
      }
    } catch (err) {
      setError('Failed to save to Google Drive.');
    } finally {
      setSaving(false);
    }
  };

  const handleLanguageChange = (e) => {
    const lang = e.target.value;
    setLanguage(lang);
    setCode(SAMPLE_CODES[lang] || '');
    setActiveFileId(null);
    setResults(null);
    setOptimizeResults(null);
    setError(null);
  };

  const apiBase = window.location.hostname === 'localhost' ? 'http://127.0.0.1:5000' : '';

  const handleAnalyze = useCallback(async () => {
    if (!code.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    setOptimizeResults(null);

    try {
      const res = await fetch(`${apiBase}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'API failed');
      const data = await res.json();
      setResults(data);
      setActiveTab('issues');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [code, language, apiBase]);

  const handleOptimize = useCallback(async () => {
    if (!code.trim()) return;
    setOptimizing(true);
    setError(null);
    setOptimizeResults(null);

    try {
      const res = await fetch(`${apiBase}/api/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });
      if (!res.ok) throw new Error((await res.json()).error || 'Optimization failed');
      const data = await res.json();
      setOptimizeResults(data);
      setActiveTab('optimizations');
    } catch (err) {
      setError(err.message);
    } finally {
      setOptimizing(false);
    }
  }, [code, language, apiBase]);

  const applyOptimizedCode = () => {
    if (optimizeResults?.optimized_code) {
      setCode(optimizeResults.optimized_code);
      setOptimizeResults(null);
      setResults(null);
    }
  };

  const getGradeColor = (grade) => {
    const map = { A: '#10b981', B: '#22d3ee', C: '#eab308', D: '#f97316', F: '#ef4444' };
    return map[grade] || '#94a3b8';
  };

  const monacoLang = LANGUAGES.find(l => l.value === language)?.monaco || 'python';

  return (
    <section className="analyzer" id="analyzer">
      <div className="container">
        <div className="analyzer__header">
          <span className="tech-label text-emerald">Live IDE + Analysis Engine</span>
          <h2 className="analyzer__title font-serif">CodeSentinel IDE</h2>
          <p className="analyzer__subtitle text-muted">
            Write or paste code, analyze for vulnerabilities, and <strong>optimize with one click</strong>. Supports <strong>15 languages</strong>.
          </p>
        </div>

        <div className="analyzer__workspace">
          {/* Drive Sidebar */}
          {user && (
            <div className="analyzer__sidebar">
              <div className="analyzer__sidebar-header">
                <span className="tech-label">Google Drive</span>
                <button className="btn-pill btn-ghost" onClick={fetchDriveFiles} style={{ padding: '0.25rem' }}>
                  ↻
                </button>
              </div>
              <div className="analyzer__sidebar-list">
                {loadingDrive ? (
                  <div className="text-muted" style={{ padding: '1rem', fontSize: '0.85rem' }}>Loading files...</div>
                ) : driveFiles.length === 0 ? (
                  <div className="text-muted" style={{ padding: '1rem', fontSize: '0.85rem' }}>No files found.</div>
                ) : (
                  driveFiles.map(file => (
                    <button 
                      key={file.id} 
                      className={`analyzer__sidebar-item ${activeFileId === file.id ? 'active' : ''}`}
                      onClick={() => handleFileClick(file)}
                    >
                      📄 {file.name}
                    </button>
                  ))
                )}
              </div>
            </div>
          )}

          <div className="analyzer__editor-panel" style={{ flex: 1 }}>
            <div className="analyzer__editor-toolbar">
              <div className="analyzer__editor-dots">
                <span style={{ background: 'rgba(255,80,80,0.7)' }}></span>
                <span style={{ background: 'rgba(255,200,50,0.7)' }}></span>
                <span style={{ background: 'rgba(80,200,120,0.7)' }}></span>
              </div>
              <div className="analyzer__toolbar-center">
                <span className="analyzer__file-label font-mono">
                  {activeFileId ? driveFiles.find(f => f.id === activeFileId)?.name : (LANGUAGES.find(l => l.value === language)?.label || language)}
                </span>
              </div>
              <div className="analyzer__toolbar-right" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <button 
                  className="btn-pill btn-ghost" 
                  onClick={handleSaveToDrive} 
                  disabled={saving}
                  style={{ padding: '0.25rem 0.75rem', fontSize: '0.85rem' }}
                >
                  {saving ? 'Saving...' : '💾 Save to Drive'}
                </button>
                <select
                  className="analyzer__lang-select"
                  value={language}
                  onChange={handleLanguageChange}
                >
                  {LANGUAGES.map(l => (
                    <option key={l.value} value={l.value}>{l.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="analyzer__monaco-wrapper">
              <Editor
                height="420px"
                language={monacoLang}
                value={code}
                onChange={(val) => setCode(val || '')}
                theme="vs-dark"
                options={{
                  fontSize: 13.5,
                  fontFamily: "'Space Grotesk', 'Fira Code', Consolas, monospace",
                  minimap: { enabled: true, scale: 1 },
                  scrollBeyondLastLine: false,
                  wordWrap: 'off',
                  automaticLayout: true,
                  padding: { top: 16, bottom: 16 },
                  lineNumbers: 'on',
                  renderLineHighlight: 'line',
                  bracketPairColorization: { enabled: true },
                  smoothScrolling: true,
                  cursorBlinking: 'smooth',
                  cursorSmoothCaretAnimation: 'on',
                  suggestOnTriggerCharacters: true,
                  tabSize: 4,
                }}
                onMount={(editor, monaco) => { 
                  editorRef.current = editor; 
                  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
                    handleSaveToDrive();
                  });
                }}
              />
            </div>

            <div className="analyzer__editor-footer">
              <span className="tech-label" style={{ color: 'rgba(235,235,235,0.3)' }}>
                {code.split('\n').length} lines • {LANGUAGES.find(l => l.value === language)?.label || language}
              </span>
              <div className="analyzer__action-btns">
                <button
                  className="btn-pill btn-emerald analyzer__run-btn"
                  onClick={handleAnalyze}
                  disabled={loading || !code.trim()}
                >
                  {loading ? (
                    <><span className="analyzer__spinner"></span>Scanning...</>
                  ) : (
                    <>
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                      </svg>
                      Analyze
                    </>
                  )}
                </button>
                <button
                  className="btn-pill btn-optimize analyzer__run-btn"
                  onClick={handleOptimize}
                  disabled={optimizing || !code.trim()}
                >
                  {optimizing ? (
                    <><span className="analyzer__spinner analyzer__spinner--opt"></span>Optimizing...</>
                  ) : (
                    <>
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
                      </svg>
                      Optimize
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="analyzer__error">
              <strong>Error:</strong> {error}
              <p style={{ marginTop: '0.5rem', fontSize: '0.8rem', opacity: 0.6 }}>
                Make sure the API server is running: <code>python api.py</code>
              </p>
            </div>
          )}

          {/* Results Panel */}
          {(results || optimizeResults) && (
            <div className="analyzer__results">
              {/* Summary Cards */}
              {results && (
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
              )}

              {optimizeResults && (
                <div className="analyzer__optimize-banner">
                  <div className="analyzer__optimize-banner-text">
                    <span style={{ fontSize: '1.25rem' }}>⚡</span>
                    <span><strong>{optimizeResults.total_optimizations}</strong> optimization{optimizeResults.total_optimizations !== 1 ? 's' : ''} found</span>
                  </div>
                  {optimizeResults.changed && (
                    <button className="btn-pill btn-emerald" onClick={applyOptimizedCode}>
                      ✅ Apply Optimized Code
                    </button>
                  )}
                </div>
              )}

              {/* Tabs */}
              <div className="analyzer__tabs">
                {results && (
                  <>
                    <button
                      className={`analyzer__tab ${activeTab === 'issues' ? 'analyzer__tab--active' : ''}`}
                      onClick={() => setActiveTab('issues')}
                    >
                      🔍 Issues ({results.summary.total_issues})
                    </button>
                    <button
                      className={`analyzer__tab ${activeTab === 'metrics' ? 'analyzer__tab--active' : ''}`}
                      onClick={() => setActiveTab('metrics')}
                    >
                      📊 Metrics
                    </button>
                  </>
                )}
                {optimizeResults && (
                  <button
                    className={`analyzer__tab ${activeTab === 'optimizations' ? 'analyzer__tab--active' : ''}`}
                    onClick={() => setActiveTab('optimizations')}
                  >
                    ⚡ Optimizations ({optimizeResults.total_optimizations})
                  </button>
                )}
              </div>

              {/* Issues Tab */}
              {activeTab === 'issues' && results && (
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
              {activeTab === 'metrics' && results && (
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

              {/* Optimizations Tab */}
              {activeTab === 'optimizations' && optimizeResults && (
                <div className="analyzer__optimizations-list">
                  {optimizeResults.optimizations.length === 0 ? (
                    <div className="analyzer__no-issues">
                      <span style={{ fontSize: '2rem' }}>🎉</span>
                      <p>No optimizations needed — your code is already well-written!</p>
                    </div>
                  ) : (
                    optimizeResults.optimizations.map((opt, i) => {
                      const cfg = OPT_TYPE_CONFIG[opt.type] || OPT_TYPE_CONFIG.quality;
                      return (
                        <div key={i} className="analyzer__optimization">
                          <div className="analyzer__opt-header">
                            <span className="analyzer__opt-badge" style={{ color: cfg.color }}>
                              {cfg.icon} {cfg.label}
                            </span>
                            <span className="tech-label" style={{ color: 'rgba(235,235,235,0.3)' }}>
                              Line {opt.line}
                            </span>
                          </div>
                          <p className="analyzer__opt-reason">{opt.reason}</p>
                          <div className="analyzer__opt-diff">
                            <div className="analyzer__opt-diff-line analyzer__opt-diff-line--remove">
                              <span className="analyzer__opt-diff-marker">−</span>
                              <code>{opt.original}</code>
                            </div>
                            <div className="analyzer__opt-diff-line analyzer__opt-diff-line--add">
                              <span className="analyzer__opt-diff-marker">+</span>
                              <code>{opt.optimized}</code>
                            </div>
                          </div>
                        </div>
                      );
                    })
                  )}
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
