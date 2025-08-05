import os
import httpx
from typing import Any, Dict, List
from dotenv import load_dotenv

load_dotenv()

CANVAS_TOKEN = os.getenv("CANVAS_API_TOKEN")
CANVAS_DOMAIN = os.getenv("CANVAS_DOMAIN")
API_BASE = f"https://{CANVAS_DOMAIN}/api/v1"
HEADERS = {"Authorization": f"Bearer {CANVAS_TOKEN}"}


async def get_user_courses() -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(headers=HEADERS) as client:
        resp = await client.get(f"{API_BASE}/courses", params={"enrollment_state": "active"})
        resp.raise_for_status()
        return resp.json()


async def get_course_assignments(course_id: int) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(headers=HEADERS) as client:
        resp = await client.get(f"{API_BASE}/courses/{course_id}/assignments")
        resp.raise_for_status()
        return resp.json()


async def get_course_files(course_id: int, fallback_attempted: bool = False) -> List[Dict[str, Any]]:
    files: List[Dict[str, Any]] = []

    async def fetch_all_pages(client: httpx.AsyncClient, url: str) -> List[Dict[str, Any]]:
        items = []
        while url:
            resp = await client.get(url)
            resp.raise_for_status()
            items.extend(resp.json())
            # Parse Link header for pagination
            links = resp.headers.get("Link", "")
            next_link = None
            for part in links.split(","):
                if 'rel="next"' in part:
                    next_link = part[part.find("<") + 1 : part.find(">")]
            url = next_link
        return items

    async with httpx.AsyncClient(headers=HEADERS) as client:
        try:
            print(f"📂 Henter filer fra /files for {course_id}")
            url = f"{API_BASE}/courses/{course_id}/files?per_page=50"
            files = await fetch_all_pages(client, url)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                if fallback_attempted:
                    print(f"⛔️ Allerede forsøkt fallback for {course_id}, hopper over.")
                    return []

                print(f"🚫 /files blokket for course {course_id}, prøver /modules fallback")
                try:
                    url = f"{API_BASE}/courses/{course_id}/modules?include=items&per_page=50"
                    modules = await fetch_all_pages(client, url)
                    for module in modules:
                        for item in module.get("items", []):
                            if item.get("type") == "File":
                                files.append({
                                    "display_name": item.get("title"),
                                    "url": item.get("html_url"),
                                    "id": item.get("content_id")
                                })
                except Exception as e2:
                    print(f"❌ Klarte ikke hente filer fra modules: {e2}")
            else:
                raise

    return files


async def fetch_student_context() -> Dict[str, Any]:
    """
    Fetches profile, active courses, and assignments for the current student.
    Returns a dict with keys: profile, courses, assignments_by_course
    """
    async with httpx.AsyncClient(headers=HEADERS) as client:
        profile_resp = await client.get(f"{API_BASE}/users/self/profile")
        profile_resp.raise_for_status()
        profile = profile_resp.json()

        resp = await client.get(
            f"{API_BASE}/courses", params={"enrollment_state": "active"}
        )
        resp.raise_for_status()
        courses = resp.json()

        assignments_by_course: List[Dict[str, Any]] = []
        for course in courses:
            cid = course.get("id")
            a_resp = await client.get(f"{API_BASE}/courses/{cid}/assignments")
            a_resp.raise_for_status()
            assignments = a_resp.json()
            assignments_by_course.append({
                "course_id": cid,
                "course_name": course.get("name"),
                "assignments": assignments,
            })

    return {
        "profile": profile,
        "courses": courses,
        "assignments_by_course": assignments_by_course,
    }
