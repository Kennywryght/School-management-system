from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    role: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    
# Class schemas
class ClassBase(BaseModel):
    name: str
    level: int
    
class ClassCreate(ClassBase):
    pass

class ClassUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
class ClassResponse(ClassBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
class SubjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    
class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    
class SubjectResponse(SubjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class TermBase(BaseModel):
    name: str
    year: int
    term_number: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool= False
    
class TermCreate(TermBase):
    pass
class TermUpdate(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    term_number: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    
class TermResponse(TermBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class TeacherBase(BaseModel):
    first_name: str 
    last_name: str
    phone: Optional[str] = None
    
class TeacherCreate(TeacherBase):
    email: EmailStr
    password: str
    
class TeacherUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
class TeacherResponse(TeacherBase):
    id: int
    email: EmailStr
    created_at: datetime
    
    class Config:
        from_attributes = True
    
# STUDENT SCHEMAS
class StudentBase(BaseModel):
    first_name: str
    last_name: str
    admission_number: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_id: Optional[int] = None
    
class StudentCreate(StudentBase):
    email: EmailStr
    password: str
    
class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    admission_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    class_id: Optional[int] = None
    
class StudentResponse(StudentBase):
    id: int
    user_id: int
    email: EmailStr
    class_name:Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        
class TeacherAssignmentBase(BaseModel):
    teacher_id: int
    subject_id: int
    class_id: int
    term_id: int
    
class TeacherAssignmentCreate(TeacherAssignmentBase):
    pass

class TeacherAssignmentResponse(TeacherAssignmentBase):
    id: int
    teacher_name: str
    subject_name: str
    class_name: str
    term_name: str
    
    class Config:
        from_attributes = True
        
class ResultBase(BaseModel):
    student_id: int
    subject_id: int
    term_id: int
    marks: float
    
class ResultCreate(ResultBase):
    pass

class ResultUpdate(BaseModel):
    marks: float
    
class ResultResponse(ResultBase):
    id: int
    teacher_id: Optional[int] = None
    student_name: str
    subject_name: str
    term_name: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True
        
class BulkResultCreate(BaseModel):
    """""Schema for bulk result upload/ multiple results at once"""""
    subject_id: int
    term_id: int
    class_id: int
    results: list[dict] # list of {studen_id: int, marks: float}
    