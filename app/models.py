from sqlalchemy import Column, Integer, String, Date, Boolean, DECIMAL, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    teacher = relationship("Teacher", back_populates="user", uselist=False)
    student = relationship("Student", back_populates="user", uselist=False)


class Teacher(Base):
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="teacher")
    assignments = relationship("TeacherAssignment", back_populates="teacher")
    results = relationship("Result", back_populates="teacher")


class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    students = relationship("Student", back_populates="class_")
    assignments = relationship("TeacherAssignment", back_populates="class_")


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    admission_number = Column(String(50), unique=True, nullable=False)
    date_of_birth = Column(Date)
    gender = Column(String(10))
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="student")
    class_ = relationship("Class", back_populates="students")
    results = relationship("Result", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assignments = relationship("TeacherAssignment", back_populates="subject")
    results = relationship("Result", back_populates="subject")


class Term(Base):
    __tablename__ = "terms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    term_number = Column(Integer, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    assignments = relationship("TeacherAssignment", back_populates="term")
    results = relationship("Result", back_populates="term")


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    class_id = Column(Integer, ForeignKey("classes.id", ondelete="CASCADE"))
    term_id = Column(Integer, ForeignKey("terms.id", ondelete="CASCADE"))
    
    teacher = relationship("Teacher", back_populates="assignments")
    subject = relationship("Subject", back_populates="assignments")
    class_ = relationship("Class", back_populates="assignments")
    term = relationship("Term", back_populates="assignments")
    
    __table_args__ = (
        UniqueConstraint('teacher_id', 'subject_id', 'class_id', 'term_id'),
    )


class Result(Base):
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"))
    term_id = Column(Integer, ForeignKey("terms.id", ondelete="CASCADE"))
    marks = Column(DECIMAL(5, 2), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("Student", back_populates="results")
    subject = relationship("Subject", back_populates="results")
    term = relationship("Term", back_populates="results")
    teacher = relationship("Teacher", back_populates="results")
    
    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', 'term_id'),
    )