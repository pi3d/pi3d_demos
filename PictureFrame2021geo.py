import os
import locale
from PictureFrame2021pic import Picture
from PictureFrame2021config import Config
from geopy.geocoders import Nominatim  ## NB other geo services will need different code



gps_data = {}
if os.path.isfile(config.GEO_PATH):
    with open(config.GEO_PATH) as gps_file:
        for line in gps_file:
            if line == '\n':
                continue
            (name, var) = line.partition('=')[::2]
            gps_data[name] = var.rstrip('\n')


def get_location(pic: Picture, config: Config):
    lat = pic.exif_data.lat
    latRef = pic.exif_data.lat_ref
    lon = pic.exif_data.lon
    lonRef = pic.exif_data.lon_ref
    decimal_lat = ((lat[0][0] / lat[0][1])
                   + (lat[1][0] / lat[1][1] / 60)
                   + (lat[2][0] / lat[2][1] / 3600))
    decimal_lon = ((lon[0][0] / lon[0][1])
                   + (lon[1][0] / lon[1][1] / 60)
                   + (lon[2][0] / lon[2][1] / 3600))
    if latRef == 'S':
        decimal_lat = -decimal_lat
    if lonRef == 'W':
        decimal_lon = -decimal_lon
    geo_key = "{:.4f},{:.4f}".format(decimal_lat, decimal_lon)

    if geo_key not in gps_data:
        language = locale.getlocale()[0][:2]
        try:
            # """
            geolocator = Nominatim(user_agent=config.geo_key)
            location = geolocator.reverse(geo_key, language=language, zoom=config.geo_zoom).address.split(",")
            location_split = [loc.strip() for loc in location]
            formatted_address = ""
            comma = ""
            for part in location_split:
                if any(c in config.codepoints for c in part):
                    formatted_address = "{}{}{}".format(formatted_address, comma, part)
                    comma = ", "
            """
      # alternative using OSM tags directly. NB you should comment out the section
      # above from `geolocator = ..`, also your config.GEO_KEY should be your email address
      import json
      import urllib.request
      URL = "https://nominatim.openstreetmap.org/reverse?format=geojson&lat={}&lon={}&zoom={}&email={}&accept-language={}"
      with urllib.request.urlopen(URL.format(decimal_lat, decimal_lon, config.GEO_ZOOM, config.GEO_KEY, language)) as req:
          data = json.loads(req.read().decode())
      adr = data['features'][0]['properties']['address']
      # change the line below to include the details you want. See nominatim.org/release-docs/develop/api/Reverse/
      # because OSM doesn't use fixed tags you probably have to experiment!
      # i.e. `suburb` will be invalid for rural images, `village` invalid for urban ones
      if 'suburb' in adr and 'city' in adr:
        formatted_address = "{}, {}, {}".format(adr['country'], adr['city'], adr['suburb'])
      elif 'village' in adr and 'city' in adr:
        formatted_address = "{}, {}, {}".format(adr['country'], adr['city'], adr['village'])
      else:
        formatted_address = ", ".join(adr.values())
      """
            if len(formatted_address) > 0:
                gps_data[geo_key] = formatted_address
                with open(config.GEO_PATH, 'a+') as file:
                    file.write("{}={}\n".format(geo_key, formatted_address))
                return formatted_address
        except Exception as e:
            print(e)  # TODO debugging
            return "Location Not Available"
    else:
        return gps_data[geo_key]

    return "No GPS Data"
