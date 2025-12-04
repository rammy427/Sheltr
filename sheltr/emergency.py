from flask import (Blueprint, render_template, g)
from sheltr.models import Emergency
from sheltr.auth import login_required
from sheltr.db import get_db

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    # Dummy test to check that the values are being inserted to the database
    Emergency.new_emergency(name = "Fuego en Ponce", status = True, date = "2020-05-10", img_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Large_bonfire.jpg/500px-Large_bonfire.jpg", description = "Fire is the rapid oxidation of a fuel in the exothermic chemical process of combustion, releasing heat, light, and various reaction products. Flames, the most visible portion of the fire, are produced in the combustion reaction when the fuel reaches its ignition point temperature. Flames from hydrocarbon fuels consist primarily of carbon dioxide, water vapor, oxygen, and nitrogen. If hot enough, the gases may become ionized to produce plasma. The color and intensity of the flame depend on the type of fuel and composition of the surrounding gases.")
    Emergency.new_emergency(name = "Inundacion en Condado", status = False, date = "2025-07-11", img_url = "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/13/40/51/e0/aerial-images.jpg?w=900&h=500&s=1", description = "Condado es una comunidad frente al mar, bordeada de árboles, orientada a los peatones en San Juan, Puerto Rico. Es una zona de clase media a alta, está situado al este del centro histórico del Viejo San Juan. Es uno de los 40 «sub-barrios» de Santurce. La superficie de tierra es de 0,82 km² (824 791 m²), con una población de 6170 residentes según el censo de los Estados Unidos de 2000. La frontera oriental se caracteriza por la Avenida de Diego y de su extensión recta hacia la costa atlántica. En el sur, el distrito está delimitado por Calle Wilson, Calle Aldea, Expreso Baldorioty de Castro, Calle Piccioni y calle Delcasse, y por la Laguna del Condado (de este a oeste). El punto más occidental es el «Puente Dos Hermanos», donde termina la Avenida Ashford y comienza el San Juan Antiguo. En el norte están las playas del Océano Atlántico.")
    # Access the database
    db = get_db()

    list_emergencies = db.execute('SELECT * FROM emergencies').fetchall()
    return render_template('emergency.html', emergency = list_emergencies)