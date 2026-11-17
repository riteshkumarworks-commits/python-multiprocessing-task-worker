# Python Multiprocessing Task Worker

A small Python project that demonstrates a task queue. A broker accepts jobs; multiple worker processes fetch jobs, execute registered functions, and report success or failure.

## Requirements
- Python 3.9+
- No third-party packages (Python standard library only)

## Run on Windows 11
Open three terminals in this project folder.

**Terminal 1 — start the broker**
```bash
python run.py broker
```

**Terminal 2 — start four workers**
```bash
python run.py worker --count 4
```

**Terminal 3 — submit tasks**
```bash
python run.py submit add --payload "{\"a\": 10, \"b\": 25}"
python run.py submit greet --payload "{\"name\": \"Ritesh\"}"
python run.py submit uppercase --payload "{\"text\": \"hello github\"}"
python run.py stats
```
Workers should print completed tasks and results. Press Ctrl+C to stop each process.

## Add your own task
Add a function in `taskworker/tasks.py` and decorate it with `@task("task_name")`. Submit it with a JSON payload whose keys match the function arguments.

## Project structure
```text
python-task-worker/
├── taskworker/
│   ├── __init__.py
│   ├── broker.py
│   ├── client.py
│   ├── tasks.py
│   └── worker.py
├── run.py
├── README.md
└── .gitignore
```

## Limitations
This is a local educational demo, not production software. The broker stores jobs in memory, so queued jobs are lost if it stops. There is no authentication, database persistence, monitoring, or production retry policy. A lease expiry can cause a task to run again, so real tasks should be idempotent (safe to repeat).
