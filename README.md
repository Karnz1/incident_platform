Incident Platform Project

🏗️ I’m building an incident management platform to map out the entire lifecycle of a multi-service application—from local development to production-grade orchestration. The core stack uses a FastAPI backend backed by PostgreSQL for state, with a Redis queue handling asynchronous worker processing for severity scoring and SLA deadlines. Right now, the app runs locally on Docker Compose, but I’m currently in the middle of migrating the whole infrastructure to Kubernetes using Terraform to manage distinct Dev, Staging, and Prod environments.

For demo purposes, Postgres and Redis are deployed inside Kubernetes.
In production, these could be replaced with managed services such as RDS, Cloud SQL etc.