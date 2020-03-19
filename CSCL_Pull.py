import requests, os, zipfile, arcpy, shutil, datetime, traceback, ConfigParser, sys

'''
This script must be run with the 64-bit version of arcpy that comes with the default installation of ArcGIS Desktop  
or with the version of arcpy that comes with the default installation of ArcGIS Pro. If the 32-bit version of arcpy
that comes with the default installation of ArcGIS Desktop is used the script will encounte a MemoryError.
'''

try:

    # Set configuration file path

    config = ConfigParser.ConfigParser()
    config.read(r"CSCL_Scrape_config_template")

    # Define necessary paths

    zip_dir_path = config.get("SHARED_PATHS", "zip_dir_path")
    zip_public_path = config.get("PULL_PATHS", "zip_public_path")
    zip_citywide_path = config.get("PULL_PATHS", "zip_citywide_path")
    gdb_path = os.path.join(zip_dir_path, "cscl.gdb")
    metadata_path = os.path.join(zip_dir_path, "metadata")
    log_path = config.get("PULL_PATHS", "log_path")


    # Set log path

    log = open(log_path, "a")
    StartTime = datetime.datetime.now().replace(microsecond=0)

    # Delete previous directory and files within

    shutil.rmtree(zip_dir_path, ignore_errors=True)
    os.mkdir(zip_dir_path)
    os.mkdir(metadata_path)

    print("Requesting CSCL Public geodatabase")

    # Establish requests object for connection to download URL for public CSCL data set.

    r = requests.get(config.get("PULL_URLS", "public_url"),
                     allow_redirects=True,
                     verify=True)

    c = r.content

    # Save the downloaded zip to a temporary location on C: drive

    print("Downloading geodatabase")
    open(zip_public_path, "wb").write(c)

    zip = zipfile.ZipFile(zip_public_path)

    # Extract zip to C:\temp\CSCL

    print("Extracting zipped public CSCL files")
    zip.extractall(zip_dir_path)
    print("Export complete")

    print("Requesting CSCL Citywide geodatabase")

    # Establish requests object for connection to download URL

    r = requests.get(config.get("PULL_URLS", "citywide_url"),
                     allow_redirects=True,
                     verify=True)

    c = r.content

    # Save the downloaded zip to a temporary location on C: drive

    print("Downloading geodatabase")
    open(zip_citywide_path, "wb").write(c)

    zip = zipfile.ZipFile(zip_citywide_path)

    # Extract zip to temp directory

    print("Extracting zipped citywide CSCL files")
    zip.extractall(zip_dir_path)
    print("Export complete")


    EndTime = datetime.datetime.now().replace(microsecond=0)
    print("Script runtime: {}".format(EndTime - StartTime))

    log.write(str(StartTime) + "\t" + str(EndTime) + "\t" + str(EndTime - StartTime) + "\n")
    log.close()

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    print(pymsg)
    print(msgs)

    log.write("" + pymsg + "\n")
    log.write("" + msgs + "")
    log.write("\n")
    log.close()