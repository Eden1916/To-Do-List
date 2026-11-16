# To-Do List Bot — Frontend

A responsive task management interface for the To-Do List Bot project, built with React and modern frontend technologies. The frontend provides a dashboard for viewing tasks, checking task statuses, and accessing task actions such as editing and deleting tasks.

**Project Status:** 🚧 In Development

## Overview

The To-Do List Bot frontend is designed to provide a clean and user-friendly interface for managing everyday tasks. It includes a dashboard layout with task summary cards and a My Tasks section where users can view tasks and access task management actions.

The long-term goal is to connect this interface to a Python backend that supports chat-based task management.

## Features

### Currently Implemented

- React application initialized with Vite
- Tailwind CSS styling
- shadcn/ui component integration
- Lucide React icons
- Dashboard layout
- Task summary cards for total, completed, and pending tasks
- My Tasks section
- Task cards with Edit and Delete buttons

### Planned Features

- Add new tasks through a form or chat interface
- Edit existing task details
- Delete tasks
- Update task completion status
- Responsive layouts for mobile, tablet, and desktop
- Connect to the backend API
- Display task data retrieved from the backend
- Integrate a conversational interface for interacting with the bot

*Planned features will be marked as complete as development progresses.*

## Technology Stack

- **React** — Building the user interface with reusable components
- **Vite** — Development server and build tool
- **JavaScript** — Application logic
- **Tailwind CSS** — Utility-first styling
- **shadcn/ui** — Reusable UI components
- **Lucide React** — Icons for task actions and dashboard elements

## Project Structure

```text
frontend/
├── public/
├── src/
│   ├── components/
│   │   └── ui/
│   ├── lib/
│   │   └── utils.js
│   ├── App.jsx
│   ├── Dashboard.jsx
│   ├── index.css
│   └── main.jsx
├── components.json
├── jsconfig.json
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```

*The structure may vary as the application grows.*

## Getting Started

### Prerequisites

Install the following before running the project:

- [Node.js](https://nodejs.org/)
- npm, which is included with Node.js
- Git (optional, for cloning the repository)

### Installation

**1. Clone the repository**

```bash
git clone <your-repository-url>
```

**2. Navigate to the frontend directory**

```bash
cd To-Do-List/frontend
```

Replace `To-Do-List` with your repository's local directory name if it differs.

**3. Install dependencies**

```bash
npm install
```

**4. Start the development server**

```bash
npm run dev
```

**5. Open the application**

Visit the local URL displayed in your terminal. With Vite's default configuration, this is usually:

```text
http://localhost:5173
```

## Available Scripts

Run these commands from the `frontend` directory.

| Command           | Description                               |
| ----------------- | ----------------------------------------- |
| `npm run dev`     | Starts the development server             |
| `npm run build`   | Builds the application for production     |
| `npm run preview` | Previews the production build locally     |
| `npm run lint`    | Runs ESLint, if configured in the project |

## Development Roadmap

- [x] Initialize React with Vite
- [x] Configure Tailwind CSS
- [x] Set up shadcn/ui
- [x] Add reusable UI components
- [x] Create the dashboard layout
- [x] Add task summary cards
- [x] Create task cards with Edit and Delete buttons
- [ ] Implement task creation
- [ ] Implement task editing and deletion
- [ ] Add task completion interactions
- [ ] Improve responsive design
- [ ] Build the chat interface
- [ ] Integrate the Python backend API
- [ ] Test and optimize the frontend
- [ ] Prepare for deployment

## Future Integration

The frontend is intended to communicate with a Python backend responsible for task management, CRUD operations, conversational logic, and session handling.

Once the backend integration is complete, the interface will display real task data instead of relying on static demonstration content.

## License

A license has not yet been selected for this project.

---

**Note:** This project is under active development. The README will be updated as new features are implemented.
