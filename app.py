import streamlit as st
import pandas as pd
import numpy as np
from models import Faculty, Classroom, Course, Department, TimeSlot
from data_manager import DataManager
import utils

# Set page configuration
st.set_page_config(
    page_title="AI Timetable & Resource Allocation System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data management
if 'data_manager' not in st.session_state:
    st.session_state.data_manager = DataManager()

# Main page content
st.title("AI Timetable & Resource Allocation System")

# Overview metrics
col1, col2, col3, col4 = st.columns(4)

# Get counts from data manager
dm = st.session_state.data_manager
faculty_count = len(dm.get_all_faculty())
classroom_count = len(dm.get_all_classrooms())
course_count = len(dm.get_all_courses())
department_count = len(dm.get_all_departments())

with col1:
    st.metric(label="Faculty", value=faculty_count)
with col2:
    st.metric(label="Classrooms", value=classroom_count)
with col3:
    st.metric(label="Courses", value=course_count)
with col4:
    st.metric(label="Departments", value=department_count)

# System overview
st.markdown("""
## System Overview
This AI-powered system helps educational institutions optimize their timetables and resource allocation. 
It automatically generates conflict-free schedules while considering various constraints like faculty 
availability, classroom capacities, and curriculum requirements.

### Key Features
- Automatic timetable generation using AI algorithms
- Resource tracking and optimization
- Faculty preference integration
- Interactive timetable visualization
- Easy rescheduling for last-minute changes
- Resource utilization analytics

### Getting Started
Use the sidebar navigation to:
1. Set up your faculty, classrooms, courses, and departments
2. Define constraints and preferences
3. Generate and visualize timetables
4. Analyze resource utilization
""")

# Quick links
st.subheader("Quick Links")
quick_links_col1, quick_links_col2 = st.columns(2)

with quick_links_col1:
    if st.button("📋 Generate New Timetable"):
        st.switch_page("pages/05_Generate_Timetable.py")
    if st.button("👥 Manage Faculty"):
        st.switch_page("pages/01_Faculty_Management.py")
    if st.button("🏢 Manage Classrooms"):
        st.switch_page("pages/02_Classrooms_Management.py")

with quick_links_col2:
    if st.button("📊 View Timetables"):
        st.switch_page("pages/06_View_Timetables.py")
    if st.button("📚 Manage Courses"):
        st.switch_page("pages/03_Courses_Management.py")
    if st.button("🏫 Manage Departments"):
        st.switch_page("pages/04_Department_Management.py")

# Recent schedules
if 'generated_timetables' in st.session_state and st.session_state.generated_timetables:
    st.subheader("Recent Timetables")
    
    timetable_names = list(st.session_state.generated_timetables.keys())
    
    # Show the 3 most recent timetables
    for name in timetable_names[-3:]:
        with st.expander(f"Timetable: {name}"):
            # Summary of the timetable
            timetable = st.session_state.generated_timetables[name]
            st.write(f"Generated on: {timetable.get('generated_date', 'Unknown date')}")
            st.write(f"Total classes scheduled: {len(timetable.get('assignments', []))}")
            
            if st.button(f"View full timetable for {name}"):
                st.session_state.selected_timetable = name
                st.switch_page("pages/06_View_Timetables.py")
