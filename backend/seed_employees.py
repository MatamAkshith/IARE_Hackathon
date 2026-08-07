"""
seed_employees.py — Stage E.1

Seeds pre-provisioned enterprise employee accounts into the database.
Public registration is disabled; only these accounts can access ThreatLens.

Run once after database initialization:
    python backend/seed_employees.py

Or call seed_enterprise_employees() from init_db startup.
"""

import sys
import os
import logging

# Allow running from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger("seed_employees")

# Pre-provisioned enterprise accounts
ENTERPRISE_ACCOUNTS = [
    {"user_id": "admin",       "passkey": "Admin@123",    "role": "admin"},
    {"user_id": "soclead",     "passkey": "SOCLead@123",  "role": "soc_lead"},
    {"user_id": "analyst01",   "passkey": "Analyst@123",  "role": "analyst"},
    {"user_id": "analyst02",   "passkey": "Analyst@456",  "role": "analyst"},
    {"user_id": "threatintel", "passkey": "Threat@123",   "role": "threat_intel"},
    {"user_id": "incident01",  "passkey": "Incident@123", "role": "incident_responder"},
    {"user_id": "securitymgr", "passkey": "Security@123", "role": "security_manager"},
]


def seed_enterprise_employees(db=None) -> None:
    """
    Insert enterprise employee accounts if they don't already exist.

    Safe to call on every startup — uses get-or-skip logic.
    """
    from app.db.session import SessionLocal
    from app.db.models.employee import EmployeeRecord
    from app.core.security import hash_passkey

    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        seeded = 0
        for account in ENTERPRISE_ACCOUNTS:
            existing = db.query(EmployeeRecord).filter(
                EmployeeRecord.user_id == account["user_id"]
            ).first()

            if existing:
                logger.debug(f"[seed_employees] Account '{account['user_id']}' already exists — skipping.")
                continue

            employee = EmployeeRecord(
                user_id=account["user_id"],
                passkey_hash=hash_passkey(account["passkey"]),
                role=account["role"],
                account_status="active",
            )
            db.add(employee)
            seeded += 1
            logger.info(f"[seed_employees] Seeded account '{account['user_id']}' (role='{account['role']}')")

        if seeded:
            db.commit()
            logger.info(f"[seed_employees] Committed {seeded} new enterprise account(s).")
        else:
            logger.info("[seed_employees] All enterprise accounts already seeded.")
    except Exception as exc:
        db.rollback()
        logger.error(f"[seed_employees] Failed to seed employees: {exc}", exc_info=True)
        raise
    finally:
        if close_db:
            db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== ThreatLens Enterprise Employee Seeder ===")
    seed_enterprise_employees()
    print("Done.")
