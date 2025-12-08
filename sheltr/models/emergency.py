"""
Emergency model for Sheltr application.
Contains all of the operations to handle emergencies.
"""
from sheltr.db import get_db

class Emergency:

    """ Emergency model for better management """

    def __init__(self, id=None, name = None, status = None, date = None, img_url = None, description = None):
        """ Emergency constructor """

        self.id = id
        self.name = name
        self.status = status
        self.date = date
        self.img_url = img_url
        self.description = description


    @classmethod
    def new_emergency(cls, name, status, date, img_url = None, description = None):

        """ This function adds an emergency to the database.
        It is a void function.
        """

        # Access the database
        db = get_db()

        try: # Insert emergency to the database
            db.execute("INSERT INTO emergencies (emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES (?, ?, ?, ?, ?)",
                (name.strip(), status, date, img_url.strip() if img_url else None, description.strip() if description else None ))

            db.commit()

        except db.OperationalError:  # pragma: no cover - defensive database error handling
            print("An error has occured within the database. Please try again.")



    def edit_em(self, name=None, date=None, img_url=None, description=None):
        """
        Edit the emergency information.
        Changes can be made to the name, date, image or the description of the emergency.
        Returns (success, error_message).
        """
        if name is not None:
            self.name = name.strip()

        if date is not None:
            self.date = date

        if img_url is not None:
            self.img_url = img_url.strip() if img_url else None

        if description is not None:
            self.description = description.strip() if description else None

        # Update emergency in the database
        db = get_db()

        try:
            db.execute(
                """UPDATE emergencies
                   SET emergency_name = ?, emergency_date = ?, image_url = ?, emergency_description = ?
                   WHERE emergency_id = ?""",
                (self.name, self.date, self.img_url, self.description, self.id)
            )
            db.commit()
            return True, None
        except db.OperationalError:  # pragma: no cover - defensive database error handling
            return False, "Database error occurred while updating emergency."


    def isActive(self):
        """ Check if the emergency is currently active. """

        return self.status
