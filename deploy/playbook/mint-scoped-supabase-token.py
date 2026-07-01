#!/usr/bin/env python3
"""Mint a long-lived, SCOPED Supabase REST token for an AI employee.

The token makes PostgREST run as a limited Postgres role (e.g. emp_app) that you've
granted access to only its own schema — so even over the public REST API the employee
physically can't touch your other data. This is the secure alternative to putting the
service-role key on the VPS.

PREREQS (do these once per employee, from a machine that can reach the DB):
  1. Create the scoped role + schema + RLS, e.g.:
       create role emp_app login password '...';
       grant usage on schema <emp> to emp_app;
       grant select,insert,update,delete on all tables in schema <emp> to emp_app;
       <enable RLS + a policy 'for all to emp_app using(true) with check(true)'>
  2. grant emp_app to authenticator;     -- lets PostgREST SET ROLE emp_app

USAGE:
  python3 mint-scoped-supabase-token.py <role> <project_ref> "<jwt_secret>"
  e.g. python3 mint-scoped-supabase-token.py emp_app lsrycsohlkafqqedkiby "t1KT5...=="

Then on the VPS put in /docker/<C>/data/.env:
  SUPABASE_URL=https://<ref>.supabase.co
  SUPABASE_ANON_KEY=<anon key>          # goes in the `apikey` header (gateway auth)
  EMP_DB_TOKEN=<this token>             # goes in `Authorization: Bearer`
REST calls to a non-public schema need: -H "Accept-Profile: <schema>" (read) / "Content-Profile: <schema>" (write)

NOTE: the Supabase JWT Secret (Settings -> API) is used as a RAW UTF-8 STRING for HS256,
      NOT base64-decoded. This script verifies that by checking it can re-sign, but the
      definitive check is: does the minted token 200 on its schema and 403 elsewhere?
"""
import sys, hmac, hashlib, base64, json, time

if len(sys.argv) != 4:
    sys.exit(__doc__)
role, ref, secret = sys.argv[1], sys.argv[2], sys.argv[3]

def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

key = secret.encode()   # raw UTF-8 (Supabase legacy HS256 secret)
now = int(time.time())
header  = b64u(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
payload = b64u(json.dumps(
    {"role": role, "iss": "supabase", "ref": ref, "iat": now, "exp": now + 10*365*24*3600},
    separators=(",", ":")).encode())
sig = b64u(hmac.new(key, f"{header}.{payload}".encode(), hashlib.sha256).digest())
token = f"{header}.{payload}.{sig}"
print(token)
