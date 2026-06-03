import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import fs from 'fs';
import path from 'path';

const html = fs.readFileSync(path.resolve(__dirname, '../index.html'), 'utf8');
const scriptCode = fs.readFileSync(path.resolve(__dirname, '../app.js'), 'utf8');

function waitForAsyncWork() {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

describe('Incident Platform Frontend', () => {
  beforeEach(() => {
    // Remove the real app.js script from index.html before putting HTML into jsdom.
    // We will run app.js manually only after fetch is mocked.
    const htmlWithoutAppScript = html.replace(
      /<script\b[^>]*\bsrc=["']app\.js["'][^>]*><\/script>/gi,
      ''
    );

    document.documentElement.innerHTML = htmlWithoutAppScript;

    // Extra safety: remove any script tag that still survived.
    document.querySelectorAll('script[src]').forEach((script) => script.remove());

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

    window.fetch = fetchMock;
    global.fetch = fetchMock;

    // Run app.js manually inside the jsdom window.
    // Attach internal functions to window so tests can call them.
    window.eval(`
      {
        ${scriptCode}

        window.showToast = showToast;
        window.escapeHtml = escapeHtml;

        if (refreshIntervalId) {
          clearInterval(refreshIntervalId);
        }
      }
    `);
  });

  afterEach(() => {
    vi.restoreAllMocks();

    delete window.fetch;
    delete global.fetch;

    document.documentElement.innerHTML = '';
  });

  it('initializes the UI with the correct title', () => {
    const h1 = document.querySelector('h1');
    expect(h1.textContent).toBe('Create and manage incidents quickly.');
  });

  it('loads incidents from the backend', async () => {
    await waitForAsyncWork();

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