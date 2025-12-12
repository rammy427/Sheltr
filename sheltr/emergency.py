from flask import (Blueprint, render_template, render_template_string, g, url_for, flash, request)
from sheltr.models import Emergency, Shelter
from sheltr.auth import login_required, manager_required
from sheltr.db import get_db
import folium
from folium.plugins import MousePosition

bp = Blueprint('emergency', __name__, url_prefix = '/emergency')

@bp.route('/')
@login_required

def view():
    """ View of all the emergencies saved in the database. """
    
    list_emergencies = Emergency.get_all()
    return render_template('emergency.html', emergency = list_emergencies)


@bp.route('/<int:e_id>', methods=['GET'])
@login_required

def specific_emergency(e_id):
    """ Display the specific emergency that was clicked on. """

    emergency = Emergency.get_one_by_id(e_id)
    shelters = Emergency.assigned_shelters(e_id)
    map = render_map(e_id = e_id)
    return render_template('single_emergency.html', emergency = emergency, shelters = shelters, map = map)

@bp.route('/<int:e_id>', methods=['DELETE'])
@manager_required
def delete_emergency(e_id):
    """Delete the specified emergency and unlink all its shelters."""
    emergency = Emergency.get_one_by_id(e_id)
    if emergency:
        Emergency.remove_em(e_id)
    return '', 204

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
        name = s.name
        coords = s.location.split(',')

        # Parse string
        name = name
        lat = float(coords[1])
        long = float(coords[2])

        # Create enhanced HTML popup for each shelter
        popup_html = f"""
        <div style="min-width: 200px; font-family: system-ui, -apple-system, sans-serif;">
            <h4 style="margin: 0 0 8px 0; color: #334155; font-size: 14px; font-weight: 600;">{name}</h4>
            <p style="margin: 0 0 8px 0; color: #64748b; font-size: 12px;">{s.description or 'No description available'}</p>
            <a href="/shelters/{s.id}"
               style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                      color: white; padding: 6px 12px; border-radius: 4px; text-decoration: none;
                      font-size: 12px; font-weight: 500;">
                View Shelter &amp; Register
            </a>
        </div>
        """
        popup = folium.Popup(popup_html, max_width=300)

        # Create a marker for each shelter
        folium.Marker(location= [lat, long], tooltip= 'Shelter', popup= popup, icon= folium.Icon(icon = 'home', color = 'persimmon')).add_to(shelter_map)

    MousePosition().add_to(shelter_map)
    # Create limiting regions
    folium.CircleMarker([max_lat, min_lon], tooltip="Upper Left Corner").add_to(shelter_map)
    folium.CircleMarker([min_lat, min_lon], tooltip="Lower Left Corner").add_to(shelter_map)
    folium.CircleMarker([min_lat, max_lon], tooltip="Lower Right Corner").add_to(shelter_map)
    folium.CircleMarker([max_lat, max_lon], tooltip="Upper Right Corner").add_to(shelter_map)

    # Render map directly to HTML string (no file write needed)
    iframe = shelter_map.get_root()._repr_html_()

    return render_template_string(
        """ <!DOCTYPE html>
            <html>
                <body>
                    {{iframe|safe}}
                </body>
            </html> """, iframe=iframe)
  
@bp.route('<int:e_id>/<int:s_id>', methods=('POST', 'DELETE'))
@manager_required
def link_unlink_shelter(e_id, s_id):
    """Link or unlink shelter with emergency."""
    emergency = Emergency.get_one_by_id(e_id)
    if not emergency:
        flash('Emergency not found.')
        return 'Emergency not found.', 404
    
    shelter = Shelter.get_by_id(s_id)
    if not shelter:
        flash('Shelter not found.')
        return 'Shelter not found.', 404
    
    if request.method == 'POST':
        success, error = emergency.assign_shelter(s_id)
    elif request.method == 'DELETE':
        success, error = emergency.remove_shelter(s_id)

    if success:
        if request.method == 'POST':
            flash('Shelter has been linked!', 'success')
        elif request.method == 'DELETE':
            flash('Shelter has been removed.', 'success')
        return '', 204
    else:
        flash(error, 'danger')
        return error, 500
