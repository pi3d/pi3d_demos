import os
import locale
import PIL
from PIL import ExifTags
from geopy.geocoders import Nominatim ## NB other geo services will need different code
import PictureFrame2020config as config

EXIF_GPSINFO = None
EXIF_GPSINFO_LAT = None
EXIF_GPSINFO_LAT_REF = None
EXIF_GPSINFO_LON = None
EXIF_GPSINFO_LON_REF = None

for k in ExifTags.TAGS:
  if ExifTags.TAGS[k] == 'GPSInfo':
    EXIF_GPSINFO = k

for k in ExifTags.GPSTAGS:
  if ExifTags.GPSTAGS[k] == 'GPSLatitude':
    EXIF_GPSINFO_LAT = k
  if ExifTags.GPSTAGS[k] == 'GPSLatitudeRef':
    EXIF_GPSINFO_LAT_REF = k
  if ExifTags.GPSTAGS[k] == 'GPSLongitude':
    EXIF_GPSINFO_LON = k
  if ExifTags.GPSTAGS[k] == 'GPSLongitudeRef':
    EXIF_GPSINFO_LON_REF = k

gps_data = {}
if os.path.isfile(config.GEO_PATH):
  with open(config.GEO_PATH) as gps_file:
    for line in gps_file:
      if line == '\n':
        continue
      (name, var) = line.partition('=')[::2]
      gps_data[name] = var.rstrip('\n')

def get_location(gps_info):
  lat = gps_info[EXIF_GPSINFO_LAT]
  latRef = gps_info[EXIF_GPSINFO_LAT_REF]
  lon = gps_info[EXIF_GPSINFO_LON]
  lonRef = gps_info[EXIF_GPSINFO_LON_REF]

  if isinstance(lat[0], PIL.TiffImagePlugin.IFDRational):
    decimal_lat = (float(lat[0])
                + (float(lat[1]) / 60)
                + (float(lat[2]) / 3600))
    decimal_lon = (float(lon[0])
                + (float(lon[1]) / 60)
                + (float(lon[2]) / 3600))
  else:
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
      #"""
      geolocator = Nominatim(user_agent=config.GEO_KEY)
      location = geolocator.reverse(geo_key, language=language, zoom=config.GEO_ZOOM).address.split(",")
      location_split = [loc.strip() for loc in location]
      formatted_address = ""
      comma = ""
      for part in location_split:
        if any(c in config.CODEPOINTS for c in part):
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
      print(e) #TODO debugging
      return "Location Not Available"
  else:
    return gps_data[geo_key]

  return "No GPS Data"
