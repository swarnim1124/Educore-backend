# EduCore ERP Backend

A modular education ERP backend built with **FastAPI** and **PostgreSQL**. It covers authentication and RBAC, student profiles, curriculum, timetables, attendance, exams, and fees. All of it runs behind a **single dynamic-dispatch endpoint** instead of hundreds of hand-registered routes.

**Stack:** Python 3.12 · FastAPI · PostgreSQL · SQLAlchemy · Pydantic · JWT · Docker · Jenkins CI/CD

---

## Highlights

- **Dispatcher architecture.** One `POST /` endpoint routes requests to `module → submodule → action` using naming conventions. Adding a feature means adding a file, not editing a router.
- **Modular monolith.** 8 domain modules, each with its own manifest, schema, data layer and submodules, loaded dynamically by a module loader.
- **Security built in.** JWT access and refresh tokens, RBAC, MFA, policy engine, and session tracking (`m_AAA`).
- **Observability.** Every request gets a UUID and a milestone timeline (`REQ001`, `AUTH001`, ...) written as structured JSON logs.
- **Integrations.** Razorpay payments, Twilio/MSG91 SMS, Firebase push, reCAPTCHA, and PDF/Excel/Word document generation.
- **Documented.** Per-module API contracts, engineering standards, ER diagrams and release-certification docs are included.

## Architecture

```text
POST /  { "mod", "subMod", "action", "actionType", "data" }
   │
   ▼
index.py ── middleware: request ID, ExecutionContext, JWT validation
   │
   ▼
ActionDispatcher ── resolves module → submodule → handler
   │
   ▼
modules/m_*/m_*_sm_*.py ── business logic → m_*_data.py ── PostgreSQL
   │
   ▼
Standard JSON response + structured log
```

Example request:

```json
{
  "mod": "m_exam",
  "subMod": "sm_schedule",
  "action": "create_schedule",
  "actionType": "add",
  "data": { "academic_year_id": "AY-2026", "exam_type": "REGULAR" }
}
```

## Modules

| Module | Responsibility |
|---|---|
| `m_AAA` | Authentication, RBAC, MFA, policies, audit |
| `m_profile` | Personal, family, academic and medical profiles |
| `m_curriculum` | Programmes, courses, curriculum, enrollment |
| `m_timetable` | Scheduling, allocation, substitution, approvals |
| `m_attendance` | Records, leave, exceptions, shortage tracking |
| `m_exam` | Schedules, seating, hall tickets, marks, results, revaluation |
| `m_fees` | Fee structures, invoices, payments, concessions, refunds |
| `m_super_admin` | Module/action registry, config, master data management |

## Project structure

```text
index.py / main.py     # FastAPI app + middleware pipeline
modules/               # Domain modules (m_* → sm_* submodules)
xsc_lib/               # Framework: dispatcher, container, loader, logger, DB, providers
xsc_conf/              # Configuration
contracts/             # API contracts per module
docs/ guidelines/      # Architecture, engineering standards, ER diagrams
seeder/                # Seed and verification scripts
Dockerfile, Jenkinsfile
```

## Getting started

```bash
git clone <your-repo-url> && cd <repo>
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
cp xsc_conf/xsc_conf_pgrs.example.json xsc_conf/xsc_conf_pgrs.json   # set your DB credentials

uvicorn main:app --reload --port 8000
```

Docker:

```bash
docker build -t educore-backend . && docker run -p 8000:8000 --env-file .env educore-backend
```

Interactive API docs are at `http://localhost:8000/docs`.

## Documentation

- [Backend architecture](guidelines/01_Backend_Architecture.md)
- [Routing specification](guidelines/02_Routing_Specification.md)
- [Module and submodule conventions](guidelines/03_Module_Submodule_Convention.md)
- [API contracts](contracts/)
- [Engineering standard](docs/engineering/OneApp_Engineering_Standard_v1.md)

## My contributions

> Edit this section to match what you actually built.

- Backend modules: _<e.g. m_profile, m_exam subsystems>_
- Dispatcher-based API design and contracts: _<...>_
- _<Tests, seeding, bug fixes, performance work, etc.>_

## Credits

Developed collaboratively. Original framework authors: Siddharth Amdal, Akshay Basutkar, Swarnim Deshpande.

## License

Add a LICENSE file before publishing.
