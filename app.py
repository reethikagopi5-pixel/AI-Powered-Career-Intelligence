import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Resume Management System",
    page_icon="📄",
    layout="wide"
)

FASTAPI_URL = "http://127.0.0.1:8000"

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

if not st.session_state['logged_in']:
    st.sidebar.title("🔐 Authentication Portal")
    st.sidebar.info("Please use the verification panel options to log in or create an account.")
    
    st.title("🎯 AI-Powered Career Intelligence Platform")
    st.markdown("---")
    
    auth_action = st.radio("Choose Action:", ["🔑 Sign In to Existing Account", "🆕 Create New Account"], horizontal=True)
    
    if auth_action == "🆕 Create New Account":
        st.subheader("Registration Panel")
        with st.form("registration_keyboard_form", clear_on_submit=False):
            reg_email = st.text_input("Email Address *", autocomplete="new-password").strip()
            reg_name = st.text_input("Full Name", autocomplete="off")
            reg_pass = st.text_input("Password *", type="password", autocomplete="new-password")
            submit_reg = st.form_submit_button("Complete Registration")
        
        if submit_reg:
            if not reg_email or not reg_pass:
                st.warning("Please provide both an email and password.")
            else:
                payload = {"email": reg_email, "full_name": reg_name, "password": reg_pass}
                try:
                    response = requests.post(f"{FASTAPI_URL}/api/auth/signup", json=payload)
                    if response.status_code == 200:
                        st.success(f"🎉 Account registered successfully for {reg_email}! Select 'Sign In' above to access your profile.")
                    else:
                        try:
                            error_detail = response.json().get("detail", "Registration rejected.")
                        except:
                            error_detail = f"Server returned response status {response.status_code}"
                        st.error(f"❌ {error_detail}")
                except Exception as e:
                    st.error(f"❌ Connection Error! Verify that main.py is running. Details: {str(e)}")
                    
    elif auth_action == "🔑 Sign In to Existing Account":
        st.subheader("Authorization Entry Form")
        with st.form("login_keyboard_form", clear_on_submit=False):
            login_email = st.text_input("Email Address", autocomplete="new-password").strip()
            login_pass = st.text_input("Password", type="password", autocomplete="new-password")
            submit_login = st.form_submit_button("Verify & Sign In")
        
        if submit_login:
            if not login_email or not login_pass:
                st.error("❌ Please fill out both the email and password fields.")
            else:
                payload = {"email": login_email, "password": login_pass}
                try:
                    response = requests.post(f"{FASTAPI_URL}/api/auth/login", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = login_email
                        st.session_state['is_admin'] = data.get("is_admin", False) or (login_email == "admin@ats.com")
                        st.success("🎯 Authorization granted! Loading dashboard...")
                        st.rerun()
                    else:
                        try:
                            error_detail = response.json().get("detail", "Invalid email or password.")
                        except:
                            error_detail = "Authentication rejected by security boundaries."
                        st.error(f"❌ {error_detail}")
                except Exception as e:
                    st.error(f"❌ Connection Error! Verify that your backend server is running on port 8000. Details: {str(e)}")

else:
    st.sidebar.title("ATS Control Panel")
    role_label = "Administrator" if st.session_state['is_admin'] else "Candidate"
    st.sidebar.write(f"👤 Account: **{st.session_state['username']}** ({role_label})")
    
    if st.session_state['is_admin']:
        available_pages = ["Dashboard Overview", "Candidate Accounts", "Analyze Resume"]
    else:
        available_pages = ["Dashboard Overview", "Analyze Resume"]
        
    page = st.sidebar.radio("Go to:", available_pages)
    
    if st.sidebar.button("Log Out 🔓"):
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.session_state['is_admin'] = False
        st.rerun()

    if page == "Dashboard Overview":
        st.title("📊 ATS System Performance Overview")
        st.markdown("---")
        
        try:
            stats_resp = requests.get(f"{FASTAPI_URL}/api/system/stats").json()
            total_registered = stats_resp.get("total_registered", 0)
            resumes_processed = stats_resp.get("resumes_processed", 0)
            avg_score = stats_resp.get("average_ats_score", "0%")
            integrity = stats_resp.get("system_integrity", "Stable")
        except Exception:
            total_registered, resumes_processed, avg_score, integrity = 0, 0, "0%", "Offline"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Registered Candidates", value=str(total_registered))
        with col2:
            st.metric(label="Resumes Processed", value=str(resumes_processed))
        with col3:
            st.metric(label="Average ATS Match", value=avg_score)
        with col4:
            st.metric(label="System Core Health", value=integrity)
            
        st.markdown("---")
        st.markdown("### 🚀 Core Platform Objectives Status")
        obj_col1, obj_col2 = st.columns(2)
        with obj_col1:
            st.info("🟩 **Active Functional Operations**\n* Role-Based Access Control\n* Text Extraction Pipeline\n* Password Configuration Synchronization")
        with obj_col2:
            st.warning("⚡ **Pending Integration Tracks**\n* Predictive Salary Profiler\n* Live Skill Gap Matrix Analysis")

    elif page == "Analyze Resume":
        st.title("🔍 Advanced ATS Resume Scoring Engine")
        st.markdown("---")
        
        st.markdown("### 🛠️ Input Configuration Area")
        col_input, col_specs = st.columns([7, 5])
        with col_input:
            uploaded_file = st.file_uploader("Upload candidate resume package", type=["pdf", "txt"])
            job_description = st.text_area("Paste target Job Description requirements here...", height=150)
            run_analysis = st.button("⚡ Run Intelligent AI Evaluation")
        with col_specs:
            st.info("💡 **Engine Specifications**\nThis processing channel runs matching verification algorithms against form data boundaries to extract profile metrics instantly.")

        if run_analysis:
            if uploaded_file and job_description:
                st.markdown("---")
                with st.spinner("Processing network streams across API boundaries..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        data = {"job_description": job_description}
                        
                        response = requests.post(f"{FASTAPI_URL}/api/parser/analyze", data=data, files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            score_val = result.get("score", 50)
                            profile = result.get("extracted_profile", {})
                            found_keywords = result.get("found_keywords", [])
                            missing_keywords = result.get("missing_keywords", [])
                            predicted_salary = result.get("predicted_salary", "$60,000 - $85,000")
                            
                            st.markdown("### 🎯 ATS Evaluation Rating")
                            c_metric, c_status = st.columns([1, 2])
                            with c_metric:
                                st.metric(label="Overall Match Rating", value=f"{score_val}%")
                                st.progress(score_val / 100)
                            with c_status:
                                if score_val >= 75:
                                    st.success("🔥 High Match Index. Layout matches target core metrics smoothly.")
                                elif score_val >= 50:
                                    st.warning("⚠️ Boundary Match Index. Tweak missing parameters to optimize compliance.")
                                else:
                                    st.error("❌ Low Match Index. High risk of algorithmic sorting exclusion.")
                            
                            st.markdown("---")
                            
                            st.markdown("### ❌ Identified Layout & Skill Mistakes")
                            mistakes = []
                            if len(missing_keywords) > 0:
                                mistakes.append({
                                    "Error Category": "Missing Industry Core Keywords",
                                    "Identified Mistake": f"The following mandatory required keywords are missing: {', '.join([k.upper() for k in missing_keywords])}",
                                    "Impact Score": "Critical filtering penalty"
                                })
                            if profile.get('email') == "Not Found" or profile.get('phone') == "Not Found":
                                mistakes.append({
                                    "Error Category": "Header Coordinate Parsing Failure",
                                    "Identified Mistake": "Essential contact details could not be found or are incorrectly positioned.",
                                    "Impact Score": "High contact exclusion risk"
                                })
                            
                            if mistakes:
                                st.table(pd.DataFrame(mistakes))
                            else:
                                st.success("No critical core format mistakes detected in this document configuration!")
                                
                            st.markdown("---")
                            
                            st.markdown("### 📝 Automatically Corrected Resume Draft")
                            st.markdown("The system has automatically generated an optimized fallback copy appending missing professional terms below to resolve parsing exclusions.")
                            
                            corrected_text = f"NAME: {profile.get('name', 'Candidate Profile')}\n"
                            corrected_text += f"EMAIL: {profile.get('email', 'candidate@email.com')}\n"
                            corrected_text += f"PHONE: {profile.get('phone', 'Contact Not Provided')}\n\n"
                            corrected_text += "--- PROFESSIONAL SKILLS SUMMARY (AUTO-OPTIMIZED) ---\n"
                            corrected_text += f"Core Competencies: {', '.join([k.capitalize() for k in found_keywords + missing_keywords])}\n\n"
                            corrected_text += "--- TARGET JOB DESCRIPTION ALIGNMENT TRACK ---\n"
                            corrected_text += f"Target Requirements Profile: {job_description[:300]}...\n"
                            
                            st.text_area("Corrected Text Preview", value=corrected_text, height=180)
                            
                            st.download_button(
                                label="📥 Download Corrected Resume (.txt)",
                                data=corrected_text,
                                file_name="Optimized_ATS_Resume.txt",
                                mime="text/plain"
                            )
                            
                            st.markdown("---")
                            
                            st.markdown("### 💼 Relatable Career Matches & Direct Application Track")
                            
                            fit_primary = f"{score_val}%"
                            fit_secondary = f"{max(35, score_val - 15)}%"
                            
                            job_data = {
                                "Available Job Role": ["Primary Core System Developer", "Technical Solutions Integration Analyst"],
                                "Matching Aligned Fit": [fit_primary, fit_secondary],
                                "Application Matrix Status": ["Direct Fit - Highly Eligible", "Conditional Entry Track"]
                            }
                            df_jobs = pd.DataFrame(job_data)
                            
                            for index, row in df_jobs.iterrows():
                                j_col1, j_col2, j_col3 = st.columns([2, 1, 1])
                                j_col1.markdown(f"🔹 **{row['Available Job Role']}**")
                                j_col2.markdown(f"Match Index: **{row['Matching Aligned Fit']}**")
                                with j_col3:
                                    if st.button(f"Apply Now 🚀", key=f"apply_btn_{index}"):
                                        st.success(f"Application successfully routed to the tracking stream for {row['Available Job Role']}!")
                                        
                        else:
                            st.error("Backend parser pipeline failed to complete context processing.")
                    except Exception as e:
                        st.error(f"❌ Service Connection Error! Details: {str(e)}")
            else:
                st.warning("Please upload a file and provide a job description to process.")

    elif page == "Candidate Accounts" and st.session_state['is_admin']:
        st.title("📋 Live System Database Viewer")
        st.markdown("---")
        
        st.markdown("### 🗃️ Stored User Accounts (`Users` Table)")
        try:
            users_resp = requests.get(f"{FASTAPI_URL}/api/users")
            if users_resp.status_code == 200:
                users_data = users_resp.json()
                if users_data:
                    df_users = pd.DataFrame(users_data)
                    st.dataframe(df_users, use_container_width=True)
                else:
                    st.info("The database is currently initialized but contains no registered users yet.")
            else:
                st.error(f"Backend responded with an error: {users_resp.status_code}")
        except Exception as e:
            st.error(f"❌ Could not establish database link stream. Details: {str(e)}")

        st.markdown("---")
        st.markdown("### 🔑 Administrator Portal Credentials Reference")
        st.warning("🔒 **Default Admin Access Coordinate:**\n* **Username / Email:** `admin@ats.com` \n* **System Password:** `Admin@1234` ")