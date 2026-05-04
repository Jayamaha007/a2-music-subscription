# a2-music-subscription

COSC2626 Cloud Computing — RMIT University  
Assessment 2: AWS Cloud Music Subscription App

A cloud-based music subscription web application backed by DynamoDB, S3, EC2, ECS (Fargate), and API Gateway + Lambda.

---

## Quick Setup (new AWS account)

These steps bootstrap all AWS infrastructure and deploy the serverless backend in one command.

### Prerequisites

| Tool | Install |
|------|---------|
| AWS CLI v2 | https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html |
| Python 3.8+ | https://www.python.org/downloads/ |
| pip3 | bundled with Python |
| Docker | required for ECS only — https://docs.docker.com/get-docker/ |

AWS credentials must be configured before running the script:

```bash
aws configure          # or use an instance profile / AWS Academy session token
aws sts get-caller-identity   # verify it works
```

---

### Step 1 — Clone and configure

```bash
git clone https://github.com/Jayamaha007/a2-music-subscription.git
cd a2-music-subscription
cp config.env.example config.env
```

Open `config.env` and set your values:

```bash
AWS_REGION=us-east-1                   # AWS Academy uses us-east-1
IAM_ROLE_NAME=LabRole                  # AWS Academy only — do not change
S3_BUCKET_NAME=yourname-music-2026     # must be globally unique
DYNAMODB_LOGIN_TABLE=LoginTable
DYNAMODB_MUSIC_TABLE=Music
DYNAMODB_SUBSCRIPTIONS_TABLE=Subscriptions
```

> `config.env` is gitignored and never committed.

---

### Step 2 — Add the song data file

Download `2026a2_songs.json` from Canvas and place it at:

```
init/2026a2_songs.json
```

---

### Step 3 — Run setup

```bash
chmod +x setup.sh
./setup.sh
```

The script runs these steps automatically:

1. Validates `config.env` and checks prerequisites
2. Installs Python dependencies (`boto3`, `requests`)
3. Creates DynamoDB tables — `LoginTable`, `Music`, `Subscriptions`
4. Seeds `LoginTable` with 10 test users
5. Loads all songs from `2026a2_songs.json` into the `Music` table
6. Downloads artist images and uploads them to S3
7. Deploys all 6 Lambda functions
8. Creates the API Gateway HTTP API and prints the `BASE_URL`

At the end you will see output like:

```
BASE_URL:
https://<api-id>.execute-api.us-east-1.amazonaws.com/prod

Paste this into frontend/js/app.js:
const BASE_URL = "https://<api-id>.execute-api.us-east-1.amazonaws.com/prod";
```

---

### Step 4 — Connect the frontend

Open [frontend/js/app.js](frontend/js/app.js) and replace the `BASE_URL` line with the URL printed above:

```javascript
const BASE_URL = "https://<api-id>.execute-api.us-east-1.amazonaws.com/prod";
```

Then serve the frontend:

```bash
cd frontend && python3 -m http.server 3000
# Open http://localhost:3000/login.html
```

---

## Switching Backends

The frontend has a single `BASE_URL` constant in [frontend/js/app.js](frontend/js/app.js). Change it to switch between backends:

| Backend | BASE_URL value |
|---------|---------------|
| Lambda (API Gateway) | `https://<api-id>.execute-api.<region>.amazonaws.com/prod` |
| EC2 | `http://<ec2-public-ip>` |
| ECS | `http://<alb-dns-name>` |

---

## EC2 Backend

After running `./setup.sh`, deploy the EC2 backend with a single command:

```bash
chmod +x backend/ec2/deploy_ec2.sh
./backend/ec2/deploy_ec2.sh
```

The script will:
1. Create a security group (ports 22 + 80) in the default VPC
2. Find the latest Amazon Linux 2023 AMI
3. Launch a `t2.micro` instance with a user-data script that clones the repo, writes the `.env`, installs Python deps, and starts the Flask service via systemd
4. Wait for status checks to pass
5. Print the public IP and the `BASE_URL` line to paste into `frontend/js/app.js`

**Requirements:** `EC2_KEY_PAIR_NAME` and `EC2_INSTANCE_PROFILE` must be set in `config.env`. The key pair must already exist in your AWS account.

---

## ECS Backend

After running `./setup.sh`, deploy the ECS backend with a single command:

```bash
chmod +x backend/ecs/deploy_ecs.sh
./backend/ecs/deploy_ecs.sh
```

The script will:
1. Create an ECR repository, build the Docker image, and push it
2. Create security groups, an Application Load Balancer, target group, and listener
3. Create an ECS Fargate cluster
4. Register a task definition with all config values injected as environment variables
5. Create (or update) the ECS service with 1 running task
6. Wait for the service to stabilise
7. Print the ALB DNS name and the `BASE_URL` line to paste into `frontend/js/app.js`

**Requirements:** Docker must be installed and running locally.

---

## Local Development (no AWS)

```bash
# Terminal 1 — mock API server
cd mock && python3 mock_server.py
# Runs on http://localhost:5001

# Terminal 2 — frontend
cd frontend && python3 -m http.server 3000
# Open http://localhost:3000/login.html
```

Test credentials: `john@example.com / password123` (has pre-loaded subscriptions)

---

## Repository Structure

```
a2-music-subscription/
├── config.env.example     ← copy to config.env and fill in values
├── setup.sh               ← single command to bootstrap everything
├── init/                  Phase 4 — initialisation scripts
│   ├── 1_seed_login_table.py
│   ├── 2_create_music_table.py
│   ├── 3_load_songs.py
│   └── 4_upload_images_to_s3.py
├── frontend/              Phase 6 — static HTML/CSS/JS
│   ├── login.html
│   ├── register.html
│   ├── main.html
│   ├── css/styles.css
│   └── js/app.js          ← set BASE_URL here
├── backend/
│   ├── ec2/               Phase 5.1 — Flask on EC2
│   ├── ecs/               Phase 5.2 — Docker / ECS Fargate
│   └── lambda/            Phase 5.3 — Lambda + API Gateway
│       ├── shared/        boto3 helpers shared by all handlers
│       ├── login/
│       ├── register/
│       ├── query/
│       ├── subscribe/
│       ├── unsubscribe/
│       └── get_subscriptions/
├── mock/                  Local mock API for frontend dev
└── docs/
    ├── schema_design.md   DynamoDB key schema rationale
    └── architecture_diagram.png
```

---

## Project Phases

| Phase | Description |
|-------|-------------|
| 1 | Project planning and AWS account setup |
| 2 | DynamoDB table design (login + music tables, GSI, LSI) |
| 3 | S3 bucket creation and IAM / LabRole configuration |
| 4 | Initialisation programs — seed tables, upload artist images |
| 5.1 | EC2 backend — Flask app deployed on a virtual server |
| 5.2 | ECS backend — Dockerised Flask app on Fargate |
| 5.3 | Lambda + API Gateway serverless backend |
| 6 | Static frontend — login, register, main pages |
| 7 | Integration testing across all three backends |
| 8 | Report, work log, and Canvas submission |

---

## AWS Constraints (COSC2626)

- IAM role: **`LabRole`** only — do not create new roles
- Elastic Beanstalk is **not allowed**
- All backends must run on **port 80 or 443**
- S3 images must use **pre-signed URLs** — bucket is private
- API Gateway must use correct HTTP methods: `GET`, `POST`, `DELETE`
- Never commit `.env` files or AWS credentials
