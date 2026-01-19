# Smart Records System - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                        │
│                     (HTML Templates)                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  login.html  │  index.html  │ view_record  │  reports.html  │
│  signup.html │  add.html    │    .html     │                │
│  edit.html   │              │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION                       │
│                         (app.py)                             │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   auth_bp    │  record_bp   │  comment_bp  │   report_bp    │
│              │              │              │                │
│ - login      │ - dashboard  │ - add        │ - reports      │
│ - signup     │ - add        │ - edit       │ - export PDF   │
│ - logout     │ - edit       │ - delete     │                │
│              │ - delete     │              │                │
│              │ - view       │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC                          │
│                        (Models Layer)                        │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  UserModel   │ RecordModel  │CommentModel  │   Database     │
│              │              │              │   (Singleton)  │
│- create_user │- create      │- create      │                │
│- authenticate│- read_all    │- get_by_rec  │- users         │
│- get_by_id   │- get_by_id   │- update      │- records       │
│              │- update      │- delete      │- comments      │
│              │- delete      │- get_stats   │                │
│              │- search      │              │                │
│              │- get_stats   │              │                │
└──────────────┴──────────────┴──────────────┴────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                          │
│                     MongoDB Collections                      │
├──────────────┬──────────────┬──────────────────────────────┤
│    Users     │   Records    │         Comments              │
│              │              │                               │
│ _id          │ _id          │ _id                           │
│ username     │ user_id  ────┼──> user_id                   │
│ password     │ title        │    record_id ───> Records._id │
│ full_name    │ description  │    content                    │
│ created_at   │ category     │    created_at                 │
│              │ date_added   │    updated_at                 │
│              │ status       │                               │
└──────────────┴──────────────┴───────────────────────────────┘
```

## Data Relationships

```
┌──────────┐         1:N         ┌──────────┐
│  Users   │◄────────────────────│ Records  │
└──────────┘                     └──────────┘
     │                                │
     │                                │
     │ 1:N                           │ 1:N
     │                                │
     ▼                                ▼
┌─────────────────────────────────────────┐
│              Comments                   │
│  (belongs to User AND Record)           │
└─────────────────────────────────────────┘
```

## Request Flow Example: Adding a Comment

```
1. User clicks "Add Comment" on view_record.html
   │
   ▼
2. POST /add/<record_id> → comment_routes.py
   │
   ▼
3. comment_routes.add_comment()
   ├── Validates user is logged in (login_required decorator)
   ├── Gets user_id from session
   └── Gets comment content from form
   │
   ▼
4. CommentModel.create_comment(record_id, user_id, content)
   ├── Creates comment document
   ├── Inserts into MongoDB comments collection
   └── Returns (success, message)
   │
   ▼
5. Redirect to view_record.html
   │
   ▼
6. record_routes.view_record(record_id)
   ├── Gets record from RecordModel
   ├── Gets comments from CommentModel
   └── Renders template with record + comments
   │
   ▼
7. User sees updated page with new comment
```

## Configuration Management

```
┌─────────────┐
│   .env      │
│ (secrets)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  config.py  │
├─────────────┤
│ - Dev       │
│ - Prod      │
│ - Test      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   app.py    │
│ create_app()│
└─────────────┘
```

## Security Features

1. **Authentication**
   - Password hashing (SHA256)
   - Session-based authentication
   - Login required decorator

2. **Authorization**
   - Users can only view their own records
   - Users can only edit/delete their own comments
   - Ownership verification in routes

3. **Data Validation**
   - Form input validation
   - Required field checks
   - Content sanitization

## Scalability Considerations

1. **Database Connection**
   - Singleton pattern for connection pooling
   - Efficient resource usage

2. **Blueprint Architecture**
   - Easy to add new features
   - Can be deployed as microservices

3. **Modular Design**
   - Each component can be scaled independently
   - Easy to add caching layer
   - Ready for API versioning

## Performance Optimizations

1. **Database Queries**
   - Indexed fields (_id, user_id, record_id)
   - Aggregation pipelines for statistics
   - Sorted queries for recent data

2. **PDF Generation**
   - Generated on-demand
   - In-memory processing (BytesIO)
   - No temporary files

3. **Frontend**
   - Tailwind CSS from CDN
   - Chart.js for visualizations
   - Minimal JavaScript
