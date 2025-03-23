import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from models import Assignment, Faculty, Classroom, Course, TimeSlot
import streamlit as st

class TimetableVisualizer:
    """Visualizes timetable data in various formats"""
    
    @staticmethod
    def create_faculty_timetable(assignments: List[Assignment], faculty_id: Optional[str] = None) -> go.Figure:
        """
        Create a timetable visualization for a specific faculty or all faculty
        
        Args:
            assignments: List of assignments in the timetable
            faculty_id: Optional faculty ID to filter for
            
        Returns:
            Plotly figure object
        """
        if faculty_id:
            # Filter for the specific faculty
            filtered_assignments = [a for a in assignments if a.faculty.id == faculty_id]
            title = f"Timetable for {filtered_assignments[0].faculty.name if filtered_assignments else 'Faculty'}"
        else:
            filtered_assignments = assignments
            title = "Faculty Timetable Overview"
        
        # Create data for heatmap
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{h}:00" for h in range(8, 18)]  # 8 AM to 6 PM
        
        # Initialize the data grid
        grid = np.empty((len(days), len(hours)), dtype=object)
        grid_values = np.zeros((len(days), len(hours)))
        
        # Fill in the data
        for assignment in filtered_assignments:
            day_idx = days.index(assignment.time_slot.day)
            hour_idx = hours.index(f"{assignment.time_slot.start_time.hour}:00")
            
            # Create the cell text
            if faculty_id:
                cell_text = f"{assignment.course.code}<br>{assignment.classroom.name}"
            else:
                cell_text = f"{assignment.faculty.name}<br>{assignment.course.code}<br>{assignment.classroom.name}"
            
            grid[day_idx, hour_idx] = cell_text
            grid_values[day_idx, hour_idx] = 1  # Just to indicate a class is scheduled
        
        # Create the heatmap with improved styling
        fig = go.Figure(data=go.Heatmap(
            z=grid_values,
            x=hours,
            y=days,
            colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(230,240,255)']],
            showscale=False,
            hoverinfo='text',
            text=grid
        ))
        
        # Add better styled text annotations
        for i, day in enumerate(days):
            for j, hour in enumerate(hours):
                if grid[i, j] is not None:
                    fig.add_annotation(
                        x=hour,
                        y=day,
                        text=grid[i, j],
                        showarrow=False,
                        font=dict(size=10, color="black"),
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="rgba(0, 0, 0, 0.3)",
                        borderwidth=1,
                        borderpad=2,
                        width=180,
                        height=60,
                        align="left"
                    )
        
        # Update layout with improved styling
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Day",
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        # Add grid lines for better visual separation
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        return fig
    
    @staticmethod
    def create_classroom_timetable(assignments: List[Assignment], classroom_id: Optional[str] = None) -> go.Figure:
        """
        Create a timetable visualization for a specific classroom or all classrooms
        
        Args:
            assignments: List of assignments in the timetable
            classroom_id: Optional classroom ID to filter for
            
        Returns:
            Plotly figure object
        """
        if classroom_id:
            # Filter for the specific classroom
            filtered_assignments = [a for a in assignments if a.classroom.id == classroom_id]
            title = f"Timetable for {filtered_assignments[0].classroom.name if filtered_assignments else 'Classroom'}"
        else:
            filtered_assignments = assignments
            title = "Classroom Timetable Overview"
        
        # Create data for heatmap
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{h}:00" for h in range(8, 18)]  # 8 AM to 6 PM
        
        # Initialize the data grid
        grid = np.empty((len(days), len(hours)), dtype=object)
        grid_values = np.zeros((len(days), len(hours)))
        
        # Fill in the data
        for assignment in filtered_assignments:
            day_idx = days.index(assignment.time_slot.day)
            hour_idx = hours.index(f"{assignment.time_slot.start_time.hour}:00")
            
            # Create the cell text
            if classroom_id:
                cell_text = f"{assignment.course.code}<br>{assignment.faculty.name}"
            else:
                cell_text = f"{assignment.classroom.name}<br>{assignment.course.code}<br>{assignment.faculty.name}"
            
            grid[day_idx, hour_idx] = cell_text
            grid_values[day_idx, hour_idx] = 1  # Just to indicate a class is scheduled
        
        # Create the heatmap with improved styling
        fig = go.Figure(data=go.Heatmap(
            z=grid_values,
            x=hours,
            y=days,
            colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(230,240,255)']],
            showscale=False,
            hoverinfo='text',
            text=grid
        ))
        
        # Add better styled text annotations
        for i, day in enumerate(days):
            for j, hour in enumerate(hours):
                if grid[i, j] is not None:
                    fig.add_annotation(
                        x=hour,
                        y=day,
                        text=grid[i, j],
                        showarrow=False,
                        font=dict(size=10, color="black"),
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="rgba(0, 0, 0, 0.3)",
                        borderwidth=1,
                        borderpad=2,
                        width=180,
                        height=60,
                        align="left"
                    )
        
        # Update layout with improved styling
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Day",
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        # Add grid lines for better visual separation
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        return fig
    
    @staticmethod
    def create_department_timetable(assignments: List[Assignment], department_id: str) -> go.Figure:
        """
        Create a timetable visualization for a specific department
        
        Args:
            assignments: List of assignments in the timetable
            department_id: Department ID to filter for
            
        Returns:
            Plotly figure object
        """
        # Filter for courses in this department
        filtered_assignments = [a for a in assignments if a.course.department == department_id]
        
        if not filtered_assignments:
            return None
        
        title = f"Timetable for Department: {department_id}"
        
        # Create data for heatmap
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{h}:00" for h in range(8, 18)]  # 8 AM to 6 PM
        
        # Initialize the data grid
        grid = np.empty((len(days), len(hours)), dtype=object)
        grid_values = np.zeros((len(days), len(hours)))
        
        # Fill in the data
        for assignment in filtered_assignments:
            day_idx = days.index(assignment.time_slot.day)
            hour_idx = hours.index(f"{assignment.time_slot.start_time.hour}:00")
            
            # Create the cell text
            cell_text = f"{assignment.course.code}<br>{assignment.faculty.name}<br>{assignment.classroom.name}"
            
            # If there's already content, append to it
            if grid[day_idx, hour_idx] is not None:
                grid[day_idx, hour_idx] += f"<br>---<br>{cell_text}"
                grid_values[day_idx, hour_idx] += 1
            else:
                grid[day_idx, hour_idx] = cell_text
                grid_values[day_idx, hour_idx] = 1
        
        # Create the heatmap with improved styling
        fig = go.Figure(data=go.Heatmap(
            z=grid_values,
            x=hours,
            y=days,
            colorscale=[[0, 'rgb(255,255,255)'], [1, 'rgb(230,240,255)']],
            showscale=False,
            hoverinfo='text',
            text=grid
        ))
        
        # Add better styled text annotations
        for i, day in enumerate(days):
            for j, hour in enumerate(hours):
                if grid[i, j] is not None:
                    fig.add_annotation(
                        x=hour,
                        y=day,
                        text=grid[i, j],
                        showarrow=False,
                        font=dict(size=10, color="black"),
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="rgba(0, 0, 0, 0.3)",
                        borderwidth=1,
                        borderpad=2,
                        width=180,
                        height=60,
                        align="left"
                    )
        
        # Update layout with improved styling
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title="Day",
            height=500,
            margin=dict(l=50, r=50, t=80, b=50),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        
        # Add grid lines for better visual separation
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        return fig
    
    @staticmethod
    def create_resource_utilization_chart(assignments: List[Assignment]) -> Dict[str, go.Figure]:
        """
        Create visualizations of resource utilization
        
        Args:
            assignments: List of assignments in the timetable
            
        Returns:
            Dictionary of Plotly figure objects for different utilization charts
        """
        # Create dictionary to store figures
        figures = {}
        
        # 1. Classroom utilization by day and hour
        classroom_usage = {}
        total_classrooms = len(set(a.classroom.id for a in assignments))
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        hours = [f"{h}:00" for h in range(8, 18)]  # 8 AM to 6 PM
        
        for day in days:
            classroom_usage[day] = {}
            for hour_str in hours:
                hour = int(hour_str.split(':')[0])
                # Count classrooms in use at this time
                in_use = len(set(a.classroom.id for a in assignments 
                               if a.time_slot.day == day and 
                               a.time_slot.start_time.hour == hour))
                
                utilization_pct = (in_use / total_classrooms * 100) if total_classrooms > 0 else 0
                classroom_usage[day][hour_str] = utilization_pct
        
        # Create DataFrame for heatmap
        classroom_usage_df = pd.DataFrame(classroom_usage)
        classroom_usage_df = classroom_usage_df.transpose()
        
        # Create heatmap with improved styling
        fig_classroom_util = px.imshow(
            classroom_usage_df,
            labels=dict(x="Hour", y="Day", color="Utilization (%)"),
            x=hours,
            y=days,
            color_continuous_scale="Blues",
            title="Classroom Utilization by Day and Hour (%)"
        )
        
        fig_classroom_util.update_layout(
            height=500,
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(family="Arial, sans-serif", size=12)
        )
        figures["classroom_utilization"] = fig_classroom_util
        
        # 2. Faculty teaching hours distribution
        faculty_hours = {}
        for a in assignments:
            if a.faculty.id not in faculty_hours:
                faculty_hours[a.faculty.id] = {
                    "name": a.faculty.name,
                    "hours": 0
                }
            faculty_hours[a.faculty.id]["hours"] += 1
        
        faculty_hours_df = pd.DataFrame([
            {"Faculty": data["name"], "Teaching Hours": data["hours"]}
            for faculty_id, data in faculty_hours.items()
        ])
        
        if not faculty_hours_df.empty:
            fig_faculty_hours = px.bar(
                faculty_hours_df, 
                x="Faculty", 
                y="Teaching Hours",
                title="Faculty Teaching Hours Distribution",
                color="Teaching Hours",
                color_continuous_scale="Viridis",
                text_auto=True  # Add text labels on bars
            )
            
            # Improve styling of faculty hours chart
            fig_faculty_hours.update_layout(
                height=500,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                xaxis=dict(tickangle=-45)  # Angle the labels for better readability
            )
            
            # Add grid lines for better readability
            fig_faculty_hours.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            
            figures["faculty_hours"] = fig_faculty_hours
        
        # 3. Room type utilization with improved styling
        room_type_usage = {}
        for a in assignments:
            room_type = a.classroom.room_type
            if room_type not in room_type_usage:
                room_type_usage[room_type] = 0
            room_type_usage[room_type] += 1
        
        room_type_df = pd.DataFrame([
            {"Room Type": rt, "Hours Used": count}
            for rt, count in room_type_usage.items()
        ])
        
        if not room_type_df.empty:
            fig_room_types = px.pie(
                room_type_df,
                values="Hours Used",
                names="Room Type",
                title="Usage by Room Type",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Plotly  # Better color scheme
            )
            
            # Improve styling of room type pie chart
            fig_room_types.update_layout(
                height=500,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )
            
            # Add percentage and values in hover
            fig_room_types.update_traces(
                textinfo='percent+label',
                hoverinfo='label+percent+value'
            )
            
            figures["room_type_usage"] = fig_room_types
        
        # 4. Department teaching hours with improved styling
        dept_hours = {}
        for a in assignments:
            dept = a.course.department
            if dept not in dept_hours:
                dept_hours[dept] = 0
            dept_hours[dept] += 1
        
        dept_hours_df = pd.DataFrame([
            {"Department": dept, "Teaching Hours": hours}
            for dept, hours in dept_hours.items()
        ])
        
        if not dept_hours_df.empty:
            fig_dept_hours = px.bar(
                dept_hours_df,
                x="Department",
                y="Teaching Hours",
                title="Teaching Hours by Department",
                color="Department",
                text_auto=True  # Add text labels on bars
            )
            
            # Improve styling of department hours chart
            fig_dept_hours.update_layout(
                height=500,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family="Arial, sans-serif", size=12),
                xaxis=dict(tickangle=-45)  # Angle the labels for better readability
            )
            
            # Add grid lines for better readability
            fig_dept_hours.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            
            figures["department_hours"] = fig_dept_hours
        
        return figures