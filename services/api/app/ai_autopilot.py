"""
AI Autopilot & Advanced AI Features
Includes: Auto task creation, Smart scheduling, Productivity coach, Burnout detection
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import openai
import os

router = APIRouter(prefix="/api/ai", tags=["AI Features"])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# ============================================
# PYDANTIC MODELS
# ============================================

class AutopilotSettings(BaseModel):
    enabled: bool = True
    auto_create_tasks: bool = True
    auto_schedule: bool = True
    auto_categorize: bool = True
    learning_mode: bool = True

class ProductivityCoachMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class BurnoutCheck(BaseModel):
    include_recommendations: bool = True

# ============================================
# AI AUTOPILOT ENDPOINTS
# ============================================

@router.post("/autopilot/enable")
async def enable_autopilot(
    settings: AutopilotSettings,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Enable/configure AI Autopilot
    """
    try:
        # Update user settings
        update_data = {
            "ai_autopilot_enabled": settings.enabled,
            "ai_autopilot_settings": settings.dict(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await db.table('users').update(update_data)\
            .eq('id', current_user['id']).execute()
        
        return {
            "success": True,
            "message": "AI Autopilot configured successfully",
            "settings": settings.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autopilot/analyze-day")
async def analyze_day(
    background_tasks: BackgroundTasks,
    target_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Analyze a day's work and generate tasks/insights
    """
    try:
        if not target_date:
            target_date = datetime.utcnow().date().isoformat()
        
        # Get time entries for the day
        time_entries = await db.table('time_entries').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('start_time', target_date)\
            .lt('start_time', (datetime.fromisoformat(target_date) + timedelta(days=1)).isoformat())\
            .execute()
        
        # Get activities
        activities = await db.table('activities').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('started_at', target_date)\
            .lt('started_at', (datetime.fromisoformat(target_date) + timedelta(days=1)).isoformat())\
            .execute()
        
        # Get screenshots
        screenshots = await db.table('screenshots').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('captured_at', target_date)\
            .lt('captured_at', (datetime.fromisoformat(target_date) + timedelta(days=1)).isoformat())\
            .execute()
        
        # Prepare data for AI analysis
        analysis_data = {
            "time_entries": len(time_entries.data),
            "total_hours": sum(e.get('duration_seconds', 0) for e in time_entries.data) / 3600,
            "activities": [{
                "app": a.get('app_name'),
                "category": a.get('category'),
                "duration": a.get('duration_seconds')
            } for a in activities.data[:50]],  # Limit to 50 most recent
            "projects_worked_on": list(set(e.get('project_id') for e in time_entries.data if e.get('project_id')))
        }
        
        # Run AI analysis in background
        background_tasks.add_task(
            run_autopilot_analysis,
            user_id=current_user['id'],
            organization_id=current_user['organization_id'],
            date=target_date,
            data=analysis_data
        )
        
        return {
            "success": True,
            "message": "Analysis started in background",
            "date": target_date,
            "data_points": {
                "time_entries": len(time_entries.data),
                "activities": len(activities.data),
                "screenshots": len(screenshots.data)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/autopilot/suggestions")
async def get_autopilot_suggestions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get AI-generated task suggestions
    """
    try:
        # Get recent AI insights
        insights = await db.table('ai_insights').select('*')\
            .eq('user_id', current_user['id'])\
            .eq('insight_type', 'task_suggestion')\
            .eq('action_taken', False)\
            .order('created_at', desc=True)\
            .limit(10)\
            .execute()
        
        suggestions = []
        for insight in insights.data:
            suggestions.append({
                "id": insight['id'],
                "title": insight['title'],
                "description": insight['description'],
                "priority": insight.get('priority', 'medium'),
                "estimated_time": insight.get('data', {}).get('estimated_hours'),
                "project_id": insight.get('data', {}).get('project_id'),
                "created_at": insight['created_at']
            })
        
        return {
            "success": True,
            "suggestions": suggestions,
            "total": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/autopilot/suggestions/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Accept an AI suggestion and create task
    """
    try:
        # Get suggestion
        suggestion = await db.table('ai_insights').select('*')\
            .eq('id', suggestion_id)\
            .single()\
            .execute()
        
        if not suggestion.data:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        
        # Create task from suggestion
        task_id = str(uuid.uuid4())
        task_data = {
            "id": task_id,
            "project_id": suggestion.data.get('data', {}).get('project_id'),
            "title": suggestion.data['title'],
            "description": suggestion.data['description'],
            "assigned_to_id": current_user['id'],
            "priority": suggestion.data.get('priority', 'medium'),
            "estimated_hours": suggestion.data.get('data', {}).get('estimated_hours'),
            "status": "todo",
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('tasks').insert(task_data).execute()
        
        # Mark suggestion as acted upon
        await db.table('ai_insights').update({
            "action_taken": True,
            "action_data": {"task_id": task_id}
        }).eq('id', suggestion_id).execute()
        
        return {
            "success": True,
            "task_id": task_id,
            "message": "Task created from AI suggestion"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# PRODUCTIVITY COACH ENDPOINTS
# ============================================

@router.post("/coach/chat")
async def chat_with_coach(
    message: ProductivityCoachMessage,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Chat with AI productivity coach
    """
    try:
        # Get or create coaching session
        active_session = await db.table('ai_coaching_sessions').select('*')\
            .eq('user_id', current_user['id'])\
            .is_('ended_at', 'null')\
            .order('started_at', desc=True)\
            .limit(1)\
            .execute()
        
        if active_session.data:
            session_id = active_session.data[0]['id']
            messages = active_session.data[0].get('messages', [])
        else:
            # Create new session
            session_id = str(uuid.uuid4())
            messages = []
            await db.table('ai_coaching_sessions').insert({
                "id": session_id,
                "user_id": current_user['id'],
                "session_type": "productivity_coaching",
                "messages": [],
                "started_at": datetime.utcnow().isoformat()
            }).execute()
        
        # Get user context for better responses
        context = await get_user_context(current_user['id'], db)
        
        # Add context to message if provided
        if message.context:
            context.update(message.context)
        
        # Prepare messages for OpenAI
        messages.append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Create system message with context
        system_message = f"""You are a productivity coach for a time tracking platform. 
        
User Context:
- Name: {current_user.get('full_name')}
- Role: {current_user.get('role')}
- Recent productivity: {context.get('recent_productivity_score', 'N/A')}%
- Average daily hours: {context.get('avg_daily_hours', 'N/A')}
- Current workload: {context.get('active_tasks', 0)} active tasks

Provide helpful, actionable advice on productivity, time management, and work-life balance.
Be encouraging but honest. Keep responses concise (2-3 paragraphs max)."""

        # Call OpenAI
        openai_messages = [{"role": "system", "content": system_message}]
        for msg in messages[-5:]:  # Last 5 messages for context
            openai_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        response = await openai.ChatCompletion.acreate(
            model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
            messages=openai_messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to messages
        messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Update session
        await db.table('ai_coaching_sessions').update({
            "messages": messages,
            "message_count": len(messages),
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', session_id).execute()
        
        return {
            "success": True,
            "session_id": session_id,
            "response": ai_response,
            "message_count": len(messages)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/coach/end-session")
async def end_coaching_session(
    session_id: str,
    rating: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    End a coaching session
    """
    try:
        update_data = {
            "ended_at": datetime.utcnow().isoformat()
        }
        
        if rating:
            update_data["satisfaction_rating"] = rating
        
        await db.table('ai_coaching_sessions').update(update_data)\
            .eq('id', session_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            "success": True,
            "message": "Coaching session ended",
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# BURNOUT DETECTION ENDPOINTS
# ============================================

@router.get("/wellness/burnout-check")
async def check_burnout(
    include_recommendations: bool = True,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Check for burnout indicators
    """
    try:
        # Get last 30 days of data
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        
        # Get time entries
        time_entries = await db.table('time_entries').select('*')\
            .eq('user_id', current_user['id'])\
            .gte('start_time', thirty_days_ago)\
            .execute()
        
        # Calculate metrics
        total_hours = sum(e.get('duration_seconds', 0) for e in time_entries.data) / 3600
        avg_daily_hours = total_hours / 30
        
        # Get working days (days with entries)
        working_days = len(set(
            datetime.fromisoformat(e['start_time']).date() 
            for e in time_entries.data
        ))
        
        # Get weekend work
        weekend_hours = sum(
            e.get('duration_seconds', 0) 
            for e in time_entries.data 
            if datetime.fromisoformat(e['start_time']).weekday() >= 5
        ) / 3600
        
        # Calculate burnout indicators
        indicators = {
            "excessive_hours": avg_daily_hours > 9,  # More than 9 hours/day
            "no_breaks": working_days >= 25,  # Working almost every day
            "weekend_work": weekend_hours > 10,  # Significant weekend work
            "late_nights": False  # TODO: Implement based on time patterns
        }
        
        # Calculate burnout score (0-100)
        burnout_score = 0
        if indicators["excessive_hours"]:
            burnout_score += 30
        if indicators["no_breaks"]:
            burnout_score += 25
        if indicators["weekend_work"]:
            burnout_score += 25
        if indicators["late_nights"]:
            burnout_score += 20
        
        # Determine risk level
        if burnout_score < 30:
            risk_level = "low"
            risk_message = "You're maintaining a healthy work-life balance!"
        elif burnout_score < 60:
            risk_level = "moderate"
            risk_message = "Watch out for signs of burnout. Consider taking breaks."
        else:
            risk_level = "high"
            risk_message = "High burnout risk detected. Please prioritize self-care."
        
        result = {
            "success": True,
            "burnout_score": burnout_score,
            "risk_level": risk_level,
            "message": risk_message,
            "metrics": {
                "avg_daily_hours": round(avg_daily_hours, 2),
                "total_hours_30_days": round(total_hours, 2),
                "working_days": working_days,
                "weekend_hours": round(weekend_hours, 2)
            },
            "indicators": indicators
        }
        
        if include_recommendations and burnout_score >= 30:
            result["recommendations"] = await generate_burnout_recommendations(
                burnout_score, 
                indicators,
                current_user
            )
        
        # Store insight
        await db.table('ai_insights').insert({
            "id": str(uuid.uuid4()),
            "user_id": current_user['id'],
            "organization_id": current_user['organization_id'],
            "insight_type": "burnout_detection",
            "title": f"Burnout Risk: {risk_level.capitalize()}",
            "description": risk_message,
            "priority": "high" if burnout_score >= 60 else "medium",
            "data": result,
            "insight_date": datetime.utcnow().date().isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# SMART CATEGORIZATION ENDPOINTS
# ============================================

@router.post("/categorize/activity")
async def categorize_activity(
    app_name: str,
    window_title: Optional[str] = None,
    url: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Automatically categorize an activity using AI
    """
    try:
        # Prepare input for AI
        activity_text = f"Application: {app_name}"
        if window_title:
            activity_text += f"\nWindow: {window_title}"
        if url:
            activity_text += f"\nURL: {url}"
        
        # Call OpenAI for categorization
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": """Categorize the following activity into one of these categories:
                - productive (work-related tasks)
                - neutral (general browsing, tools)
                - distracting (social media, entertainment)
                
                Also assign a productivity score from 0-100.
                
                Respond ONLY with JSON: {"category": "...", "productivity_score": 0-100, "reasoning": "..."}"""
            }, {
                "role": "user",
                "content": activity_text
            }],
            max_tokens=150,
            temperature=0.3
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            "success": True,
            "category": result.get("category", "neutral"),
            "productivity_score": result.get("productivity_score", 50),
            "reasoning": result.get("reasoning", "AI categorization")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

async def run_autopilot_analysis(user_id: str, organization_id: str, date: str, data: dict):
    """Background task for autopilot analysis"""
    try:
        # Analyze patterns
        prompt = f"""Analyze this day's work data and suggest 2-3 tasks for tomorrow:

Data:
- Total hours worked: {data['total_hours']}
- Number of time entries: {data['time_entries']}
- Apps/activities: {', '.join([a['app'] for a in data['activities'][:10] if a.get('app')])}
- Projects: {len(data['projects_worked_on'])} different projects

Generate practical, specific task suggestions based on the work patterns."""

        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo-preview",
            messages=[{
                "role": "system",
                "content": "You are a productivity AI analyzing work patterns. Suggest specific, actionable tasks."
            }, {
                "role": "user",
                "content": prompt
            }],
            max_tokens=400
        )
        
        suggestions_text = response.choices[0].message.content
        
        # Parse and store suggestions (simplified)
        # In production, parse structured output
        db = get_db()
        await db.table('ai_insights').insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "organization_id": organization_id,
            "insight_type": "task_suggestion",
            "title": "AI-Generated Task Suggestions",
            "description": suggestions_text,
            "priority": "medium",
            "data": data,
            "insight_date": date,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
    except Exception as e:
        print(f"Autopilot analysis error: {e}")

async def get_user_context(user_id: str, db):
    """Get user context for AI coach"""
    # Get recent productivity
    seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
    
    time_entries = await db.table('time_entries').select('*')\
        .eq('user_id', user_id)\
        .gte('start_time', seven_days_ago)\
        .execute()
    
    total_hours = sum(e.get('duration_seconds', 0) for e in time_entries.data) / 3600
    
    tasks = await db.table('tasks').select('*')\
        .eq('assigned_to_id', user_id)\
        .in_('status', ['todo', 'in_progress'])\
        .execute()
    
    return {
        "recent_productivity_score": 75,  # TODO: Calculate actual score
        "avg_daily_hours": round(total_hours / 7, 1),
        "active_tasks": len(tasks.data)
    }

async def generate_burnout_recommendations(score: int, indicators: dict, user: dict):
    """Generate personalized burnout recommendations"""
    recommendations = []
    
    if indicators["excessive_hours"]:
        recommendations.append({
            "title": "Reduce Daily Hours",
            "description": "Try to limit work to 8 hours per day",
            "action": "Set a daily reminder to stop working"
        })
    
    if indicators["no_breaks"]:
        recommendations.append({
            "title": "Take Regular Breaks",
            "description": "Schedule at least 1-2 days off per week",
            "action": "Block weekends in your calendar"
        })
    
    if indicators["weekend_work"]:
        recommendations.append({
            "title": "Protect Your Weekends",
            "description": "Avoid work on weekends to recharge",
            "action": "Turn off work notifications on weekends"
        })
    
    return recommendations

async def get_current_user():
    """Get current user from token"""
    pass

async def get_db():
    """Get database connection"""
    pass
