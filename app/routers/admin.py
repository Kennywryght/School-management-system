from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Class, Subject, Term, Teacher, Student, TeacherAssignment
from app.auth import get_current_user, require_role, get_password_hash
from app.schemas import UserResponse, ClassCreate, ClassUpdate, ClassResponse, SubjectCreate ,SubjectUpdate,SubjectResponse, TermCreate, TermUpdate, TermResponse, TeacherCreate, TeacherUpdate, TeacherResponse, StudentCreate, StudentUpdate, StudentResponse, TeacherAssignmentCreate, TeacherAssignmentResponse

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ============= DASHBOARD =============
@router.get("/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):
    return {
        "message": f"Welcome to admin dashboard, {current_user.email}!",
        "role": current_user.role
    }


@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return users


# ============= CLASSES MANAGEMENT =============

@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new class"""
    # Check if class already exists
    existing_class = db.query(Class).filter(Class.name == class_data.name).first()
    if existing_class:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Class '{class_data.name}' already exists"
        )
    
    new_class = Class(
        name=class_data.name,
        level=class_data.level
    )
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    
    return new_class


@router.get("/classes", response_model=List[ClassResponse])
def get_all_classes(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all classes"""
    classes = db.query(Class).order_by(Class.level).all()
    return classes


@router.get("/classes/{class_id}", response_model=ClassResponse)
def get_class(
    class_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific class by ID"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {class_id} not found"
        )
    return class_obj


@router.put("/classes/{class_id}", response_model=ClassResponse)
def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update a class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {class_id} not found"
        )
    
    # Update fields if provided
    if class_data.name is not None:
        class_obj.name = class_data.name
    if class_data.level is not None:
        class_obj.level = class_data.level
    
    db.commit()
    db.refresh(class_obj)
    
    return class_obj


@router.delete("/classes/{class_id}")
def delete_class(
    class_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a class"""
    class_obj = db.query(Class).filter(Class.id == class_id).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {class_id} not found"
        )
    
    db.delete(class_obj)
    db.commit()
    
    return {"message": f"Class '{class_obj.name}' deleted successfully"}


# subject management 
@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    subject_data: SubjectCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new subject"""
    # Check if subject already exists
    existing_subject = db.query(Subject).filter(Subject.name == subject_data.name).first()
    if existing_subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Subject '{subject_data.name}' already exists"
        )
    
    # Check if code already exists (if provided)
    if subject_data.code:
        existing_code = db.query(Subject).filter(Subject.code == subject_data.code).first()
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Subject code '{subject_data.code}' already exists"
            )
    
    new_subject = Subject(
        name=subject_data.name,
        code=subject_data.code
    )
    db.add(new_subject)
    db.commit()
    db.refresh(new_subject)
    
    return new_subject


@router.get("/subjects", response_model=List[SubjectResponse])
def get_all_subjects(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all subjects"""
    subjects = db.query(Subject).order_by(Subject.name).all()
    return subjects


@router.get("/subjects/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific subject by ID"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    return subject


@router.put("/subjects/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update a subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    
    # Update fields if provided
    if subject_data.name is not None:
        subject.name = subject_data.name
    if subject_data.code is not None:
        subject.code = subject_data.code
    
    db.commit()
    db.refresh(subject)
    
    return subject


@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a subject"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {subject_id} not found"
        )
    
    db.delete(subject)
    db.commit()
    
    return {"message": f"Subject '{subject.name}' deleted successfully"}

# TERMS MANAGEMENT
@router.post("/terms", response_model=TermResponse, status_code=status.HTTP_201_CREATED)
def create_term(
    term_data: TermCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new term"""
    # Check if term already exists
    existing_term = db.query(Term).filter(
        Term.year == term_data.year,
        Term.term_number == term_data.term_number
    ).first()
    
    if existing_term:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Term {term_data.term_number} for year {term_data.year} already exists"
        )
    
    # If setting this term as active, deactivate all other terms
    if term_data.is_active:
        db.query(Term).update({Term.is_active: False})
    
    new_term = Term(
        name=term_data.name,
        year=term_data.year,
        term_number=term_data.term_number,
        start_date=term_data.start_date,
        end_date=term_data.end_date,
        is_active=term_data.is_active
    )
    db.add(new_term)
    db.commit()
    db.refresh(new_term)
    
    return new_term


@router.get("/terms", response_model=List[TermResponse])
def get_all_terms(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all terms"""
    terms = db.query(Term).order_by(Term.year.desc(), Term.term_number.desc()).all()
    return terms


@router.get("/terms/active", response_model=TermResponse)
def get_active_term(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get the currently active term"""
    term = db.query(Term).filter(Term.is_active == True).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active term found"
        )
    return term


@router.get("/terms/{term_id}", response_model=TermResponse)
def get_term(
    term_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific term by ID"""
    term = db.query(Term).filter(Term.id == term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {term_id} not found"
        )
    return term


@router.put("/terms/{term_id}", response_model=TermResponse)
def update_term(
    term_id: int,
    term_data: TermUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update a term"""
    term = db.query(Term).filter(Term.id == term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {term_id} not found"
        )
    
    # If setting this term as active, deactivate all other terms
    if term_data.is_active is True:
        db.query(Term).update({Term.is_active: False})
    
    # Update fields if provided
    if term_data.name is not None:
        term.name = term_data.name
    if term_data.year is not None:
        term.year = term_data.year
    if term_data.term_number is not None:
        term.term_number = term_data.term_number
    if term_data.start_date is not None:
        term.start_date = term_data.start_date
    if term_data.end_date is not None:
        term.end_date = term_data.end_date
    if term_data.is_active is not None:
        term.is_active = term_data.is_active
    
    db.commit()
    db.refresh(term)
    
    return term


@router.put("/terms/{term_id}/activate")
def activate_term(
    term_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Activate a term (deactivates all others)"""
    term = db.query(Term).filter(Term.id == term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {term_id} not found"
        )
    
    # Deactivate all terms
    db.query(Term).update({Term.is_active: False})
    
    # Activate this term
    term.is_active = True
    db.commit()
    db.refresh(term)
    
    return {"message": f"Term '{term.name}' is now active"}


@router.delete("/terms/{term_id}")
def delete_term(
    term_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a term"""
    term = db.query(Term).filter(Term.id == term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {term_id} not found"
        )
    
    db.delete(term)
    db.commit()
    
    return {"message": f"Term '{term.name}' deleted successfully"}

# ============= TEACHERS MANAGEMENT =============

@router.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new teacher (creates user account and teacher profile)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{teacher_data.email}' is already registered"
        )
    
    # Create user account
    hashed_password = get_password_hash(teacher_data.password)
    new_user = User(
        email=teacher_data.email,
        password_hash=hashed_password,
        role="teacher"
    )
    db.add(new_user)
    db.flush()  # Get the user ID without committing
    
    # Create teacher profile
    new_teacher = Teacher(
        user_id=new_user.id,
        first_name=teacher_data.first_name,
        last_name=teacher_data.last_name,
        phone=teacher_data.phone
    )
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    
    # Add email to response
    response = TeacherResponse(
        id=new_teacher.id,
        user_id=new_teacher.user_id,
        first_name=new_teacher.first_name,
        last_name=new_teacher.last_name,
        phone=new_teacher.phone,
        email=new_user.email,
        created_at=new_teacher.created_at
    )
    
    return response


@router.get("/teachers", response_model=List[TeacherResponse])
def get_all_teachers(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all teachers"""
    teachers = db.query(Teacher).join(User).all()
    
    # Build response with email from user
    response = []
    for teacher in teachers:
        response.append(TeacherResponse(
            id=teacher.id,
            user_id=teacher.user_id,
            first_name=teacher.first_name,
            last_name=teacher.last_name,
            phone=teacher.phone,
            email=teacher.user.email,
            created_at=teacher.created_at
        ))
    
    return response


@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific teacher by ID"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found"
        )
    
    response = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        phone=teacher.phone,
        email=teacher.user.email,
        created_at=teacher.created_at
    )
    
    return response


@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update a teacher"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found"
        )
    
    # Update fields if provided
    if teacher_data.first_name is not None:
        teacher.first_name = teacher_data.first_name
    if teacher_data.last_name is not None:
        teacher.last_name = teacher_data.last_name
    if teacher_data.phone is not None:
        teacher.phone = teacher_data.phone
    
    db.commit()
    db.refresh(teacher)
    
    response = TeacherResponse(
        id=teacher.id,
        user_id=teacher.user_id,
        first_name=teacher.first_name,
        last_name=teacher.last_name,
        phone=teacher.phone,
        email=teacher.user.email,
        created_at=teacher.created_at
    )
    
    return response


@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a teacher (also deletes their user account)"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found"
        )
    
    teacher_name = f"{teacher.first_name} {teacher.last_name}"
    
    # Delete teacher (user will be deleted automatically due to CASCADE)
    db.delete(teacher)
    db.commit()
    
    return {"message": f"Teacher '{teacher_name}' deleted successfully"}

# ============= STUDENTS MANAGEMENT =============

@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create a new student (creates user account and student profile)"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == student_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email '{student_data.email}' is already registered"
        )
    
    # Check if admission number already exists
    existing_admission = db.query(Student).filter(
        Student.admission_number == student_data.admission_number
    ).first()
    if existing_admission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Admission number '{student_data.admission_number}' already exists"
        )
    
    # Check if class exists (if provided)
    if student_data.class_id:
        class_exists = db.query(Class).filter(Class.id == student_data.class_id).first()
        if not class_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID {student_data.class_id} not found"
            )
    
    # Create user account
    hashed_password = get_password_hash(student_data.password)
    new_user = User(
        email=student_data.email,
        password_hash=hashed_password,
        role="student"
    )
    db.add(new_user)
    db.flush()
    
    # Create student profile
    new_student = Student(
        user_id=new_user.id,
        first_name=student_data.first_name,
        last_name=student_data.last_name,
        admission_number=student_data.admission_number,
        date_of_birth=student_data.date_of_birth,
        gender=student_data.gender,
        class_id=student_data.class_id
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    # Build response
    class_name = None
    if new_student.class_id:
        class_obj = db.query(Class).filter(Class.id == new_student.class_id).first()
        class_name = class_obj.name if class_obj else None
    
    response = StudentResponse(
        id=new_student.id,
        user_id=new_student.user_id,
        first_name=new_student.first_name,
        last_name=new_student.last_name,
        admission_number=new_student.admission_number,
        date_of_birth=new_student.date_of_birth,
        gender=new_student.gender,
        class_id=new_student.class_id,
        email=new_user.email,
        class_name=class_name,
        created_at=new_student.created_at
    )
    
    return response


@router.get("/students", response_model=List[StudentResponse])
def get_all_students(
    class_id: int = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all students, optionally filter by class"""
    query = db.query(Student).join(User)
    
    if class_id:
        query = query.filter(Student.class_id == class_id)
    
    students = query.all()
    
    # Build response
    response = []
    for student in students:
        class_name = None
        if student.class_id:
            class_obj = db.query(Class).filter(Class.id == student.class_id).first()
            class_name = class_obj.name if class_obj else None
        
        response.append(StudentResponse(
            id=student.id,
            user_id=student.user_id,
            first_name=student.first_name,
            last_name=student.last_name,
            admission_number=student.admission_number,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            class_id=student.class_id,
            email=student.user.email,
            class_name=class_name,
            created_at=student.created_at
        ))
    
    return response


@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    class_name = None
    if student.class_id:
        class_obj = db.query(Class).filter(Class.id == student.class_id).first()
        class_name = class_obj.name if class_obj else None
    
    response = StudentResponse(
        id=student.id,
        user_id=student.user_id,
        first_name=student.first_name,
        last_name=student.last_name,
        admission_number=student.admission_number,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        class_id=student.class_id,
        email=student.user.email,
        class_name=class_name,
        created_at=student.created_at
    )
    
    return response


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    # Check if new class exists (if provided)
    if student_data.class_id:
        class_exists = db.query(Class).filter(Class.id == student_data.class_id).first()
        if not class_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class with ID {student_data.class_id} not found"
            )
    
    # Update fields if provided
    if student_data.first_name is not None:
        student.first_name = student_data.first_name
    if student_data.last_name is not None:
        student.last_name = student_data.last_name
    if student_data.admission_number is not None:
        student.admission_number = student_data.admission_number
    if student_data.date_of_birth is not None:
        student.date_of_birth = student_data.date_of_birth
    if student_data.gender is not None:
        student.gender = student_data.gender
    if student_data.class_id is not None:
        student.class_id = student_data.class_id
    
    db.commit()
    db.refresh(student)
    
    class_name = None
    if student.class_id:
        class_obj = db.query(Class).filter(Class.id == student.class_id).first()
        class_name = class_obj.name if class_obj else None
    
    response = StudentResponse(
        id=student.id,
        user_id=student.user_id,
        first_name=student.first_name,
        last_name=student.last_name,
        admission_number=student.admission_number,
        date_of_birth=student.date_of_birth,
        gender=student.gender,
        class_id=student.class_id,
        email=student.user.email,
        class_name=class_name,
        created_at=student.created_at
    )
    
    return response


@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a student (also deletes their user account)"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )
    
    student_name = f"{student.first_name} {student.last_name}"
    
    # Delete student (user will be deleted automatically due to CASCADE)
    db.delete(student)
    db.commit()
    
    return {"message": f"Student '{student_name}' deleted successfully"}

# ============= TEACHER ASSIGNMENTS MANAGEMENT =============

@router.post("/assignments", response_model=TeacherAssignmentResponse, status_code=status.HTTP_201_CREATED)
def create_assignment(
    assignment_data: TeacherAssignmentCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Assign a teacher to teach a subject in a class for a term"""
    # Verify teacher exists
    teacher = db.query(Teacher).filter(Teacher.id == assignment_data.teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {assignment_data.teacher_id} not found"
        )
    
    # Verify subject exists
    subject = db.query(Subject).filter(Subject.id == assignment_data.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {assignment_data.subject_id} not found"
        )
    
    # Verify class exists
    class_obj = db.query(Class).filter(Class.id == assignment_data.class_id).first()
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with ID {assignment_data.class_id} not found"
        )
    
    # Verify term exists
    term = db.query(Term).filter(Term.id == assignment_data.term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {assignment_data.term_id} not found"
        )
    
    # Check if assignment already exists
    existing_assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == assignment_data.teacher_id,
        TeacherAssignment.subject_id == assignment_data.subject_id,
        TeacherAssignment.class_id == assignment_data.class_id,
        TeacherAssignment.term_id == assignment_data.term_id
    ).first()
    
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This assignment already exists"
        )
    
    # Create assignment
    new_assignment = TeacherAssignment(
        teacher_id=assignment_data.teacher_id,
        subject_id=assignment_data.subject_id,
        class_id=assignment_data.class_id,
        term_id=assignment_data.term_id
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    # Build response with names
    response = TeacherAssignmentResponse(
        id=new_assignment.id,
        teacher_id=new_assignment.teacher_id,
        subject_id=new_assignment.subject_id,
        class_id=new_assignment.class_id,
        term_id=new_assignment.term_id,
        teacher_name=f"{teacher.first_name} {teacher.last_name}",
        subject_name=subject.name,
        class_name=class_obj.name,
        term_name=term.name
    )
    
    return response


@router.get("/assignments", response_model=List[TeacherAssignmentResponse])
def get_all_assignments(
    teacher_id: Optional[int] = None,
    class_id: Optional[int] = None,
    term_id: Optional[int] = None,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get all assignments, with optional filters"""
    query = db.query(TeacherAssignment)
    
    if teacher_id:
        query = query.filter(TeacherAssignment.teacher_id == teacher_id)
    if class_id:
        query = query.filter(TeacherAssignment.class_id == class_id)
    if term_id:
        query = query.filter(TeacherAssignment.term_id == term_id)
    
    assignments = query.all()
    
    # Build response with names
    response = []
    for assignment in assignments:
        # Safely get related records
        teacher = db.query(Teacher).filter(Teacher.id == assignment.teacher_id).first()
        subject = db.query(Subject).filter(Subject.id == assignment.subject_id).first()
        class_obj = db.query(Class).filter(Class.id == assignment.class_id).first()
        term = db.query(Term).filter(Term.id == assignment.term_id).first()
        
        # Skip this assignment if any related record is missing
        if not teacher or not subject or not class_obj or not term:
            continue
        
        response.append(TeacherAssignmentResponse(
            id=assignment.id,
            teacher_id=assignment.teacher_id,
            subject_id=assignment.subject_id,
            class_id=assignment.class_id,
            term_id=assignment.term_id,
            teacher_name=f"{teacher.first_name} {teacher.last_name}",
            subject_name=subject.name,
            class_name=class_obj.name,
            term_name=term.name
        ))
    
    return response

@router.get("/assignments/{assignment_id}", response_model=TeacherAssignmentResponse)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get a specific assignment by ID"""
    assignment = db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {assignment_id} not found"
        )
    
    teacher = db.query(Teacher).filter(Teacher.id == assignment.teacher_id).first()
    subject = db.query(Subject).filter(Subject.id == assignment.subject_id).first()
    class_obj = db.query(Class).filter(Class.id == assignment.class_id).first()
    term = db.query(Term).filter(Term.id == assignment.term_id).first()
    
    response = TeacherAssignmentResponse(
        id=assignment.id,
        teacher_id=assignment.teacher_id,
        subject_id=assignment.subject_id,
        class_id=assignment.class_id,
        term_id=assignment.term_id,
        teacher_name=f"{teacher.first_name} {teacher.last_name}" if teacher else "Unknown",
        subject_name=subject.name if subject else "Unknown",
        class_name=class_obj.name if class_obj else "Unknown",
        term_name=term.name if term else "Unknown"
    )
    
    return response


@router.delete("/assignments/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete a teacher assignment"""
    assignment = db.query(TeacherAssignment).filter(TeacherAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID {assignment_id} not found"
        )
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Assignment deleted successfully"}