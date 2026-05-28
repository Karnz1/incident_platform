# Frontend for Incident Platform

This folder contains a lightweight static frontend for the incident platform.

## Features

- Create incident reports with title and description
- Delete incidents from the list
- Modern responsive layout with a glassmorphism-inspired UI

## Usage

1. Start the backend API on `http://localhost:8000`.
2. Open `frontend/index.html` in a browser, or serve the folder with a static server.
3. Use the form to create incidents and delete them from the list.

## Notes

- The frontend sends requests to `http://localhost:8000/incidents`.
- Because the backend currently has placeholder list endpoints, the app keeps the created incidents in the browser session.
