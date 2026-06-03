import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fs from 'fs';
import path from 'path';

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
const scriptCode = fs.readFileSync(path.resolve(__dirname, '../app.js'), 'utf8');

function flushPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe('Incident Platform Frontend', () => {
  beforeEach(() => {
    vi.useFakeTimers();

    // Remove the real <script src="app.js"></script> from the HTML.
    // The test injects app.js manually after mocks are ready.
    document.documentElement.innerHTML = html.replace(
      /<script\s+src="app\.js"><\/script>/,
      ''
    );

    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              title: 'Test',
              description: 'Test desc',
              status: 'Open',
              severity: 'Low',
            },
          ]),
      })
    );

    // jsdom script context needs fetch on window.
    window.fetch = fetchMock;
    global.fetch = fetchMock;

    const wrappedScript = `
      {
        ${scriptCode}

        window.showToast = showToast;
        window.escapeHtml = escapeHtml;

        if (refreshIntervalId) {
          clearInterval(refreshIntervalId);
        }
      }
    `;

    const scriptEl = document.createElement('script');
    scriptEl.textContent = wrappedScript;
    document.body.appendChild(scriptEl);
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.restoreAllMocks();
    delete window.fetch;
    delete global.fetch;
  });

  it('initializes the UI with the correct title', () => {
    const h1 = document.querySelector('h1');
    expect(h1.textContent).toBe('Create and manage incidents quickly.');
  });

  it('loads incidents from the backend', async () => {
    await flushPromises();

    const countBadge = document.getElementById('incidentCount');
    expect(countBadge.textContent).toBe('1');
  });

  it('displays the toast when showToast is triggered', () => {
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