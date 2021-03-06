import sys
import time
import board
from adafruit_pyportal import PyPortal
cwd = ("/"+__file__).rsplit('/', 1)[0] # the current working directory (where this file is)
sys.path.append(cwd)
import covid_graphics  # pylint: disable=wrong-import-position

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Use country
LOCATION = "usa"

# Set up where we'll be fetching data from
DATA_SOURCE = "https://corona.lmao.ninja/countries/"+LOCATION
DATA_LOCATION = []


# Initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=DATA_SOURCE,
                    json_path=DATA_LOCATION,
                    status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000)

gfx = covid_graphics.Covid_Graphics(pyportal.splash, am_pm=True)

localtile_refresh = None
covid_refresh = None
while True:
    # only query the online time once per hour (and on first run)
    if (not localtile_refresh) or (time.monotonic() - localtile_refresh) > 3600:
        try:
            print("Getting time from internet!")
            pyportal.get_local_time()
            localtile_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    # only query the covid data every 5 minutes (and on first run)
    if (not covid_refresh) or (time.monotonic() - covid_refresh) > 300:
        try:
            value = pyportal.fetch()
            print("Querying corona stats")
            gfx.display_cases(value)
            covid_refresh = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue

    gfx.update_time()

    time.sleep(30)  # wait 30 seconds before updating anything again