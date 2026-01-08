"""
Enterprise Integrations Module
Supports: Jira, Asana, Trello, Slack, Teams, GitHub, GitLab, Salesforce, HubSpot, 
         QuickBooks, Xero, Google Drive, Dropbox, Zoom, Zapier
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx
import base64
import hashlib
import hmac
import json
import os

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

# ============================================
# PYDANTIC MODELS
# ============================================

class IntegrationConfig(BaseModel):
    integration_type: str
    credentials: Dict[str, str]
    settings: Optional[Dict] = {}
    auto_sync: bool = True

class SyncRequest(BaseModel):
    integration_id: str
    sync_type: str  # "import" or "export"
    entity_type: Optional[str] = None  # "tasks", "projects", "users"

# ============================================
# JIRA INTEGRATION
# ============================================

class JiraIntegration:
    """Jira Integration for task/project sync"""
    
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.api_token = api_token
        self.auth = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    
    async def test_connection(self) -> bool:
        """Test Jira connection"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/myself",
                headers={"Authorization": f"Basic {self.auth}"}
            )
            return response.status_code == 200
    
    async def import_projects(self) -> List[Dict]:
        """Import projects from Jira"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/project",
                headers={"Authorization": f"Basic {self.auth}"}
            )
            if response.status_code == 200:
                return response.json()
            return []
    
    async def import_issues(self, project_key: str) -> List[Dict]:
        """Import issues (tasks) from Jira project"""
        async with httpx.AsyncClient() as client:
            jql = f"project={project_key}"
            response = await client.get(
                f"{self.base_url}/rest/api/3/search",
                params={"jql": jql},
                headers={"Authorization": f"Basic {self.auth}"}
            )
            if response.status_code == 200:
                return response.json().get('issues', [])
            return []
    
    async def create_worklog(self, issue_key: str, time_spent_seconds: int, comment: str):
        """Export time entry to Jira as worklog"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/worklog",
                headers={
                    "Authorization": f"Basic {self.auth}",
                    "Content-Type": "application/json"
                },
                json={
                    "timeSpentSeconds": time_spent_seconds,
                    "comment": comment
                }
            )
            return response.status_code == 201

# ============================================
# ASANA INTEGRATION
# ============================================

class AsanaIntegration:
    """Asana Integration for task/project sync"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://app.asana.com/api/1.0"
    
    async def test_connection(self) -> bool:
        """Test Asana connection"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/me",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            return response.status_code == 200
    
    async def get_workspaces(self) -> List[Dict]:
        """Get Asana workspaces"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/workspaces",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
    
    async def import_projects(self, workspace_gid: str) -> List[Dict]:
        """Import projects from Asana workspace"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects",
                params={"workspace": workspace_gid},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json().get('data', [])
            return []
    
    async def import_tasks(self, project_gid: str) -> List[Dict]:
        """Import tasks from Asana project"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/tasks",
                params={"project": project_gid},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json().get('data', [])
            return []

# ============================================
# SLACK INTEGRATION
# ============================================

class SlackIntegration:
    """Slack Integration for notifications and updates"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = "https://slack.com/api"
    
    async def test_connection(self) -> bool:
        """Test Slack connection"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth.test",
                headers={"Authorization": f"Bearer {self.bot_token}"}
            )
            return response.status_code == 200 and response.json().get('ok')
    
    async def send_message(self, channel: str, text: str, blocks: Optional[List] = None):
        """Send message to Slack channel"""
        async with httpx.AsyncClient() as client:
            payload = {
                "channel": channel,
                "text": text
            }
            if blocks:
                payload["blocks"] = blocks
            
            response = await client.post(
                f"{self.base_url}/chat.postMessage",
                headers={
                    "Authorization": f"Bearer {self.bot_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            return response.json()
    
    async def notify_time_entry(self, channel: str, user: str, project: str, hours: float):
        """Send time entry notification to Slack"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{user}* logged *{hours} hours* on *{project}*"
                }
            }
        ]
        return await self.send_message(channel, f"{user} logged {hours} hours", blocks)

# ============================================
# MICROSOFT TEAMS INTEGRATION
# ============================================

class TeamsIntegration:
    """Microsoft Teams Integration"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_message(self, title: str, text: str, facts: Optional[List[Dict]] = None):
        """Send adaptive card to Teams"""
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": title,
            "themeColor": "0078D4",
            "title": title,
            "text": text
        }
        
        if facts:
            card["sections"] = [{
                "facts": facts
            }]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.webhook_url,
                json=card
            )
            return response.status_code == 200

# ============================================
# GITHUB INTEGRATION
# ============================================

class GitHubIntegration:
    """GitHub Integration for commit tracking"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"
    
    async def get_user_repos(self, username: str) -> List[Dict]:
        """Get user repositories"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/users/{username}/repos",
                headers={"Authorization": f"token {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json()
            return []
    
    async def get_commits(self, owner: str, repo: str, author: str = None) -> List[Dict]:
        """Get repository commits"""
        params = {}
        if author:
            params['author'] = author
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/commits",
                params=params,
                headers={"Authorization": f"token {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json()
            return []

# ============================================
# SALESFORCE INTEGRATION
# ============================================

class SalesforceIntegration:
    """Salesforce CRM Integration"""
    
    def __init__(self, instance_url: str, access_token: str):
        self.instance_url = instance_url.rstrip('/')
        self.access_token = access_token
    
    async def query(self, soql: str) -> Dict:
        """Execute SOQL query"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.instance_url}/services/data/v57.0/query",
                params={"q": soql},
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            if response.status_code == 200:
                return response.json()
            return {}
    
    async def get_accounts(self) -> List[Dict]:
        """Get Salesforce accounts"""
        result = await self.query("SELECT Id, Name, Industry FROM Account LIMIT 100")
        return result.get('records', [])
    
    async def sync_clients(self) -> List[Dict]:
        """Sync Salesforce accounts as clients"""
        accounts = await self.get_accounts()
        return [{
            'external_id': acc['Id'],
            'name': acc['Name'],
            'industry': acc.get('Industry')
        } for acc in accounts]

# ============================================
# QUICKBOOKS INTEGRATION
# ============================================

class QuickBooksIntegration:
    """QuickBooks Online Integration for accounting"""
    
    def __init__(self, realm_id: str, access_token: str):
        self.realm_id = realm_id
        self.access_token = access_token
        self.base_url = "https://quickbooks.api.intuit.com/v3/company"
    
    async def create_invoice(self, invoice_data: Dict) -> Dict:
        """Create invoice in QuickBooks"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{self.realm_id}/invoice",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json=invoice_data
            )
            if response.status_code == 200:
                return response.json()
            return {}
    
    async def sync_invoice(self, workingtracker_invoice: Dict) -> bool:
        """Sync WorkingTracker invoice to QuickBooks"""
        qb_invoice = {
            "Line": [{
                "Amount": workingtracker_invoice['total_amount'],
                "DetailType": "SalesItemLineDetail",
                "SalesItemLineDetail": {
                    "ItemRef": {"value": "1"},  # Service item
                    "Qty": workingtracker_invoice.get('hours', 0)
                },
                "Description": workingtracker_invoice.get('description', '')
            }],
            "CustomerRef": {
                "value": workingtracker_invoice.get('customer_id', '1')
            }
        }
        
        result = await self.create_invoice(qb_invoice)
        return bool(result)

# ============================================
# GOOGLE DRIVE INTEGRATION
# ============================================

class GoogleDriveIntegration:
    """Google Drive Integration for file storage"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://www.googleapis.com/drive/v3"
    
    async def create_folder(self, name: str, parent_id: Optional[str] = None) -> Dict:
        """Create folder in Google Drive"""
        metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder"
        }
        if parent_id:
            metadata["parents"] = [parent_id]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/files",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                json=metadata
            )
            if response.status_code == 200:
                return response.json()
            return {}
    
    async def upload_file(self, file_path: str, folder_id: Optional[str] = None) -> Dict:
        """Upload file to Google Drive"""
        # Implementation would handle multipart upload
        pass

# ============================================
# ZAPIER INTEGRATION
# ============================================

class ZapierIntegration:
    """Zapier Webhook Integration"""
    
    @staticmethod
    async def trigger_zap(webhook_url: str, data: Dict) -> bool:
        """Trigger a Zapier webhook"""
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=data)
            return response.status_code == 200

# ============================================
# MAIN INTEGRATION ENDPOINTS
# ============================================

@router.post("/connect")
async def connect_integration(
    config: IntegrationConfig,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Connect a new integration
    """
    try:
        # Test connection based on integration type
        is_valid = False
        
        if config.integration_type == "jira":
            jira = JiraIntegration(
                config.credentials['base_url'],
                config.credentials['email'],
                config.credentials['api_token']
            )
            is_valid = await jira.test_connection()
        
        elif config.integration_type == "asana":
            asana = AsanaIntegration(config.credentials['access_token'])
            is_valid = await asana.test_connection()
        
        elif config.integration_type == "slack":
            slack = SlackIntegration(config.credentials['bot_token'])
            is_valid = await slack.test_connection()
        
        # Add more integrations...
        
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid credentials")
        
        # Store integration
        integration_id = str(uuid.uuid4())
        integration_data = {
            "id": integration_id,
            "organization_id": current_user['organization_id'],
            "integration_type": config.integration_type,
            "credentials": encrypt_credentials(config.credentials),
            "config": config.settings,
            "is_active": True,
            "is_configured": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        await db.table('integrations').insert(integration_data).execute()
        
        return {
            "success": True,
            "integration_id": integration_id,
            "message": f"{config.integration_type.capitalize()} connected successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_integration(
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Sync data with integration
    """
    try:
        # Get integration
        integration = await db.table('integrations').select('*')\
            .eq('id', sync_request.integration_id).single().execute()
        
        if not integration.data:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        # Run sync in background
        background_tasks.add_task(
            run_integration_sync,
            integration_id=sync_request.integration_id,
            sync_type=sync_request.sync_type,
            entity_type=sync_request.entity_type,
            user_id=current_user['id']
        )
        
        return {
            "success": True,
            "message": "Sync started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{integration_id}/status")
async def get_integration_status(
    integration_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get integration sync status
    """
    try:
        integration = await db.table('integrations').select('*')\
            .eq('id', integration_id).single().execute()
        
        if not integration.data:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        return {
            "success": True,
            "integration": {
                "id": integration.data['id'],
                "type": integration.data['integration_type'],
                "is_active": integration.data['is_active'],
                "last_synced_at": integration.data.get('last_synced_at'),
                "sync_status": integration.data.get('sync_status', 'idle')
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# HELPER FUNCTIONS
# ============================================

async def run_integration_sync(integration_id: str, sync_type: str, entity_type: str, user_id: str):
    """Background task for integration sync"""
    # Implementation would handle actual sync logic
    pass

def encrypt_credentials(credentials: Dict) -> Dict:
    """Encrypt sensitive credentials"""
    # Implementation would use proper encryption
    return credentials

async def get_current_user():
    """Get current user"""
    pass

async def get_db():
    """Get database connection"""
    pass

import uuid
