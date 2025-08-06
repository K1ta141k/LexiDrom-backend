"""
Supabase Manager Service
Handles all database operations with Supabase
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.models.schemas import Activity

class SupabaseManager:
    def __init__(self):
        self.client: Optional[Client] = None
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self._connected = False
    
    async def connect(self):
        """Connect to Supabase"""
        try:
            if not self.supabase_url or not self.supabase_key:
                print("⚠️ Supabase credentials not found in environment variables")
                return False
            
            print(f"🔗 Attempting to connect to Supabase...")
            print(f"   URL: {self.supabase_url}")
            print(f"   Key length: {len(self.supabase_key) if self.supabase_key else 0}")
            
            # Create client
            self.client = create_client(self.supabase_url, self.supabase_key)
            
            # Test connection by trying to access a table
            try:
                # Try to access users table to verify connection
                result = self.client.table("users").select("count", count="exact").execute()
                self._connected = True
                print("✅ Connected to Supabase successfully")
                return True
            except Exception as table_error:
                error_msg = str(table_error).lower()
                print(f"🔍 Connection test error: {table_error}")
                
                # If table doesn't exist, that's okay - connection is still valid
                if "relation" in error_msg or "does not exist" in error_msg:
                    self._connected = True
                    print("✅ Connected to Supabase (tables may need to be created)")
                    return True
                # If it's an authentication error, connection failed
                elif "invalid" in error_msg and "key" in error_msg:
                    print(f"❌ Authentication failed: Invalid API key")
                    self._connected = False
                    self.client = None
                    return False
                # If it's a JWT error, also authentication failure
                elif "jwt" in error_msg:
                    print(f"❌ Authentication failed: JWT error")
                    self._connected = False
                    self.client = None
                    return False
                else:
                    print(f"❌ Connection test failed: {table_error}")
                    self._connected = False
                    self.client = None
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            self._connected = False
            self.client = None
            return False
    
    async def disconnect(self):
        """Disconnect from Supabase"""
        self.client = None
        self._connected = False
        print("🔌 Disconnected from Supabase")
    
    def is_connected(self) -> bool:
        """Check if connected to Supabase"""
        return self._connected and self.client is not None
    
    async def create_user(self, email: str, name: Optional[str] = None, picture: Optional[str] = None) -> bool:
        """Create a new user"""
        if not self.is_connected():
            print("⚠️ Supabase not connected, cannot create user")
            return False
        
        try:
            print(f"📝 Attempting to create/update user in database: {email}")
            user_data = {
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            }
            
            result = self.client.table("users").upsert(user_data).execute()
            
            # Verify the upsert was successful
            if result.data:
                print(f"✅ Database user record created/updated successfully!")
                print(f"   User ID: {result.data[0].get('id', 'N/A')}")
                print(f"   Email: {result.data[0].get('email')}")
                print(f"   Created: {result.data[0].get('created_at')}")
                print(f"   Last Login: {result.data[0].get('last_login')}")
                return True
            else:
                print(f"❌ Database upsert returned no data")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create user in database: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    async def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        if not self.is_connected():
            return None
        
        try:
            result = self.client.table("users").select("*").eq("email", email).execute()
            if result.data:
                print(f"✅ Found user in database: {email}")
                return result.data[0]
            else:
                print(f"⚠️ User not found in database: {email}")
                return None
        except Exception as e:
            print(f"❌ Failed to get user: {e}")
            return None
    
    async def update_user_last_login(self, email: str) -> bool:
        """Update user's last login timestamp"""
        if not self.is_connected():
            print("⚠️ Supabase not connected, cannot update user login")
            return False
        
        try:
            print(f"📝 Attempting to update user last login: {email}")
            result = self.client.table("users").update({
                "last_login": datetime.now().isoformat()
            }).eq("email", email).execute()
            
            # Verify the update was successful
            if result.data:
                print(f"✅ Database user login updated successfully!")
                print(f"   User ID: {result.data[0].get('id', 'N/A')}")
                print(f"   Email: {result.data[0].get('email')}")
                print(f"   Updated Last Login: {result.data[0].get('last_login')}")
                return True
            else:
                print(f"❌ Database update returned no data - user may not exist")
                return False
                
        except Exception as e:
            print(f"❌ Failed to update user last login in database: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    

    
    async def log_activity(self, activity_data: Dict[str, Any]) -> bool:
        """Log activity to database"""
        if not self.is_connected():
            print("⚠️ Supabase not connected, cannot log activity")
            return False
        
        try:
            print(f"📝 Attempting to insert activity into database...")
            result = self.client.table("activities").insert(activity_data).execute()
            
            # Verify the insert was successful
            if result.data:
                print(f"✅ Database record created successfully!")
                print(f"   Record ID: {result.data[0].get('id', 'N/A')}")
                print(f"   User: {activity_data.get('user_email', 'guest')}")
                print(f"   Activity Type: {activity_data.get('activity_type')}")
                print(f"   Reading Mode: {activity_data.get('reading_mode', 'N/A')}")
                if activity_data.get('accuracy_score') is not None:
                    print(f"   Accuracy Score: {activity_data.get('accuracy_score')}")
                print(f"   Timestamp: {activity_data.get('created_at')}")
                return True
            else:
                print(f"❌ Database insert returned no data")
                return False
                
        except Exception as e:
            print(f"❌ Failed to log activity to database: {e}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    async def get_user_activities(self, email: str, limit: int = 100) -> List[Activity]:
        """Get activities for a specific user"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table("activities").select("*").eq("user_email", email).order("created_at", desc=True).limit(limit).execute()
            activities = []
            for activity_data in result.data:
                activities.append(Activity(
                    id=activity_data["id"],
                    user_email=activity_data["user_email"],
                    user_type=activity_data["user_type"],
                    activity_type=activity_data["activity_type"],
                    accuracy_score=activity_data.get("accuracy_score"),
                    reading_mode=activity_data.get("reading_mode"),
                    wpm=activity_data.get("wpm"),
                    lpm=activity_data.get("lpm"),
                    created_at=datetime.fromisoformat(activity_data["created_at"]),
                    ip_address=activity_data.get("ip_address"),
                    user_agent=activity_data.get("user_agent")
                ))
            print(f"📊 Found {len(activities)} activities for user: {email}")
            return activities
        except Exception as e:
            print(f"❌ Failed to get user activities: {e}")
            return []
    
    async def verify_recent_activity(self, user_email: str, activity_type: str = "text_comparison", minutes: int = 5) -> bool:
        """Verify that a recent activity exists in the database"""
        if not self.is_connected():
            return False
        
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            
            result = self.client.table("activities").select("*").eq("user_email", user_email).eq("activity_type", activity_type).gte("created_at", cutoff_time.isoformat()).execute()
            
            if result.data:
                print(f"✅ Verified recent {activity_type} activity exists in database for {user_email}")
                print(f"   Found {len(result.data)} recent activities")
                return True
            else:
                print(f"❌ No recent {activity_type} activity found in database for {user_email}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to verify recent activity: {e}")
            return False
    
    async def get_guest_activities(self, limit: int = 100) -> List[Activity]:
        """Get all guest activities"""
        if not self.is_connected():
            return []
        
        try:
            result = self.client.table("activities").select("*").eq("user_type", "guest").order("created_at", desc=True).limit(limit).execute()
            activities = []
            for activity_data in result.data:
                activities.append(Activity(
                    id=activity_data["id"],
                    user_email=activity_data["user_email"],
                    user_type=activity_data["user_type"],
                    activity_type=activity_data["activity_type"],
                    accuracy_score=activity_data.get("accuracy_score"),
                    reading_mode=activity_data.get("reading_mode"),
                    wpm=activity_data.get("wpm"),
                    lpm=activity_data.get("lpm"),
                    created_at=datetime.fromisoformat(activity_data["created_at"]),
                    ip_address=activity_data.get("ip_address"),
                    user_agent=activity_data.get("user_agent")
                ))
            return activities
        except Exception as e:
            print(f"❌ Failed to get guest activities: {e}")
            return []
    
    async def get_activity_stats(self) -> Dict[str, Any]:
        """Get overall activity statistics"""
        if not self.is_connected():
            return {}
        
        try:
            # Get total activities
            total_result = self.client.table("activities").select("id", count="exact").execute()
            total_activities = total_result.count or 0
            
            # Get authenticated users count
            users_result = self.client.table("users").select("id", count="exact").execute()
            authenticated_users = users_result.count or 0
            
            # Get guest activities count
            guest_result = self.client.table("activities").select("id", count="exact").eq("user_type", "guest").execute()
            guest_activities = guest_result.count or 0
            
            # Get average accuracy
            accuracy_result = self.client.table("activities").select("accuracy_score").not_.is_("accuracy_score", "null").execute()
            accuracy_scores = [a["accuracy_score"] for a in accuracy_result.data if a["accuracy_score"] is not None]
            average_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
            
            # Get most popular reading mode
            mode_result = self.client.table("activities").select("reading_mode").not_.is_("reading_mode", "null").execute()
            mode_counts = {}
            for activity in mode_result.data:
                mode = activity["reading_mode"]
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
            most_popular_mode = max(mode_counts.items(), key=lambda x: x[1])[0] if mode_counts else "detailed"
            
            # Get activity breakdown
            breakdown_result = self.client.table("activities").select("activity_type").execute()
            activity_breakdown = {}
            for activity in breakdown_result.data:
                activity_type = activity["activity_type"]
                activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
            
            return {
                "total_activities": total_activities,
                "authenticated_users": authenticated_users,
                "guest_activities": guest_activities,
                "average_accuracy": round(average_accuracy, 2),
                "most_popular_reading_mode": most_popular_mode,
                "activity_breakdown": activity_breakdown
            }
        except Exception as e:
            print(f"❌ Failed to get activity stats: {e}")
            return {}
    
    async def get_points_analysis(self) -> Dict[str, Any]:
        """Get detailed points analysis"""
        if not self.is_connected():
            return {}
        
        try:
            # Get all activities with points
            result = self.client.table("activities").select("correct_points, missed_points, wrong_points").not_.is_("correct_points", "null").execute()
            
            correct_points = []
            missed_points = []
            wrong_points = []
            
            for activity in result.data:
                correct_points.extend(activity.get("correct_points", []))
                missed_points.extend(activity.get("missed_points", []))
                wrong_points.extend(activity.get("wrong_points", []))
            
            # Count occurrences
            def count_points(points_list):
                point_counts = {}
                for point in points_list:
                    point_counts[point] = point_counts.get(point, 0) + 1
                return sorted(point_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_activities": len(result.data),
                "points_analysis": {
                    "correct_points": {
                        "total_count": len(correct_points),
                        "most_common": [{"point": p, "frequency": f} for p, f in count_points(correct_points)]
                    },
                    "missed_points": {
                        "total_count": len(missed_points),
                        "most_common": [{"point": p, "frequency": f} for p, f in count_points(missed_points)]
                    },
                    "wrong_points": {
                        "total_count": len(wrong_points),
                        "most_common": [{"point": p, "frequency": f} for p, f in count_points(wrong_points)]
                    }
                }
            }
        except Exception as e:
            print(f"❌ Failed to get points analysis: {e}")
            return {}
    
    async def get_reading_modes_analytics(self) -> Dict[str, Any]:
        """Get reading modes analytics"""
        if not self.is_connected():
            return {}
        
        try:
            result = self.client.table("activities").select("reading_mode, accuracy_score").not_.is_("reading_mode", "null").execute()
            
            mode_stats = {}
            total_activities = len(result.data)
            
            for activity in result.data:
                mode = activity["reading_mode"]
                accuracy = activity.get("accuracy_score")
                
                if mode not in mode_stats:
                    mode_stats[mode] = {
                        "count": 0,
                        "accuracies": []
                    }
                
                mode_stats[mode]["count"] += 1
                if accuracy is not None:
                    mode_stats[mode]["accuracies"].append(accuracy)
            
            # Calculate statistics for each mode
            for mode, stats in mode_stats.items():
                accuracies = stats["accuracies"]
                if accuracies:
                    stats["percentage"] = round((stats["count"] / total_activities) * 100, 2)
                    stats["average_accuracy"] = round(sum(accuracies) / len(accuracies), 2)
                    stats["min_accuracy"] = min(accuracies)
                    stats["max_accuracy"] = max(accuracies)
                else:
                    stats["percentage"] = round((stats["count"] / total_activities) * 100, 2)
                    stats["average_accuracy"] = 0
                    stats["min_accuracy"] = 0
                    stats["max_accuracy"] = 0
                
                del stats["accuracies"]
            
            # Find most popular and highest accuracy modes
            most_popular_mode = max(mode_stats.items(), key=lambda x: x[1]["count"])[0] if mode_stats else "detailed"
            highest_accuracy_mode = max(mode_stats.items(), key=lambda x: x[1]["average_accuracy"])[0] if mode_stats else "detailed"
            
            return {
                "total_activities": total_activities,
                "reading_modes": mode_stats,
                "most_popular_mode": most_popular_mode,
                "highest_accuracy_mode": highest_accuracy_mode
            }
        except Exception as e:
            print(f"❌ Failed to get reading modes analytics: {e}")
            return {}
    
    async def get_user_reading_modes(self, email: str) -> Dict[str, Any]:
        """Get reading mode preferences for a specific user"""
        if not self.is_connected():
            return {}
        
        try:
            result = self.client.table("activities").select("reading_mode, accuracy_score").eq("user_email", email).not_.is_("reading_mode", "null").execute()
            
            mode_stats = {}
            total_activities = len(result.data)
            
            for activity in result.data:
                mode = activity["reading_mode"]
                accuracy = activity.get("accuracy_score")
                
                if mode not in mode_stats:
                    mode_stats[mode] = {
                        "count": 0,
                        "accuracies": []
                    }
                
                mode_stats[mode]["count"] += 1
                if accuracy is not None:
                    mode_stats[mode]["accuracies"].append(accuracy)
            
            # Calculate statistics for each mode
            for mode, stats in mode_stats.items():
                accuracies = stats["accuracies"]
                if accuracies:
                    stats["percentage"] = round((stats["count"] / total_activities) * 100, 2)
                    stats["average_accuracy"] = round(sum(accuracies) / len(accuracies), 2)
                else:
                    stats["percentage"] = round((stats["count"] / total_activities) * 100, 2)
                    stats["average_accuracy"] = 0
                
                del stats["accuracies"]
            
            # Find preferred and best performing modes
            preferred_mode = max(mode_stats.items(), key=lambda x: x[1]["count"])[0] if mode_stats else "detailed"
            best_performing_mode = max(mode_stats.items(), key=lambda x: x[1]["average_accuracy"])[0] if mode_stats else "detailed"
            
            return {
                "user_email": email,
                "preferred_mode": preferred_mode,
                "best_performing_mode": best_performing_mode,
                "mode_preferences": mode_stats
            }
        except Exception as e:
            print(f"❌ Failed to get user reading modes: {e}")
            return {} 