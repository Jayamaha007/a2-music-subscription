# a2-music-subscription

COSC2626 Cloud Computing — RMIT University  
Assessment 2: AWS Cloud Music Subscription App

A cloud-based music subscription web application built with AWS services including DynamoDB, S3, EC2, ECS (Fargate), and API Gateway + Lambda.

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

## Repository Structure

```
a2-music-subscription/
├── init/          Phase 4 — initialisation scripts
├── frontend/      Phase 6 — HTML/CSS/JS pages
├── backend/
│   ├── ec2/       Phase 5.1 — EC2 Flask backend
│   ├── ecs/       Phase 5.2 — ECS/Docker backend
│   └── lambda/    Phase 5.3 — Lambda handlers
└── docs/          Schema design and architecture diagram
```

## Getting Started

1. Add `2026a2_songs.json` (from Canvas) to `init/`.
2. Configure AWS credentials via environment or instance profile (`LabRole`).
3. Run `init/` scripts in order (1 → 4) to provision tables and upload images.
4. Deploy your chosen backend and update `frontend/js/app.js` `BASE_URL`.
