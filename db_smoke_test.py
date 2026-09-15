"""Cross-database ELT smoke test using generated, non-sensitive records."""
import os
import time
from decimal import Decimal

from sqlalchemy import Column, Integer, MetaData, Numeric, String, Table, create_engine, func, select


def run(database_url: str, rows: int = 10_000) -> dict:
    engine = create_engine(database_url, future=True)
    metadata = MetaData()
    customers = Table(
        "dim_customer", metadata,
        Column("customer_id", Integer, primary_key=True),
        Column("region", String(20), nullable=False),
    )
    orders = Table(
        "fact_order", metadata,
        Column("order_id", Integer, primary_key=True),
        Column("customer_id", Integer, nullable=False),
        Column("amount", Numeric(12, 2), nullable=False),
        Column("status", String(20), nullable=False),
    )
    started = time.perf_counter()
    with engine.begin() as conn:
        metadata.drop_all(conn)
        metadata.create_all(conn)
        conn.execute(customers.insert(), [
            {"customer_id": i, "region": ("Central", "East", "West", "South")[i % 4]}
            for i in range(1, 1001)
        ])
        batch = [
            {"order_id": i, "customer_id": ((i - 1) % 1000) + 1,
             "amount": Decimal(f"{20 + (i % 480)}.00"),
             "status": "completed" if i % 10 else "cancelled"}
            for i in range(1, rows + 1)
        ]
        conn.execute(orders.insert(), batch)
        loaded = conn.scalar(select(func.count()).select_from(orders))
        distinct_ids = conn.scalar(select(func.count(func.distinct(orders.c.order_id))))
        completed = conn.scalar(select(func.count()).where(orders.c.status == "completed"))
        if loaded != rows or distinct_ids != rows or completed != rows * 9 // 10:
            raise AssertionError({"loaded": loaded, "distinct_ids": distinct_ids, "completed": completed})
    return {"rows": loaded, "completed": completed, "seconds": round(time.perf_counter() - started, 3)}


if __name__ == "__main__":
    result = run(os.getenv("DATABASE_URL", "sqlite:///warehouse_smoke.db"))
    print(result)
