"""
Activity Tracker Service
Handles tracking of user activities and analytics
"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.services.supabase_manager import SupabaseManager

class ActivityTracker:
    def __init__(self, supabase: Optional[SupabaseManager] = None):
        self.supabase = supabase
    
    async def track_text_comparison(
        self,
        user_email: Optional[str],
        original_text: str,
        summary_text: str,
        accuracy_score: int,
        correct_points: List[str],
        missed_points: List[str],
        wrong_points: List[str],
        reading_mode: str = "detailed",
        additional_params: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Track text comparison activity"""
        try:
            # Determine user type
            user_type = "authenticated" if user_email else "guest"
            
            # Prepare activity data
            activity_data = {
                "user_email": user_email or "guest",
                "user_type": user_type,
                "activity_type": "text_comparison",
                "original_text": original_text,
                "summary_text": summary_text,
                "accuracy_score": accuracy_score,
                "correct_points": correct_points or [],
                "missed_points": missed_points or [],
                "wrong_points": wrong_points or [],
                "correct_points_count": len(correct_points or []),
                "missed_points_count": len(missed_points or []),
                "wrong_points_count": len(wrong_points or []),
                "reading_mode": reading_mode,
                "additional_params": additional_params or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now().isoformat()
            }
            
            # Log to Supabase if available
            print(f"🔍 Checking Supabase availability...")
            print(f"   Supabase instance: {'✅ Available' if self.supabase else '❌ Not available'}")
            if self.supabase:
                connected = self.supabase.is_connected()
                print(f"   Connection status: {'✅ Connected' if connected else '❌ Not connected'}")
            
            if self.supabase:
                # Try to reconnect if not connected
                if not self.supabase.is_connected():
                    print(f"🔄 Attempting to reconnect to Supabase...")
                    await self.supabase.connect()
                
                if self.supabase.is_connected():
                    print(f"📊 Logging activity to database for {user_type} user...")
                    success = await self.supabase.log_activity(activity_data)
                    if success:
                        print(f"✅ Activity tracking completed successfully")
                        
                        # Verify the record was actually created
                        if user_email:
                            await self.supabase.verify_recent_activity(user_email, "text_comparison", 1)
                        
                        return True
                    else:
                        print("⚠️ Failed to log activity to Supabase")
                        return False
                else:
                    print("⚠️ Supabase connection failed after retry")
                    return False
            else:
                print("⚠️ Supabase not available, activity not tracked")
                return False
                
        except Exception as e:
            print(f"❌ Error tracking text comparison activity: {e}")
            return False
    
    async def track_user_login(
        self,
        user_email: str,
        user_name: Optional[str] = None,
        user_picture: Optional[str] = None,
        login_method: str = "google",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Track user login activity"""
        try:
            # Create or update user in users table
            if self.supabase:
                # Try to reconnect if not connected
                if not self.supabase.is_connected():
                    print(f"🔄 Attempting to reconnect to Supabase for login...")
                    await self.supabase.connect()
                
                if self.supabase.is_connected():
                    print(f"📊 Processing user login for: {user_email}")
                    existing_user = await self.supabase.get_user(user_email)
                    
                    if existing_user:
                        print(f"   User exists, updating last login...")
                        await self.supabase.update_user_last_login(user_email)
                    else:
                        print(f"   New user, creating account...")
                        await self.supabase.create_user(user_email, user_name, user_picture)
                else:
                    print("⚠️ Supabase connection failed for login")
                    return False
            
            # Log login activity
            activity_data = {
                "user_email": user_email,
                "user_type": "authenticated",
                "activity_type": "login",
                "login_method": login_method,
                "additional_params": {
                    "user_name": user_name,
                    "user_picture": user_picture
                },
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now().isoformat()
            }
            
            if self.supabase:
                # Try to reconnect if not connected
                if not self.supabase.is_connected():
                    print(f"🔄 Attempting to reconnect to Supabase for login activity...")
                    await self.supabase.connect()
                
                if self.supabase.is_connected():
                    print(f"📊 Logging login activity to database...")
                    success = await self.supabase.log_activity(activity_data)
                    if success:
                        print(f"✅ Login tracking completed successfully")
                        return True
                    else:
                        print("⚠️ Failed to log login activity to Supabase")
                        return False
                else:
                    print("⚠️ Supabase connection failed for login activity")
                    return False
            else:
                print("⚠️ Supabase not available, login activity not tracked")
                return False
                
        except Exception as e:
            print(f"❌ Error tracking login activity: {e}")
            return False
    
    async def log_activity(
        self,
        user_email: Optional[str],
        activity_type: str,
        additional_data: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """Log general activity"""
        try:
            user_type = "authenticated" if user_email else "guest"
            
            activity_data = {
                "user_email": user_email or "guest",
                "user_type": user_type,
                "activity_type": activity_type,
                "additional_params": additional_data or {},
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now().isoformat()
            }
            
            if self.supabase:
                # Try to reconnect if not connected
                if not self.supabase.is_connected():
                    print(f"🔄 Attempting to reconnect to Supabase for {activity_type}...")
                    await self.supabase.connect()
                
                if self.supabase.is_connected():
                    success = await self.supabase.log_activity(activity_data)
                    if success:
                        print(f"✅ Logged {activity_type} activity for {user_type} user")
                        return True
                    else:
                        print(f"⚠️ Failed to log {activity_type} activity to Supabase")
                        return False
                else:
                    print(f"⚠️ Supabase connection failed for {activity_type}")
                    return False
            else:
                print(f"⚠️ Supabase not available, {activity_type} activity not tracked")
                return False
                
        except Exception as e:
            print(f"❌ Error logging activity: {e}")
            return False 