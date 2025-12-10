"""
Emergency model for Sheltr application.
Contains all of the operations to handle emergencies.
"""
from sheltr.db import get_db
from .shelter import Shelter

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
    def new_emergency(self, name, status, date, img_url = None, description = None):

        """ This function adds an emergency to the database. 
        It is a void function. 
        """

        # Access the database
        db = get_db()

        try: # Insert emergency to the database
            db.execute("INSERT INTO emergencies (emergency_name, emergency_status, emergency_date, image_url, emergency_description) VALUES (?, ?, ?, ?, ?)",
                (name.strip(), status, date, img_url.strip() if img_url else None, description.strip() if description else None ))
            
            db.commit()

        except db.OperationalError:
            print("An error has occured creating a new emergency. Please try again.")   


    @classmethod
    def _from_db_row(self, row):

        """Create emergency object from database row."""

        return self(
            id = row['emergency_id'],
            name = row['emergency_name'],
            status = row['emergency_status'],
            date = row['emergency_date'],
            img_url = row['image_url'],
            description = row['emergency_description'])
    

    @classmethod
    def edit_em(self, name = None, date = None, img_url = None, description = None):

        """
        Let's the manager edit the emergency information.
        Changes can be made to the name, date, image or the description of the emergency.
        """

        if name is not None:
            self.name = name.strip()
        
        if date is not None:
            self.date = date

        if img_url is not None:
            self.img_url = img_url

        # Update emergency in the database
        db = get_db()

        db.execute("UPDATE emergencies SET name = ?, date = ?, img_url = ?, description = ? WHERE id = ?", 
            (self.name, self.date, self.img_url, self.description, self.id))
        
        db.commit()

    
    @classmethod
    def remove_em(self, e_id):

        """
        Lets the manager remove emergencies.
        """

        # Remove an emergency from the database
        db = get_db()

        db.execute('DELETE * FROM emergencies WHERE emergency_id = ?', (e_id))
        db.commit()


    @classmethod
    def get_one_by_id(self, e_id):

        """Get emergency by ID."""

        db = get_db()
        row = db.execute('SELECT * FROM emergencies WHERE emergency_id = ?', (e_id,)).fetchone()

        if row is None:
            return None
        return self._from_db_row(row)
    

    @classmethod
    def get_all(self):

        """Get all of the emergencies."""

        db = get_db()
        rows = db.execute('SELECT * FROM emergencies').fetchall()

        if rows is None:
            return None
        return [self._from_db_row(row) for row in rows]
    

    @classmethod
    def get_all_by_status(self, status):

        """Get all of the emergencies with a specific status."""

        db = get_db()
        rows = db.execute('SELECT * FROM emergencies WHERE emergency_status = ?', (status)).fetchall()

        if rows is None:
            return None
        return [self._from_db_row(row) for row in rows]
    

    @classmethod
    def assigned_shelters(self, e_id):

        """Get all of the shelters for an emergency."""

        db = get_db()
        rows = db.execute('''SELECT *
                          FROM shelters JOIN shelters_of_emergency
                          WHERE shelters.shelter_id = shelters_of_emergency.shelter_id
                          AND emergency_id = ?''', (e_id,)).fetchall()

        if rows is None:
            return None
        return [Shelter._from_db_row(row) for row in rows]

    def assign_shelter(self, shelter_id):
        """Assign shelter to this emergency.
        Returns (success, error_message)."""
        shelter = Shelter.get_by_id(shelter_id)
        if not shelter:
            return False, "Shelter not found."
        
        from datetime import date
        cur_date = date.today()
        db = get_db()
        db.execute("INSERT INTO shelters_of_emergency (emergency_id, shelter_id, starting_date) VALUES (?, ?, ?)", (self.id, shelter_id, cur_date))
        db.commit()
        return True, None

    def to_dict(self):

        """Convert emergency to dictionary."""

        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'date': self.date,
            'img': self.img_url,
            'description': self.description}
    

    def isActive(self):

        """ Check if the emergency is currently active. """
        
        return self.status
