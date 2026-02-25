"""
SEO API Tests - Tests for sitemap.xml and robots.txt endpoints
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestSEOEndpoints:
    """Tests for SEO endpoints (sitemap.xml and robots.txt)"""

    def test_sitemap_xml_returns_200(self):
        """Test that /api/sitemap.xml returns status 200"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Sitemap.xml returns 200 OK")

    def test_sitemap_xml_content_type(self):
        """Test that sitemap returns XML content type"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content_type = response.headers.get('content-type', '')
        assert 'xml' in content_type.lower(), f"Expected XML content-type, got {content_type}"
        print("✓ Sitemap.xml returns correct content-type (XML)")

    def test_sitemap_xml_valid_structure(self):
        """Test that sitemap has valid XML structure"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Check for XML declaration
        assert '<?xml version="1.0" encoding="UTF-8"?>' in content, "Missing XML declaration"
        # Check for urlset element
        assert '<urlset' in content, "Missing urlset element"
        assert '</urlset>' in content, "Missing urlset closing tag"
        # Check for xmlns
        assert 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"' in content, "Missing sitemap namespace"
        print("✓ Sitemap.xml has valid XML structure")

    def test_sitemap_contains_homepage(self):
        """Test that sitemap contains homepage URL"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Check for homepage URL
        assert f'<loc>{BASE_URL}/</loc>' in content, "Homepage URL missing from sitemap"
        print("✓ Sitemap.xml contains homepage URL")

    def test_sitemap_contains_multilingual_leagues(self):
        """Test that sitemap contains multilingual league URLs with hreflang"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Check for Italian league URL (Serie A)
        assert '/biglietti-serie-a' in content, "Italian league URL missing"
        # Check for English league URL
        assert '/serie-a-tickets' in content, "English league URL missing"
        # Check for Spanish league URL
        assert '/entradas-serie-a' in content, "Spanish league URL missing"
        
        # Check for hreflang tags
        assert 'hreflang="it"' in content, "Italian hreflang missing"
        assert 'hreflang="en"' in content, "English hreflang missing"
        assert 'hreflang="es"' in content, "Spanish hreflang missing"
        print("✓ Sitemap.xml contains multilingual league URLs with hreflang")

    def test_sitemap_contains_team_urls(self):
        """Test that sitemap contains team URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Check for team URLs (e.g., Inter)
        assert '/biglietti-inter' in content, "Team URL (biglietti-inter) missing"
        assert '/inter-tickets' in content, "Team URL (inter-tickets) missing"
        assert '/entradas-inter' in content, "Team URL (entradas-inter) missing"
        print("✓ Sitemap.xml contains team URLs")

    def test_sitemap_contains_event_urls(self):
        """Test that sitemap contains event URLs from database"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Check for event URLs pattern
        assert '/event/' in content, "Event URLs missing from sitemap"
        print("✓ Sitemap.xml contains event URLs")

    def test_sitemap_priority_values(self):
        """Test that sitemap has correct priority values"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        content = response.text
        
        # Homepage should have highest priority
        assert '<priority>1.0</priority>' in content, "Homepage priority 1.0 missing"
        # Leagues should have 0.9 priority
        assert '<priority>0.9</priority>' in content, "League priority 0.9 missing"
        # Teams should have 0.8 priority
        assert '<priority>0.8</priority>' in content, "Team priority 0.8 missing"
        # Events should have 0.7 priority
        assert '<priority>0.7</priority>' in content, "Event priority 0.7 missing"
        print("✓ Sitemap.xml has correct priority values")

    def test_robots_txt_returns_200(self):
        """Test that /api/robots.txt returns status 200"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ Robots.txt returns 200 OK")

    def test_robots_txt_content_type(self):
        """Test that robots.txt returns text/plain content type"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content_type = response.headers.get('content-type', '')
        assert 'text/plain' in content_type.lower(), f"Expected text/plain, got {content_type}"
        print("✓ Robots.txt returns correct content-type (text/plain)")

    def test_robots_txt_allows_all(self):
        """Test that robots.txt allows all user agents"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        
        assert 'User-agent: *' in content, "User-agent: * missing"
        assert 'Allow: /' in content, "Allow: / missing"
        print("✓ Robots.txt allows all user agents")

    def test_robots_txt_contains_sitemap_url(self):
        """Test that robots.txt contains sitemap URL"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        
        assert 'Sitemap:' in content, "Sitemap directive missing"
        assert '/api/sitemap.xml' in content, "Sitemap URL missing"
        print("✓ Robots.txt contains sitemap URL")

    def test_robots_txt_disallows_admin(self):
        """Test that robots.txt disallows admin area"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        content = response.text
        
        assert 'Disallow: /admin/' in content, "Admin disallow rule missing"
        print("✓ Robots.txt disallows admin area")


class TestAPIEndpoints:
    """Test basic API endpoints are working"""

    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        print("✓ API root endpoint working")

    def test_events_endpoint(self):
        """Test events endpoint"""
        response = requests.get(f"{BASE_URL}/api/events?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert 'events' in data
        assert isinstance(data['events'], list)
        print(f"✓ Events endpoint working - returned {len(data['events'])} events")

    def test_single_event_endpoint(self):
        """Test getting a single event"""
        # First get list of events
        response = requests.get(f"{BASE_URL}/api/events?limit=1")
        assert response.status_code == 200
        data = response.json()
        
        if data['events']:
            event_id = data['events'][0]['id']
            # Get single event
            response = requests.get(f"{BASE_URL}/api/events/{event_id}")
            assert response.status_code == 200
            event = response.json()
            assert 'title' in event
            print(f"✓ Single event endpoint working - event: {event['title'][:50]}")
        else:
            print("⚠ No events found to test single event endpoint")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
