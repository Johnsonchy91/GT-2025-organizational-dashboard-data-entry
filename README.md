# GirlTREK Dashboard Data Entry Portal

A secure, user-friendly web application built with Streamlit that allows authorized GirlTREK team members to submit data for the organizational dashboard with GitHub integration for version control and data persistence.

## Features

- **Secure User Authentication**: Multi-user system with login/password protection
- **GitHub Integration**: Automatic syncing of submitted data to a GitHub repository
- **Data Entry Form**: Specialized inputs based on metric type (percentages, dollar values, numbers)
- **Submission History**: View and filter previous data submissions
- **Admin Controls**: User management interface for administrators
- **Data Export**: Download submissions as CSV files

## Setup Instructions

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/your-username/girltrek-dashboard-entry.git
cd girltrek-dashboard-entry

# Install dependencies
pip install -r requirements.txt
```

### 2. GitHub Configuration

1. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with `repo` permissions
   - Copy the token

2. Configure Streamlit secrets:
   - Create a `.streamlit` directory in the project root (if it doesn't exist)
   - Create a `secrets.toml` file inside the `.streamlit` directory
   - Add your GitHub token:
     ```toml
     github_token = "your-github-personal-access-token-here"
     ```

### 3. Running the App

```bash
streamlit run app.py
```

The first time you run the app, it will:
- Create a default admin user (username: `admin`, password: `admin`)
- Attempt to connect to GitHub (if configured) or use local storage
- Set up necessary data structures

**Important**: Change the default admin password immediately after first login.

## Usage Guide

### Admin Functions

As an admin user, you can:
1. Register new users
2. View and delete existing users
3. Manage data submissions
4. Force sync with GitHub

### Data Entry

1. Log in with your credentials
2. Select a dashboard section
3. Choose a specific metric
4. Enter the new value
5. Add any notes for context
6. Submit the data

### Data Retrieval

1. Navigate to "View Submissions"
2. Filter by section or metric type
3. Sort by timestamp
4. Export filtered data as CSV

## GitHub Workflow

The app maintains data in two locations:
1. **Local Storage**: For quick access and backup
2. **GitHub Repository**: For version control and team access

Data is automatically synced between these locations whenever submissions are made or when a manual sync is triggered.

## Deployment

For production deployment:

1. Update `.streamlit/secrets.toml`:
   ```toml
   [app]
   environment = "production"
   ```

2. Deploy using Streamlit Community Cloud:
   - Connect your GitHub repository to Streamlit Community Cloud
   - Configure the app with appropriate secrets
   - Deploy the app through the Streamlit interface

## Requirements

- Python 3.7+
- Streamlit 1.22+
- PyGithub
- pandas
- streamlit-authenticator
- pyyaml

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
