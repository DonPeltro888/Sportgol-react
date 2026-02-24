# Golevents Backend Integration Contracts

## Overview
Full-stack sports event booking platform with MongoDB, FastAPI backend, and React frontend.

## Database Schema

### Collections

#### 1. **events**
```javascript
{
  _id: ObjectId,
  title: String,          // "Roma – Juventus"
  image: String,          // URL to stadium image
  categories: [String],   // ["AS ROMA", "FOOTBALL", "JUVENTUS FC", "SERIE A"]
  date: String,          // "March 1, 2026"
  location: String,       // "Stadio Olimpico"
  stadium: String,        // Stadium name
  price_range: {
    min: Number,
    max: Number
  },
  available_tickets: Number,
  featured: Boolean,
  league: String,         // "SERIE A", "PREMIER LEAGUE", etc.
  created_at: Date,
  updated_at: Date
}
```

#### 2. **categories**
```javascript
{
  _id: ObjectId,
  name: String,           // "AC Milan"
  label: String,          // "Tickets"
  slug: String,           // "ac-milan"
  event_count: Number,
  created_at: Date
}
```

## API Endpoints

### Events APIs

#### GET `/api/events`
- **Description**: Get all events with pagination and filtering
- **Query Params**:
  - `page` (default: 1)
  - `limit` (default: 20)
  - `search` (optional): Search by title, location, categories
  - `league` (optional): Filter by league
  - `featured` (optional): true/false
  - `date_from` (optional): Filter events from date
  - `date_to` (optional): Filter events to date
- **Response**: 
```json
{
  "events": [...],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

#### GET `/api/events/{event_id}`
- **Description**: Get single event details
- **Response**: Single event object

#### POST `/api/events` (Admin)
- **Description**: Create new event
- **Body**: Event object
- **Response**: Created event

#### PUT `/api/events/{event_id}` (Admin)
- **Description**: Update event
- **Body**: Event object
- **Response**: Updated event

#### DELETE `/api/events/{event_id}` (Admin)
- **Description**: Delete event
- **Response**: Success message

### Categories APIs

#### GET `/api/categories`
- **Description**: Get all categories
- **Response**: Array of categories

#### GET `/api/categories/{slug}`
- **Description**: Get category with events
- **Response**: Category object with events array

### Search APIs

#### GET `/api/search`
- **Description**: Global search across events
- **Query Params**:
  - `q`: Search query
- **Response**: Array of matching events

## Frontend-Backend Integration

### Data Flow

1. **Initial Load**:
   - Frontend fetches events from `/api/events`
   - Frontend fetches categories from `/api/categories`
   - Replace mock data in mockEvents.js with API calls

2. **Search**:
   - User types in search bar
   - Frontend calls `/api/search?q={query}`
   - Display filtered results

3. **Filtering**:
   - User clicks league/category
   - Frontend calls `/api/events?league={league}` or `/api/categories/{slug}`
   - Display filtered results

### Files to Update

#### Frontend Changes:
1. **src/services/api.js** (NEW):
   - Create axios instance
   - Define all API methods
   
2. **src/App.js**:
   - Replace mockEvents with API calls
   - Add loading states
   - Add error handling

3. **src/components/EventsGrid.jsx**:
   - Add loading skeleton
   - Handle empty states

4. **src/data/mockEvents.js**:
   - Keep as fallback/demo data
   - Comment out after backend integration

#### Backend Files:
1. **backend/models/event.py** (NEW)
2. **backend/models/category.py** (NEW)
3. **backend/routes/events.py** (NEW)
4. **backend/routes/categories.py** (NEW)
5. **backend/routes/search.py** (NEW)
6. **backend/server.py** (UPDATE)
7. **backend/seed_data.py** (NEW) - Populate initial data

## Implementation Steps

### Phase 1: Backend Setup
1. Create MongoDB models
2. Create API routes
3. Add seed data script
4. Test with curl/Postman

### Phase 2: Frontend Integration
1. Create API service layer
2. Update App.js to use APIs
3. Add loading states
4. Add error handling
5. Test search functionality

### Phase 3: Testing
1. Test all API endpoints
2. Test frontend-backend integration
3. Test search and filtering
4. Test error scenarios

## Mock Data Migration

Current mock data in `mockEvents.js` will be:
1. Migrated to MongoDB via seed script
2. Frontend will fetch from API instead of importing mock
3. Keep mock file as backup for offline demo

## Notes
- All API routes must be prefixed with `/api` for Kubernetes routing
- Use environment variables for MongoDB connection
- Implement proper error handling on both frontend and backend
- Add loading states for better UX
- Consider adding pagination for better performance
