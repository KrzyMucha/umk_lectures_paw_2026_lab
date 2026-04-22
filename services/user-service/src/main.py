import os
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from psycopg.rows import dict_row

app = FastAPI(title="User Service")

ROLE_CUSTOMER = "ROLE_CUSTOMER"
ROLE_SELLER = "ROLE_SELLER"


class UserCreatePayload(BaseModel):
    email: EmailStr
    firstName: str
    lastName: str
    roles: list[str] = [ROLE_CUSTOMER]


def _normalize_database_url(database_url: str) -> str:
    parsed = urlsplit(database_url)
    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    filtered_query = [(k, v) for k, v in query_items if k not in {"serverVersion", "charset"}]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(filtered_query), parsed.fragment))


def _db_url() -> str:
    raw = os.getenv("DATABASE_URL", "").strip()
    if raw == "":
        raise HTTPException(status_code=500, detail="DATABASE_URL is not configured")
    return _normalize_database_url(raw)


def _serialize_user(row: dict[str, Any]) -> dict[str, Any]:
    roles_raw = row.get("roles") or ""
    roles = [role.strip() for role in roles_raw.split(",") if role.strip()]
    return {
        "id": row["id"],
        "email": row["email"],
        "firstName": row["first_name"],
        "lastName": row["last_name"],
        "fullName": f"{row['first_name']} {row['last_name']}",
        "roles": roles,
        "isCustomer": ROLE_CUSTOMER in roles,
        "isSeller": ROLE_SELLER in roles,
        "superSellerId": row.get("super_seller_id"),
    }


def _deduplicate_roles(roles: list[str]) -> list[str]:
    normalized = []
    for role in roles:
        value = role.strip()
        if value == "":
            continue
        if value not in {ROLE_CUSTOMER, ROLE_SELLER}:
            raise HTTPException(status_code=400, detail=f"Invalid role: {value}")
        if value not in normalized:
            normalized.append(value)
    if not normalized:
        raise HTTPException(status_code=400, detail="Roles must be a non-empty array")
    return normalized


@app.get("/users")
def get_users() -> list[dict[str, Any]]:
    with psycopg.connect(_db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, email, first_name, last_name, roles, super_seller_id FROM "user" ORDER BY id')
            rows = cur.fetchall()

    return [_serialize_user(row) for row in rows]


@app.get("/users-super")
def get_super_users() -> list[dict[str, Any]]:
    with psycopg.connect(_db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, email, first_name, last_name, roles, super_seller_id FROM "user" WHERE super_seller_id IS NOT NULL ORDER BY id'
            )
            rows = cur.fetchall()

    return [_serialize_user(row) for row in rows]


@app.get("/user/{user_id}")
def get_user_by_id(user_id: int) -> dict[str, Any]:
    with psycopg.connect(_db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, email, first_name, last_name, roles, super_seller_id FROM "user" WHERE id = %s',
                (user_id,),
            )
            row = cur.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="User not found")

    return _serialize_user(row)


@app.post("/users", status_code=201)
def create_user(payload: UserCreatePayload) -> dict[str, Any]:
    first_name = payload.firstName.strip()
    last_name = payload.lastName.strip()

    if first_name == "":
        raise HTTPException(status_code=400, detail="First name is required")
    if last_name == "":
        raise HTTPException(status_code=400, detail="Last name is required")

    roles = _deduplicate_roles(payload.roles)
    roles_string = ",".join(roles)

    try:
        with psycopg.connect(_db_url(), row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO "user" (email, first_name, last_name, roles) VALUES (%s, %s, %s, %s) RETURNING id, email, first_name, last_name, roles, super_seller_id',
                    (str(payload.email), first_name, last_name, roles_string),
                )
                row = cur.fetchone()
            conn.commit()
    except psycopg.errors.UniqueViolation as exc:
        raise HTTPException(status_code=409, detail="Email already exists") from exc

    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return _serialize_user(row)
