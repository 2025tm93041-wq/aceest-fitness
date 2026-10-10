# ACEest Fitness & Gym — Flask Service with CI/CD

A REST API for gym management (programs, clients, progress, workouts, BMI, membership),
ported from the original Tkinter desktop versions and shipped through an automated
DevOps pipeline: **Git → Pytest → Docker → Jenkins → GitHub Actions**.

## Project structure

| Path | Purpose |
|------|---------|
| `app.py` | Flask application (app factory + business logic) |
| `tests/test_app.py` | Pytest suite |
| `Dockerfile` | Multi-stage, non-root production image (gunicorn) |
| `.github/workflows/main.yml` | GitHub Actions CI pipeline |
| `Jenkinsfile` | Jenkins declarative pipeline |

## Local setup

```bash
git clone https://github.com/2025tm93041-wq/aceest-fitness.git
cd aceest-fitness
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python app.py                    # http://localhost:5000
```

Try it:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/programs
curl -X POST http://localhost:5000/clients -H "Content-Type: application/json" \
     -d '{"name":"Arun","height":175,"weight":80,"program":"MG"}'
curl http://localhost:5000/clients/Arun/bmi
```

## API summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Liveness check |
| GET | `/programs`, `/programs/<FL\|MG\|BG>` | Program list / workout + diet plan |
| POST/GET | `/clients` | Add client (auto-calculates calories) / list clients |
| GET | `/clients/<name>` | Client details |
| GET | `/clients/<name>/bmi` | BMI and category |
| GET | `/clients/<name>/membership` | Active / Expired / Inactive |
| POST/GET | `/clients/<name>/progress` | Weekly adherence (0-100) |
| POST/GET | `/clients/<name>/workouts` | Workout log |

## Running tests manually

```bash
pytest -v            # unit tests
flake8 .             # lint
```

Inside Docker:

```bash
docker build -t aceest-fitness .
docker run --rm --user root -v "$PWD/tests:/app/tests:ro" -v "$PWD/pytest.ini:/app/pytest.ini:ro" \
  aceest-fitness sh -c "pip install pytest==8.3.3 && pytest -v"
```

## Docker

```bash
docker build -t aceest-fitness .
docker run -d -p 5000:5000 --name aceest aceest-fitness
```

The image uses a multi-stage build on `python:3.12-slim`, runs as a non-root user,
excludes tests and dev files via `.dockerignore`, and includes a `HEALTHCHECK`.

## CI/CD overview

### GitHub Actions (`.github/workflows/main.yml`)
Triggered on every **push** and **pull_request**. Three dependent jobs:

1. **Build & Lint** – installs dependencies, byte-compiles the code (syntax check), runs `flake8`.
2. **Docker Image Assembly** – builds the image and hands it to the next job as an artifact.
3. **Automated Tests** – loads that exact image and runs Pytest *inside the container*.

A failure in any job stops the pipeline, so broken code never reaches the next stage.

### Jenkins (`Jenkinsfile`)
A Pipeline job polls/pulls the latest code from GitHub and acts as a second, independent
validation layer: **Checkout → clean virtualenv → install → lint → Pytest → docker build**.
Because the workspace is rebuilt from scratch every run, it proves the project builds in a
clean, controlled environment.

## Version history
The repository history mirrors the evolution of the original application
(v1.0 program viewer → v3.2.4 full management suite) plus infrastructure commits.

Author: 2025tm93041 - BITS Pilani, Introduction to DevOps
