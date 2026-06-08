**Incident Management Platform**

A cloud-native, microservices-based incident management system, built as a hands-on
portfolio project to demonstrate end-to-end DevOps practices: containerization,
Kubernetes orchestration, GitOps continuous delivery, CI/CD, observability, and
Infrastructure-as-Code.


Table of Contents

Overview
Architecture
Tech Stack
How It Works
Repository Structure
Running Locally (Docker Compose)
Kubernetes Deployment (Helm + ArgoCD)
CI/CD Pipeline
Project Status & Roadmap
Design Decisions


Overview
This project is a small but realistic distributed system: users create incidents through a
web UI, an API persists them, and a background worker asynchronously enriches each incident
with a severity level and an SLA deadline. The application itself is intentionally simple —
its purpose is to serve as a vehicle for demonstrating the operational tooling and delivery
practices built around it.
The focus of this project is the infrastructure and delivery layer, not the business logic.

Architecture
#mermaid-rfo-r3{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;fill:#191919;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-rfo-r3 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-rfo-r3 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-rfo-r3 .error-icon{fill:#CC785C;}#mermaid-rfo-r3 .error-text{fill:#3387a3;stroke:#3387a3;}#mermaid-rfo-r3 .edge-thickness-normal{stroke-width:1px;}#mermaid-rfo-r3 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-rfo-r3 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-rfo-r3 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-rfo-r3 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-rfo-r3 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-rfo-r3 .marker{fill:#91918D;stroke:#91918D;}#mermaid-rfo-r3 .marker.cross{stroke:#91918D;}#mermaid-rfo-r3 svg{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;}#mermaid-rfo-r3 p{margin:0;}#mermaid-rfo-r3 .label{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#191919;}#mermaid-rfo-r3 .cluster-label text{fill:#3387a3;}#mermaid-rfo-r3 .cluster-label span{color:#3387a3;}#mermaid-rfo-r3 .cluster-label span p{background-color:transparent;}#mermaid-rfo-r3 .label text,#mermaid-rfo-r3 span{fill:#191919;color:#191919;}#mermaid-rfo-r3 .node rect,#mermaid-rfo-r3 .node circle,#mermaid-rfo-r3 .node ellipse,#mermaid-rfo-r3 .node polygon,#mermaid-rfo-r3 .node path{fill:#F0F0EB;stroke:#D9D8D5;stroke-width:1px;}#mermaid-rfo-r3 .rough-node .label text,#mermaid-rfo-r3 .node .label text,#mermaid-rfo-r3 .image-shape .label,#mermaid-rfo-r3 .icon-shape .label{text-anchor:middle;}#mermaid-rfo-r3 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-rfo-r3 .rough-node .label,#mermaid-rfo-r3 .node .label,#mermaid-rfo-r3 .image-shape .label,#mermaid-rfo-r3 .icon-shape .label{text-align:center;}#mermaid-rfo-r3 .node.clickable{cursor:pointer;}#mermaid-rfo-r3 .root .anchor path{fill:#91918D!important;stroke-width:0;stroke:#91918D;}#mermaid-rfo-r3 .arrowheadPath{fill:#0b0b0b;}#mermaid-rfo-r3 .edgePath .path{stroke:#91918D;stroke-width:1px;}#mermaid-rfo-r3 .flowchart-link{stroke:#91918D;fill:none;}#mermaid-rfo-r3 .edgeLabel{background-color:#F5E6D8;text-align:center;}#mermaid-rfo-r3 .edgeLabel p{background-color:#F5E6D8;}#mermaid-rfo-r3 .edgeLabel rect{opacity:0.5;background-color:#F5E6D8;fill:#F5E6D8;}#mermaid-rfo-r3 .labelBkg{background-color:rgba(245, 230, 216, 0.5);}#mermaid-rfo-r3 .cluster rect{fill:#CC785C;stroke:hsl(15, 12.3364485981%, 48.0392156863%);stroke-width:1px;}#mermaid-rfo-r3 .cluster text{fill:#3387a3;}#mermaid-rfo-r3 .cluster span{color:#3387a3;}#mermaid-rfo-r3 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:12px;background:#CC785C;border:1px solid hsl(15, 12.3364485981%, 48.0392156863%);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-rfo-r3 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#191919;}#mermaid-rfo-r3 rect.text{fill:none;stroke-width:0;}#mermaid-rfo-r3 .icon-shape,#mermaid-rfo-r3 .image-shape{background-color:#F5E6D8;text-align:center;}#mermaid-rfo-r3 .icon-shape p,#mermaid-rfo-r3 .image-shape p{background-color:#F5E6D8;padding:2px;}#mermaid-rfo-r3 .icon-shape .label rect,#mermaid-rfo-r3 .image-shape .label rect{opacity:0.5;background-color:#F5E6D8;fill:#F5E6D8;}#mermaid-rfo-r3 .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#mermaid-rfo-r3 .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#mermaid-rfo-r3 .node .neo-node{stroke:#D9D8D5;}#mermaid-rfo-r3 [data-look="neo"].node rect,#mermaid-rfo-r3 [data-look="neo"].cluster rect,#mermaid-rfo-r3 [data-look="neo"].node polygon{stroke:url(#mermaid-rfo-r3-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfo-r3 [data-look="neo"].node path{stroke:url(#mermaid-rfo-r3-gradient);stroke-width:1px;}#mermaid-rfo-r3 [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfo-r3 [data-look="neo"].node .neo-line path{stroke:#D9D8D5;filter:none;}#mermaid-rfo-r3 [data-look="neo"].node circle{stroke:url(#mermaid-rfo-r3-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfo-r3 [data-look="neo"].node circle .state-start{fill:#000000;}#mermaid-rfo-r3 [data-look="neo"].icon-shape .icon{fill:url(#mermaid-rfo-r3-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfo-r3 [data-look="neo"].icon-shape .icon-neo path{stroke:url(#mermaid-rfo-r3-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfo-r3 :root{--mermaid-font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}RESTread / write incidentsenqueue new incidentpoll queueassign severity + SLA,update recordsource of truthsync queue state/health, /metricsUserFrontendVanilla JS SPAAPIFastAPIPostgreSQLSource of TruthRedisQueue · transientWorkerPythonReconcilerplannedPrometheusplannedGrafanaplanned
The system is composed of four services and two backing stores. PostgreSQL is the single
source of truth for all incident state; Redis is treated as a disposable, transient
queue that holds no authoritative data and can be rebuilt from PostgreSQL.

Frontend — a single-page vanilla-JS app to create, view, and delete incidents.
API — a FastAPI service exposing incident CRUD endpoints plus /health and /metrics.
Worker — a Python service that consumes incidents from the queue and processes them.
PostgreSQL — the single source of truth for all incident state.
Redis — a transient work queue connecting the API and the worker; it stores no
authoritative state and can be reconstructed from PostgreSQL by the reconciler (planned).


Tech Stack
LayerTechnologyAPIPython, FastAPIFrontendVanilla JavaScript (SPA)WorkerPythonStatePostgreSQLQueueRedisContainerizationDocker, Docker ComposeOrchestrationKubernetes, HelmGitOps / CDArgoCDCIGitHub Actions RegistryDocker HubObservabilityPrometheus, Grafana (planned)IaC / CloudTerraform, AWS (planned)

How It Works

A user creates an incident through the frontend, which calls the API.
The API writes the incident to PostgreSQL and enqueues a processing job in Redis.
The worker polls the Redis queue, picks up the incident, and computes its severity
and SLA deadline.
The worker writes the enriched data back to PostgreSQL.
The frontend reflects the updated incident on the next read.

This separation lets the API stay fast and responsive while heavier processing happens
asynchronously in the worker — a common pattern for decoupling user-facing requests from
background work.

Kubernetes Deployment (Helm + ArgoCD)
The application is deployed to Kubernetes using Helm charts, with ArgoCD providing
GitOps-based continuous delivery. Rather than pushing changes to the cluster imperatively,
the desired state is declared in Git, and ArgoCD continuously reconciles the cluster to
match it.
#mermaid-rfr-r4{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;fill:#191919;}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#mermaid-rfr-r4 .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#mermaid-rfr-r4 .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#mermaid-rfr-r4 .error-icon{fill:#CC785C;}#mermaid-rfr-r4 .error-text{fill:#3387a3;stroke:#3387a3;}#mermaid-rfr-r4 .edge-thickness-normal{stroke-width:1px;}#mermaid-rfr-r4 .edge-thickness-thick{stroke-width:3.5px;}#mermaid-rfr-r4 .edge-pattern-solid{stroke-dasharray:0;}#mermaid-rfr-r4 .edge-thickness-invisible{stroke-width:0;fill:none;}#mermaid-rfr-r4 .edge-pattern-dashed{stroke-dasharray:3;}#mermaid-rfr-r4 .edge-pattern-dotted{stroke-dasharray:2;}#mermaid-rfr-r4 .marker{fill:#91918D;stroke:#91918D;}#mermaid-rfr-r4 .marker.cross{stroke:#91918D;}#mermaid-rfr-r4 svg{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:16px;}#mermaid-rfr-r4 p{margin:0;}#mermaid-rfr-r4 .label{font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#191919;}#mermaid-rfr-r4 .cluster-label text{fill:#3387a3;}#mermaid-rfr-r4 .cluster-label span{color:#3387a3;}#mermaid-rfr-r4 .cluster-label span p{background-color:transparent;}#mermaid-rfr-r4 .label text,#mermaid-rfr-r4 span{fill:#191919;color:#191919;}#mermaid-rfr-r4 .node rect,#mermaid-rfr-r4 .node circle,#mermaid-rfr-r4 .node ellipse,#mermaid-rfr-r4 .node polygon,#mermaid-rfr-r4 .node path{fill:#F0F0EB;stroke:#D9D8D5;stroke-width:1px;}#mermaid-rfr-r4 .rough-node .label text,#mermaid-rfr-r4 .node .label text,#mermaid-rfr-r4 .image-shape .label,#mermaid-rfr-r4 .icon-shape .label{text-anchor:middle;}#mermaid-rfr-r4 .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#mermaid-rfr-r4 .rough-node .label,#mermaid-rfr-r4 .node .label,#mermaid-rfr-r4 .image-shape .label,#mermaid-rfr-r4 .icon-shape .label{text-align:center;}#mermaid-rfr-r4 .node.clickable{cursor:pointer;}#mermaid-rfr-r4 .root .anchor path{fill:#91918D!important;stroke-width:0;stroke:#91918D;}#mermaid-rfr-r4 .arrowheadPath{fill:#0b0b0b;}#mermaid-rfr-r4 .edgePath .path{stroke:#91918D;stroke-width:1px;}#mermaid-rfr-r4 .flowchart-link{stroke:#91918D;fill:none;}#mermaid-rfr-r4 .edgeLabel{background-color:#F5E6D8;text-align:center;}#mermaid-rfr-r4 .edgeLabel p{background-color:#F5E6D8;}#mermaid-rfr-r4 .edgeLabel rect{opacity:0.5;background-color:#F5E6D8;fill:#F5E6D8;}#mermaid-rfr-r4 .labelBkg{background-color:rgba(245, 230, 216, 0.5);}#mermaid-rfr-r4 .cluster rect{fill:#CC785C;stroke:hsl(15, 12.3364485981%, 48.0392156863%);stroke-width:1px;}#mermaid-rfr-r4 .cluster text{fill:#3387a3;}#mermaid-rfr-r4 .cluster span{color:#3387a3;}#mermaid-rfr-r4 div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;font-size:12px;background:#CC785C;border:1px solid hsl(15, 12.3364485981%, 48.0392156863%);border-radius:2px;pointer-events:none;z-index:100;}#mermaid-rfr-r4 .flowchartTitleText{text-anchor:middle;font-size:18px;fill:#191919;}#mermaid-rfr-r4 rect.text{fill:none;stroke-width:0;}#mermaid-rfr-r4 .icon-shape,#mermaid-rfr-r4 .image-shape{background-color:#F5E6D8;text-align:center;}#mermaid-rfr-r4 .icon-shape p,#mermaid-rfr-r4 .image-shape p{background-color:#F5E6D8;padding:2px;}#mermaid-rfr-r4 .icon-shape .label rect,#mermaid-rfr-r4 .image-shape .label rect{opacity:0.5;background-color:#F5E6D8;fill:#F5E6D8;}#mermaid-rfr-r4 .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#mermaid-rfr-r4 .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#mermaid-rfr-r4 .node .neo-node{stroke:#D9D8D5;}#mermaid-rfr-r4 [data-look="neo"].node rect,#mermaid-rfr-r4 [data-look="neo"].cluster rect,#mermaid-rfr-r4 [data-look="neo"].node polygon{stroke:url(#mermaid-rfr-r4-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfr-r4 [data-look="neo"].node path{stroke:url(#mermaid-rfr-r4-gradient);stroke-width:1px;}#mermaid-rfr-r4 [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfr-r4 [data-look="neo"].node .neo-line path{stroke:#D9D8D5;filter:none;}#mermaid-rfr-r4 [data-look="neo"].node circle{stroke:url(#mermaid-rfr-r4-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfr-r4 [data-look="neo"].node circle .state-start{fill:#000000;}#mermaid-rfr-r4 [data-look="neo"].icon-shape .icon{fill:url(#mermaid-rfr-r4-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfr-r4 [data-look="neo"].icon-shape .icon-neo path{stroke:url(#mermaid-rfr-r4-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#mermaid-rfr-r4 :root{--mermaid-font-family:"Anthropic Sans",system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}push imageupdate image tag in HelmvaluessyncCI: lint to test to buildDocker HubGitOps repoArgoCDKubernetes - devnamespace
<!-- TODO: add the actual commands / steps to bootstrap, e.g. installing the ArgoCD
     Application manifest, namespace setup, secrets, etc. -->

CI/CD Pipeline
Each of the three services has its own CI pipeline. On a change, the pipeline runs the
following stages in order:

Lint — static analysis and style checks.
Unit test — run the service's unit test suite.
Build — build the service's Docker image.
Push — push the tagged image to Docker Hub.
Update Helm values — bump the image tag in the Helm values file in the GitOps repo.

ArgoCD detects the change to the Helm values and automatically syncs the new image into the
dev namespace — no manual kubectl steps. This gives a fully automated path from code
change to a running deployment in dev.

Project Status & Roadmap
Legend: ✅ done · 🚧 in progress · ⬜ planned
Phase 1 — Core Application ✅

✅ FastAPI API with create / delete / get-all incident endpoints
✅ /health and /metrics endpoints scaffolded (metrics not yet emitting data)
✅ Vanilla JS frontend (create / view / delete incidents)
✅ PostgreSQL for state, Redis for the queue
✅ Worker that assigns severity + SLA deadline and updates state
✅ Full local stack via Docker Compose

Phase 2 — Continuous Integration ✅

✅ Per-service CI pipelines that build and push images to Docker Hub
✅ Automated update of values.yaml in the GitOps repo

Phase 3 — Kubernetes + GitOps 🚧

🚧 Helm charts / Kubernetes manifests for all services
🚧 ArgoCD auto-sync to the dev namespace

Phase 4 — Environment Promotion ⬜

⬜ Promotion pipeline: dev → staging → prod

Phase 5 — Observability ⬜

⬜ Real Prometheus metrics from the API and worker (/metrics)
⬜ Grafana dashboards for key signals (request rate, queue depth, processing latency)

Phase 6 — Cloud + Infrastructure-as-Code ⬜

⬜ Provision equivalent infrastructure on AWS with Terraform

Phase 7 — Resilience & State Reconciliation ⬜

⬜ Reconciler that keeps Redis in sync with PostgreSQL (the source of truth), so the
transient queue can be rebuilt automatically if Redis is restarted or loses data


Design Decisions

Why a queue + worker instead of processing inline in the API?
decoupling, responsiveness, mirrors real async processing patterns.

Why GitOps / ArgoCD instead of pushing deployments from CI?
Git as single source of truth, auditability, declarative reconciliation.

Why Helm?
templating across environments, reuse, values-per-environment.

Why treat Redis as disposable, with PostgreSQL as the single source of truth?
Resilience to Redis restarts or data loss via a reconciler that re-derives queue state from PG 