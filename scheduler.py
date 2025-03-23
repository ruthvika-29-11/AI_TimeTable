import pandas as pd
import numpy as np
from ortools.sat.python import cp_model
from datetime import datetime, time
from typing import List, Dict, Optional, Set, Tuple
from models import Faculty, Classroom, Course, Department, TimeSlot, Assignment
import random

class TimetableScheduler:
    """Uses OR-Tools CP-SAT solver to generate optimized timetables"""
    
    def __init__(self, faculty: List[Faculty], classrooms: List[Classroom], 
                 courses: List[Course], departments: List[Department]):
        self.faculty = faculty
        self.classrooms = classrooms
        self.courses = courses
        self.departments = departments
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Default time periods (8AM to 6PM, 1-hour slots)
        self.time_periods = [
            (time(hour=h, minute=0), time(hour=h+1, minute=0)) 
            for h in range(8, 18)
        ]
    
    def set_time_periods(self, periods: List[Tuple[time, time]]):
        """Set custom time periods for scheduling"""
        self.time_periods = periods
    
    def generate_timetable(self, 
                           max_time_limit_seconds: int = 60,
                           respect_faculty_preferences: bool = True,
                           prioritize_department_grouping: bool = True,
                           distribute_courses_evenly: bool = True) -> List[Assignment]:
        """
        Generate an optimized timetable using constraint programming
        
        Args:
            max_time_limit_seconds: Maximum time to spend solving (seconds)
            respect_faculty_preferences: Whether to prioritize faculty preferred slots
            prioritize_department_grouping: Whether to group department courses together
            distribute_courses_evenly: Whether to distribute courses evenly through the week
            
        Returns:
            List of assignments representing the timetable
        """
        # Create the model
        model = cp_model.CpModel()
        
        # Define time slots
        time_slots = []
        for day in self.days:
            for start_time, end_time in self.time_periods:
                time_slots.append(TimeSlot(day=day, start_time=start_time, end_time=end_time))
        
        # Create variables
        # For each course, faculty, classroom, time_slot combination, create a binary variable
        assignments = {}
        for course in self.courses:
            for faculty in self.faculty:
                # Skip faculty without required expertise for this course
                if course.faculty_requirements and not any(req in faculty.expertise for req in course.faculty_requirements):
                    continue
                
                for classroom in self.classrooms:
                    # Skip classrooms that don't meet the course requirements
                    if (classroom.capacity < course.min_capacity or 
                        classroom.room_type != course.required_room_type or
                        not all(facility in classroom.facilities for facility in course.required_facilities)):
                        continue
                    
                    for time_slot in time_slots:
                        # Skip unavailable faculty slots
                        if any(unavailable_slot.overlaps(time_slot) for unavailable_slot in faculty.unavailable_slots):
                            continue
                        
                        # Skip unavailable classroom slots
                        if any(unavailable_slot.overlaps(time_slot) for unavailable_slot in classroom.unavailable_slots):
                            continue
                        
                        # Create a binary variable for this assignment
                        var_name = f"C{course.id}_F{faculty.id}_R{classroom.id}_T{time_slot.day}_{time_slot.start_time}"
                        assignments[(course.id, faculty.id, classroom.id, time_slot)] = model.NewBoolVar(var_name)
        
        # Constraints
        
        # 1. Each course must be assigned exactly once for each hour it needs
        for course in self.courses:
            # Create a list of all possible assignments for this course
            course_assignments = []
            for (c_id, f_id, r_id, ts), var in assignments.items():
                if c_id == course.id:
                    course_assignments.append(var)
            
            if course_assignments:
                model.Add(sum(course_assignments) == course.hours_per_week)
        
        # 2. Faculty can't teach multiple courses at the same time
        for faculty in self.faculty:
            for time_slot in time_slots:
                conflicting_assignments = []
                for (c_id, f_id, r_id, ts), var in assignments.items():
                    if f_id == faculty.id and ts.overlaps(time_slot):
                        conflicting_assignments.append(var)
                
                if len(conflicting_assignments) > 1:
                    model.Add(sum(conflicting_assignments) <= 1)
        
        # 3. Classrooms can't host multiple courses at the same time
        for classroom in self.classrooms:
            for time_slot in time_slots:
                conflicting_assignments = []
                for (c_id, f_id, r_id, ts), var in assignments.items():
                    if r_id == classroom.id and ts.overlaps(time_slot):
                        conflicting_assignments.append(var)
                
                if len(conflicting_assignments) > 1:
                    model.Add(sum(conflicting_assignments) <= 1)
        
        # 4. Faculty shouldn't exceed their weekly teaching hours
        for faculty in self.faculty:
            faculty_assignments = []
            for (c_id, f_id, r_id, ts), var in assignments.items():
                if f_id == faculty.id:
                    faculty_assignments.append(var)
            
            if faculty_assignments:
                model.Add(sum(faculty_assignments) <= faculty.weekly_hours)
        
        # Objective function components
        
        # 1. Respect faculty preferences (if enabled)
        faculty_preferences_terms = []
        if respect_faculty_preferences:
            for (c_id, f_id, r_id, ts), var in assignments.items():
                # Get the faculty object
                faculty_obj = next((f for f in self.faculty if f.id == f_id), None)
                if faculty_obj:
                    # Check if this time slot is preferred
                    is_preferred = any(preferred.overlaps(ts) for preferred in faculty_obj.preferred_slots)
                    if is_preferred:
                        # Add a positive weight for preferred slots
                        faculty_preferences_terms.append(var)
        
        # 2. Group department courses together (if enabled)
        department_grouping_terms = []
        if prioritize_department_grouping:
            # For each pair of courses in the same department, reward scheduling them on the same day
            course_by_dept = {}
            for course in self.courses:
                if course.department not in course_by_dept:
                    course_by_dept[course.department] = []
                course_by_dept[course.department].append(course.id)
            
            for dept, course_ids in course_by_dept.items():
                if len(course_ids) <= 1:
                    continue
                
                # For each day, create incentives for courses in the same department to be on the same day
                for day in self.days:
                    for course_id in course_ids:
                        day_assignments = []
                        for (c_id, f_id, r_id, ts), var in assignments.items():
                            if c_id == course_id and ts.day == day:
                                day_assignments.append(var)
                        
                        if day_assignments:
                            department_grouping_terms.append(sum(day_assignments))
        
        # 3. Distribute courses evenly (if enabled)
        distribution_terms = []
        if distribute_courses_evenly:
            # Count assignments per day
            day_counts = {day: [] for day in self.days}
            for (c_id, f_id, r_id, ts), var in assignments.items():
                day_counts[ts.day].append(var)
            
            # Add terms to minimize differences between daily counts
            # Convert to integer to avoid type errors
            target_per_day_int = int(sum(len(course.faculty_requirements) for course in self.courses) // len(self.days))
            for day, vars_list in day_counts.items():
                if vars_list:
                    # Try to get counts close to target by minimizing absolute difference
                    # This is approximated in a linear model by adding a penalty
                    diff = model.NewIntVar(0, 100, f"diff_{day}")
                    model.Add(diff >= sum(vars_list) - target_per_day_int)
                    model.Add(diff >= target_per_day_int - sum(vars_list))
                    distribution_terms.append(diff)
        
        # Combine objective terms
        objective_terms = []
        
        # Add faculty preferences with weight 3
        if faculty_preferences_terms:
            objective_terms.extend(faculty_preferences_terms)
        
        # Add department grouping with weight 2
        if department_grouping_terms:
            objective_terms.extend(department_grouping_terms)
        
        # Add distribution terms with negative weight (to minimize)
        if distribution_terms:
            objective_terms.extend([-1 * term for term in distribution_terms])
        
        # Set the objective
        if objective_terms:
            model.Maximize(sum(objective_terms))
        
        # Create a solver and solve the model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = max_time_limit_seconds
        status = solver.Solve(model)
        
        # Process the solution
        assignments_result = []
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            for (c_id, f_id, r_id, ts), var in assignments.items():
                if solver.Value(var) == 1:
                    course = next((c for c in self.courses if c.id == c_id), None)
                    faculty = next((f for f in self.faculty if f.id == f_id), None)
                    classroom = next((r for r in self.classrooms if r.id == r_id), None)
                    
                    if course and faculty and classroom:
                        assignment = Assignment(
                            course=course,
                            faculty=faculty,
                            classroom=classroom,
                            time_slot=ts
                        )
                        assignments_result.append(assignment)
        
        return assignments_result
    
    def handle_last_minute_changes(self, timetable: List[Assignment], 
                                  unavailable_faculty: List[str] = [],
                                  unavailable_classrooms: List[str] = [], 
                                  additional_courses: List[Course] = []) -> List[Assignment]:
        """
        Adjust an existing timetable to accommodate last-minute changes
        
        Args:
            timetable: The existing timetable assignments
            unavailable_faculty: IDs of faculty who are now unavailable
            unavailable_classrooms: IDs of classrooms that are now unavailable
            additional_courses: New courses to add to the timetable
            
        Returns:
            Updated list of assignments
        """
        # Convert None to empty lists to avoid any issues
        if unavailable_faculty is None:
            unavailable_faculty = []
        if unavailable_classrooms is None:
            unavailable_classrooms = []
        if additional_courses is None:
            additional_courses = []
            
        # If no changes are requested, return the original timetable
        if not unavailable_faculty and not unavailable_classrooms and not additional_courses:
            return timetable
        
        # Create a copy of the original timetable
        updated_timetable = []
        affected_time_slots = set()
        
        # First, handle unavailable faculty and classrooms
        for assignment in timetable:
            if (unavailable_faculty and assignment.faculty.id in unavailable_faculty) or \
               (unavailable_classrooms and assignment.classroom.id in unavailable_classrooms):
                # This assignment needs to be rescheduled
                affected_time_slots.add(assignment.time_slot)
            else:
                # Keep this assignment as is
                updated_timetable.append(assignment)
        
        # Get all affected courses that need to be rescheduled
        affected_courses = [
            a.course for a in timetable if 
            (unavailable_faculty and a.faculty.id in unavailable_faculty) or
            (unavailable_classrooms and a.classroom.id in unavailable_classrooms)
        ]
        
        # Add new courses if any
        if additional_courses:
            affected_courses.extend(additional_courses)
        
        if not affected_courses:
            return timetable
        
        # Get currently available faculty and classrooms
        available_faculty = [f for f in self.faculty if not unavailable_faculty or f.id not in unavailable_faculty]
        available_classrooms = [c for c in self.classrooms if not unavailable_classrooms or c.id not in unavailable_classrooms]
        
        # Create a mini-scheduler for just the affected courses
        mini_scheduler = TimetableScheduler(
            faculty=available_faculty,
            classrooms=available_classrooms,
            courses=affected_courses,
            departments=self.departments
        )
        
        # Get already used time slots to avoid conflicts
        used_time_slots = {(a.faculty.id, a.time_slot): True for a in updated_timetable}
        used_time_slots.update({(a.classroom.id, a.time_slot): True for a in updated_timetable})
        
        # Add these constraints to faculty and classroom availability
        for faculty in available_faculty:
            # Add time slots where this faculty already has classes
            for a in updated_timetable:
                if a.faculty.id == faculty.id:
                    if not any(unavailable.overlaps(a.time_slot) for unavailable in faculty.unavailable_slots):
                        faculty.unavailable_slots.append(a.time_slot)
        
        for classroom in available_classrooms:
            # Add time slots where this classroom is already in use
            for a in updated_timetable:
                if a.classroom.id == classroom.id:
                    if not any(unavailable.overlaps(a.time_slot) for unavailable in classroom.unavailable_slots):
                        classroom.unavailable_slots.append(a.time_slot)
        
        # Generate a new mini-timetable for affected courses
        additional_assignments = mini_scheduler.generate_timetable(
            max_time_limit_seconds=30,  # Less time for urgent rescheduling
            respect_faculty_preferences=False,  # In emergency, preferences are less important
            prioritize_department_grouping=False,
            distribute_courses_evenly=False
        )
        
        # Combine original unaffected assignments with new ones
        updated_timetable.extend(additional_assignments)
        
        # If some courses couldn't be scheduled, try a more aggressive approach
        if len(additional_assignments) < len(affected_courses):
            # Get courses that failed to schedule
            scheduled_course_ids = {a.course.id for a in additional_assignments}
            unscheduled_courses = [c for c in affected_courses if c.id not in scheduled_course_ids]
            
            # Try manual assignment for these courses
            for course in unscheduled_courses:
                # Find suitable faculty
                suitable_faculty = [f for f in available_faculty 
                                   if not course.faculty_requirements or 
                                   any(req in f.expertise for req in course.faculty_requirements)]
                
                if not suitable_faculty:
                    continue
                
                # Find suitable classrooms
                suitable_classrooms = [c for c in available_classrooms
                                      if c.capacity >= course.min_capacity and
                                      c.room_type == course.required_room_type and
                                      all(facility in c.facilities for facility in course.required_facilities)]
                
                if not suitable_classrooms:
                    continue
                
                # Try to find an available time slot
                for day in self.days:
                    for start_time, end_time in self.time_periods:
                        ts = TimeSlot(day=day, start_time=start_time, end_time=end_time)
                        
                        # Check if this time slot works
                        for faculty in suitable_faculty:
                            if (faculty.id, ts) in used_time_slots:
                                continue
                                
                            if any(unavailable.overlaps(ts) for unavailable in faculty.unavailable_slots):
                                continue
                                
                            for classroom in suitable_classrooms:
                                if (classroom.id, ts) in used_time_slots:
                                    continue
                                    
                                if any(unavailable.overlaps(ts) for unavailable in classroom.unavailable_slots):
                                    continue
                                
                                # This is a valid assignment
                                assignment = Assignment(
                                    course=course,
                                    faculty=faculty,
                                    classroom=classroom,
                                    time_slot=ts
                                )
                                updated_timetable.append(assignment)
                                
                                # Mark this slot as used
                                used_time_slots[(faculty.id, ts)] = True
                                used_time_slots[(classroom.id, ts)] = True
                                
                                # Move to next course
                                break
                            
                            # If we found an assignment, break out of faculty loop
                            if (faculty.id, ts) in used_time_slots:
                                break
                        
                        # If we found an assignment, break out of time slot loop
                        if any((faculty.id, ts) in used_time_slots for faculty in suitable_faculty):
                            break
                    
                    # If we found an assignment, break out of days loop
                    if any((faculty.id, ts) in used_time_slots for faculty in suitable_faculty for ts in [TimeSlot(day=day, start_time=start, end_time=end) for start, end in self.time_periods]):
                        break
        
        return updated_timetable
