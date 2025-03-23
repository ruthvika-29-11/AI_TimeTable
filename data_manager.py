import pandas as pd
import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from models import Faculty, Classroom, Course, Department, TimeSlot, Assignment

class DataManager:
    """Handles data storage and retrieval for the timetable system"""
    
    def __init__(self):
        """Initialize the data manager with empty collections"""
        self.faculty: Dict[str, Faculty] = {}
        self.classrooms: Dict[str, Classroom] = {}
        self.courses: Dict[str, Course] = {}
        self.departments: Dict[str, Department] = {}
        self.timetables: Dict[str, Dict[str, Any]] = {}
        
        # Create folders for data storage if they don't exist
        os.makedirs("data", exist_ok=True)
        
        # Load any existing data
        self.load_data()
    
    def load_data(self):
        """Load data from storage files if they exist"""
        try:
            if os.path.exists("data/faculty.json"):
                with open("data/faculty.json", "r") as f:
                    faculty_data = json.load(f)
                    for faculty_dict in faculty_data:
                        faculty = Faculty.from_dict(faculty_dict)
                        self.faculty[faculty.id] = faculty
            
            if os.path.exists("data/classrooms.json"):
                with open("data/classrooms.json", "r") as f:
                    classroom_data = json.load(f)
                    for classroom_dict in classroom_data:
                        classroom = Classroom.from_dict(classroom_dict)
                        self.classrooms[classroom.id] = classroom
            
            if os.path.exists("data/courses.json"):
                with open("data/courses.json", "r") as f:
                    course_data = json.load(f)
                    for course_dict in course_data:
                        course = Course.from_dict(course_dict)
                        self.courses[course.id] = course
            
            if os.path.exists("data/departments.json"):
                with open("data/departments.json", "r") as f:
                    department_data = json.load(f)
                    for department_dict in department_data:
                        department = Department.from_dict(department_dict)
                        self.departments[department.id] = department
            
            if os.path.exists("data/timetables.json"):
                with open("data/timetables.json", "r") as f:
                    self.timetables = json.load(f)
                    
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save_data(self):
        """Save all data to storage files"""
        try:
            with open("data/faculty.json", "w") as f:
                faculty_data = [faculty.to_dict() for faculty in self.faculty.values()]
                json.dump(faculty_data, f, indent=2)
            
            with open("data/classrooms.json", "w") as f:
                classroom_data = [classroom.to_dict() for classroom in self.classrooms.values()]
                json.dump(classroom_data, f, indent=2)
            
            with open("data/courses.json", "w") as f:
                course_data = [course.to_dict() for course in self.courses.values()]
                json.dump(course_data, f, indent=2)
            
            with open("data/departments.json", "w") as f:
                department_data = [department.to_dict() for department in self.departments.values()]
                json.dump(department_data, f, indent=2)
            
            with open("data/timetables.json", "w") as f:
                json.dump(self.timetables, f, indent=2)
                
        except Exception as e:
            print(f"Error saving data: {e}")
    
    # Faculty methods
    def add_faculty(self, faculty: Faculty) -> str:
        """Add a new faculty member"""
        if not faculty.id:
            faculty.id = str(uuid.uuid4())
        self.faculty[faculty.id] = faculty
        self.save_data()
        return faculty.id
    
    def update_faculty(self, faculty: Faculty) -> bool:
        """Update an existing faculty member"""
        if faculty.id in self.faculty:
            self.faculty[faculty.id] = faculty
            self.save_data()
            return True
        return False
    
    def delete_faculty(self, faculty_id: str) -> bool:
        """Delete a faculty member by ID"""
        if faculty_id in self.faculty:
            del self.faculty[faculty_id]
            self.save_data()
            return True
        return False
    
    def get_faculty(self, faculty_id: str) -> Optional[Faculty]:
        """Get a faculty member by ID"""
        return self.faculty.get(faculty_id)
    
    def get_all_faculty(self) -> List[Faculty]:
        """Get all faculty members"""
        return list(self.faculty.values())
    
    # Classroom methods
    def add_classroom(self, classroom: Classroom) -> str:
        """Add a new classroom"""
        if not classroom.id:
            classroom.id = str(uuid.uuid4())
        self.classrooms[classroom.id] = classroom
        self.save_data()
        return classroom.id
    
    def update_classroom(self, classroom: Classroom) -> bool:
        """Update an existing classroom"""
        if classroom.id in self.classrooms:
            self.classrooms[classroom.id] = classroom
            self.save_data()
            return True
        return False
    
    def delete_classroom(self, classroom_id: str) -> bool:
        """Delete a classroom by ID"""
        if classroom_id in self.classrooms:
            del self.classrooms[classroom_id]
            self.save_data()
            return True
        return False
    
    def get_classroom(self, classroom_id: str) -> Optional[Classroom]:
        """Get a classroom by ID"""
        return self.classrooms.get(classroom_id)
    
    def get_all_classrooms(self) -> List[Classroom]:
        """Get all classrooms"""
        return list(self.classrooms.values())
    
    # Course methods
    def add_course(self, course: Course) -> str:
        """Add a new course"""
        if not course.id:
            course.id = str(uuid.uuid4())
        self.courses[course.id] = course
        self.save_data()
        return course.id
    
    def update_course(self, course: Course) -> bool:
        """Update an existing course"""
        if course.id in self.courses:
            self.courses[course.id] = course
            self.save_data()
            return True
        return False
    
    def delete_course(self, course_id: str) -> bool:
        """Delete a course by ID"""
        if course_id in self.courses:
            del self.courses[course_id]
            self.save_data()
            return True
        return False
    
    def get_course(self, course_id: str) -> Optional[Course]:
        """Get a course by ID"""
        return self.courses.get(course_id)
    
    def get_all_courses(self) -> List[Course]:
        """Get all courses"""
        return list(self.courses.values())
    
    # Department methods
    def add_department(self, department: Department) -> str:
        """Add a new department"""
        if not department.id:
            department.id = str(uuid.uuid4())
        self.departments[department.id] = department
        self.save_data()
        return department.id
    
    def update_department(self, department: Department) -> bool:
        """Update an existing department"""
        if department.id in self.departments:
            self.departments[department.id] = department
            self.save_data()
            return True
        return False
    
    def delete_department(self, department_id: str) -> bool:
        """Delete a department by ID"""
        if department_id in self.departments:
            del self.departments[department_id]
            self.save_data()
            return True
        return False
    
    def get_department(self, department_id: str) -> Optional[Department]:
        """Get a department by ID"""
        return self.departments.get(department_id)
    
    def get_all_departments(self) -> List[Department]:
        """Get all departments"""
        return list(self.departments.values())
    
    # Timetable methods
    def save_timetable(self, name: str, assignments: List[Assignment]) -> bool:
        """Save a generated timetable"""
        timetable_data = {
            "name": name,
            "generated_date": datetime.now().isoformat(),
            "assignments": [assignment.to_dict() for assignment in assignments]
        }
        self.timetables[name] = timetable_data
        self.save_data()
        return True
    
    def get_timetable(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a saved timetable by name"""
        return self.timetables.get(name)
    
    def get_all_timetables(self) -> Dict[str, Dict[str, Any]]:
        """Get all saved timetables"""
        return self.timetables
    
    def delete_timetable(self, name: str) -> bool:
        """Delete a timetable by name"""
        if name in self.timetables:
            del self.timetables[name]
            self.save_data()
            return True
        return False
    
    def export_timetable_to_csv(self, name: str, output_path: str) -> bool:
        """Export a timetable to CSV format"""
        timetable = self.get_timetable(name)
        if not timetable:
            return False
        
        assignments_data = []
        for assignment_dict in timetable["assignments"]:
            course_id = assignment_dict["course"]["id"]
            faculty_id = assignment_dict["faculty"]["id"]
            classroom_id = assignment_dict["classroom"]["id"]
            
            course = self.get_course(course_id) or Course.from_dict(assignment_dict["course"])
            faculty = self.get_faculty(faculty_id) or Faculty.from_dict(assignment_dict["faculty"])
            classroom = self.get_classroom(classroom_id) or Classroom.from_dict(assignment_dict["classroom"])
            time_slot = TimeSlot.from_dict(assignment_dict["time_slot"])
            
            assignments_data.append({
                "Day": time_slot.day,
                "Start Time": time_slot.start_time.strftime('%H:%M'),
                "End Time": time_slot.end_time.strftime('%H:%M'),
                "Course Code": course.code,
                "Course Name": course.name,
                "Faculty": faculty.name,
                "Classroom": classroom.name,
                "Building": classroom.building
            })
        
        df = pd.DataFrame(assignments_data)
        df.to_csv(output_path, index=False)
        return True
    
    def import_data_from_csv(self, entity_type: str, file_path: str) -> bool:
        """Import data from a CSV file"""
        try:
            df = pd.read_csv(file_path)
            
            if entity_type == "faculty":
                for _, row in df.iterrows():
                    faculty = Faculty(
                        id=str(uuid.uuid4()),
                        name=row["name"],
                        department=row["department"],
                        weekly_hours=int(row.get("weekly_hours", 20)),
                        expertise=row.get("expertise", "").split(",") if pd.notna(row.get("expertise")) else []
                    )
                    self.add_faculty(faculty)
            
            elif entity_type == "classrooms":
                for _, row in df.iterrows():
                    classroom = Classroom(
                        id=str(uuid.uuid4()),
                        name=row["name"],
                        capacity=int(row["capacity"]),
                        building=row["building"],
                        room_type=row["room_type"],
                        facilities=row.get("facilities", "").split(",") if pd.notna(row.get("facilities")) else []
                    )
                    self.add_classroom(classroom)
            
            elif entity_type == "courses":
                for _, row in df.iterrows():
                    course = Course(
                        id=str(uuid.uuid4()),
                        code=row["code"],
                        name=row["name"],
                        department=row["department"],
                        credits=int(row["credits"]),
                        hours_per_week=int(row["hours_per_week"]),
                        required_room_type=row.get("required_room_type", "Lecture"),
                        min_capacity=int(row.get("min_capacity", 10)),
                        required_facilities=row.get("required_facilities", "").split(",") if pd.notna(row.get("required_facilities")) else [],
                        faculty_requirements=row.get("faculty_requirements", "").split(",") if pd.notna(row.get("faculty_requirements")) else []
                    )
                    self.add_course(course)
            
            elif entity_type == "departments":
                for _, row in df.iterrows():
                    department = Department(
                        id=str(uuid.uuid4()),
                        name=row["name"],
                        code=row["code"]
                    )
                    self.add_department(department)
            
            self.save_data()
            return True
            
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
