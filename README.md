# CSCL Web Scrape

*******************************

The NYC Street Centerline (CSCL) is a road-bed representation of New York City streets containing address ranges and other information such as traffic directions, road types, segment types These scripts are used to scrape the DOITT's Citywide GIS data repository for the most recent CSCL data sets to update and distribute accordingly across DCP's internal network file-systems.

### Prerequisites

##### CSCL\_Pull.py

```
requests, os, zipfile, arcpy, shutil, datetime, traceback, ConfigParser, sys
```

##### CSCL\_Distribute.py

```
os, arcpy, datetime, xml.etree.ElementTree as ET, traceback, sys, ConfigParser
```

### Instructions for running

##### CSCL\_Pull.py

1. Open the script in any integrated development environment (PyCharm is suggested)

2. Ensure that your IDE is set to be using the 64-bit version of Python 2 that comes with the default installation of ArcGIS Desktop with 64-bit Background Geoprocessing installed or a version of Python 3. Also ensure that the required python packages are available in whichever version of Python that is used.

3. Ensure that the configuration ini file is up-to-date with path variables. If any paths have changed since the time of this writing, those changes must be reflected in the Config.ini file.

4. Run the script. It will pull the latest public and citywide CSCL release data sets as zips and extract them to a CSCL directory in the user's temp directory


##### CSCL\_Distribute.py

1. Open the script in any integrated development environment (PyCharm is suggested)

2. Ensure that your IDE is set to be using the 32-bit version of Python 2 that comes with the default installation of ArcGIS Desktop. This version of Python must be used to acccess the metadata functionality not currently available in other ArcGIS python distributions.

3. Ensure that the configuration ini file is up-to-date with path variables. If any paths have changed since the time of this writing, those changes must be reflected in the Config ini file.

4. Run the script. It will disconnect users from the Production SDE, parse the downloaded public and citywide geodatabases for requisite data sets, and replace out-of-date Feature Classes/Tables with their downloaded equivalent on the Production SDE. It will also create required Relationship Classes between certain FCs and Tables and update/replace metadata information for related CSCL layer files across DCP's internal filesystem network.

5. After the SDE/layer files have been updated, the script will re-allow connections to the Production SDE and log results of the script (including any errors that arose during runtime)
