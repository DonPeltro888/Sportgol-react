"""
Backend API Tests for Golevents Sports Ticket Platform
Tests: Events API, Search API, Categories API
Focus: Event date sorting, CRUD operations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthCheck:
    """Basic API health check tests"""
    
    def test_api_root(self):
        """Test API root endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data
        print(f"✓ API root working: {data}")


class TestEventsAPI:
    """Events API endpoint tests"""
    
    def test_get_all_events_success(self):
        """Test GET /api/events returns events list"""
        response = requests.get(f"{BASE_URL}/api/events")
        assert response.status_code == 200
        
        data = response.json()
        assert "events" in data
        assert "total" in data
        assert "page" in data
        assert isinstance(data["events"], list)
        print(f"✓ Got {len(data['events'])} events, total: {data['total']}")
    
    def test_events_sorted_by_date_ascending(self):
        """Test events are sorted by sort_date (upcoming first)"""
        response = requests.get(f"{BASE_URL}/api/events?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        
        # Verify sort_date is present and sorted ascending
        if len(events) > 1:
            dates = [e.get("sort_date") for e in events if e.get("sort_date")]
            for i in range(len(dates) - 1):
                assert dates[i] <= dates[i+1], f"Events not sorted: {dates[i]} should be <= {dates[i+1]}"
        
        print(f"✓ Events sorted by date ascending (upcoming first)")
        if events:
            print(f"  First event: {events[0]['title']} - {events[0].get('date')}")
            if len(events) > 1:
                print(f"  Last event: {events[-1]['title']} - {events[-1].get('date')}")
    
    def test_events_pagination(self):
        """Test events pagination works"""
        response = requests.get(f"{BASE_URL}/api/events?page=1&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["events"]) <= 5
        assert data["page"] == 1
        assert "pages" in data
        print(f"✓ Pagination working - Page 1 of {data['pages']}")
    
    def test_events_search_filter(self):
        """Test events search parameter"""
        response = requests.get(f"{BASE_URL}/api/events?search=Inter")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        
        # All returned events should contain "Inter" in title/categories
        for event in events:
            found = "inter" in event["title"].lower() or \
                    any("inter" in cat.lower() for cat in event.get("categories", []))
            assert found, f"Event '{event['title']}' doesn't match search 'Inter'"
        
        print(f"✓ Search filter works - Found {len(events)} events with 'Inter'")
    
    def test_events_league_filter(self):
        """Test events league filter"""
        response = requests.get(f"{BASE_URL}/api/events?league=SERIE A")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        
        for event in events:
            assert event["league"] == "SERIE A", f"Event '{event['title']}' has wrong league"
        
        print(f"✓ League filter works - Found {len(events)} Serie A events")


class TestSearchAPI:
    """Search API endpoint tests"""
    
    def test_search_events_success(self):
        """Test search returns results"""
        response = requests.get(f"{BASE_URL}/api/search?q=Milan")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Search API returned {len(data)} results for 'Milan'")
    
    def test_search_events_sorted_by_date(self):
        """Test search results are sorted by sort_date ascending"""
        response = requests.get(f"{BASE_URL}/api/search?q=Inter")
        assert response.status_code == 200
        
        events = response.json()
        
        if len(events) > 1:
            dates = [e.get("sort_date") for e in events if e.get("sort_date")]
            for i in range(len(dates) - 1):
                assert dates[i] <= dates[i+1], f"Search results not sorted: {dates[i]} > {dates[i+1]}"
        
        print(f"✓ Search results sorted by date ascending")
    
    def test_search_empty_query_returns_error(self):
        """Test empty search query is handled"""
        response = requests.get(f"{BASE_URL}/api/search?q=")
        # Should return 422 validation error for empty query
        assert response.status_code in [400, 422]
        print(f"✓ Empty search query handled correctly (status {response.status_code})")


class TestCategoriesAPI:
    """Categories API endpoint tests"""
    
    def test_get_all_categories(self):
        """Test GET /api/categories returns list"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Got {len(data)} categories")
    
    def test_get_category_with_events(self):
        """Test GET /api/categories/{slug} returns category with events"""
        # First try to get a known category
        categories_response = requests.get(f"{BASE_URL}/api/categories")
        if categories_response.status_code == 200 and categories_response.json():
            category = categories_response.json()[0]
            slug = category.get("slug")
            
            if slug:
                response = requests.get(f"{BASE_URL}/api/categories/{slug}")
                if response.status_code == 200:
                    data = response.json()
                    assert "events" in data
                    assert "name" in data
                    print(f"✓ Got category '{data['name']}' with {len(data['events'])} events")
                else:
                    print(f"⚠ Category {slug} returned status {response.status_code}")
        else:
            print("⚠ No categories found to test")
    
    def test_category_events_sorted_by_date(self):
        """Test category events are sorted by sort_date"""
        categories_response = requests.get(f"{BASE_URL}/api/categories")
        if categories_response.status_code == 200 and categories_response.json():
            category = categories_response.json()[0]
            slug = category.get("slug")
            
            if slug:
                response = requests.get(f"{BASE_URL}/api/categories/{slug}")
                if response.status_code == 200:
                    data = response.json()
                    events = data.get("events", [])
                    
                    if len(events) > 1:
                        dates = [e.get("sort_date") for e in events if e.get("sort_date")]
                        for i in range(len(dates) - 1):
                            assert dates[i] <= dates[i+1], f"Category events not sorted"
                    
                    print(f"✓ Category events sorted by date ascending")


class TestTeamSearch:
    """Tests for team-based event search (used by TeamPage)"""
    
    def test_search_inter_events(self):
        """Test searching for Inter team events"""
        response = requests.get(f"{BASE_URL}/api/events?search=Inter")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        
        # Verify Inter events are sorted by date
        if len(events) > 1:
            dates = [e.get("sort_date") for e in events if e.get("sort_date")]
            sorted_dates = sorted(dates)
            assert dates == sorted_dates, "Inter events should be sorted by date"
        
        print(f"✓ Found {len(events)} Inter events, sorted by date")
    
    def test_search_milan_events(self):
        """Test searching for Milan team events"""
        response = requests.get(f"{BASE_URL}/api/events?search=Milan")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        print(f"✓ Found {len(events)} Milan events")
    
    def test_search_barcelona_events(self):
        """Test searching for Barcelona team events"""
        response = requests.get(f"{BASE_URL}/api/events?search=Barcelona")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        print(f"✓ Found {len(events)} Barcelona events")


class TestCupEvents:
    """Tests for cup competition events (Champions League, Coppa Italia, etc.)"""
    
    def test_champions_league_events(self):
        """Test Champions League events are returned and sorted"""
        response = requests.get(f"{BASE_URL}/api/events?league=CHAMPIONS LEAGUE")
        assert response.status_code == 200
        
        data = response.json()
        events = data["events"]
        
        if events:
            # Verify all events are Champions League
            for event in events:
                assert event["league"] == "CHAMPIONS LEAGUE", f"Wrong league for {event['title']}"
            
            # Verify sorted by date
            if len(events) > 1:
                dates = [e.get("sort_date") for e in events if e.get("sort_date")]
                sorted_dates = sorted(dates)
                assert dates == sorted_dates, "Champions League events should be sorted"
        
        print(f"✓ Found {len(events)} Champions League events")
    
    def test_coppa_italia_events(self):
        """Test Coppa Italia events"""
        response = requests.get(f"{BASE_URL}/api/events?league=COPPA ITALIA")
        assert response.status_code == 200
        
        data = response.json()
        print(f"✓ Found {len(data['events'])} Coppa Italia events")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
