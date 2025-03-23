import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, time

@dataclass(frozen=True)
class TimeSlot:
    day: str  # Monday, Tuesday, etc.
    start_time: time
    end_time: time
    
    def __str__(self):
        return f"{self.day} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    def __hash__(self):
        return hash((self.day, self.start_time.strftime('%H:%M'), self.end_time.strftime('%H:%M')))
    
    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return (self.day == other.day and 
                self.start_time == other.start_time and 
                self.end_time == other.end_time)
    
    def overlaps(self, other):
        """Check if this timeslot overlaps with another one"""
        if self.day != other.day:
            return False
        return (self.start_time < other.end_time and 
                other.start_time < self.end_time)
    
    def to_dict(self):
        return {
            "day": self.day,
            "start_time": self.start_time.strftime('%H:%M'),
            "end_time": self.end_time.strftime('%H:%M')
        }
    
    @staticmethod
    def from_dict(data):
        return TimeSlot(
            day=data["day"],
            start_time=datetime.strptime(data["start_time"], '%H:%M').time(),
            end_time=datetime.strptime(data["end_time"], '%H:%M').time()
        )

@dataclass
class Faculty:
    id: str
    name: str
    department: str
    weekly_hours: int = 20
    expertise: List[str] = field(default_factory=list)
    unavailable_slots: List[TimeSlot] = field(default_factory=list)
    preferred_slots: List[TimeSlot] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "department": self.department,
            "weekly_hours": self.weekly_hours,
            "expertise": self.expertise,
            "unavailable_slots": [slot.to_dict() for slot in self.unavailable_slots],
            "preferred_slots": [slot.to_dict() for slot in self.preferred_slots]
        }
    
    @staticmethod
    def from_dict(data):
        return Faculty(
            id=data["id"],
            name=data["name"],
            department=data["department"],
            weekly_hours=data["weekly_hours"],
            expertise=data["expertise"],
            unavailable_slots=[TimeSlot.from_dict(slot) for slot in data.get("unavailable_slots", [])],
            preferred_slots=[TimeSlot.from_dict(slot) for slot in data.get("preferred_slots", [])]
        )

@dataclass
class Classroom:
    id: str
    name: str
    capacity: int
    building: str
    room_type: str  # Lecture, Lab, Seminar, etc.
    facilities: List[str] = field(default_factory=list)
    unavailable_slots: List[TimeSlot] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "building": self.building,
            "room_type": self.room_type,
            "facilities": self.facilities,
            "unavailable_slots": [slot.to_dict() for slot in self.unavailable_slots]
        }
    
    @staticmethod
    def from_dict(data):
        return Classroom(
            id=data["id"],
            name=data["name"],
            capacity=data["capacity"],
            building=data["building"],
            room_type=data["room_type"],
            facilities=data["facilities"],
            unavailable_slots=[TimeSlot.from_dict(slot) for slot in data.get("unavailable_slots", [])]
        )

@dataclass
class Department:
    id: str
    name: str
    code: str
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
        }
    
    @staticmethod
    def from_dict(data):
        return Department(
            id=data["id"],
            name=data["name"],
            code=data["code"]
        )

@dataclass
class Course:
    id: str
    code: str
    name: str
    department: str
    credits: int
    hours_per_week: int
    required_room_type: str = "Lecture"
    required_facilities: List[str] = field(default_factory=list)
    min_capacity: int = 10
    faculty_requirements: List[str] = field(default_factory=list)  # faculty expertise required
    
    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "department": self.department,
            "credits": self.credits,
            "hours_per_week": self.hours_per_week,
            "required_room_type": self.required_room_type,
            "required_facilities": self.required_facilities,
            "min_capacity": self.min_capacity,
            "faculty_requirements": self.faculty_requirements
        }
    
    @staticmethod
    def from_dict(data):
        return Course(
            id=data["id"],
            code=data["code"],
            name=data["name"],
            department=data["department"],
            credits=data["credits"],
            hours_per_week=data["hours_per_week"],
            required_room_type=data.get("required_room_type", "Lecture"),
            required_facilities=data.get("required_facilities", []),
            min_capacity=data.get("min_capacity", 10),
            faculty_requirements=data.get("faculty_requirements", [])
        )

@dataclass
class Assignment:
    course: Course
    faculty: Faculty
    classroom: Classroom
    time_slot: TimeSlot
    
    def to_dict(self):
        return {
            "course": self.course.to_dict(),
            "faculty": self.faculty.to_dict(),
            "classroom": self.classroom.to_dict(),
            "time_slot": self.time_slot.to_dict()
        }
    
    @staticmethod
    def from_dict(data, course_dict, faculty_dict, classroom_dict):
        course = course_dict.get(data["course"]["id"]) or Course.from_dict(data["course"])
        faculty = faculty_dict.get(data["faculty"]["id"]) or Faculty.from_dict(data["faculty"])
        classroom = classroom_dict.get(data["classroom"]["id"]) or Classroom.from_dict(data["classroom"])
        time_slot = TimeSlot.from_dict(data["time_slot"])
        
        return Assignment(
            course=course,
            faculty=faculty,
            classroom=classroom,
            time_slot=time_slot
        )
