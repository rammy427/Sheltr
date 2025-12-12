"""
Donation model for Sheltr application.
Contains all of the operations to handle donations.
"""

import re
from datetime import datetime, UTC
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from sheltr.db import get_db


class Donation:
    def __init__(self, donation_id=None, emergency_id=None, emergency_name=None, user_id=None, donation_date=None, donation_quantity=None, donation_message=None, payment_process_provider=None):

        self.id = donation_id
        self.emergency_id = emergency_id
        self.emergency_name = emergency_name
        self.user_id = user_id
        self.date = donation_date
        self.quantity = donation_quantity
        self.message = donation_message
        self.provider = payment_process_provider

    
    @staticmethod
    def validate_quantity(amount):
        """
        Validate and normalize a donation amount.
        Returns (is_valid, error_message, normalized_amount).
        """
        if amount is None or str(amount).strip() == "":
            return False, "Donation amount is required.", None

        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError):
            return False, "Donation amount must be a number.", None

        
        value = value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if value < Decimal("1.00"):
            return False, "Minimum donation is $1.00.", None

        return True, None, value

    @staticmethod
    def validate_msg(msg, max_length = 400):
        """
        Validate an optional/required message.
        Returns (is_valid, error_message, cleaned_message).
        """
        cleaned = msg.strip()

        if cleaned and len(cleaned) > max_length:
            return False, f"Message must be at most {max_length} characters.", None

        # Reject anything outside of match list
        if cleaned and not re.match(r"^[\w\s\.,!?'\"-]*$", cleaned):
            return False, "Message contains invalid characters.", None

        return True, None, cleaned if cleaned else None

    @staticmethod
    def validate_provider(provider):
        """
        Validate payment provider.
        Returns (is_valid, error_message).
        """
        valid_providers = ['Paypal', 'Venmo', 'Apple Pay', 'Credit Card']
        if provider is None or str(provider).strip() == "":
            return False, "Payment provider is required."

        if provider not in valid_providers:
            return False, f"Invalid payment provider. Must be one of: {', '.join(valid_providers)}."

        return True, None

    @staticmethod
    def validate_ids(emergency_id, user_id):
        """Ensure IDs are present and positive integers."""
        if emergency_id is None or user_id is None:
            return False, "Emergency and user are required."
        try:
            if int(emergency_id) <= 0 or int(user_id) <= 0:
                return False, "Invalid emergency or user id."
        except (TypeError, ValueError):
            return False, "Invalid emergency or user id."
        return True, None

    @classmethod
    def create(cls, emergency_id, user_id, amount, message=None, date=None, provider=None):
        """
        Create a new donation after validation.
        Returns (Donation instance, error_message).
        """
        valid, error = cls.validate_ids(emergency_id, user_id)
        if not valid:
            return None, error

        valid, error, normalized_amount = cls.validate_quantity(amount)
        if not valid:
            return None, error

        valid, error, cleaned_msg = cls.validate_msg(message)

        if not valid and error:
            return None, error

        valid, error = cls.validate_provider(provider)
        if not valid:
            return None, error

        donation_date = date or datetime.now(UTC).isoformat()

        db = get_db()
        try:
            cursor = db.execute(
                """
                INSERT INTO donation (emergency_id, user_id, donation_date, donation_quantity, donation_message, payment_process_provider)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    int(emergency_id),
                    int(user_id),
                    donation_date,
                    str(normalized_amount),
                    cleaned_msg,
                    provider,
                ),
            )
            db.commit()
        except Exception as exc:
            return None, f"Database error creating donation: {exc}"

        return (
            cls(
                donation_id=cursor.lastrowid,
                emergency_id=int(emergency_id),
                user_id=int(user_id),
                donation_date=donation_date,
                donation_quantity=normalized_amount,
                donation_message=cleaned_msg,
                payment_process_provider=provider,
            ),
            None,
        )

    @classmethod
    def get_by_id(cls, donation_id):
        db = get_db()
        row = db.execute(
            "SELECT * FROM donation WHERE donation_id = ?",
            (donation_id,),
        ).fetchone()
        if row is None:
            return None
        return cls.from_row(row)

    @classmethod
    def list_recent(cls, limit: int = 10):
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM donation
            ORDER BY donation_date DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def user_donation_history(cls, user_id: int, limit: int = 50):
        db = get_db()
        rows = db.execute(
            """
            SELECT
                emergencies.emergency_name AS emergency_name,
                donation.donation_date AS donation_date,
                donation.donation_quantity AS donation_quantity,
                donation.donation_message AS donation_message
            FROM donation
            JOIN emergencies ON donation.emergency_id = emergencies.emergency_id
            WHERE donation.user_id = ?
            ORDER BY donation.donation_date DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
        history = []
        for row in rows:
            donation_date = row["donation_date"]
            if isinstance(donation_date, str):
                try:
                    donation_date = datetime.fromisoformat(donation_date)
                except ValueError:
                    donation_date = None

            history.append(
                {
                    "emergency_name": row["emergency_name"],
                    "donation_date": donation_date,
                    "donation_quantity": Decimal(str(row["donation_quantity"])),
                    "donation_message": row["donation_message"],
                }
            )

        return history

    @classmethod
    def emergency_donation_history(cls, emergency_id: int, limit: int = 50):
        db = get_db()
        rows = db.execute(
            """
            SELECT * FROM donation
            WHERE emergency_id = ?
            ORDER BY donation_date DESC
            LIMIT ?
            """,
            (emergency_id, limit),
        ).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def sum_by_emergency(cls, emergency_id: int):
        db = get_db()
        row = db.execute(
            "SELECT COALESCE(SUM(donation_quantity), 0) AS total FROM donation WHERE emergency_id = ?",
            (emergency_id,),
        ).fetchone()
        return Decimal(str(row["total"])) if row else Decimal("0.00")
    
    @classmethod
    def sum_by_user_donation(cls, user_id: int):
        db = get_db()
        row = db.execute(
            "SELECT COALESCE(SUM(donation_quantity), 0) AS total FROM donation WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return Decimal(str(row["total"])) if row else Decimal("0.00")

    @classmethod
    def count_by_emergency(cls, emergency_id: int):
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) AS count FROM donation WHERE emergency_id = ?",
            (emergency_id,),
        ).fetchone()
        return int(row["count"]) if row else 0
    
    @classmethod
    def count_by_donations(cls, user_id: int):
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) AS count FROM donation WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return int(row["count"]) if row else 0


  
    @classmethod
    def from_row(cls, row):
        return cls(
            donation_id=row["donation_id"],
            emergency_id=row["emergency_id"],
            user_id=row["user_id"],
            donation_date=row["donation_date"],
            donation_quantity=Decimal(str(row["donation_quantity"])),
            donation_message=row["donation_message"],
            payment_process_provider=row.get("payment_process_provider"),
        )
    
    def to_dict(self):
        return {
            "donation_id": self.id,
            "emergency_id": self.emergency_id,
            "user_id": self.user_id,
            "donation_date": self.date,
            "donation_quantity": str(self.quantity) if self.quantity is not None else None,
            "donation_message": self.message,
            "payment_process_provider": self.provider,
        }
