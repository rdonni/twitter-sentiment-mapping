from typing import Dict, List

import numpy as np
import requests
from geopy import distance
from tqdm import tqdm


def get_boundingbox_country(country, output_as='boundingbox') -> List[float]:
    """
    Get the bounding box of a country in EPSG4326 given a country name
    Value are given by nominatim APIs which is the geocoding software that powers Open Street Map

    Parameters
    ----------
    country : str
        name of the country in english and lowercase
    output_as : 'str
        chose from 'boundingbox' or 'center'. 
         - 'boundingbox' for [latmin, latmax, lonmin, lonmax]
         - 'center' for [latcenter, loncenter]

    Returns
    -------
    output : list
        list with coordinates as str
    """
    # Create url
    url = 'http://nominatim.openstreetmap.org/search?country=' + country + '&format=json&polygon=0'
    response = requests.get(url).json()[0]

    # Parse response to list
    if output_as == 'boundingbox':
        lst = response[output_as]
        output = [float(i) for i in lst]
    if output_as == 'center':
        lst = [response.get(key) for key in ['lat', 'lon']]
        output = [float(i) for i in lst]
    return output


def minimal_radius(country: str) -> float:
    """
    Return the minimal radius for a circle to encompass a country as a float
    """

    latmin, latmax, lonmin, lonmax = np.array(get_boundingbox_country(country, output_as='boundingbox'))
    center = np.array(get_boundingbox_country(country, output_as='center'))

    # We calculate the distance between these points and the center of the country 
    # to define the smallest radius that encompasses the country
    extremal_points = [np.array([center[0], lonmin]),
                       np.array([center[0], lonmax]),
                       np.array([latmin, center[1]]),
                       np.array([latmax, center[1]])]

    # Distance between these extremal points to the center
    possible_radiuses = []
    for point in extremal_points:
        possible_radiuses.append(distance.geodesic(point, center).km)

    radius = max(possible_radiuses)

    return radius


def geocode(countries: List[str]) -> Dict[str, str]:
    """
    Generate a dictionary dict[country: str, geocode: str] from a list of countries

    For some countries not available in nominatim APIs (as Ukraine)
    an approximation of the coordinates obtained by hand is provided
    """
    print('----------------------- Computing geocodes... -----------------------')
    geocodes = {}
    for country in tqdm(countries):
        if country == "Ukraine":
            geocodes[country] = "48.2289622,27.1482283,400km"
        elif country == "Iceland":
            geocodes[country] = '64.128288,-21.827774,240km'
        elif country == 'Kosovo':
            geocodes[country] = '42.667542,21.166191,100km'
        elif country == 'Montenegro':
            geocodes[country] = '42.393097,18.911596,100km'
        else:
            country_center = get_boundingbox_country(country, output_as='center')
            geocodes[country] = f'{country_center[0]},{country_center[1]},{minimal_radius(country)}km'
    print("----------------------- Geocodes generated -----------------------")
    return geocodes
