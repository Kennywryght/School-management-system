from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import User, Student, Result, Subject, Term, Class
from app.auth import get_current_user, require_role
from app.schemas import ResultResponse

router = APIRouter(prefix="/api/student", tags=["Student"])


# ============= VIEW RESULTS =============

@router.get("/results", response_model=List[ResultResponse])
def get_my_results(
    term_id: Optional[int] = None,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    """Get results for the logged-in student"""
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Query results
    query = db.query(Result).filter(Result.student_id == student.id)
    
    # Filter by term if provided, otherwise get active term results
    if term_id:
        query = query.filter(Result.term_id == term_id)
    else:
        # Get active term
        active_term = db.query(Term).filter(Term.is_active == True).first()
        if active_term:
            query = query.filter(Result.term_id == active_term.id)
    
    results = query.all()
    
    # Build response
    response = []
    for result in results:
        subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
        term = db.query(Term).filter(Term.id == result.term_id).first()
        
        response.append(ResultResponse(
            id=result.id,
            student_id=result.student_id,
            subject_id=result.subject_id,
            term_id=result.term_id,
            marks=result.marks,
            teacher_id=result.teacher_id,
            student_name=f"{student.first_name} {student.last_name}",
            subject_name=subject.name if subject else "Unknown",
            term_name=term.name if term else "Unknown",
            uploaded_at=result.uploaded_at
        ))
    
    return response


@router.get("/results/summary")
def get_results_summary(
    term_id: Optional[int] = None,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    """Get results summary with total marks, average, and position in class"""
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    if not student.class_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is not assigned to any class"
        )
    
    # Determine which term to use
    if term_id:
        term = db.query(Term).filter(Term.id == term_id).first()
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Term with ID {term_id} not found"
            )
    else:
        # Get active term
        term = db.query(Term).filter(Term.is_active == True).first()
        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active term found"
            )
    
    # Get student's results for this term
    student_results = db.query(Result).filter(
        Result.student_id == student.id,
        Result.term_id == term.id
    ).all()
    
    if not student_results:
        return {
            "student_id": student.id,
            "student_name": f"{student.first_name} {student.last_name}",
            "class_name": student.class_.name if student.class_ else "Unknown",
            "term_name": term.name,
            "results": [],
            "total_marks": 0,
            "average_marks": 0,
            "position": None,
            "total_students": 0,
            "message": "No results uploaded yet for this term"
        }
    
    # Calculate student's total
    student_total = sum([r.marks for r in student_results])
    student_average = student_total / len(student_results)
    
    # Get all students in the same class
    classmates = db.query(Student).filter(Student.class_id == student.class_id).all()
    
    # Calculate totals for all students in class
    student_totals = []
    for classmate in classmates:
        classmate_results = db.query(Result).filter(
            Result.student_id == classmate.id,
            Result.term_id == term.id
        ).all()
        
        if classmate_results:
            total = sum([r.marks for r in classmate_results])
            student_totals.append({
                "student_id": classmate.id,
                "total": total
            })
    
    # Sort by total marks (descending)
    student_totals.sort(key=lambda x: x["total"], reverse=True)
    
    # Find position
    position = None
    for idx, st in enumerate(student_totals, start=1):
        if st["student_id"] == student.id:
            position = idx
            break
    
    # Build detailed results
    detailed_results = []
    for result in student_results:
        subject = db.query(Subject).filter(Subject.id == result.subject_id).first()
        detailed_results.append({
            "subject_id": result.subject_id,
            "subject_name": subject.name if subject else "Unknown",
            "marks": float(result.marks),
            "grade": get_grade(float(result.marks))
        })
    
    return {
        "student_id": student.id,
        "student_name": f"{student.first_name} {student.last_name}",
        "admission_number": student.admission_number,
        "class_name": student.class_.name if student.class_ else "Unknown",
        "term_name": term.name,
        "results": detailed_results,
        "total_marks": float(student_total),
        "average_marks": round(student_average, 2),
        "position": position,
        "total_students": len(student_totals)
    }


def get_grade(marks: float) -> str:
    """Convert marks to grade"""
    if marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"


@router.get("/profile")
def get_my_profile(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db)
):
    """Get student's own profile information"""
    # Get student record
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    class_name = None
    if student.class_id:
        class_obj = db.query(Class).filter(Class.id == student.class_id).first()
        class_name = class_obj.name if class_obj else None
    
    return {
        "id": student.id,
        "first_name": student.first_name,
        "last_name": student.last_name,
        "admission_number": student.admission_number,
        "date_of_birth": student.date_of_birth,
        "gender": student.gender,
        "email": current_user.email,
        "class_id": student.class_id,
        "class_name": class_name
    }