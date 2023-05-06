from django.shortcuts import render
from django.views.decorators.cache import cache_page
import datetime
from map import map
import geopandas as gpd
from .models import Aircraft
from django.db.models import Max
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='10/m', block=True)
@cache_page(120)  # Cache the response for 2 minutes
def aircraft_info(request):
    # Load the shapefile
    shapefile = gpd.read_file("static/gadm41_UKR_shp/gadm41_UKR_0.shp")
    shapefile = shapefile.to_crs(epsg=4326)

    # Retrieve the most recent data for each icao24
    aircraft_qs = Aircraft.objects.values('icao24').annotate(max_id=Max('id')).values('max_id')
    aircraft_df = gpd.GeoDataFrame(
        Aircraft.objects.filter(id__in=aircraft_qs).values(),
        geometry=gpd.points_from_xy(
            Aircraft.objects.filter(id__in=aircraft_qs).values_list('longitude', flat=True),
            Aircraft.objects.filter(id__in=aircraft_qs).values_list('latitude', flat=True)
        ),
        crs=shapefile.crs
    )

    # Perform a spatial join with the shapefile
    aircraft_within = gpd.sjoin(aircraft_df, shapefile, op="within")

    # Create a list of aircraft data
    aircrafts = []
    for index, row in aircraft_within.iterrows():
        aircrafts.append({
            "icao24": row["icao24"],
            "callsign": row["callsign"],
            "origin_country": row["origin_country"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "altitude": row["altitude"],
            "velocity": row["velocity"],
            "heading": row["heading"]
        })
        Aircraft.objects.create(
            icao24=row["icao24"],
            callsign=row["callsign"],
            origin_country=row["origin_country"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            altitude=row["altitude"],
            velocity=row["velocity"],
            heading=row["heading"]
        )

    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Render the template with the aircraft data and the current timestamp
    context = {"aircrafts": aircrafts, "timestamp": timestamp}
    map()
    return render(request, "index.html", context)
