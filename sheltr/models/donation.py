"""
Donation model for Sheltr application.
Contains all of the operations to handle donations.
"""
import re
from sheltr.db import get_db
from decimal import Decimal, ROUND_HALF_UP


class Donation:

    def __init__(self, donation_id = None, emergengy_id = None, user_id = None, transaction_date = None, donation_quantity = 0, donation_msg = None ):
        self.id = donation_id
        self.e_id = emergengy_id
        self.u_id = user_id
        self.date = transaction_date
        self.quantity = str(donation_quantity)
        self.msg = donation_msg

    @staticmethod
    def validate_quantity(donation_quantity):
        """Validate quantiy meets:
        - Minimum of 1 dollar
        - Value must be decimal
        - 
        """
        if Decimal(str(donation_quantity)) <= 0.99:
            return False, "Minimum of 1 dollar requiered "
        if not re.match(r'^\d+(\.\d+)?$', donation_quantity):
            return False, "Invalid input"      
        return True, None
    @staticmethod
    def validate_msg():
        pass

    @classmethod
    def new_donation(cls, e_id, u_id, date, quantity, msg = None):
        
        db = get_db()

        try:
            db.execute("INSERT INTO donation (donation_id, emergency_id, user_id, donation_date, donation_quantity, donation_message) VALUES (?, ?, ?, ?, ?)", 
                (e_id, u_id, date, quantity, msg.strip() if msg else None))
            db.commit()

        except:
            "An error occured in the database please try again"
    
    @classmethod
    def user_donation_history(self):
        db = get_db()

        try:
            db.execute("SELECT * FROM donation WHERE user_id = ? ", (self.u_id))

        except: 
            pass

    @classmethod
    def emergency_donation_history(cls, e_id): 
        pass
