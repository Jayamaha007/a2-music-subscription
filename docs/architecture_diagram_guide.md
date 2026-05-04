# Architecture Diagram Guide
## COSC2626 — AWS Cloud Music Subscription App

This guide describes every component that must appear in your architecture diagram and exactly how each one connects to the others. The diagram should show all three backend deployment options side-by-side, with the shared AWS data layer at the bottom.

---

## 1. Components to Include

### User / Client Layer

| Component | Label in Diagram | Notes |
|---|---|---|
| Web Browser | **Browser / User** | Runs `login.html`, `register.html`, `main.html` |
| Frontend Static Files | **Frontend (HTML/JS/CSS)** | Served locally via `python3 -m http.server 3000`, or hosted on S3 static hosting if you deploy it |

The frontend uses a single `BASE_URL` constant in `frontend/js/app.js` to reach whichever backend is active. Show this as an HTTP/HTTPS arrow from the browser to each backend option.

---

### Backend Option 1 — EC2

| Component | Label | Notes |
|---|---|---|
| EC2 Instance | **EC2 Instance (Flask, port 80)** | `t2.micro` (or similar); Flask app from `backend/ec2/app.py` |
| Security Group | **EC2 Security Group** | Inbound: TCP 80 from `0.0.0.0/0` |
| IAM Role | **LabRole** | Attached to EC2; grants DynamoDB + S3 access |

The browser sends HTTP requests directly to the EC2 public IP on port 80. The EC2 instance talks to DynamoDB and S3 via the AWS SDK (boto3) using the LabRole.

---

### Backend Option 2 — ECS / Fargate

| Component | Label | Notes |
|---|---|---|
| Application Load Balancer | **ALB (music-app-alb)** | Internet-facing; listens on port 80 |
| ALB Security Group | **ALB SG** | Inbound TCP 80 from `0.0.0.0/0` |
| Target Group | **Target Group (music-app-tg)** | IP-type; health check on `/health` |
| ECS Fargate Cluster | **ECS Cluster (music-cluster)** | Serverless compute; no EC2 to manage |
| ECS Service | **ECS Service (music-service)** | Desired count 1; auto-restarts failed tasks |
| ECS Task / Container | **Fargate Task (Flask, port 80)** | Runs the Docker image from ECR |
| Task Security Group | **Task SG** | Inbound TCP 80 from ALB SG only |
| ECR Repository | **ECR (music-app)** | Stores the Docker image; task pulls from here |
| CloudWatch Logs | **CloudWatch Log Group (/ecs/music-app-task)** | Container stdout/stderr |
| IAM Role | **LabRole** | Execution role + task role; grants ECR pull + DynamoDB + S3 access |

The browser sends HTTP to the ALB DNS name. The ALB forwards to the Target Group, which routes to the Fargate task over the task's private IP. The container uses boto3 with LabRole to reach DynamoDB and S3.

---

### Backend Option 3 — Lambda + API Gateway

| Component | Label | Notes |
|---|---|---|
| API Gateway (HTTP API) | **API Gateway (music-subscription-api)** | Stage: `prod`; auto-deploy enabled |
| CORS Config | *(shown as a property of API Gateway)* | `AllowOrigins: *`, Methods: GET/POST/DELETE/OPTIONS |
| Lambda — login | **Lambda: login** | POST /login → validates against LoginTable |
| Lambda — register | **Lambda: register** | POST /register → writes to LoginTable |
| Lambda — query | **Lambda: query** | GET /music → queries Music table via GSI/LSI |
| Lambda — get_subscriptions | **Lambda: get_subscriptions** | GET /subscriptions → queries Subscriptions table |
| Lambda — subscribe | **Lambda: subscribe** | POST /subscriptions → writes to Subscriptions table |
| Lambda — unsubscribe | **Lambda: unsubscribe** | DELETE /subscriptions → deletes from Subscriptions table |
| IAM Role | **LabRole** | Execution role for all Lambdas; grants DynamoDB + S3 access |

The browser sends HTTPS to the API Gateway invoke URL. API Gateway routes each method+path to the matching Lambda function via AWS_PROXY integration (payload format v2.0). Each Lambda handler uses boto3 with LabRole to reach DynamoDB and S3.

---

### Shared AWS Data Layer

| Component | Label | Notes |
|---|---|---|
| DynamoDB Table | **LoginTable** | PK: `email`; stores `user_name`, `password` |
| DynamoDB Table | **Music** | PK: `artist`, SK: `title#year`; LSI: `year-index` (artist+year); GSI: `title-index` (title+artist) |
| DynamoDB Table | **Subscriptions** | PK: `email`, SK: `song_id` (`artist#title`) |
| S3 Bucket | **S3 Bucket (artist images)** | No public access; all image access via pre-signed URLs (1-hour expiry) |

---

### Initialisation Scripts (show as a separate "Setup" swim lane or footnote box)

| Component | Label | Notes |
|---|---|---|
| `1_seed_login_table.py` | **Seed LoginTable** | Creates table + loads 10 users |
| `2_create_music_table.py` | **Create Music Table** | Creates table + GSI + LSI |
| `3_load_songs.py` | **Load Songs** | Loads `2026a2_songs.json` into Music table |
| `4_upload_images_to_s3.py` | **Upload Images to S3** | Downloads artist images → uploads to S3 |

These run once from a local machine (or AWS CloudShell). They connect to DynamoDB and S3 directly via boto3 using the LabRole / AWS Academy lab credentials.

---

## 2. How the Components Connect

### Request flow — EC2 path
```
Browser → [HTTP :80] → EC2 Instance (Flask)
                              │
                  ┌───────────┼───────────┐
                  ▼           ▼           ▼
           LoginTable      Music      Subscriptions
           (DynamoDB)    (DynamoDB)   (DynamoDB)
                                          │
                                    S3 Bucket
                              (pre-signed URL for image_key)
```

### Request flow — ECS path
```
Browser → [HTTP :80] → ALB → Target Group → Fargate Task (Flask)
                                                      │
                                          ┌───────────┼───────────┐
                                          ▼           ▼           ▼
                                   LoginTable      Music      Subscriptions
                                   (DynamoDB)    (DynamoDB)   (DynamoDB)
                                                                   │
                                                             S3 Bucket
```

The Fargate task pulls its Docker image from **ECR** at startup, and sends logs to **CloudWatch**.

### Request flow — Lambda path
```
Browser → [HTTPS] → API Gateway (prod stage)
                          │
          ┌───────────────┼──────────────────┐
          │               │                  │
     POST /login    GET /music      GET /subscriptions
     POST /register                POST /subscriptions
                                  DELETE /subscriptions
          │               │                  │
    Lambda:login   Lambda:query    Lambda:get_subscriptions
    Lambda:register               Lambda:subscribe
                                  Lambda:unsubscribe
          │               │                  │
          ▼               ▼                  ▼
    LoginTable          Music           Subscriptions
    (DynamoDB)        (DynamoDB)        (DynamoDB)
                          │
                     S3 Bucket
               (presigned URL for images)
```

---

## 3. IAM — LabRole

All three backends use the single **LabRole** IAM role. In the diagram, draw one IAM box labelled `LabRole` and connect it with a dotted "assumes role" arrow to:
- The EC2 instance (instance profile)
- The ECS task definition (execution role + task role)
- Every Lambda function (execution role)

Do **not** show any other IAM roles — creating new roles is not permitted for this assignment.

---

## 4. Suggested Diagram Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  USER LAYER                                                       │
│  [ Browser ]  ←→  [ Frontend HTML/JS (login / register / main) ] │
└──────┬──────────────────────────────────────────────────────────-┘
       │  HTTP/HTTPS
       ▼
┌──────────────────────────────────────────────────────────────────┐
│  BACKEND OPTIONS (show all three, choose one BASE_URL at a time) │
│                                                                   │
│  ┌─────────────┐  ┌───────────────────────────┐  ┌────────────┐ │
│  │  EC2        │  │  ECS / Fargate             │  │  Lambda    │ │
│  │  Flask :80  │  │  ALB → Target Group        │  │  + API GW  │ │
│  │             │  │  → Fargate Task (Flask :80)│  │  6 funcs   │ │
│  │             │  │  pulls from ECR            │  │            │ │
│  │             │  │  logs to CloudWatch        │  │            │ │
│  └──────┬──────┘  └────────────┬──────────────┘  └─────┬──────┘ │
└─────────┼────────────────────-─┼───────────────────────┼────────┘
          └────────────┬─────────┘                        │
                       └──────────────────────────────────┘
                                        │
                       ┌────────────────▼──────────────────┐
                       │  AWS DATA LAYER                    │
                       │                                    │
                       │  [ DynamoDB: LoginTable ]          │
                       │  [ DynamoDB: Music (GSI + LSI) ]   │
                       │  [ DynamoDB: Subscriptions ]       │
                       │  [ S3 Bucket (artist images) ]     │
                       │                                    │
                       │  [ IAM: LabRole ] ← used by all   │
                       └────────────────────────────────────┘
                                        ▲
                       ┌────────────────┴──────────────────┐
                       │  SETUP / INIT (run once locally)   │
                       │  1. seed_login_table.py            │
                       │  2. create_music_table.py          │
                       │  3. load_songs.py                  │
                       │  4. upload_images_to_s3.py         │
                       └────────────────────────────────────┘
```

---

## 5. Key Details to Label on Each Arrow

| Arrow | Label |
|---|---|
| Browser → EC2 | `HTTP :80  (REST API calls)` |
| Browser → ALB | `HTTP :80  (REST API calls)` |
| ALB → Fargate Task | `HTTP :80  (forwarded)` |
| Browser → API Gateway | `HTTPS (REST API calls)` |
| API Gateway → Lambda | `AWS_PROXY integration (payload v2.0)` |
| Any backend → DynamoDB | `boto3 / AWS SDK  (get_item / query / put_item / delete_item)` |
| Any backend → S3 | `boto3 generate_presigned_url (expires 1h)` |
| Fargate Task → ECR | `Docker image pull` |
| Fargate Task → CloudWatch | `awslogs driver (stdout/stderr)` |
| Init scripts → DynamoDB | `boto3 (create_table / put_item / batch_write)` |
| Init scripts → S3 | `boto3 (put_object)` |

---

## 6. What NOT to Include

- Elastic Beanstalk (not allowed per assignment spec)
- NAT Gateways or private subnets (default VPC with public subnets is sufficient)
- Any custom IAM roles other than LabRole
- RDS or any other database service (DynamoDB only)
- Any `.env` files or AWS credentials boxes
