#!/usr/bin/env python3
"""Debug end session endpoint"""

import asyncio
import aiohttp

ASSIGNMENT_SERVICE = "http://localhost:8004"

async def debug_end_session():
    async with aiohttp.ClientSession() as session:
        print("Testing end session endpoint...")
        
        try:
            # First start a session
            start_url = f"{ASSIGNMENT_SERVICE}/api/sessions/assignments/1/start?student_id=1"
            async with session.post(start_url) as response:
                if response.status == 201:
                    session_data = await response.json()
                    session_id = session_data['id']
                    print(f"Started session {session_id}")
                    
                    # Now end it
                    end_url = f"{ASSIGNMENT_SERVICE}/api/sessions/{session_id}/end"
                    end_data = {"items_studied": 5}
                    
                    async with session.post(end_url, json=end_data) as end_response:
                        print(f"End status: {end_response.status}")
                        text = await end_response.text()
                        print(f"End response: {text}")
                else:
                    print(f"Failed to start session: {response.status}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_end_session())
