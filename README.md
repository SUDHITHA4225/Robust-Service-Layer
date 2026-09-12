# Robust Django Service Layer

This project demonstrates the limits of model signals and the explicit service-layer approach for order statistics.

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
```

The default local configuration uses SQLite. Copy `.env.example` to `.env` and provide PostgreSQL values when needed.

## Docker

Copy `.env.example` to `.env`, replace its placeholders, then run:

```bash
docker compose up --build
```

PostgreSQL becomes healthy before the application starts. The application entrypoint applies migrations automatically, and the app healthcheck runs `manage.py check`.

## Order creation

Use `orders.services.create_order(user, total)` for production order creation. It atomically creates the order, creates missing `UserStats`, and updates totals with database-side `F()` expressions. `orders.signals` remains as an isolated legacy example for tests, but it is not registered by `OrdersConfig`.

## Benchmark

```bash
python manage.py benchmark_updates
```

The command compares 1,000 individual order/stat updates with a bulk-create plus one aggregate stat update and prints parseable timing lines.