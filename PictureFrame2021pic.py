import logging
import os
from datetime import datetime

from PIL import ExifTags, Image

log = logging.getLogger(__name__)

EXIF_DATE_TIME_ORIG = 'DateTimeOriginal'
EXIF_ORIENTATION = 'Orientation'
EXIF_RATING = 'Rating'
EXIF_GPS_INFO = 'GPSInfo'

EXIF_GPS_INFO_LAT = 'GPSLatitude'
EXIF_GPS_INFO_LAT_REF = 'GPSLatitudeRef'
EXIF_GPS_INFO_LON = 'GPSLongitude'
EXIF_GPS_INFO_LON_REF = 'GPSLongitudeRef'


class ExifData:
    def __init__(self, path):
        self.reverse_exif_tags = {v: k for k, v in ExifTags.TAGS.items()}
        self.reverse_exif_gps_tags = {v: k for k, v in ExifTags.GPSTAGS.items()}
        image = Image.open(path)
        try:
            self._exif_data = image.getexif()
        except AttributeError:
            log.debug(f'No getexif function for file {path}. Trying _getexif')
            self._exif_data = image._getexif()
        if self._exif_data is None:
            log.info(f'No exif data found for file {path}')
        self.orig_date_time = self._get_date_time(path)
        self.orientation = int(self._get_from_exif(EXIF_ORIENTATION) or 1)
        self.rating = int(self._get_from_exif(EXIF_RATING) or -1)
        self._gps = self._get_from_exif(EXIF_GPS_INFO)
        self.lat = self._get_from_gps_exif(EXIF_GPS_INFO_LAT)
        self.lat_ref = self._get_from_gps_exif(EXIF_GPS_INFO_LAT_REF)
        self.long = self._get_from_gps_exif(EXIF_GPS_INFO_LON)
        self.long_ref = self._get_from_gps_exif(EXIF_GPS_INFO_LON_REF)

    def _get_from_exif(self, tag):
        if tag in self.reverse_exif_tags:
            exif_tag = self.reverse_exif_tags[tag]
            if self._exif_data and exif_tag in self._exif_data:
                return self._exif_data[exif_tag]
        return None

    def _get_from_gps_exif(self, tag):
        if tag in self.reverse_exif_gps_tags:
            exif_gps_tag = self.reverse_exif_gps_tags[tag]
            if self._gps and exif_gps_tag in self._gps:
                return self._gps[exif_gps_tag]
        return None

    def _get_date_time(self, path):
        exif_dt = self._get_from_exif(EXIF_DATE_TIME_ORIG)
        if exif_dt:
            return datetime.strptime(exif_dt, '%Y:%m:%d %H:%M:%S')
        else:
            return datetime.fromtimestamp(os.path.getmtime(path))

    def __str__(self):
        return f'Original Date Time: {self.orig_date_time}\n' \
               f'Orientation: {self.orientation}\n' \
               f'Rating: {self.rating}\n' \
               f'GPS: {self._gps}'


def lazy_property(fn):
    """
    Decorator that makes a property lazy-evaluated.
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


class Picture:
    def __init__(self, path):
        self.path = path

    @lazy_property
    def exif_data(self) -> ExifData:
        return ExifData(self.path)

    def __str__(self):
        return f'Picture:\n' \
               f'File Path: {self.path}\n' \
               f'Exif Data:\n{self.exif_data}'
