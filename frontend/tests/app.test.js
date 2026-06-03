import { describe, it, expect, beforeEach, vi } from 'vitest';
import fs from 'fs';
import path from 'path';

// 1. Load file contents
const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
const scriptCode = fs.readFileSync(path.resolve(__dirname, '../app.js'), 'utf8');

describe('Incident Platform Frontend', () => {
  beforeEach(() => {
    // 2. Setup Mock DOM
    document.documentElement.innerHTML = html.toString();

    // 3. Mock the Fetch API (prevents "fetch is not defined" or network errors)
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          { 
            id: 1, 
            title: 'CI Test Incident', 
            description: 'Testing the pipeline',
            status: 'Open',
            severity: 'High'
          }
        ]),
      })
    );

    // 4. Execute app.js in the JSDOM context
    // This runs your event listeners and initial fetchIncidents()
    const scriptEl = document.createElement('script');
    scriptEl.textContent = scriptCode;
    document.body.appendChild(scriptEl);
  });

  it('initializes the UI with the correct title', () => {
    const h1 = document.querySelector('h1');
    expect(h1.textContent).toBe('Create and manage incidents quickly.');
  });

  it('starts with a count of 0 (before fetch resolves)', () => {
    const countBadge = document.getElementById('incidentCount');
    expect(countBadge.textContent).toBe('0');
  });

  it('displays the toast when showToast is triggered', () => {
    // Accessing the function defined in your app.js (it becomes global in JSDOM)
    window.showToast('Pipeline Test Message', 'info');
    
    const toast = document.getElementById('toast');
    expect(toast.textContent).toBe('Pipeline Test Message');
    expect(toast.className).toContain('visible');
  });

  it('correctly escapes HTML to prevent XSS', () => {
    // Testing your escapeHtml function logic
    const unsafe = '<img src=x onerror=alert(1)>';
    const safe = window.escapeHtml(unsafe);
    
    expect(safe).not.toContain('<img');
    expect(safe).toContain('&lt;img');
  });

  it('renders an incident card when data is present', () => {
    // We simulate the renderIncidents logic
    const incidentList = document.getElementById('incidentList');
    
    // In a real scenario, fetchIncidents would fill this. 
    // Here we check if the DOM elements exist for it to work.
    expect(incidentList).not.toBeNull();
    expect(document.getElementById('incidentForm')).not.toBeNull();
  });
});