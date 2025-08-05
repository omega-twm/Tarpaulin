#!/usr/bin/env python3
"""
Canvas AI Dashboard CLI Tool
A command-line interface for querying your Canvas data using AI.
"""

import argparse
import sys
import json
import requests
from typing import Optional
import time

class CanvasCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def _print_box(self, text: str, title: str = "", width: int = 80) -> None:
        """Print text in a nice ASCII box with proper text wrapping"""
        import textwrap
        
        # Wrap long lines
        wrapped_lines = []
        for line in text.split('\n'):
            if len(line) <= width - 4:
                wrapped_lines.append(line)
            else:
                # Wrap long lines
                wrapped = textwrap.wrap(line, width=width-4, break_long_words=False, break_on_hyphens=False)
                wrapped_lines.extend(wrapped)
        
        # Calculate box width
        content_width = max(len(line) for line in wrapped_lines) if wrapped_lines else 0
        if title:
            content_width = max(content_width, len(title) + 4)
        
        box_width = min(max(content_width + 4, 40), width)
        
        # Top border
        if title:
            title_padding = (box_width - len(title) - 4) // 2
            remaining_padding = box_width - len(title) - 4 - title_padding
            print(f"┌{title_padding * '─'} {title} {remaining_padding * '─'}┐")
        else:
            print(f"┌{'─' * (box_width - 2)}┐")
        
        # Content
        for line in wrapped_lines:
            padding = box_width - len(line) - 4
            print(f"│ {line}{' ' * padding} │")
        
        # Bottom border
        print(f"└{'─' * (box_width - 2)}┘")
        
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make HTTP request to the backend API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to Canvas AI backend\nMake sure the backend is running on:\nhttp://localhost:8000"
            self._print_box(error_msg, "CONNECTION ERROR")
            sys.exit(1)
        except requests.exceptions.Timeout:
            error_msg = "Request timed out\nBackend might be overloaded"
            self._print_box(error_msg, "TIMEOUT ERROR")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 503:
                error_msg = "Backend is not ready\nVector database might be initializing\nTry: canvas refresh"
                self._print_box(error_msg, "SERVICE UNAVAILABLE")
            elif response.status_code == 402:
                error_msg = "API quota exceeded\nCheck billing settings"
                self._print_box(error_msg, "QUOTA EXCEEDED")
            elif response.status_code == 401:
                error_msg = "API key invalid\nCheck .env configuration"
                self._print_box(error_msg, "AUTHENTICATION ERROR")
            else:
                try:
                    error_data = response.json()
                    self._print_box(error_data.get('detail', str(e)), "ERROR")
                except:
                    self._print_box(str(e), "ERROR")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            self._print_box(f"Network error: {e}", "ERROR")
            sys.exit(1)

    def health(self) -> None:
        """Check backend health status"""
        self._print_box("Checking backend status...", "SYSTEM HEALTH CHECK")
        
        result = self._make_request("GET", "/health")
        
        status = result.get("status", "unknown")
        
        # Build status report
        status_lines = []
        
        if status == "healthy":
            status_lines.append("✓ System Status: HEALTHY")
        else:
            status_lines.append(f"✗ System Status: {status.upper()}")
            
        vdb_ready = result.get('vector_db_ready')
        status_lines.append(f"{'✓' if vdb_ready else '✗'} Vector Database: {'READY' if vdb_ready else 'NOT READY'}")
        
        docs_loaded = result.get('documents_loaded', 0)
        status_lines.append(f"✓ Documents: {docs_loaded} loaded")
        
        ai_configured = result.get('openai_configured')
        status_lines.append(f"{'✓' if ai_configured else '✗'} AI Engine: {'CONFIGURED' if ai_configured else 'NOT CONFIGURED'}")
        
        canvas_configured = result.get('canvas_configured')
        status_lines.append(f"{'✓' if canvas_configured else '✗'} Canvas API: {'CONNECTED' if canvas_configured else 'NOT CONNECTED'}")
        
        self._print_box("\n".join(status_lines), "STATUS REPORT")
        
        if result.get("message"):
            self._print_box(result['message'], "NOTICE")

    def refresh(self) -> None:
        """Refresh embeddings from Canvas data"""
        refresh_msg = "Fetching latest Canvas content...\nThis may take a moment..."
        self._print_box(refresh_msg, "REFRESHING CANVAS DATA")
        
        start_time = time.time()
        result = self._make_request("POST", "/refresh-embeddings")
        elapsed = time.time() - start_time
        
        success_msg = f"{result['message']}\n"
        success_msg += f"Documents loaded: {result['documents_loaded']}\n"
        success_msg += f"Completed in {elapsed:.1f} seconds"
        
        self._print_box(success_msg, "REFRESH COMPLETE")

    def ask(self, question: str) -> None:
        """Ask a question about your Canvas data"""
        if not question.strip():
            self._print_box("Question cannot be empty", "ERROR")
            sys.exit(1)
        
        # Question header with proper formatting
        self._print_box(question, "QUERY")
        
        print("\n[INFO] Processing your question...")
        
        start_time = time.time()
        result = self._make_request("POST", "/qa", {"query": question})
        elapsed = time.time() - start_time
        
        # Answer in a nice box
        answer = result['result']
        self._print_box(answer, "RESPONSE")
        
        # Footer with timing
        stats_msg = f"Response time: {elapsed:.1f}s"
        self._print_box(stats_msg, "QUERY STATS")

    def _filter_actual_courses(self, courses):
        """Filter out information hub courses that aren't actual academic courses"""
        excluded_keywords = [
            'studentdemokratiet',
            'velkommen',
            'welcome',
            'informasjon',
            'information',
            'engasjement',
            'all you need to know',
            'alt du trenger å vite',
            'b-inf',
            'ifi'
        ]
        
        excluded_course_codes = [
            'b-inf',
            'ifi',
            'informasjon og engasjement',
            'alt du trenger å vite - all you need to know'
        ]
        
        filtered_courses = []
        for course in courses:
            course_name = course.get('name', '').lower()
            course_code = course.get('course_code', '').lower()
            
            # Check if course name or code contains excluded keywords
            is_info_hub = (
                any(keyword in course_name or keyword in course_code 
                    for keyword in excluded_keywords) or
                course_code in excluded_course_codes or
                course_name in ['b-inf', 'ifi']
            )
            
            if not is_info_hub:
                filtered_courses.append(course)
        
        return filtered_courses

    def context(self) -> None:
        """Show Canvas context data (courses, assignments, files)"""
        self._print_box("Fetching your Canvas data...", "CANVAS CONTEXT OVERVIEW")
        
        result = self._make_request("GET", "/context")
        
        all_courses = result.get("courses", [])
        courses = self._filter_actual_courses(all_courses)  # Filter out info hubs
        assignments_by_course = result.get("assignments_by_course", [])
        files_by_course = result.get("files_by_course", [])
        
        # Filter assignments and files to only include actual courses
        actual_course_ids = {course['id'] for course in courses}
        assignments_by_course = [a for a in assignments_by_course if a.get('course_id') in actual_course_ids]
        files_by_course = [f for f in files_by_course if f.get('course_id') in actual_course_ids]
        
        # Courses section
        courses_content = []
        for i, course in enumerate(courses, 1):
            name = course.get('name', 'Unknown')
            course_id = course.get('id')
            code = course.get('course_code', '')
            
            course_line = f"[{i}] {name}"
            courses_content.append(course_line)
            if code:
                courses_content.append(f"    Code: {code}")
            courses_content.append(f"    ID: {course_id}")
            if i < len(courses):
                courses_content.append("")
        
        self._print_box("\n".join(courses_content), f"COURSES ({len(courses)})")
        
        # Assignments section
        assignments_content = []
        for course_assignments in assignments_by_course:
            course_id = course_assignments.get("course_id")
            assignments = course_assignments.get("assignments", [])
            course_name = next((c['name'] for c in courses if c['id'] == course_id), f"Course {course_id}")
            
            if assignments:
                assignments_content.append(f"► {course_name} ({len(assignments)} assignments)")
                for j, assignment in enumerate(assignments[:3], 1):
                    assignments_content.append(f"  [{j}] {assignment.get('name', 'Unnamed assignment')}")
                if len(assignments) > 3:
                    assignments_content.append(f"  ... and {len(assignments) - 3} more")
            else:
                assignments_content.append(f"► {course_name} (no assignments)")
            assignments_content.append("")
        
        self._print_box("\n".join(assignments_content), "ASSIGNMENTS BY COURSE")
        
        # Files section
        files_content = []
        for course_files in files_by_course:
            course_id = course_files.get("course_id")
            files = course_files.get("files", [])
            course_name = next((c['name'] for c in courses if c['id'] == course_id), f"Course {course_id}")
            
            if files:
                files_content.append(f"► {course_name} ({len(files)} files)")
                for j, file in enumerate(files[:3], 1):
                    size = file.get('size', 0)
                    size_str = f"{size:,} bytes" if size else "Unknown size"
                    files_content.append(f"  [{j}] {file.get('display_name', 'Unknown file')}")
                    files_content.append(f"      Size: {size_str}")
                if len(files) > 3:
                    files_content.append(f"  ... and {len(files) - 3} more")
            else:
                files_content.append(f"► {course_name} (no files)")
            files_content.append("")
        
        self._print_box("\n".join(files_content), "FILES BY COURSE")

    def debug(self) -> None:
        """Show debug information about indexed documents"""
        self._print_box("Fetching debug data...", "DEBUG INFORMATION")
        
        result = self._make_request("GET", "/debug/docs")
        
        # Document statistics
        doc_types = {}
        for doc in result:
            doc_type = doc.get("type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        stats_lines = []
        for doc_type, count in doc_types.items():
            stats_lines.append(f"{doc_type:<12} {count:>6}")
        stats_lines.append(f"{'TOTAL':<12} {len(result):>6}")
        
        self._print_box("\n".join(stats_lines), "DOCUMENT STATISTICS")
        
        # Document details
        details_lines = []
        for i, doc in enumerate(result[:10], 1):  # Show first 10
            doc_type = doc.get('type', 'unknown')
            details_lines.append(f"[{i:2}] Type: {doc_type}")
            
            if doc.get('course_id'):
                details_lines.append(f"     Course ID: {doc['course_id']}")
            if doc.get('assignment_id'):
                details_lines.append(f"     Assignment ID: {doc['assignment_id']}")
            if doc.get('file_id'):
                details_lines.append(f"     File ID: {doc['file_id']}")
            
            if i < min(len(result), 10):
                details_lines.append("")
        
        if len(result) > 10:
            details_lines.append(f"... and {len(result) - 10} more documents")
        
        self._print_box("\n".join(details_lines), "DOCUMENT DETAILS")


def main():
    parser = argparse.ArgumentParser(
        description="Canvas AI Dashboard CLI - Query your Canvas data with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  canvas ask "Hvilke kurs har jeg?"
  canvas ask "Hva er mine obliger denne uken?"
  canvas health
  canvas refresh
  canvas context
        """
    )
    
    parser.add_argument(
        "--url", 
        default="http://localhost:8000",
        help="Backend URL (default: http://localhost:8000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question about your Canvas data")
    ask_parser.add_argument("question", nargs="+", help="Your question")
    
    # Health command
    subparsers.add_parser("health", help="Check backend health status")
    
    # Refresh command
    subparsers.add_parser("refresh", help="Refresh Canvas data and embeddings")
    
    # Context command
    subparsers.add_parser("context", help="Show Canvas context (courses, assignments, files)")
    
    # Debug command
    subparsers.add_parser("debug", help="Show debug information about indexed documents")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = CanvasCLI(args.url)
    
    try:
        if args.command == "ask":
            question = " ".join(args.question)
            cli.ask(question)
        elif args.command == "health":
            cli.health()
        elif args.command == "refresh":
            cli.refresh()
        elif args.command == "context":
            cli.context()
        elif args.command == "debug":
            cli.debug()
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
