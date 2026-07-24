from math import radians, sin, cos, sqrt, atan2

from django.conf import settings

EARTH_RADIUS = 6371000  # meters


def distance_in_meters(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two GPS coordinates
    using the Haversine formula.
    """

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return EARTH_RADIUS * c


def is_within_tolerance(lat1, lon1, lat2, lon2):
    """
    Returns True if the two coordinates are within
    the configured tolerance distance.
    """

    distance = distance_in_meters(lat1, lon1, lat2, lon2)

    return distance <= settings.FLOOD_REPORT_TOLERANCE_METERS