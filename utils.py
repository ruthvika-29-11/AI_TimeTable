import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, time
import io
import base64
from typing import List, Dict, Optional, Any, Tuple
from models import Faculty, Classroom, Course, Department, TimeSlot, Assignment


def create_download_link(df: pd.DataFrame, filename: str, text: str) -> str:
    """
    Create a download link for a dataframe
    
    Args:
        df: Pandas DataFrame to export
        filename: Name of the file to download
        text: Text to display for the download link
        
    Returns:
        HTML string with the download link
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def format_time_input(hour: int, minute: int = 0) -> time:
    """
    Format hour and minute into a time object
    
    Args:
        hour: Hour (0-23)
        minute: Minute (0-59)
        
    Returns:
        time object
    """
    return time(hour=max(0, min(23, hour)), minute=max(0, min(59, minute)))

def parse_time_str(time_str: str) -> Optional[time]:
    """
    Parse a time string in format HH:MM
    
    Args:
        time_str: Time string to parse
        
    Returns:
        time object or None if parsing fails
    """
    try:
        hour, minute = map(int, time_str.split(':'))
        return format_time_input(hour, minute)
    except:
        return None

def create_faculty_form(existing_faculty: Optional[Faculty] = None, form_key: str = "faculty_form") -> Tuple[bool, Optional[Faculty]]:
    """
    Create a form for adding/editing faculty
    
    Args:
        existing_faculty: Optional existing faculty to edit
        form_key: Unique key for the form
        
    Returns:
        Tuple of (form_submitted, faculty_object)
    """
    with st.form(f"{form_key}_{id(existing_faculty)}"):
        st.subheader("Faculty Information")
        
        name = st.text_input("Name", value=existing_faculty.name if existing_faculty else "")
        
        # Get departments for dropdown
        departments = st.session_state.data_manager.get_all_departments()
        dept_options = [d.id for d in departments]
        dept_names = {d.id: d.name for d in departments}
        
        department = st.selectbox(
            "Department", 
            options=dept_options,
            format_func=lambda x: dept_names.get(x, x),
            index=dept_options.index(existing_faculty.department) if existing_faculty and existing_faculty.department in dept_options else 0
        ) if dept_options else st.text_input("Department", value=existing_faculty.department if existing_faculty else "")
        
        weekly_hours = st.number_input(
            "Weekly Teaching Hours", 
            min_value=1, 
            max_value=40, 
            value=existing_faculty.weekly_hours if existing_faculty else 20
        )
        
        expertise = st.text_input(
            "Expertise (comma separated)", 
            value=",".join(existing_faculty.expertise) if existing_faculty and existing_faculty.expertise else ""
        )
        
        st.subheader("Availability")
        
        unavailable_days = st.multiselect(
            "Unavailable Days",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            default=[slot.day for slot in existing_faculty.unavailable_slots] if existing_faculty and existing_faculty.unavailable_slots else []
        )
        
        preferred_days = st.multiselect(
            "Preferred Days",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            default=[slot.day for slot in existing_faculty.preferred_slots] if existing_faculty and existing_faculty.preferred_slots else []
        )
        
        submitted = st.form_submit_button("Save Faculty")
        
        if submitted:
            # Process expertise
            expertise_list = [e.strip() for e in expertise.split(",") if e.strip()]
            
            # Process unavailable slots
            unavailable_slots = []
            for day in unavailable_days:
                # Make the whole day unavailable (8 AM to 6 PM)
                unavailable_slots.append(TimeSlot(
                    day=day,
                    start_time=time(hour=8),
                    end_time=time(hour=18)
                ))
            
            # Process preferred slots
            preferred_slots = []
            for day in preferred_days:
                # Prefer the whole day (8 AM to 6 PM)
                preferred_slots.append(TimeSlot(
                    day=day,
                    start_time=time(hour=8),
                    end_time=time(hour=18)
                ))
            
            # Create or update faculty object
            faculty = Faculty(
                id=existing_faculty.id if existing_faculty else "",
                name=name,
                department=department,
                weekly_hours=weekly_hours,
                expertise=expertise_list,
                unavailable_slots=unavailable_slots,
                preferred_slots=preferred_slots
            )
            
            return True, faculty
        
        return False, None

def create_classroom_form(existing_classroom: Optional[Classroom] = None, form_key: str = "classroom_form") -> Tuple[bool, Optional[Classroom]]:
    """
    Create a form for adding/editing classroom
    
    Args:
        existing_classroom: Optional existing classroom to edit
        form_key: Unique key for the form
        
    Returns:
        Tuple of (form_submitted, classroom_object)
    """
    with st.form(f"{form_key}_{id(existing_classroom)}"):
        st.subheader("Classroom Information")
        
        name = st.text_input("Name/Number", value=existing_classroom.name if existing_classroom else "")
        building = st.text_input("Building", value=existing_classroom.building if existing_classroom else "")
        
        capacity = st.number_input(
            "Seating Capacity", 
            min_value=1, 
            max_value=500, 
            value=existing_classroom.capacity if existing_classroom else 30
        )
        
        room_type = st.selectbox(
            "Room Type",
            options=["Lecture", "Lab", "Seminar", "Conference"],
            index=["Lecture", "Lab", "Seminar", "Conference"].index(existing_classroom.room_type) if existing_classroom else 0
        )
        
        facilities = st.multiselect(
            "Facilities",
            options=["Projector", "Computer", "Smart Board", "Video Conference", "Lab Equipment", "Whiteboard"],
            default=existing_classroom.facilities if existing_classroom else ["Projector", "Whiteboard"]
        )
        
        st.subheader("Availability")
        
        unavailable_days = st.multiselect(
            "Unavailable Days",
            options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            default=[slot.day for slot in existing_classroom.unavailable_slots] if existing_classroom and existing_classroom.unavailable_slots else []
        )
        
        submitted = st.form_submit_button("Save Classroom")
        
        if submitted:
            # Process unavailable slots
            unavailable_slots = []
            for day in unavailable_days:
                # Make the whole day unavailable (8 AM to 6 PM)
                unavailable_slots.append(TimeSlot(
                    day=day,
                    start_time=time(hour=8),
                    end_time=time(hour=18)
                ))
            
            # Create or update classroom object
            classroom = Classroom(
                id=existing_classroom.id if existing_classroom else "",
                name=name,
                building=building,
                capacity=capacity,
                room_type=room_type,
                facilities=facilities,
                unavailable_slots=unavailable_slots
            )
            
            return True, classroom
        
        return False, None

def create_course_form(existing_course: Optional[Course] = None, form_key: str = "course_form") -> Tuple[bool, Optional[Course]]:
    """
    Create a form for adding/editing course
    
    Args:
        existing_course: Optional existing course to edit
        form_key: Unique key for the form
        
    Returns:
        Tuple of (form_submitted, course_object)
    """
    with st.form(f"{form_key}_{id(existing_course)}"):
        st.subheader("Course Information")
        
        code = st.text_input("Course Code", value=existing_course.code if existing_course else "")
        name = st.text_input("Course Name", value=existing_course.name if existing_course else "")
        
        # Get departments for dropdown
        departments = st.session_state.data_manager.get_all_departments()
        dept_options = [d.id for d in departments]
        dept_names = {d.id: d.name for d in departments}
        
        department = st.selectbox(
            "Department", 
            options=dept_options,
            format_func=lambda x: dept_names.get(x, x),
            index=dept_options.index(existing_course.department) if existing_course and existing_course.department in dept_options else 0
        ) if dept_options else st.text_input("Department", value=existing_course.department if existing_course else "")
        
        credits = st.number_input(
            "Credits", 
            min_value=1, 
            max_value=12, 
            value=existing_course.credits if existing_course else 3
        )
        
        hours_per_week = st.number_input(
            "Hours per Week", 
            min_value=1, 
            max_value=20, 
            value=existing_course.hours_per_week if existing_course else 3
        )
        
        min_capacity = st.number_input(
            "Minimum Classroom Capacity", 
            min_value=1, 
            max_value=500, 
            value=existing_course.min_capacity if existing_course else 20
        )
        
        room_type = st.selectbox(
            "Required Room Type",
            options=["Lecture", "Lab", "Seminar", "Any"],
            index=["Lecture", "Lab", "Seminar", "Any"].index(existing_course.required_room_type) if existing_course and existing_course.required_room_type in ["Lecture", "Lab", "Seminar", "Any"] else 0
        )
        
        # Convert "Any" to "Lecture" (default) for storage
        room_type = "Lecture" if room_type == "Any" else room_type
        
        required_facilities = st.multiselect(
            "Required Facilities",
            options=["Projector", "Computer", "Smart Board", "Video Conference", "Lab Equipment", "Whiteboard"],
            default=existing_course.required_facilities if existing_course else []
        )
        
        # Get faculty expertise for dropdown
        faculty_list = st.session_state.data_manager.get_all_faculty()
        all_expertise = set()
        for faculty in faculty_list:
            all_expertise.update(faculty.expertise)
        
        faculty_requirements = st.multiselect(
            "Faculty Expertise Required",
            options=sorted(list(all_expertise)),
            default=existing_course.faculty_requirements if existing_course else []
        )
        
        submitted = st.form_submit_button("Save Course")
        
        if submitted:
            # Create or update course object
            course = Course(
                id=existing_course.id if existing_course else "",
                code=code,
                name=name,
                department=department,
                credits=credits,
                hours_per_week=hours_per_week,
                required_room_type=room_type,
                required_facilities=required_facilities,
                min_capacity=min_capacity,
                faculty_requirements=faculty_requirements
            )
            
            return True, course
        
        return False, None

def create_department_form(existing_department: Optional[Department] = None, form_key: str = "department_form") -> Tuple[bool, Optional[Department]]:
    """
    Create a form for adding/editing department
    
    Args:
        existing_department: Optional existing department to edit
        form_key: Unique key for the form
        
    Returns:
        Tuple of (form_submitted, department_object)
    """
    with st.form(f"{form_key}_{id(existing_department)}"):
        st.subheader("Department Information")
        
        name = st.text_input("Department Name", value=existing_department.name if existing_department else "")
        code = st.text_input("Department Code", value=existing_department.code if existing_department else "")
        
        submitted = st.form_submit_button("Save Department")
        
        if submitted:
            # Create or update department object
            department = Department(
                id=existing_department.id if existing_department else "",
                name=name,
                code=code
            )
            
            return True, department
        
        return False, None

def get_assignment_info(assignment: Assignment) -> Dict[str, str]:
    """
    Get formatted information from an assignment for display
    
    Args:
        assignment: Assignment object
        
    Returns:
        Dictionary with formatted information
    """
    return {
        "Day": assignment.time_slot.day,
        "Time": f"{assignment.time_slot.start_time.strftime('%H:%M')} - {assignment.time_slot.end_time.strftime('%H:%M')}",
        "Course": f"{assignment.course.code} - {assignment.course.name}",
        "Faculty": assignment.faculty.name,
        "Classroom": f"{assignment.classroom.name} ({assignment.classroom.building})",
        "Department": assignment.course.department
    }

def display_timetable_as_table(assignments: List[Assignment]) -> None:
    """
    Display timetable as a formatted table
    
    Args:
        assignments: List of assignments to display
    """
    if not assignments:
        st.info("No assignments to display")
        return
    
    # Option to switch between different view types
    # Add unique key based on a hash of the assignments to avoid duplicate ID errors
    radio_key = f"view_format_{hash(tuple(a.course.id for a in assignments))}"


    view_type = st.radio(
        "Select View Type:",
        ("Table", "Grid"),
        key=f"view_format_{time.time()}"  # Unique key using timestamp
    )


    
    if view_type == "Traditional Table":
        # Convert to dataframe for display
        assignments_data = [get_assignment_info(a) for a in assignments]
        df = pd.DataFrame(assignments_data)
        
        # Sort by day (custom order) and time
        day_order = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4}
        df["Day_order"] = df["Day"].map(day_order)
        df = df.sort_values(["Day_order", "Time"]).drop("Day_order", axis=1)
        
        # Display as styled dataframe
        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Course": st.column_config.TextColumn("Course", width="large"),
                "Time": st.column_config.TextColumn("Time", width="medium"),
                "Day": st.column_config.TextColumn("Day", width="small"),
                "Faculty": st.column_config.TextColumn("Faculty", width="medium"),
                "Classroom": st.column_config.TextColumn("Classroom", width="medium"),
                "Department": st.column_config.TextColumn("Department", width="medium")
            },
            height=400
        )
    else:
        # Create a grid view like a weekly calendar
        # Define days and time slots
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Extract all unique time slots
        time_slots = sorted(list(set([f"{a.time_slot.start_time.strftime('%H:%M')} - {a.time_slot.end_time.strftime('%H:%M')}" 
                               for a in assignments])))
        
        # Create empty grid
        grid_data = {}
        for day in days:
            grid_data[day] = {}
            for time_slot in time_slots:
                grid_data[day][time_slot] = []
        
        # Fill grid with class info
        for a in assignments:
            day = a.time_slot.day
            time_slot = f"{a.time_slot.start_time.strftime('%H:%M')} - {a.time_slot.end_time.strftime('%H:%M')}"
            
            # Create a concise class entry
            class_info = f"{a.course.code}<br>{a.faculty.name}<br>{a.classroom.name}"
            grid_data[day][time_slot].append(class_info)
        
        # Convert to DataFrame for display
        grid_df = pd.DataFrame(index=time_slots, columns=days)
        
        for day in days:
            for time_slot in time_slots:
                if grid_data[day][time_slot]:
                    # Join multiple classes with a separator
                    grid_df.at[time_slot, day] = "<br>--------<br>".join(grid_data[day][time_slot])
                else:
                    grid_df.at[time_slot, day] = ""
        
        # Create HTML table with styling
        html_table = """
        <style>
            .timetable-grid {
                width: 100%;
                border-collapse: collapse;
                font-family: Arial, sans-serif;
            }
            .timetable-grid th {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                text-align: center;
                font-weight: bold;
                border: 1px solid #ddd;
            }
            .timetable-grid td {
                padding: 10px;
                border: 1px solid #ddd;
                vertical-align: top;
                min-height: 80px;
                background-color: #f9f9f9;
                font-size: 14px;
                max-width: 200px;
            }
            .timetable-grid td:not(:empty) {
                background-color: #e6f7ff;
            }
            .timetable-grid tr:nth-child(even) td {
                background-color: #f2f2f2;
            }
            .timetable-grid tr:nth-child(even) td:not(:empty) {
                background-color: #d9f0ff;
            }
            .time-column {
                font-weight: bold;
                background-color: #e6e6e6 !important;
            }
        </style>
        <table class="timetable-grid">
            <tr>
                <th>Time</th>
        """
        
        # Add day headers
        for day in days:
            html_table += f"<th>{day}</th>"
        
        html_table += "</tr>"
        
        # Add rows for each time slot
        for time_slot in time_slots:
            html_table += f"""
            <tr>
                <td class="time-column">{time_slot}</td>
            """
            
            # Add cells for each day
            for day in days:
                cell_content = grid_df.at[time_slot, day] if not pd.isna(grid_df.at[time_slot, day]) else ""
                html_table += f"<td>{cell_content}</td>"
            
            html_table += "</tr>"
        
        html_table += "</table>"
        
        # Display HTML table
        st.markdown(html_table, unsafe_allow_html=True)
