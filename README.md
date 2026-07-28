# Carmel Bible Church Project

This is a full-stack application built using:
- **Backend**: Django REST Framework (Python 3.x)
- **Frontend**: React + Vite + TypeScript (Node.js & npm)

---

## Quick Start (Any System)

We have provided automated scripts to install dependencies, run database migrations, seed initial data, and launch both backend and frontend servers in parallel.

### For Windows Users
Double-click the **`run_project.bat`** file in the root folder, or run in command prompt:
```cmd
run_project.bat
```

### For macOS / Linux Users
Run the **`run_project.sh`** script in your terminal (make sure to give it execution permissions first):
```bash
chmod +x run_project.sh
./run_project.sh
```

---

## Seeded Login Credentials

Run `seed.py` (handled automatically by the scripts above) to populate the database with these default users:

### Admin Accounts
- **Username**: `Shyam`
  - **Email**: `pastor@carmelbiblechurch.org`
  - **Password**: `CBC Church`
- **Username**: `DEVA`
  - **Email**: `devakadari277@gmail.com`
  - **Password**: `DEVA`
- **Username**: `Uday`
  - **Email**: `brother@carmelbiblechurch.org`
  - **Password**: `CBC Church`

### Member Account
- **Username**: `john_member`
  - **Email**: `john@example.com`
  - **Password**: `MemberPassword123`

---

## Troubleshooting ngrok Connection Errors (`ERR_NGROK_8012`)

If you see a browser error from ngrok like this:
> **ERR_NGROK_8012**: Traffic successfully made it to the ngrok agent, but the agent failed to establish a connection to the upstream web service at http://localhost:5173

This means **ngrok is running, but the Vite frontend development server is NOT running** on port 5173.

### Solution
1. Ensure the Vite dev server is running. You can run the automation script (`run_project.bat` or `run_project.sh`) which will start it automatically.
2. If running manually, open a terminal, navigate to the `frontend` directory, and start Vite:
   ```bash
   cd frontend
   npm run dev
   ```
3. Once the terminal shows `Local: http://localhost:5173/`, refresh your ngrok URL in the browser, and the application will load correctly.
