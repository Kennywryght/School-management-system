from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Teacher, TeacherAssignment, Class, Subject, Term, Student, Result
from app.auth import get_current_user, require_role
from app.schemas import TeacherAssignmentResponse, ResultCreate, ResultUpdate, ResultResponse, BulkResultCreate

router = APIRouter(prefix="/api/teacher", tags=["Teacher"])


# ============= VIEW ASSIGNMENTS =============

@router.get("/my-assignments", response_model=List[TeacherAssignmentResponse])
def get_my_assignments(
    term_id: int = None,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Get assignments for the logged-in teacher"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Query assignments
    query = db.query(TeacherAssignment).filter(TeacherAssignment.teacher_id == teacher.id)
    
    # Filter by term if provided, otherwise get active term assignments
    if term_id:
        query = query.filter(TeacherAssignment.term_id == term_id)
    else:
        # Get active term
        active_term = db.query(Term).filter(Term.is_active == True).first()
        if active_term:
            query = query.filter(TeacherAssignment.term_id == active_term.id)
    
    assignments = query.all()
    
    # Build response
    response = []
    for assignment in assignments:
        subject = db.query(Subject).filter(Subject.id == assignment.subject_id).first()
        class_obj = db.query(Class).filter(Class.id == assignment.class_id).first()
        term = db.query(Term).filter(Term.id == assignment.term_id).first()
        
        # Skip assignments with missing related records
        if not subject or not class_obj or not term:
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
@router.get("/classes/{class_id}/students", response_model=List[dict])
def get_students_in_class(
    class_id: int,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Get all students in a specific class (for teachers to see who they teach)"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Verify teacher is assigned to this class
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.class_id == class_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to teach this class"
        )
    
    # Get students in this class
    students = db.query(Student).filter(Student.class_id == class_id).all()
    
    # Build response
    response = []
    for student in students:
        response.append({
            "id": student.id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "admission_number": student.admission_number,
            "email": student.user.email
        })
    
    return response

# ============= UPLOAD RESULTS =============

@router.post("/results", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
def upload_result(
    result_data: ResultCreate,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Upload a single result for a student"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Verify student exists
    student = db.query(Student).filter(Student.id == result_data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {result_data.student_id} not found"
        )
    
    # Verify subject exists
    subject = db.query(Subject).filter(Subject.id == result_data.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with ID {result_data.subject_id} not found"
        )
    
    # Verify term exists
    term = db.query(Term).filter(Term.id == result_data.term_id).first()
    if not term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Term with ID {result_data.term_id} not found"
        )
    
    # Verify teacher is assigned to teach this subject to this student's class
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.subject_id == result_data.subject_id,
        TeacherAssignment.class_id == student.class_id,
        TeacherAssignment.term_id == result_data.term_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to teach this subject to this student's class"
        )
    
    # Validate marks
    if result_data.marks < 0 or result_data.marks > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Marks must be between 0 and 100"
        )
    
    # Check if result already exists
    existing_result = db.query(Result).filter(
        Result.student_id == result_data.student_id,
        Result.subject_id == result_data.subject_id,
        Result.term_id == result_data.term_id
    ).first()
    
    if existing_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Result already exists for this student, subject, and term. Use PUT to update."
        )
    
    # Create result
    new_result = Result(
        student_id=result_data.student_id,
        subject_id=result_data.subject_id,
        term_id=result_data.term_id,
        marks=result_data.marks,
        teacher_id=teacher.id
    )
    db.add(new_result)
    db.commit()
    db.refresh(new_result)
    
    # Build response
    response = ResultResponse(
        id=new_result.id,
        student_id=new_result.student_id,
        subject_id=new_result.subject_id,
        term_id=new_result.term_id,
        marks=new_result.marks,
        teacher_id=new_result.teacher_id,
        student_name=f"{student.first_name} {student.last_name}",
        subject_name=subject.name,
        term_name=term.name,
        uploaded_at=new_result.uploaded_at
    )
    
    return response


@router.post("/results/bulk", status_code=status.HTTP_201_CREATED)
def upload_bulk_results(
    bulk_data: BulkResultCreate,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Upload multiple results at once (e.g., for entire class)"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Verify teacher is assigned to teach this subject to this class
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher.id,
        TeacherAssignment.subject_id == bulk_data.subject_id,
        TeacherAssignment.class_id == bulk_data.class_id,
        TeacherAssignment.term_id == bulk_data.term_id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to teach this subject to this class"
        )
    
    # Process each result
    created_count = 0
    updated_count = 0
    errors = []
    
    for result_item in bulk_data.results:
        try:
            student_id = result_item.get("student_id")
            marks = result_item.get("marks")
            
            # Validate
            if not student_id or marks is None:
                errors.append(f"Missing student_id or marks in result item")
                continue
            
            if marks < 0 or marks > 100:
                errors.append(f"Student {student_id}: Marks must be between 0 and 100")
                continue
            
            # Check if result exists
            existing_result = db.query(Result).filter(
                Result.student_id == student_id,
                Result.subject_id == bulk_data.subject_id,
                Result.term_id == bulk_data.term_id
            ).first()
            
            if existing_result:
                # Update existing result
                existing_result.marks = marks
                existing_result.teacher_id = teacher.id
                updated_count += 1
            else:
                # Create new result
                new_result = Result(
                    student_id=student_id,
                    subject_id=bulk_data.subject_id,
                    term_id=bulk_data.term_id,
                    marks=marks,
                    teacher_id=teacher.id
                )
                db.add(new_result)
                created_count += 1
        
        except Exception as e:
            errors.append(f"Error processing student {student_id}: {str(e)}")
    
    db.commit()
    
    return {
        "message": "Bulk upload completed",
        "created": created_count,
        "updated": updated_count,
        "errors": errors
    }


@router.get("/results", response_model=List[ResultResponse])
def get_my_results(
    class_id: int = None,
    subject_id: int = None,
    term_id: int = None,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Get results uploaded by the logged-in teacher"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Query results
    query = db.query(Result).filter(Result.teacher_id == teacher.id)
    
    if subject_id:
        query = query.filter(Result.subject_id == subject_id)
    if term_id:
        query = query.filter(Result.term_id == term_id)
    
    results = query.all()
    
    # Filter by class if provided
    if class_id:
        results = [r for r in results if r.student.class_id == class_id]
    
    # Build response
    response = []
    for result in results:
        student = db.query(Student).filter(Student.id == result.student_id).first()
        subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
        term = db.query(Term).filter(Term.id == result.term_id).first()
        
        response.append(ResultResponse(
            id=result.id,
            student_id=result.student_id,
            subject_id=result.subject_id,
            term_id=result.term_id,
            marks=result.marks,
            teacher_id=result.teacher_id,
            student_name=f"{student.first_name} {student.last_name}" if student else "Unknown",
            subject_name=subject.name if subject else "Unknown",
            term_name=term.name if term else "Unknown",
            uploaded_at=result.uploaded_at
        ))
    
    return response


@router.put("/results/{result_id}", response_model=ResultResponse)
def update_result(
    result_id: int,
    result_data: ResultUpdate,
    current_user: User = Depends(require_role("teacher")),
    db: Session = Depends(get_db)
):
    """Update a result (change marks)"""
    # Get teacher record
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Get result
    result = db.query(Result).filter(Result.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with ID {result_id} not found"
        )
    
    # Verify teacher owns this result
    if result.teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update results you uploaded"
        )
    
    # Validate marks
    if result_data.marks < 0 or result_data.marks > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Marks must be between 0 and 100"
        )
    
    # Update marks
    result.marks = result_data.marks
    db.commit()
    db.refresh(result)
    
    # Build response
    student = db.query(Student).filter(Student.id == result.student_id).first()
    subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
    term = db.query(Term).filter(Term.id == result.term_id).first()
    
    response = ResultResponse(
        id=result.id,
        student_id=result.student_id,
        subject_id=result.subject_id,
        term_id=result.term_id,
        marks=result.marks,
        teacher_id=result.teacher_id,
        student_name=f"{student.first_name} {student.last_name}",
        subject_name=subject.name,
        term_name=term.name,
        uploaded_at=result.uploaded_at
    )
    
    return response