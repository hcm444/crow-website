import sqlite3
import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import csv


class FlightMap:
    def __init__(self, db_filename, shapefile):
        self.conn = sqlite3.connect(db_filename)
        self.gdf = gpd.read_file(shapefile)
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.flight_time = datetime.utcnow() - timedelta(hours=1)

    def plot_routes(self):
        self.ax.set_facecolor('black')
        self.ax.set_axis_off()
        self.gdf.plot(ax=self.ax, edgecolor='green', facecolor='none')  # Set border color to green
        c = self.conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'aircraft_%'")
        tables = c.fetchall()
        for table in tables:
            table_name = table[0]
            c.execute(
                f"SELECT icao24, latitude, longitude, timestamp, callsign FROM {table_name} WHERE strftime('%Y-%m-%d %H:%M:%S', timestamp) >= strftime('%Y-%m-%d %H:%M:%S', ?)",
                (self.flight_time.strftime('%Y-%m-%d %H:%M:%S'),))
            rows = c.fetchall()
            if len(rows) > 1:
                flights = {}
                for row in rows:
                    flight_id, lat, lon, _, callsign = row
                    if flight_id not in flights:
                        flights[flight_id] = [[], [], []]
                    flights[flight_id][0].append(lon)
                    flights[flight_id][1].append(lat)
                    flights[flight_id][2].append(callsign)
                for flight_id, coords in flights.items():
                    lons, lats, callsigns = coords
                    alpha = 0.0
                    num_points = len(lons) - 1
                    for i in range(num_points):
                        if num_points > 1:
                            alpha += 1 / (num_points - 1)
                        self.ax.plot([lons[i], lons[i + 1]], [lats[i], lats[i + 1]], alpha=min(alpha, 1), color='white')
                    latest_lat = lats[-1]
                    latest_lon = lons[-1]
                    latest_callsign = callsigns[-1]
                    self.ax.annotate(f"{latest_callsign} ({flight_id})", xy=(latest_lon, latest_lat), xytext=(0, 5),
                                     textcoords='offset points', color='white', fontsize=7)

    def plot_cities(self, csv_file):
        with open(csv_file) as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                city_name, lat, lon = row[0], float(row[1]), float(row[2])
                self.ax.scatter(lon, lat, color='green', s=10, label='')
                self.ax.annotate(city_name, xy=(lon, lat), xytext=(0, 5), textcoords='offset points', color='green',
                                 fontsize=8)

    def save(self, filename, dpi=100):
        self.fig.patch.set_facecolor('black')
        plt.savefig(filename, dpi=dpi, facecolor='black', bbox_inches='tight')
        handles, labels = self.ax.get_legend_handles_labels()
        legend_fig = plt.figure(figsize=(4, 2))
        plt.legend(handles, labels, loc='center', title_fontsize='small', facecolor='green', framealpha=0.7,
                   fontsize=10)
        plt.axis('off')
        legend_fig.savefig('static/maps/legend.png', dpi=dpi, facecolor='black', bbox_inches='tight')
        if self.ax.get_legend():
            self.ax.get_legend().remove()


def map():
    flight_map = FlightMap('db.sqlite3', 'static/gadm41_UKR_shp/gadm41_UKR_1.shp')
    flight_map.plot_routes()
    flight_map.plot_cities('ukraine_cities.csv')
    flight_map.save('static/maps/map.png')



