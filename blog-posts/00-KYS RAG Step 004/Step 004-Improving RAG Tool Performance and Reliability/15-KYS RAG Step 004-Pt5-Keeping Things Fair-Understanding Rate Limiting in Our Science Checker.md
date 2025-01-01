# Keeping Things Fair: Understanding Rate Limiting in Our Science Checker

Have you ever been to a busy ice cream shop where they ask people to wait in line so everyone gets served? Rate limiting in software works the same way. It helps make sure everyone gets a fair chance to use our science checking tool, even when lots of people want to use it at once. Today, we'll explore how we build this fair-play system into our tool.

## Why Do We Need Rate Limiting?

Imagine if one person tried to check a thousand scientific articles all at once. This could:
1. Make the tool slow for everyone else
2. Use up all our computing resources
3. Cost us extra money for server usage
4. Potentially crash our system

Let's see how we build a system to prevent these problems:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import logging
import asyncio
from redis import Redis
from fastapi import HTTPException, BackgroundTasks
from app.core.database import database

@dataclass
class RateLimitData:
    """Keeps track of how many requests each user makes"""
    requests: int
    first_request_time: datetime
    last_request_time: datetime

class RateLimiter:
    """Manages fair usage of our science checking tool"""
    
    def __init__(self):
        """Set up our rate limiting system"""
        # Connect to our Redis database for tracking
        self.redis = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD
        )
        
        # Set up different rate limits for different actions
        self.limits = {
            "study_analysis": {
                "requests": 100,    # Number of requests allowed
                "window": 3600,     # Time window in seconds (1 hour)
                "burst": 10         # Maximum requests at once
            },
            "article_check": {
                "requests": 50,
                "window": 3600,
                "burst": 5
            },
            "claim_verification": {
                "requests": 200,
                "window": 3600,
                "burst": 20
            }
        }
        
        # Keep track of background tasks
        self.background_tasks: Dict[str, List[str]] = {}
        
        # Set up logging
        self.logger = logging.getLogger(__name__)

    async def check_rate_limit(
        self,
        user_id: str,
        action_type: str
    ) -> Tuple[bool, Optional[int]]:
        """Check if a user can make another request"""
        try:
            # Get the limits for this type of action
            limit_config = self.limits.get(action_type)
            if not limit_config:
                raise ValueError(f"Unknown action type: {action_type}")
            
            # Create a unique key for this user and action
            rate_key = f"rate:{user_id}:{action_type}"
            
            # Get current usage data
            usage_data = await self._get_usage_data(rate_key)
            
            # Check if we're within limits
            current_time = datetime.utcnow()
            window_start = current_time - timedelta(
                seconds=limit_config['window']
            )
            
            if usage_data:
                # Clean up old data
                if usage_data.first_request_time < window_start:
                    await self._reset_usage_data(rate_key)
                    return True, None
                
                # Check if we're over the limit
                if usage_data.requests >= limit_config['requests']:
                    # Calculate wait time
                    wait_time = int(
                        (window_start - usage_data.first_request_time)
                        .total_seconds()
                    )
                    return False, wait_time
                
                # Check burst limit
                recent_requests = await self._count_recent_requests(
                    rate_key,
                    seconds=60
                )
                if recent_requests >= limit_config['burst']:
                    return False, 60  # Wait a minute
            
            # If we get here, request is allowed
            await self._update_usage_data(rate_key, current_time)
            return True, None
            
        except Exception as e:
            self.logger.error(f"Rate limit check failed: {e}")
            # If rate limiting fails, allow the request but log the error
            return True, None

    async def _get_usage_data(self, key: str) -> Optional[RateLimitData]:
        """Get current usage information for a user"""
        try:
            data = self.redis.hgetall(key)
            if not data:
                return None
                
            return RateLimitData(
                requests=int(data[b'requests']),
                first_request_time=datetime.fromisoformat(
                    data[b'first_request_time'].decode()
                ),
                last_request_time=datetime.fromisoformat(
                    data[b'last_request_time'].decode()
                )
            )
        except Exception as e:
            self.logger.error(f"Error getting usage data: {e}")
            return None

    async def _update_usage_data(
        self,
        key: str,
        request_time: datetime
    ) -> None:
        """Update usage tracking information"""
        try:
            current_data = await self._get_usage_data(key)
            
            if current_data:
                # Update existing data
                self.redis.hset(key, mapping={
                    'requests': current_data.requests + 1,
                    'last_request_time': request_time.isoformat()
                })
            else:
                # Create new tracking data
                self.redis.hset(key, mapping={
                    'requests': 1,
                    'first_request_time': request_time.isoformat(),
                    'last_request_time': request_time.isoformat()
                })
                
            # Set expiration
            self.redis.expire(key, self.limits['study_analysis']['window'])
            
        except Exception as e:
            self.logger.error(f"Error updating usage data: {e}")

    async def process_in_background(
        self,
        task_id: str,
        user_id: str,
        action_type: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, str]:
        """Handle long-running tasks in the background"""
        try:
            # Check if user has too many background tasks
            user_tasks = self.background_tasks.get(user_id, [])
            if len(user_tasks) >= 5:  # Maximum concurrent tasks
                raise HTTPException(
                    status_code=429,
                    detail="Too many background tasks. Please wait."
                )
            
            # Add task to tracking
            if user_id not in self.background_tasks:
                self.background_tasks[user_id] = []
            self.background_tasks[user_id].append(task_id)
            
            # Add the actual task to background processing
            background_tasks.add_task(
                self._run_background_task,
                task_id,
                user_id,
                action_type
            )
            
            return {
                "task_id": task_id,
                "status": "processing",
                "message": "Task started in background"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting background task: {e}")
            raise

    async def _run_background_task(
        self,
        task_id: str,
        user_id: str,
        action_type: str
    ) -> None:
        """Run a task in the background"""
        try:
            # Do the actual work here
            # This would call the appropriate service method
            
            # Clean up when done
            if user_id in self.background_tasks:
                self.background_tasks[user_id].remove(task_id)
                
        except Exception as e:
            self.logger.error(f"Background task failed: {e}")
            # Update task status to failed
            await self._update_task_status(task_id, "failed", str(e))
            
        finally:
            # Always clean up task tracking
            if user_id in self.background_tasks:
                self.background_tasks[user_id].remove(task_id)

class StudyAnalysisService:
    """Service for analyzing scientific studies"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.logger = logging.getLogger(__name__)

    async def analyze_study(
        self,
        study_id: str,
        user_id: str,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Analyze a scientific study with rate limiting"""
        try:
            # Check rate limit
            allowed, wait_time = await self.rate_limiter.check_rate_limit(
                user_id,
                "study_analysis"
            )
            
            if not allowed:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Please wait {wait_time} seconds."
                )
            
            # Check if this needs background processing
            if await self._needs_background_processing(study_id):
                task_id = f"study_analysis_{study_id}_{datetime.utcnow().timestamp()}"
                return await self.rate_limiter.process_in_background(
                    task_id,
                    user_id,
                    "study_analysis",
                    background_tasks
                )
            
            # If not, process normally
            return await self._perform_analysis(study_id)
            
        except Exception as e:
            self.logger.error(f"Study analysis failed: {e}")
            raise

```

## How Our Rate Limiter Works

Let's break down the important parts of our system:

### 1. Different Limits for Different Actions
We set different limits based on what people are trying to do:

```python
self.limits = {
    "study_analysis": {
        "requests": 100,    # Requests per hour
        "window": 3600,     # One hour in seconds
        "burst": 10         # Maximum at once
    },
    ...
}
```

This means:
- You can analyze up to 100 studies per hour
- But you can't do more than 10 at the exact same time
- Different actions (like checking articles) have their own limits

### 2. Keeping Track of Usage
We carefully track how much each person uses the tool:

```python
@dataclass
class RateLimitData:
    requests: int
    first_request_time: datetime
    last_request_time: datetime
```

This helps us:
- Know how many requests someone has made
- See when they started using the tool
- Track their most recent request

### 3. Background Processing
For big jobs, we use a special system:

```python
async def process_in_background(
    self,
    task_id: str,
    user_id: str,
    action_type: str,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
```

This:
- Puts big tasks in a separate line
- Lets people know their request is being worked on
- Prevents one big job from blocking others

## Making It Fair for Everyone

Our system uses several strategies to keep things fair:

### 1. Time Windows
We look at usage over time:
```python
window_start = current_time - timedelta(seconds=limit_config['window'])
```

This means:
- Limits reset after a certain time
- People can't use up all their requests at once
- Everyone gets a fresh start each hour

### 2. Burst Protection
We prevent too many requests at once:
```python
if recent_requests >= limit_config['burst']:
    return False, 60  # Wait a minute
```

This stops:
- Automated scripts from overwhelming the system
- Accidental duplicate requests
- Intentional misuse

### 3. Smart Queuing
For bigger tasks:
```python
if await self._needs_background_processing(study_id):
    task_id = f"study_analysis_{study_id}_{datetime.utcnow().timestamp()}"
    return await self.rate_limiter.process_in_background(...)
```

This helps by:
- Moving big jobs to the background
- Letting small jobs go through quickly
- Keeping track of what's being worked on

## Real-World Example

Let's see how this works in practice:

### Scenario 1: Normal Usage
A user wants to check 5 scientific articles:
```
Request 1: Allowed immediately
Request 2: Allowed immediately
Request 3: Allowed immediately
Request 4: Allowed immediately
Request 5: Allowed immediately
```

### Scenario 2: Heavy Usage
A user tries to check 1000 articles at once:
```
Requests 1-10: Allowed (burst limit)
Request 11: "Please wait 60 seconds"
After waiting: Next batch allowed
```

### Scenario 3: Big Analysis Job
User wants to analyze a very large study:
```
Request received: "Task started in background"
User can still make other small requests
Gets notified when big job is done
```

## What's Next?

We're working on making our rate limiting even better by:
1. Adding priority queues for different types of users
2. Making smarter decisions about what needs background processing
3. Adding better feedback about wait times
4. Improving how we handle very large requests

In our next post, we'll look at how we test our rate limiting system and make sure it's working fairly. We'll also explore how to handle special cases like emergency requests or system maintenance.

Remember, good rate limiting is like a good traffic system - it keeps everything moving smoothly even when it's busy. By building these limits into our system, we help make sure everyone gets good service!
