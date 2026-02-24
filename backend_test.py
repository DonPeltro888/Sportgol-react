#!/usr/bin/env python3
"""
Golevents Backend API Testing Script
Tests all backend endpoints including health check, events, categories, and search
"""

import requests
import json
import sys
from datetime import datetime
from urllib.parse import quote

# Backend URL from frontend .env
BACKEND_URL = "https://ticket-hub-eu.preview.emergentagent.com/api"

def log_test_result(test_name, success, details=""):
    """Log test results with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"[{timestamp}] {status} - {test_name}")
    if details:
        print(f"    Details: {details}")
    print()

def test_health_check():
    """Test GET /api/ - Health check endpoint"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data and "status" in data:
                log_test_result("Health Check Endpoint", True, f"Status: {data['status']}, Message: {data['message']}")
                return True
            else:
                log_test_result("Health Check Endpoint", False, "Missing required fields in response")
                return False
        else:
            log_test_result("Health Check Endpoint", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Health Check Endpoint", False, f"Exception: {str(e)}")
        return False

def test_events_pagination():
    """Test GET /api/events - Get all events with pagination"""
    try:
        # Test with pagination parameters
        response = requests.get(f"{BACKEND_URL}/events?page=1&limit=10", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["events", "total", "page", "pages"]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                log_test_result("Events Pagination", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify data types
            if (isinstance(data["events"], list) and 
                isinstance(data["total"], int) and 
                isinstance(data["page"], int) and 
                isinstance(data["pages"], int)):
                
                log_test_result("Events Pagination", True, 
                              f"Found {data['total']} total events, page {data['page']} of {data['pages']}, {len(data['events'])} events returned")
                return True
            else:
                log_test_result("Events Pagination", False, "Invalid data types in response")
                return False
        else:
            log_test_result("Events Pagination", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Events Pagination", False, f"Exception: {str(e)}")
        return False

def test_events_search():
    """Test GET /api/events?search=milan - Search events by query"""
    try:
        response = requests.get(f"{BACKEND_URL}/events?search=milan", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            if "events" in data and isinstance(data["events"], list):
                # Check if search actually filters results (if any events exist)
                search_term = "milan"
                events = data["events"]
                
                if len(events) > 0:
                    # Verify that returned events match search criteria
                    relevant_events = []
                    for event in events:
                        title_match = search_term.lower() in event.get("title", "").lower()
                        location_match = search_term.lower() in event.get("location", "").lower()
                        categories_match = search_term.lower() in str(event.get("categories", "")).lower()
                        
                        if title_match or location_match or categories_match:
                            relevant_events.append(event)
                    
                    if len(relevant_events) > 0:
                        log_test_result("Events Search", True, 
                                      f"Found {len(relevant_events)} events matching 'milan' search")
                        return True
                    else:
                        log_test_result("Events Search", False, 
                                      f"Search returned {len(events)} events but none match 'milan'")
                        return False
                else:
                    log_test_result("Events Search", True, "Search executed successfully - no events found (empty database)")
                    return True
            else:
                log_test_result("Events Search", False, "Invalid response structure")
                return False
        else:
            log_test_result("Events Search", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Events Search", False, f"Exception: {str(e)}")
        return False

def test_events_league_filter():
    """Test GET /api/events?league=SERIE A - Filter by league"""
    try:
        # URL encode the league name
        league_name = "SERIE A"
        encoded_league = quote(league_name)
        response = requests.get(f"{BACKEND_URL}/events?league={encoded_league}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if "events" in data and isinstance(data["events"], list):
                events = data["events"]
                
                if len(events) > 0:
                    # Verify that all returned events are from SERIE A
                    serie_a_events = [event for event in events if event.get("league") == league_name]
                    
                    if len(serie_a_events) == len(events):
                        log_test_result("Events League Filter", True, 
                                      f"Found {len(serie_a_events)} Serie A events")
                        return True
                    else:
                        log_test_result("Events League Filter", False, 
                                      f"Filter failed: {len(serie_a_events)} Serie A events out of {len(events)} returned")
                        return False
                else:
                    log_test_result("Events League Filter", True, 
                                  "League filter executed successfully - no Serie A events found")
                    return True
            else:
                log_test_result("Events League Filter", False, "Invalid response structure")
                return False
        else:
            log_test_result("Events League Filter", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Events League Filter", False, f"Exception: {str(e)}")
        return False

def test_categories():
    """Test GET /api/categories - Get all categories"""
    try:
        response = requests.get(f"{BACKEND_URL}/categories", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                if len(data) > 0:
                    # Check if categories have required fields
                    first_category = data[0]
                    required_fields = ["name"]  # Based on the model structure
                    
                    has_required = all(field in first_category for field in required_fields)
                    
                    if has_required:
                        log_test_result("Categories Endpoint", True, 
                                      f"Found {len(data)} categories")
                        return True
                    else:
                        log_test_result("Categories Endpoint", False, 
                                      f"Categories missing required fields: {required_fields}")
                        return False
                else:
                    log_test_result("Categories Endpoint", True, 
                                  "Categories endpoint working - no categories found (empty database)")
                    return True
            else:
                log_test_result("Categories Endpoint", False, "Expected array response")
                return False
        else:
            log_test_result("Categories Endpoint", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Categories Endpoint", False, f"Exception: {str(e)}")
        return False

def test_global_search():
    """Test GET /api/search?q=roma - Global search"""
    try:
        response = requests.get(f"{BACKEND_URL}/search?q=roma", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                search_term = "roma"
                
                if len(data) > 0:
                    # Verify that returned events match search criteria
                    relevant_events = []
                    for event in data:
                        title_match = search_term.lower() in event.get("title", "").lower()
                        location_match = search_term.lower() in event.get("location", "").lower()
                        categories_match = search_term.lower() in str(event.get("categories", "")).lower()
                        stadium_match = search_term.lower() in event.get("stadium", "").lower()
                        league_match = search_term.lower() in event.get("league", "").lower()
                        
                        if any([title_match, location_match, categories_match, stadium_match, league_match]):
                            relevant_events.append(event)
                    
                    if len(relevant_events) > 0:
                        log_test_result("Global Search", True, 
                                      f"Found {len(relevant_events)} events matching 'roma' in global search")
                        return True
                    else:
                        log_test_result("Global Search", False, 
                                      f"Global search returned {len(data)} events but none match 'roma'")
                        return False
                else:
                    log_test_result("Global Search", True, 
                                  "Global search executed successfully - no events found")
                    return True
            else:
                log_test_result("Global Search", False, "Expected array response")
                return False
        else:
            log_test_result("Global Search", False, f"Expected 200, got {response.status_code}")
            return False
            
    except Exception as e:
        log_test_result("Global Search", False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 80)
    print("GOLEVENTS BACKEND API TESTING")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Events Pagination", test_events_pagination),
        ("Events Search", test_events_search),
        ("Events League Filter", test_events_league_filter),
        ("Categories", test_categories),
        ("Global Search", test_global_search),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print()
    print(f"OVERALL: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)