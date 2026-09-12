# Robust Django Service Layer

This project demonstrates the limitations of **Django model signals** and the use of an explicit **service layer** for reliable order statistics.

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
```

The project uses **SQLite by default**. To use PostgreSQL, copy `.env.example` to `.env` and configure the database values.

## Docker

```bash
docker compose up --build
```

Docker starts PostgreSQL, waits for it to become healthy, and automatically applies database migrations. The application healthcheck uses `manage.py check`.

## Order Creation

For production order creation, use:

```python
orders.services.create_order(user, total)
```

The service layer:

* Creates orders atomically.
* Creates `UserStats` when needed.
* Updates order totals using database-side `F()` expressions.

The signal implementation is kept as a **legacy example for testing** and is not registered through `OrdersConfig`.

## Benchmark

Run the benchmark with:

```bash
python manage.py benchmark_updates
```

It compares **1,000 individual updates** with **bulk order creation and a single aggregate statistics update**, and reports the execution times.

## Conclusion

The project shows that a **service-layer approach** provides clearer control over order processing, safer database updates, and better maintainability than relying on model signals.
