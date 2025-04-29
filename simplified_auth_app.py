import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime
import yaml
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="GirlTREK Data Entry Portal",
    page_icon="📊",
    layout="wide"
)

# Define constants
DATA_DIR = "data"
SUBMISSIONS_FILE = os.path.join(DATA_DIR, "submissions.csv")
CONFIG_FILE = ".streamlit/config.yaml"

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Create .streamlit directory if it doesn't exist
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

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
</style>
""", unsafe_allow_html=True)

# Simple user authentication (basic implementation)
def init_auth():
    # Check if config exists
    if not os.path.exists(CONFIG_FILE):
        # Create default admin user
        default_config = {
            'users': {
                'admin': {
                    'password': 'admin',  # In a real app, this would be hashed
                    'name': 'GirlTREK Admin',
                    'email': 'admin@girltrek.org'
                }
            }
        }
        # Save default config
        with open(CONFIG_FILE, 'w') as f:
            yaml.dump(default_config, f)
        
    # Load config
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f)

# Simple function to check login
def check_login(username, password, config):
    if username in config['users']:
        if password == config['users'][username]['password']:  # In real app, use password hashing
            return True, config['users'][username]
    return False, None

# Load or initialize submissions dataframe
def load_submissions():
    if os.path.exists(SUBMISSIONS_FILE):
        return pd.read_csv(SUBMISSIONS_FILE)
    else:
        return pd.DataFrame(columns=[
            'submission_id', 'timestamp', 'first_name', 'last_name', 'email',
            'dashboard_section', 'metric_name', 'metric_value', 'notes'
        ])

# Save submissions to CSV
def save_submission(submission_data):
    submissions_df = load_submissions()
    new_submission = pd.DataFrame([submission_data])
    updated_df = pd.concat([submissions_df, new_submission], ignore_index=True)
    updated_df.to_csv(SUBMISSIONS_FILE, index=False)
    return True

# Get metrics based on selected section
def get_metrics_for_section(section):
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

# Format value based on metric type
def format_value(value, metric_name):
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

# Main application
st.markdown('<h1 class="main-header">GirlTREK Dashboard Data Entry Portal</h1>', unsafe_allow_html=True)

# Initialize authentication
auth_config = init_auth()

# Session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_info = None

# Login form if not authenticated
if not st.session_state.authenticated:
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            authenticated, user_info = check_login(username, password, auth_config)
            if authenticated:
                st.session_state.authenticated = True
                st.session_state.user_info = user_info
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    # Show default credentials for demo
    st.info("Default login: username: admin, password: admin")

# Main app content when authenticated
else:
    # Sidebar with logout button
    st.sidebar.title(f"Welcome, {st.session_state.user_info['name']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_info = None
        st.experimental_rerun()
    
    # Navigation
    page = st.sidebar.radio("Go to", ["Data Entry", "View Submissions"])
    
    if page == "Data Entry":
        st.markdown('<h2 class="sub-header">Data Entry Form</h2>', unsafe_allow_html=True)
        
        # User info display
        st.markdown(
            f"""
            <div class="card">
            <p><strong>Logged in as:</strong> {st.session_state.user_info['name']}</p>
            <p><strong>Email:</strong> {st.session_state.user_info['email']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Data entry form
        with st.form("data_entry_form"):
            st.subheader("Metric Information")
            
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
                'first_name': st.session_state.user_info['name'].split()[0],
                'last_name': ' '.join(st.session_state.user_info['name'].split()[1:]) if len(st.session_state.user_info['name'].split()) > 1 else "",
                'email': st.session_state.user_info['email'],
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
            st.info("No submissions yet. Use the Data Entry tab to add data.")

# Footer
st.markdown("""
---
<p style="text-align: center;">GirlTREK Dashboard Data Entry System | © 2025 GirlTREK</p>
""", unsafe_allow_html=True)
