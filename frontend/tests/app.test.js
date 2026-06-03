import { describe, it, expect, beforeEach, vi } from 'vitest';
import fs from 'fs';
import path from 'path';

// 1. Setup global fetch mock BEFORE anything else
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([{ id: 1, title: 'Test', description: 'Test desc' }]),
  })
);

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
const scriptCode = fs.readFileSync(path.resolve(__dirname, '../app.js'), 'utf8');

describe('Incident Platform Frontend', () => {
  beforeEach(() => {
    // 2. Reset DOM
    document.documentElement.innerHTML = html.toString();

    // 3. To fix the "API_BASE already declared" error, 
    // we wrap your script in a block {} so the const stays local to this execution.
    const wrappedScript = `{ ${scriptCode} }`;
    
    const scriptEl = document.createElement('script');
    scriptEl.textContent = wrappedScript;
    document.body.appendChild(scriptEl);
  });

  it('initializes the UI with the correct title', () => {
    const h1 = document.querySelector('h1');
    expect(h1.textContent).toBe('Create and manage incidents quickly.');
  });

  it('starts with a count of 0', () => {
    const countBadge = document.getElementById('incidentCount');
    expect(countBadge.textContent).toBe('0');
  });

  it('displays the toast when showToast is triggered', () => {
    // We check the DOM directly after calling the function
    window.showToast('Pipeline Test', 'info');
    const toast = document.getElementById('toast');
    expect(toast.textContent).toBe('Pipeline Test');
    expect(toast.className).toContain('visible');
  });

  it('correctly escapes HTML to prevent XSS', () => {
    const safe = window.escapeHtml('<img src=x>');
    expect(safe).toContain('&lt;img');
  });

  it('renders the form correctly', () => {
    const form = document.getElementById('incidentForm');
    expect(form).not.toBeNull();
  });
});