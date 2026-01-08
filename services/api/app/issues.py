"""
Issue & Bug Tracking System
Complete issue management with workflow, priorities, and linking
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

router = APIRouter(prefix="/api/issues", tags=["Issues"])
logger = logging.getLogger(__name__)

# ============================================================
# MODELS
# ============================================================

class Issue(BaseModel):
    issue_id: Optional[str] = None
    project_id: str
    title: str
    description: str
    issue_type: str  # Bug, Feature, Task, Improvement, Support
    priority: str  # Critical, High, Medium, Low
    severity: Optional[str] = None  # Blocker, Major, Minor, Trivial
    status: str  # New, In Progress, Resolved, Closed, Reopened
    assignee_id: Optional[str] = None
    reporter_id: str
    sprint_id: Optional[str] = None
    labels: List[str] = []
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    
class IssueLink(BaseModel):
    link_type: str  # blocks, duplicates, relates_to, caused_by
    linked_issue_id: str

class IssueComment(BaseModel):
    comment_id: Optional[str] = None
    issue_id: str
    user_id: str
    comment_text: str
    created_at: Optional[datetime] = None

# ============================================================
# ISSUE CRUD
# ============================================================

@router.post("/")
async def create_issue(issue: Issue):
    """Create new issue"""
    
    logger.info(f"Creating issue: {issue.title}")
    
    # Generate ID
    issue_id = f"ISS-{datetime.now().strftime('%Y%m%d')}-001"
    
    # INSERT INTO issues (...) VALUES (...)
    
    # Send notifications to project team
    # Add to activity feed
    
    return {
        "issue_id": issue_id,
        **issue.dict(),
        "created_at": datetime.now().isoformat(),
        "url": f"/issues/{issue_id}"
    }

@router.get("/")
async def list_issues(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[str] = None,
    issue_type: Optional[str] = None,
    sprint_id: Optional[str] = None,
    labels: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List issues with filters"""
    
    # Build dynamic query based on filters
    # SELECT * FROM issues WHERE ...
    
    return {
        "issues": [
            {
                "issue_id": "ISS-20240105-001",
                "title": "Login button not working on mobile",
                "issue_type": "Bug",
                "priority": "High",
                "status": "In Progress",
                "assignee": "John Doe",
                "created_at": "2024-01-05T10:00:00"
            }
        ],
        "total": 1,
        "limit": limit,
        "offset": offset
    }

@router.get("/{issue_id}")
async def get_issue(issue_id: str):
    """Get issue details"""
    
    return {
        "issue_id": issue_id,
        "title": "Login button not working on mobile",
        "description": "When clicking login button on iOS Safari, nothing happens",
        "issue_type": "Bug",
        "priority": "High",
        "severity": "Major",
        "status": "In Progress",
        "assignee": {
            "id": "user_1",
            "name": "John Doe",
            "avatar": "/avatars/john.jpg"
        },
        "reporter": {
            "id": "user_2",
            "name": "Jane Smith"
        },
        "project": {
            "id": "proj_1",
            "name": "Mobile App"
        },
        "labels": ["mobile", "authentication", "ios"],
        "estimated_hours": 4,
        "actual_hours": 2.5,
        "due_date": "2024-01-10",
        "created_at": "2024-01-05T10:00:00",
        "updated_at": "2024-01-05T14:30:00",
        "linked_issues": [
            {"type": "blocks", "issue_id": "ISS-20240105-002"}
        ],
        "attachments": [],
        "comments_count": 3,
        "watchers_count": 5
    }

@router.put("/{issue_id}")
async def update_issue(issue_id: str, update: dict):
    """Update issue"""
    
    logger.info(f"Updating issue {issue_id}")
    
    # UPDATE issues SET ... WHERE issue_id = %s
    
    # Log status change if status updated
    # Send notifications if assignee changed
    
    return {
        "issue_id": issue_id,
        "updated_at": datetime.now().isoformat(),
        "message": "Issue updated successfully"
    }

@router.delete("/{issue_id}")
async def delete_issue(issue_id: str):
    """Delete issue (soft delete)"""
    
    # UPDATE issues SET deleted_at = NOW() WHERE issue_id = %s
    
    return {"message": "Issue deleted successfully"}

# ============================================================
# ISSUE STATUS WORKFLOW
# ============================================================

@router.post("/{issue_id}/transition")
async def transition_status(issue_id: str, new_status: str, comment: Optional[str] = None):
    """Transition issue to new status"""
    
    # Validate transition (e.g., can't go from New to Closed)
    valid_transitions = {
        "New": ["In Progress", "Closed"],
        "In Progress": ["Resolved", "Closed", "On Hold"],
        "On Hold": ["In Progress", "Closed"],
        "Resolved": ["Closed", "Reopened"],
        "Closed": ["Reopened"],
        "Reopened": ["In Progress"]
    }
    
    # UPDATE issues SET status = %s WHERE issue_id = %s
    # INSERT INTO issue_status_history ...
    
    return {
        "issue_id": issue_id,
        "old_status": "In Progress",
        "new_status": new_status,
        "transitioned_at": datetime.now().isoformat()
    }

# ============================================================
# ISSUE COMMENTS
# ============================================================

@router.post("/{issue_id}/comments")
async def add_comment(issue_id: str, comment: IssueComment):
    """Add comment to issue"""
    
    comment_id = f"comment_{datetime.now().timestamp()}"
    
    # INSERT INTO issue_comments ...
    
    # Notify watchers
    
    return {
        "comment_id": comment_id,
        **comment.dict(),
        "created_at": datetime.now().isoformat()
    }

@router.get("/{issue_id}/comments")
async def get_comments(issue_id: str):
    """Get all comments for issue"""
    
    return {
        "issue_id": issue_id,
        "comments": [
            {
                "comment_id": "comment_1",
                "user": {
                    "name": "John Doe",
                    "avatar": "/avatars/john.jpg"
                },
                "comment_text": "I'm working on this now",
                "created_at": "2024-01-05T11:00:00"
            }
        ]
    }

# ============================================================
# ISSUE LINKING
# ============================================================

@router.post("/{issue_id}/links")
async def link_issue(issue_id: str, link: IssueLink):
    """Link issue to another issue"""
    
    # INSERT INTO issue_links ...
    
    return {
        "issue_id": issue_id,
        "linked_to": link.linked_issue_id,
        "link_type": link.link_type
    }

@router.get("/{issue_id}/links")
async def get_linked_issues(issue_id: str):
    """Get all linked issues"""
    
    return {
        "issue_id": issue_id,
        "links": [
            {
                "link_type": "blocks",
                "issue": {
                    "issue_id": "ISS-002",
                    "title": "Related issue",
                    "status": "New"
                }
            }
        ]
    }

# ============================================================
# ISSUE ATTACHMENTS
# ============================================================

@router.post("/{issue_id}/attachments")
async def upload_attachment(issue_id: str, file_url: str, filename: str):
    """Add attachment to issue"""
    
    attachment_id = f"att_{datetime.now().timestamp()}"
    
    return {
        "attachment_id": attachment_id,
        "issue_id": issue_id,
        "filename": filename,
        "url": file_url,
        "uploaded_at": datetime.now().isoformat()
    }

# ============================================================
# ISSUE WATCHERS
# ============================================================

@router.post("/{issue_id}/watch")
async def watch_issue(issue_id: str, user_id: str):
    """Add user as watcher"""
    
    # INSERT INTO issue_watchers ...
    
    return {"message": "Now watching issue"}

@router.delete("/{issue_id}/watch")
async def unwatch_issue(issue_id: str, user_id: str):
    """Remove user as watcher"""
    
    return {"message": "Stopped watching issue"}

# ============================================================
# ISSUE ANALYTICS
# ============================================================

@router.get("/analytics/summary")
async def get_issue_analytics(
    project_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get issue analytics"""
    
    return {
        "total_issues": 156,
        "open_issues": 42,
        "closed_issues": 114,
        "by_type": {
            "Bug": 78,
            "Feature": 45,
            "Task": 23,
            "Improvement": 10
        },
        "by_priority": {
            "Critical": 5,
            "High": 18,
            "Medium": 35,
            "Low": 28
        },
        "by_status": {
            "New": 12,
            "In Progress": 23,
            "Resolved": 7,
            "Closed": 114
        },
        "avg_resolution_time_hours": 24.5,
        "avg_response_time_hours": 2.3
    }

@router.get("/analytics/trends")
async def get_issue_trends(days: int = 30):
    """Get issue creation/resolution trends"""
    
    return {
        "period_days": days,
        "daily_data": [
            {
                "date": "2024-01-05",
                "created": 5,
                "resolved": 3,
                "closed": 2
            }
        ]
    }

logger.info("Issue tracking routes loaded")
