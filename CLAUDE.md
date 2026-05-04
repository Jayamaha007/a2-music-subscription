# COSC2626 — AWS Cloud Music Subscription App
## Project Instructions for Claude Code

**Course:** COSC2626 Cloud Computing — RMIT University
**Due:** Friday 8 May 2026, 11:59 PM
**Goal:** Cloud-based music subscription web app using AWS services.

---

## Current State of the Project

### ✅ Done
- Full repository structure scaffolded and committed to GitHub (`Jayamaha007/a2-music-subscription`)
- **Frontend** — fully implemented:
  - `frontend/login.html` — email + password login, redirects to main on success
  - `frontend/register.html` — email + username + password registration
  - `frontend/main.html` — user area, subscriptions sidebar, music search + subscribe/unsubscribe
  - `frontend/css/styles.css` — dark theme, responsive layout
  - `frontend/js/app.js` — full API client (`API.login`, `API.register`, `API.queryMusic`, `API.getSubscriptions`, `API.subscribe`, `API.unsubscribe`)
- **Mock server** — `mock/mock_server.py` runs on port 5001 for local frontend testing
- **Backend scaffolds** — placeholder files exist for EC2, ECS, and Lambda backends

### 🔲 Still To Do
- `init/` — implement all 4 initialisation scripts
- `backend/ec2/routes/` — implement all route handlers
- `backend/ecs/routes/` — implement all route handlers (same as EC2)
- `backend/lambda/` — implement all Lambda handlers + shared helpers
- `docs/schema_design.md` — document DynamoDB PK/SK/GSI/LSI decisions
- AWS deployment (EC2, ECS/ECR, Lambda + API Gateway)

---

## Repository Structure

```
a2-music-subscription/
├── .gitignore
├── README.md
├── CLAUDE.md                          ← this file
├── init/                              # Phase 4 — four initialisation programs
│   ├── 1_seed_login_table.py          # Creates & seeds login table with 10 users
│   ├── 2_create_music_table.py        # Creates music table with key schema, GSIs, LSIs
│   ├── 3_load_songs.py                # Loads 2026a2_songs.json into music table
│   ├── 4_upload_images_to_s3.py       # Downloads artist images, uploads to S3
│   └── 2026a2_songs.json              # Song data (already in repo)
├── frontend/                          # Phase 6 — COMPLETE
│   ├── login.html
│   ├── register.html
│   ├── main.html
│   ├── css/styles.css
│   └── js/app.js                      # BASE_URL = http://localhost:5001 (mock)
├── backend/
│   ├── ec2/                           # Phase 5.1 — Flask on EC2, port 80
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   ├── setup.sh
│   │   └── routes/
│   │       ├── auth.py                # POST /login, POST /register
│   │       ├── music.py               # GET /music
│   │       └── subscriptions.py       # GET/POST/DELETE /subscriptions
│   ├── ecs/                           # Phase 5.2 — same API, Dockerised
│   │   ├── app.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── music.py
│   │       └── subscriptions.py
│   └── lambda/                        # Phase 5.3 — API Gateway + Lambda
│       ├── shared/
│       │   ├── db.py                  # boto3 DynamoDB helpers
│       │   └── s3.py                  # S3 pre-signed URL helpers
│       ├── login/handler.py           # POST /login
│       ├── register/handler.py        # POST /register
│       ├── query/handler.py           # GET /music
│       ├── subscribe/handler.py       # POST /subscriptions
│       ├── unsubscribe/handler.py     # DELETE /subscriptions
│       └── get_subscriptions/handler.py # GET /subscriptions
├── mock/
│   └── mock_server.py                 # Local dev mock API on port 5001
└── docs/
    ├── schema_design.md
    └── architecture_diagram.png       # Add manually
```

---

## API Contract (all three backends must match exactly)

| Method | Path | Request | Response |
|--------|------|---------|----------|
| POST | `/login` | `{ email, password }` | `{ success: true, user_name }` or `{ success: false, message }` |
| POST | `/register` | `{ email, user_name, password }` | `{ success: true }` or `{ success: false, message }` |
| GET | `/music` | query params: `title`, `artist`, `year`, `album` | `{ songs: [...] }` |
| GET | `/subscriptions` | query param: `email` | `{ subscriptions: [...] }` |
| POST | `/subscriptions` | `{ email, title, artist, album, year, image_url }` | `{ success: true }` |
| DELETE | `/subscriptions` | `{ email, title, artist }` | `{ success: true }` |

Song object shape: `{ title, artist, year, album, image_url }`

---

## DynamoDB Table Designs

### `login` table
| Attribute | Type | Role |
|-----------|------|------|
| `email` | String | Partition Key |
| `user_name` | String | Attribute |
| `password` | String | Attribute (plain text OK for this assignment) |

### `music` table
- Analyse `init/2026a2_songs.json` to confirm PK/SK — must avoid data loss
- Required attributes: `title`, `artist`, `year`, `album`, `image_url`
- Must have at least **1 GSI** and **1 LSI** — document rationale in `docs/schema_design.md`

### Subscriptions
- Store subscriptions in a separate DynamoDB table OR as items in an existing table
- Must support: write, delete, and query by email

---

## AWS Constraints

- IAM: use **`LabRole`** only — do not create new roles
- Elastic Beanstalk is **NOT allowed**
- All backends must run on **port 80 or 443**
- S3 images must use **pre-signed URLs** — no public bucket access
- API Gateway must use correct HTTP methods: **GET, POST, DELETE** — do not route everything through POST
- Use **`boto3`** for all AWS SDK calls in Python
- **Never commit `.env` files or AWS credentials**

---

## Frontend Notes

- `frontend/js/app.js` has a single `BASE_URL` constant at the top
- To switch backends: change `BASE_URL` to the EC2 IP, ECS ALB DNS, or API Gateway URL
- Current value: `http://localhost:5001` (mock server for local dev)
- Frontend uses `sessionStorage` to store `user_email` and `user_name` after login
- `main.html` redirects to `login.html` if session is empty

### Running locally
```bash
# Terminal 1 — mock API
cd mock && python3 mock_server.py
# Runs on http://localhost:5001

# Terminal 2 — frontend
cd frontend && python3 -m http.server 3000
# Open http://localhost:3000/login.html

# Test credentials
# john@example.com / password123  (has 3 subscriptions pre-loaded)
# jane@example.com / password123
```

---

## Backend Implementation Notes

### EC2 / ECS
- Use **Flask** with `flask-cors` enabled
- Register blueprints: `auth_bp`, `music_bp`, `subscriptions_bp`
- Run on `host="0.0.0.0", port=80`
- EC2: use `setup.sh` as user-data script to install deps and start server
- ECS: build Docker image from `backend/ecs/Dockerfile`, push to ECR

### Lambda
- Each handler file has a single `lambda_handler(event, context)` function
- Parse request body from `event["body"]` (JSON string), query params from `event["queryStringParameters"]`
- Return responses as: `{ "statusCode": 200, "headers": { "Access-Control-Allow-Origin": "*" }, "body": json.dumps({...}) }`
- Copy `shared/` into each Lambda deployment package OR use a Lambda Layer
- API Gateway: create HTTP API, map routes to Lambda functions using correct HTTP methods

---

## Submission Checklist

- [ ] Group formed on Canvas before 7 May 2026 11:59 PM
- [ ] Work log filled in throughout
- [ ] All 4 init scripts working and tested
- [ ] EC2 backend deployed and tested on port 80
- [ ] ECS backend deployed (Docker image in ECR) and tested on port 80
- [ ] Lambda + API Gateway deployed, all HTTP methods correct
- [ ] Frontend tested against all three backends (swap BASE_URL)
- [ ] Demo scenarios tested: **"Taylor Swift — Fearless"**, **"Jimmy Buffett — 1974"**
- [ ] Report written (architecture diagram, frontend justification, backend comparison, schema justification)
- [ ] Files named: `GroupLeaderStudentID_Group<N>.zip`, `_report.pdf`, `_worklog.pdf`
- [ ] Submitted via Canvas > Assignments > Assessment 2
