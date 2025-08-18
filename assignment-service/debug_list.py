#!/usr/bin/env python3
"""Debug list assignments endpoint"""

import asyncio
import aiohttp

ASSIGNMENT_SERVICE = "http://localhost:8004"

async def debug_list():
    async with aiohttp.ClientSession() as session:
        print("Testing list assignments endpoint...")
        
        try:
            url = f"{ASSIGNMENT_SERVICE}/api/assignments/"
            print(f"URL: {url}")
            
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response: {text}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_list())
