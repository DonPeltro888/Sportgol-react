from fastapi import APIRouter
from fastapi.responses import Response
from database import db
from datetime import datetime
import os

router = APIRouter(prefix="/api", tags=["seo"])

BASE_URL = os.environ.get("BASE_URL", "https://campionato-demo.preview.emergentagent.com")

@router.get("/sitemap.xml")
async def sitemap():
    """Generate dynamic sitemap.xml"""
    
    urls = []
    
    # Static pages
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/about", "priority": "0.5", "changefreq": "monthly"},
    ]
    
    for page in static_pages:
        urls.append(f"""
    <url>
        <loc>{BASE_URL}{page['loc']}</loc>
        <changefreq>{page['changefreq']}</changefreq>
        <priority>{page['priority']}</priority>
    </url>""")
    
    # Events
    events = await db.events.find({}, {"_id": 1, "date": 1}).to_list(1000)
    for event in events:
        urls.append(f"""
    <url>
        <loc>{BASE_URL}/event/{str(event['_id'])}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>""")
    
    # Categories/Leagues
    categories = await db.categories.find({}, {"slug": 1}).to_list(100)
    for cat in categories:
        if cat.get("slug"):
            urls.append(f"""
    <url>
        <loc>{BASE_URL}/league/{cat['slug']}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>""")
    
    # Menu Categories (leagues & cups)
    menu_cats = await db.menu_categories.find({}, {"slug": 1}).to_list(50)
    for cat in menu_cats:
        if cat.get("slug"):
            urls.append(f"""
    <url>
        <loc>{BASE_URL}/league/{cat['slug']}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.7</priority>
    </url>""")
    
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{''.join(urls)}
</urlset>"""
    
    return Response(content=sitemap_xml, media_type="application/xml")


@router.get("/robots.txt")
async def robots():
    """Generate robots.txt"""
    
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {BASE_URL}/sitemap.xml

# Disallow admin
Disallow: /admin/
"""
    
    return Response(content=robots_txt, media_type="text/plain")
