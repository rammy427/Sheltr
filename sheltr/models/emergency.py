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
            print("An error has occured within the database. Please try again.")
            

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

        db.execute("UPDATE emergencies SET name = ?, date = ?, img_url = ? WHERE id = ?", 
            (self.name, self.date, self.img_url, self.id))
        
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
