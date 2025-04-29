import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import uuid
import base64
from datetime import datetime
import requests
from github import Github
import yaml
import streamlit_authenticator as stauth
import re

# Set page config
st.set_page_config(
    page_title="GirlTREK Data Entry Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define constants
DATA_DIR = "data"
CONFIG_FILE = "config.yaml"
GITHUB_REPO = "girltrek-dashboard-data"

# GitHub API configurations - to be stored in secrets.toml in production
# These would be set in Streamlit's secrets manager for security
if 'github_token' not in st.secrets:
    st.secrets['github_token'] = os.getenv('GITHUB_TOKEN', '')

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# CSS for styling
st.markdown("""
<style>
    .main-header {
        color: #0088FF;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #FF5722;
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #f8f9fa;
        border-left: 4px solid #0088FF;
    }
    .success-message {
        padding: 15px;
        border-radius: 5px;
        background-color: #E8F5E9;
        color: #2E7D32;
        margin-bottom: 15px;
        border-left: 4px solid #4CAF50;
    }
    .warning-message {
        padding: 15px;
        border-radius: 5px;
        background-color: #FFF3E0;
        color: #E65100;
        margin-bottom: 15px;
        border-left: 4px solid #FF9800;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #757575;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize authentication
def load_auth_config():
    """Load authentication configuration or create default if not exists"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
    else:
        # Create a default configuration with a single admin user
        # In production, this should be done through a secure admin interface
        config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@girltrek.org',
                        'name': 'GirlTREK Admin',
                        'password': stauth.Hasher(['admin']).generate()[0]  # Default password is 'admin'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': str(uuid.uuid4()),  # Random key for extra security
                'name': 'girltrek_dash_auth'
            },
            'preauthorized': {
                'emails': ['admin@girltrek.org']
            }
        }
        # Save the default configuration
        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(config, file)
    
    return config

# GitHub data operations
def init_github():
    """Initialize GitHub connection"""
    if st.secrets['github_token']:
        try:
            return Github(st.secrets['github_token'])
        except Exception as e:
            st.error(f"Error connecting to GitHub: {e}")
            return None
    else:
        st.warning("GitHub token not found. Please set in secrets or environment.")
        return None

def get_github_repo(g, repo_name):
    """Get GitHub repository or create if not exists"""
    if not g:
        return None
    
    try:
        user = g.get_user()
        try:
            repo = user.get_repo(repo_name)
            return repo
        except:
            # Create new repository if it doesn't exist
            repo = user.create_repo(repo_name, private=True)
            # Create basic structure
            repo.create_file("README.md", 
                            "Initial commit", 
                            "# GirlTREK Dashboard Data\n\nThis repository contains data for the GirlTREK organizational dashboard.")
            repo.create_file("data/submissions.csv", 
                            "Create data directory", 
                            "timestamp,user_id,first_name,last_name,email,dashboard_section,metric_name,metric_value,notes")
            return repo
    except Exception as e:
        st.error(f"GitHub repository error: {e}")
        return None

def save_data_to_github(repo, file_path, data, commit_message):
    """Save data to GitHub repo, create or update file"""
    if not repo:
        return False
    
    try:
        # Check if file exists
        try:
            contents = repo.get_contents(file_path)
            # Update existing file
            repo.update_file(contents.path, commit_message, data, contents.sha)
        except:
            # Create new file
            repo.create_file(file_path, commit_message, data)
        return True
    except Exception as e:
        st.error(f"Error saving to GitHub: {e}")
        return False

def fetch_data_from_github(repo, file_path):
    """Fetch data from GitHub repo"""
    if not repo:
        return None
    
    try:
        contents = repo.get_contents(file_path)
        return contents.decoded_content.decode('utf-8')
    except Exception as e:
        # File might not exist yet
        return None

# Data operations 
def load_submissions():
    """Load submissions from GitHub or local CSV"""
    # Initialize GitHub
    g = init_github()
    if g:
        repo = get_github_repo(g, GITHUB_REPO)
        data = fetch_data_from_github(repo, "data/submissions.csv")
        if data:
            return pd.read_csv(pd.StringIO(data))
    
    # Fallback to local file if GitHub fails
    if os.path.exists(os.path.join(DATA_DIR, "submissions.csv")):
        return pd.read_csv(os.path.join(DATA_DIR, "submissions.csv"))
    
    # Return empty DataFrame if no data found
    return pd.DataFrame(columns=[
        'submission_id', 'timestamp', 'user_id', 'first_name', 'last_name', 'email',
        'dashboard_section', 'metric_name', 'metric_value', 'notes'
    ])

def save_submission(submission_data):
    """Save submission to both GitHub and local storage"""
    # Load existing submissions
    submissions_df = load_submissions()
    
    # Create new submission dataframe
    new_submission = pd.DataFrame([submission_data])
    
    # Concat with existing data
    updated_df = pd.concat([submissions_df, new_submission], ignore_index=True)
    
    # Save locally first as backup
    updated_df.to_csv(os.path.join(DATA_DIR, "submissions.csv"), index=False)
    
    # Save to GitHub if configured
    g = init_github()
    if g:
        repo = get_github_repo(g, GITHUB_REPO)
        commit_message = f"Update data from {submission_data['first_name']} {submission_data['last_name']}"
        return save_data_to_github(repo, "data/submissions.csv", updated_df.to_csv(index=False), commit_message)
    
    return True

def get_metrics_for_section(section):
    """Define metrics based on selected dashboard section"""
    if section == "Executive Summary":
        return [
            "Total Membership",
            "Total New Members",
            "Total Contributions",
            "New Members by Age Group",
            "Total Trekkers by Region"
        ]
    elif section == "Recruitment":
        return [
            "Total New Members",
            "New Members Age 18-30",
            "Recruitment Partnerships",
            "Recruitment Events"
        ]
    elif section == "Engagement":
        return [
            "Total New Crews",
            "Members Walking Daily",
            "Active Volunteers",
            "Documented Crew Leaders",
            "Active Crew Leaders",
            "Self-Care School Registrants"
        ]
    elif section == "Development":
        return [
            "Total Contributions",
            "Total Grants",
            "Corporate Sponsorships",
            "Store Sales",
            "Other Revenue"
        ]
    elif section == "Marketing":
        return [
            "Total Subscribers",
            "Active Subscribers",
            "Facebook Followers",
            "Instagram Followers",
            "LinkedIn Followers",
            "Social Media Impressions"
        ]
    elif section == "Operations":
        return [
            "Budget Performance",
            "ASANA Adoption",
            "Audit Compliance",
            "Cybersecurity Compliance"
        ]
    elif section == "Member Care":
        return [
            "Member Satisfaction Rating",
            "Resolution/Responsiveness Rate",
            "New Member Stories"
        ]
    elif section == "Advocacy":
        return [
            "Advocacy Briefs Published",
            "Advocacy Partnerships"
        ]
    elif section == "Impact":
        return [
            "Health Knowledge Change",
            "Mental Well-being Change",
            "Connection Improvement",
            "Weight Loss Percentage",
            "Chronic Condition Management"
        ]
    return []

def format_value(value, metric_name):
    """Format values based on metric type"""
    if metric_name in ["Total Contributions", "Total Grants", "Corporate Sponsorships", "Store Sales", "Other Revenue"]:
        try:
            return f"${float(value):,.2f}"
        except:
            return value
    elif metric_name in ["Member Satisfaction Rating", "ASANA Adoption"]:
        if not str(value).endswith('%'):
            return f"{value}%"
        return value
    else:
        try:
            return f"{int(float(value)):,}"
        except:
            return value

def is_valid_email(email):
    """Validate email format"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Main application
def main():
    st.markdown('<h1 class="main-header">GirlTREK Dashboard Data Entry Portal</h1>', unsafe_allow_html=True)
    
    # Initialize authentication
    auth_config = load_auth_config()
    authenticator = stauth.Authenticate(
        auth_config['credentials'],
        auth_config['cookie']['name'],
        auth_config['cookie']['key'],
        auth_config['cookie']['expiry_days'],
        auth_config['preauthorized']['emails']
    )
    
    # Authentication
    name, authentication_status, username = authenticator.login("Login", "main")
    
    if authentication_status == False:
        st.error("Username/password is incorrect")
        
    elif authentication_status == None:
        st.warning("Please enter your username and password")
        
    elif authentication_status:
        # User is authenticated
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Welcome {name}")
        
        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Go to", ["Data Entry", "View Submissions", "GitHub Status", "Settings"])
        
        if page == "Data Entry":
            st.markdown('<h2 class="sub-header">Data Entry Form</h2>', unsafe_allow_html=True)
            
            # Get user info from auth
            user_info = auth_config['credentials']['usernames'][username]
            first_name = user_info['name'].split()[0] if ' ' in user_info['name'] else user_info['name']
            last_name = user_info['name'].split()[1] if ' ' in user_info['name'] else ""
            email = user_info['email']
            
            # Display user info
            st.markdown(
                f"""
                <div class="card">
                <p><strong>Logged in as:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Create data entry form
            with st.form("data_entry_form"):
                # Dashboard section selection
                dashboard_sections = [
                    "Executive Summary",
                    "Recruitment",
                    "Engagement",
                    "Development",
                    "Marketing",
                    "Operations",
                    "Member Care",
                    "Advocacy",
                    "Impact"
                ]
                
                dashboard_section = st.selectbox(
                    "Select Dashboard Section *",
                    options=dashboard_sections
                )
                
                # Metric selection based on dashboard section
                metric_options = get_metrics_for_section(dashboard_section)
                metric_name = st.selectbox(
                    "Select Metric *",
                    options=metric_options
                )
                
                # Value input based on metric type
                if metric_name in ["Member Satisfaction Rating", "ASANA Adoption"]:
                    metric_value = st.slider("Percentage Value", 0, 100, 50)
                    metric_value = f"{metric_value}%"
                elif metric_name in ["Total Contributions", "Total Grants", "Corporate Sponsorships", "Store Sales", "Other Revenue"]:
                    metric_value = st.number_input("Dollar Value", min_value=0.0, format="%.2f")
                    metric_value = f"${metric_value:,.2f}"
                elif metric_name in ["New Member Stories"]:
                    metric_value = st.text_area("Story Content", height=150)
                else:
                    metric_value = st.number_input("Numeric Value", min_value=0, step=1)
                    metric_value = f"{int(metric_value):,}"
                
                # Notes
                notes = st.text_area("Additional Notes/Context", height=100)
                
                submitted = st.form_submit_button("Submit Data")
            
            if submitted:
                # Prepare submission data
                submission_id = str(uuid.uuid4())
                submission_data = {
                    'submission_id': submission_id,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'user_id': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'dashboard_section': dashboard_section,
                    'metric_name': metric_name,
                    'metric_value': metric_value,
                    'notes': notes
                }
                
                # Save submission
                if save_submission(submission_data):
                    st.markdown(
                        f"""
                        <div class="success-message">
                        <h4>Data Submitted Successfully!</h4>
                        <p><strong>ID:</strong> {submission_id}</p>
                        <p><strong>Dashboard Section:</strong> {dashboard_section}</p>
                        <p><strong>Metric:</strong> {metric_name}</p>
                        <p><strong>Value:</strong> {metric_value}</p>
                        <p><strong>Timestamp:</strong> {submission_data['timestamp']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.error("Error saving submission. Please try again.")
            
        elif page == "View Submissions":
            st.markdown('<h2 class="sub-header">Recent Submissions</h2>', unsafe_allow_html=True)
            
            # Load submissions
            submissions_df = load_submissions()
            
            if len(submissions_df) > 0:
                # Filter options
                st.subheader("Filter Submissions")
                
                # Add filters
                col1, col2 = st.columns(2)
                
                with col1:
                    filter_section = st.selectbox(
                        "Filter by Dashboard Section",
                        options=["All Sections"] + list(submissions_df['dashboard_section'].unique())
                    )
                
                with col2:
                    filter_metrics = st.selectbox(
                        "Filter by Metric",
                        options=["All Metrics"] + list(submissions_df['metric_name'].unique())
                    )
                
                # Apply filters
                filtered_df = submissions_df.copy()
                
                if filter_section != "All Sections":
                    filtered_df = filtered_df[filtered_df['dashboard_section'] == filter_section]
                    
                if filter_metrics != "All Metrics":
                    filtered_df = filtered_df[filtered_df['metric_name'] == filter_metrics]
                
                # Sort by newest first
                filtered_df = filtered_df.sort_values(by='timestamp', ascending=False)
                
                # Display as table
                st.subheader(f"Showing {len(filtered_df)} submissions")
                st.dataframe(
                    filtered_df[[
                        'timestamp', 'first_name', 'last_name', 
                        'dashboard_section', 'metric_name', 'metric_value', 'notes'
                    ]],
                    use_container_width=True
                )
                
                # Export functionality
                csv = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download as CSV",
                    data=csv,
                    file_name=f"girltrek_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No submissions yet. Use the Data Entry page to add data.")
        
        elif page == "GitHub Status":
            st.markdown('<h2 class="sub-header">GitHub Integration Status</h2>', unsafe_allow_html=True)
            
            # Check GitHub connection
            g = init_github()
            if g:
                try:
                    user = g.get_user()
                    repo = get_github_repo(g, GITHUB_REPO)
                    
                    if repo:
                        st.success(f"Connected to GitHub as: {user.login}")
                        st.success(f"Repository: {repo.full_name}")
                        
                        # Check if data file exists
                        try:
                            contents = repo.get_contents("data/submissions.csv")
                            last_commit = repo.get_commits()[0]
                            
                            st.markdown(
                                f"""
                                <div class="card">
                                <h4>Repository Details</h4>
                                <p><strong>Last Updated:</strong> {last_commit.commit.author.date}</p>
                                <p><strong>Last Commit Message:</strong> {last_commit.commit.message}</p>
                                <p><strong>Data File Size:</strong> {contents.size} bytes</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Sync option
                            if st.button("Force Sync with GitHub"):
                                st.info("Syncing data...")
                                # Fetch latest data
                                data = fetch_data_from_github(repo, "data/submissions.csv")
                                if data:
                                    # Save locally
                                    with open(os.path.join(DATA_DIR, "submissions.csv"), 'w') as f:
                                        f.write(data)
                                    st.success("Data synchronized successfully!")
                                else:
                                    st.error("No data found on GitHub.")
                        except:
                            st.warning("Data file not found in repository.")
                    else:
                        st.error("Failed to access GitHub repository.")
                except Exception as e:
                    st.error(f"GitHub error: {e}")
            else:
                st.error("GitHub integration not configured.")
                
                # Show configuration help
                st.markdown(
                    """
                    <div class="warning-message">
                    <h4>GitHub Setup Instructions</h4>
                    <p>To enable GitHub integration, you need to set up a Personal Access Token:</p>
                    <ol>
                        <li>Go to GitHub Settings > Developer settings > Personal access tokens</li>
                        <li>Generate a new token with repo permissions</li>
                        <li>Add the token to your Streamlit secrets.toml file as:</li>
                    </ol>
                    <code>github_token = "your-token-here"</code>
                    <p>This will allow the app to save and retrieve data from GitHub automatically.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        elif page == "Settings":
            st.markdown('<h2 class="sub-header">User Settings</h2>', unsafe_allow_html=True)
            
            # Change password form
            st.subheader("Change Password")
            
            if authenticator.reset_password(username, "Reset Password"):
                st.success("Password modified successfully")
                with open(CONFIG_FILE, 'w') as file:
                    yaml.dump(auth_config, file)
            
            # User management (admin only)
            if username == "admin":
                st.markdown('<h3 class="sub-header">User Management (Admin)</h3>', unsafe_allow_html=True)
                
                # Register users form
                with st.expander("Register New User"):
                    reg_username = st.text_input("Username (no spaces)", key="reg_username")
                    reg_name = st.text_input("Full Name", key="reg_name")
                    reg_email = st.text_input("Email", key="reg_email")
                    reg_password = st.text_input("Password", type="password", key="reg_password")
                    
                    if st.button("Register User"):
                        if not reg_username or not reg_name or not reg_email or not reg_password:
                            st.error("All fields are required")
                        elif not is_valid_email(reg_email):
                            st.error("Please enter a valid email address")
                        elif " " in reg_username:
                            st.error("Username cannot contain spaces")
                        elif reg_username in auth_config['credentials']['usernames']:
                            st.error("Username already exists")
                        else:
                            # Add new user
                            auth_config['credentials']['usernames'][reg_username] = {
                                'name': reg_name,
                                'email': reg_email,
                                'password': stauth.Hasher([reg_password]).generate()[0]
                            }
                            
                            # Add to preauthorized emails
                            if reg_email not in auth_config['preauthorized']['emails']:
                                auth_config['preauthorized']['emails'].append(reg_email)
                            
                            # Save config
                            with open(CONFIG_FILE, 'w') as file:
                                yaml.dump(auth_config, file)
                            
                            st.success(f"User {reg_username} registered successfully")
                
                # View/delete users
                with st.expander("Manage Existing Users"):
                    users_df = pd.DataFrame([
                        {
                            'username': username,
                            'name': user_data['name'],
                            'email': user_data['email']
                        } for username, user_data in auth_config['credentials']['usernames'].items()
                    ])
                    
                    st.dataframe(users_df, use_container_width=True)
                    
                    # Delete user option
                    del_username = st.selectbox(
                        "Select User to Delete",
                        options=[""] + [u for u in auth_config['credentials']['usernames'].keys() if u != "admin"]
                    )
                    
                    if del_username and st.button(f"Delete User: {del_username}"):
                        if del_username == "admin":
                            st.error("Cannot delete admin user")
                        else:
                            # Remove from usernames
                            email = auth_config['credentials']['usernames'][del_username]['email']
                            del auth_config['credentials']['usernames'][del_username]
                            
                            # Remove from preauthorized emails if no other user has it
                            if not any(user_data['email'] == email for user_data in auth_config['credentials']['usernames'].values()):
                                if email in auth_config['preauthorized']['emails']:
                                    auth_config['preauthorized']['emails'].remove(email)
                            
                            # Save config
                            with open(CONFIG_FILE, 'w') as file:
                                yaml.dump(auth_config, file)
                            
                            st.success(f"User {del_username} deleted successfully")
    
    # Footer
    st.markdown(
        """
        <div class="footer">
        <p>GirlTREK Dashboard Data Entry System | © 2025 GirlTREK</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
