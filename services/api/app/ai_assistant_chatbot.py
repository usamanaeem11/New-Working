"""
AI Chatbot Assistant
Provides guidance on WorkingTracker usage, working ethics, rules, and best practices
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import openai
import os
import json

router = APIRouter(prefix="/api/assistant", tags=["AI Assistant"])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# ============================================
# KNOWLEDGE BASE
# ============================================

ASSISTANT_KNOWLEDGE = """
# WorkingTracker AI Assistant Knowledge Base

## About WorkingTracker
WorkingTracker is a comprehensive time tracking and productivity platform that helps:
- Companies manage employee time and productivity
- Offices track projects and billable hours
- Employees monitor their work-life balance
- Freelancers manage clients and invoicing
- Teams collaborate effectively

## Core Features
1. **Time Tracking**: Manual and automatic time tracking with screenshot capture
2. **Project Management**: Create projects, assign tasks, track budgets
3. **Team Collaboration**: Real-time chat, shared calendars, team dashboards
4. **HRMS**: Leave management, expense tracking, payroll processing
5. **AI Features**: Productivity coach, burnout detection, auto-categorization
6. **Invoicing**: Generate professional invoices from tracked time
7. **Reports**: Detailed analytics and custom reports
8. **Mobile Apps**: iOS and Android with GPS and offline mode
9. **Integrations**: Jira, Asana, Slack, QuickBooks, and more

## Getting Started
1. **Sign Up**: Create an organization account
2. **Add Team**: Invite team members
3. **Create Projects**: Set up your first project
4. **Start Tracking**: Use desktop app or manual timer
5. **Review Reports**: Check productivity dashboards

## Time Tracking Best Practices
1. **Be Consistent**: Track time daily
2. **Use Projects**: Always assign time to projects
3. **Add Descriptions**: Describe what you worked on
4. **Review Weekly**: Check your time entries for accuracy
5. **Set Reminders**: Enable notifications to start tracking

## Working Ethics & Rules
1. **Honesty**: Always track actual time worked
2. **Privacy**: Respect screenshot privacy settings
3. **Breaks**: Take regular breaks (tracked separately)
4. **Communication**: Update project status regularly
5. **Professionalism**: Keep descriptions professional

## Productivity Tips
1. **Pomodoro Technique**: 25-minute focused work sessions
2. **Time Blocking**: Schedule specific tasks
3. **Eliminate Distractions**: Use focus mode
4. **Regular Breaks**: Take breaks to avoid burnout
5. **Review & Reflect**: Weekly review of productivity

## Common Questions

### How do I start tracking time?
Click the "Start Timer" button or press Ctrl+Shift+T (desktop app).

### Can I edit time entries?
Yes, click on any time entry to edit start time, end time, or description.

### How do screenshots work?
Desktop app captures screenshots at configured intervals (default: 10 minutes).
You can delete screenshots you don't want to keep.

### How do I track breaks?
Pause the timer when taking breaks, or mark time entries as "break time".

### How do I generate invoices?
Go to Invoicing → Create Invoice, select project and time period.

### What are billable vs non-billable hours?
Billable: Time that can be charged to clients
Non-billable: Internal work, meetings, training

### How do I request leave?
Go to HRMS → Leave Requests → Create New Request

### How do I submit expenses?
Go to HRMS → Expenses → Add Expense, upload receipt

### Can I work offline?
Yes, mobile and desktop apps work offline and sync when connected.

### How do I improve my productivity score?
- Track time consistently
- Work on important tasks
- Minimize distracting activities
- Take regular breaks
- Review AI insights

## Troubleshooting

### Timer won't start
- Check if you're connected to internet
- Verify desktop app is installed
- Try restarting the app

### Screenshots not uploading
- Check internet connection
- Verify storage space
- Check privacy settings

### Reports not showing data
- Ensure time entries exist for selected period
- Check project/user filters
- Verify permissions

### Mobile app sync issues
- Ensure stable internet connection
- Check if background sync is enabled
- Try manual sync

## Keyboard Shortcuts
- **Ctrl+Shift+T**: Start/stop timer
- **Ctrl+Shift+E**: Edit current entry
- **Ctrl+Shift+P**: Create project
- **Ctrl+Shift+R**: Open reports

## For Managers
1. **Approve Time**: Review and approve team entries
2. **Monitor Productivity**: Check team dashboards
3. **Budgets**: Set and monitor project budgets
4. **Reports**: Generate team performance reports
5. **Leave Approval**: Approve/reject leave requests

## For Admins
1. **User Management**: Add/remove users, assign roles
2. **Organization Settings**: Configure company preferences
3. **Integrations**: Connect third-party tools
4. **Billing**: Manage subscription and payments
5. **White-label**: Customize branding (enterprise)

## Security & Privacy
1. **Data Encryption**: All data encrypted in transit and at rest
2. **Screenshot Privacy**: Blur sensitive information
3. **Access Control**: Role-based permissions
4. **Audit Logs**: Complete activity trail
5. **GDPR Compliant**: Data export and deletion rights

## Billing & Pricing
- **Free Plan**: 1 user, basic features
- **Pro Plan**: $12/user/month, all features
- **Enterprise**: Custom pricing, white-label, SSO
- **Freelancer**: $8/month, unlimited clients

## Support
- **Help Center**: help.workingtracker.com
- **Email**: support@workingtracker.com
- **Live Chat**: Available in-app
- **Documentation**: docs.workingtracker.com
"""

# ============================================
# PYDANTIC MODELS
# ============================================

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict] = None

class ConversationHistory(BaseModel):
    messages: List[Dict]
    session_id: str

# ============================================
# CHATBOT LOGIC
# ============================================

class WorkingTrackerAssistant:
    """AI Assistant for WorkingTracker"""
    
    def __init__(self):
        self.system_prompt = f"""You are the WorkingTracker AI Assistant, a friendly and knowledgeable helper for users of the WorkingTracker platform.

Your role is to:
1. Help users understand and use WorkingTracker features
2. Provide guidance on working ethics and best practices
3. Answer questions about time tracking, productivity, and team management
4. Offer personalized advice based on user context
5. Guide users through troubleshooting issues

Guidelines:
- Be friendly, professional, and concise
- Provide step-by-step instructions when needed
- Ask clarifying questions if the user's request is unclear
- Offer relevant tips and best practices
- If you don't know something, suggest checking the documentation or contacting support

Knowledge Base:
{ASSISTANT_KNOWLEDGE}

Always provide accurate, helpful information based on the knowledge base above.
"""
    
    async def chat(self, user_message: str, conversation_history: List[Dict] = None, user_context: Dict = None) -> str:
        """Process user message and return response"""
        
        # Build conversation context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add user context if available
        if user_context:
            context_message = f"""
User Context:
- Name: {user_context.get('name', 'User')}
- Role: {user_context.get('role', 'Employee')}
- Organization: {user_context.get('organization', 'N/A')}
- Current Plan: {user_context.get('plan', 'Pro')}
- Days Active: {user_context.get('days_active', 0)}
- Total Hours Tracked: {user_context.get('total_hours', 0)}
"""
            messages.append({"role": "system", "content": context_message})
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 messages
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Call OpenAI
        try:
            response = await openai.ChatCompletion.acreate(
                model=os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview'),
                messages=messages,
                max_tokens=800,
                temperature=0.7,
                presence_penalty=0.6,
                frequency_penalty=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return "I apologize, but I'm having trouble processing your request. Please try again or contact support@workingtracker.com for assistance."
    
    def get_quick_replies(self, user_message: str) -> List[str]:
        """Get suggested quick replies based on user message"""
        
        quick_replies = {
            "start": [
                "How do I start tracking time?",
                "Show me the dashboard",
                "Add a new project"
            ],
            "track": [
                "How do screenshots work?",
                "Can I edit time entries?",
                "How do I track breaks?"
            ],
            "invoice": [
                "How do I create an invoice?",
                "Export invoice to PDF",
                "Send invoice to client"
            ],
            "team": [
                "How do I add team members?",
                "View team productivity",
                "Approve time entries"
            ],
            "report": [
                "Generate time report",
                "Show productivity trends",
                "Export data to Excel"
            ],
            "help": [
                "Contact support",
                "View documentation",
                "Watch tutorial videos"
            ]
        }
        
        # Simple keyword matching
        message_lower = user_message.lower()
        
        for key, replies in quick_replies.items():
            if key in message_lower:
                return replies
        
        return quick_replies["help"]

# ============================================
# REST ENDPOINTS
# ============================================

assistant = WorkingTrackerAssistant()

@router.post("/chat")
async def chat_with_assistant(
    message: ChatMessage,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Chat with AI assistant
    """
    try:
        # Get or create conversation session
        session_id = message.context.get('session_id') if message.context else None
        
        if not session_id:
            session_id = str(uuid.uuid4())
            # Create new session
            await db.table('assistant_sessions').insert({
                "id": session_id,
                "user_id": current_user['id'],
                "messages": [],
                "started_at": datetime.utcnow().isoformat()
            }).execute()
        
        # Get conversation history
        session = await db.table('assistant_sessions').select('*')\
            .eq('id', session_id).single().execute()
        
        conversation_history = session.data.get('messages', []) if session.data else []
        
        # Get user context
        user_context = {
            "name": current_user['full_name'],
            "role": current_user['role'],
            "organization": current_user.get('organization_name', 'N/A'),
            "plan": "Pro",  # Get from org
            "days_active": 30,  # Calculate
            "total_hours": 160  # Calculate
        }
        
        # Get response from assistant
        response = await assistant.chat(
            message.message,
            conversation_history,
            user_context
        )
        
        # Get quick replies
        quick_replies = assistant.get_quick_replies(message.message)
        
        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": message.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Save to database
        await db.table('assistant_sessions').update({
            "messages": conversation_history,
            "updated_at": datetime.utcnow().isoformat()
        }).eq('id', session_id).execute()
        
        return {
            "success": True,
            "session_id": session_id,
            "response": response,
            "quick_replies": quick_replies,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_chat_sessions(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get user's chat sessions
    """
    try:
        sessions = await db.table('assistant_sessions').select('*')\
            .eq('user_id', current_user['id'])\
            .order('updated_at', desc=True)\
            .limit(20)\
            .execute()
        
        return {
            "success": True,
            "sessions": sessions.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete chat session
    """
    try:
        await db.table('assistant_sessions').delete()\
            .eq('id', session_id)\
            .eq('user_id', current_user['id'])\
            .execute()
        
        return {
            "success": True,
            "message": "Session deleted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_index: int,
    helpful: bool,
    comment: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Submit feedback on assistant response
    """
    try:
        await db.table('assistant_feedback').insert({
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": current_user['id'],
            "message_index": message_index,
            "helpful": helpful,
            "comment": comment,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        
        return {
            "success": True,
            "message": "Feedback submitted"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# WEBSOCKET FOR REAL-TIME CHAT
# ============================================

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str
):
    """
    WebSocket endpoint for real-time chat
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            user_message = data.get('message')
            
            if not user_message:
                continue
            
            # Get response (simplified - would need proper user context)
            response = await assistant.chat(user_message, [])
            
            # Send response
            await websocket.send_json({
                "type": "message",
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
    except WebSocketDisconnect:
        pass

# ============================================
# HELPER FUNCTIONS
# ============================================

async def get_current_user():
    """Get current user"""
    pass

async def get_db():
    """Get database connection"""
    pass

import uuid
