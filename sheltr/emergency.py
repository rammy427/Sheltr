from flask import (Blueprint, render_template, render_template_string, g)
from sheltr.models import Emergency
from sheltr.auth import login_required
from sheltr.db import get_db
import folium

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    list_emergencies = Emergency.get_all()
    return render_template('emergency.html', emergency = list_emergencies)



@bp.route('/<int:e_id>')
@login_required

def specific_emergency(e_id):
    """ Display the specific emergency that was clicked on. """

    emergency = Emergency.get_one_by_id(e_id)
    shelters = Emergency.assigned_shelters(e_id)
    map = render_map(e_id = e_id)
    return render_template('single_emergency.html', emergency = emergency, shelters = shelters, map = map)


@bp.route('/<int:e_id>')
@login_required

def render_map(e_id):
    """ Create the map to render in a single emergency. """
    
    # Limiting regions
    min_lon = -68.3469
    max_lon = -65.1156267
    min_lat = 17.630649
    max_lat = 18.636163

    shelter_map = folium.Map(location = [18.200178, -66.5], tiles = 'OpenStreetMap', 
    width = '100%', height = '100%', zoom_start = 9, max_bounds = True, control_scale = True, 
    min_lon = min_lon, max_lon = max_lon, min_lat = min_lat, max_lat = max_lat)

    # Get list of shelters 
    shelters = Emergency.assigned_shelters(e_id)

    for s in shelters:
        coords = s.location.split(',')

        # Parse string
        name = coords[0]
        lat = float(coords[1])
        long = float(coords[2])

        # Create a marker for each shelter 
        folium.Marker(location= [lat, long], tooltip= 'Shelter', popup= name, icon= folium.Icon(icon = 'home', color = 'persimmon')).add_to(shelter_map)


    # Create limiting regions
    folium.CircleMarker([max_lat, min_lon], tooltip="Upper Left Corner").add_to(shelter_map)
    folium.CircleMarker([min_lat, min_lon], tooltip="Lower Left Corner").add_to(shelter_map)
    folium.CircleMarker([min_lat, max_lon], tooltip="Lower Right Corner").add_to(shelter_map)
    folium.CircleMarker([max_lat, max_lon], tooltip="Upper Right Corner").add_to(shelter_map) 

    shelter_map.save('sheltr/templates/shelter_map.html')
    iframe = shelter_map.get_root()._repr_html_()

    return render_template_string(
        """ <!DOCTYPE html>
            <html>
                <body>
                    {{iframe|safe}}
                </body>
            </html> """, iframe=iframe)
