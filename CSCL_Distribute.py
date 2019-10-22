import os, arcpy, datetime, xml.etree.ElementTree as ET, traceback, sys, ConfigParser

'''
This script must be run with the 32-bit version of arcpy that comes with the default installation of ArcGIS Desktop  
If the 32-bit version of arcpy that comes with the default installation of ArcGIS Desktop is not used the script will 
fail as all other available arcpy versions lack the metadata functionality tools provided in the 32-bit version.
'''

# Set configuration file path

config = ConfigParser.ConfigParser()
config.read(r"G:\SCRIPTS\Open_Data_CSCL_Scrape\ini\CSCL_Scrape_config.ini")

# Define necessary paths

zip_dir_path = config.get("SHARED_PATHS", "zip_dir_path")
citywide_gdb_path = os.path.join(zip_dir_path, "cscL.gdb")
public_gdb_path = os.path.join(zip_dir_path, "cscl_pub.gdb")
sde_path = config.get("DISTRIBUTE_PATHS", "sde_path")
metadata_path = os.path.join(zip_dir_path, "metadata")
Arcdir = arcpy.GetInstallInfo("desktop")["InstallDir"]
translator = Arcdir + "Metadata/Translator/ARCGIS2FGDC.xml"
stylesheet = Arcdir + "Metadata/Stylesheets/gpTools/remove geoprocessing history.xslt"
m_drive_path = config.get("DISTRIBUTE_PATHS", "m_drive_path")
today = datetime.datetime.now()
today_longform = datetime.datetime.strftime(today, "%b %d %Y")
log_path = config.get("DISTRIBUTE_PATHS", "log_path")

try:

    # Disconnect active users who may be locking desired SDE Feature Classes

    arcpy.AcceptConnections(sde_path, False)
    arcpy.DisconnectUser(sde_path, "ALL")

    # Define log file variable for writing run-times and/or error messages

    log = open(log_path, "a")
    StartTime = datetime.datetime.now().replace(microsecond=0)

    # Define function for parsing and copying CSCL gdb to SDE

    def copy_modify_fc(fc, gdb_path):
        arcpy.env.workspace = gdb_path
        arcpy.env.overwriteOutput = True
        desc = arcpy.Describe(fc)
        if hasattr(desc, "dataType"):
            print("Data set Data Type - {}".format(desc.dataType))
            if desc.dataType == "FeatureClass":
                print("Copying {} to SDE".format(fc))
                arcpy.env.workspace = sde_path
                arcpy.env.overwriteOutput = True
                arcpy.FeatureClassToFeatureClass_conversion(os.path.join(gdb_path, fc), sde_path, "CSCL_{}".format(fc))
                print("{} copy complete".format(fc))
                arcpy.ExportMetadata_conversion(os.path.join(sde_path, "CSCL_{}".format(fc)),
                                                translator,
                                                os.path.join(metadata_path, "{}.xml".format(fc)))
                print("Exporting metadata with geoprocessing history removed")
                arcpy.XSLTransform_conversion(os.path.join(metadata_path, "{}.xml".format(fc)),
                                              stylesheet,
                                              os.path.join(metadata_path, "{}_xslt.xml".format(fc)))
                print("Metadata exported")
                tree = ET.parse(os.path.join(metadata_path, "{}_xslt.xml".format(fc)))
                root = tree.getroot()
                print("Removing Publication Date since it is not currently maintained")
                for citeinfo in root.iter("citeinfo"):
                    for pubdate in citeinfo.findall("pubdate"):
                        citeinfo.remove(pubdate)
                print("Publication Date removed")
                print("Appending download date to metadata description")
                for descrip in root.iter("purpose"):
                    descrip.text = descrip.text + " Dataset Last Downloaded: {}".format(today_longform)
                tree.write(os.path.join(metadata_path, "{}_xslt_moded.xml".format(fc)))
                print("Download date appended to metadata description")
                print("Importing altered metadata to SDE")
                arcpy.MetadataImporter_conversion(os.path.join(metadata_path, "{}_xslt_moded.xml".format(fc)),
                                                  os.path.join(sde_path, "CSCL_{}".format(fc)))
                print("Metadata imported")
                arcpy.UpgradeMetadata_conversion(os.path.join(sde_path, "CSCL_{}".format(fc)), "FGDC_TO_ARCGIS")
                print("Metadata upgraded")
            if desc.dataType == "Table":
                print("Copying {} to SDE".format(fc))
                arcpy.env.workspace = sde_path
                arcpy.env.overwriteOutput = True
                arcpy.TableToTable_conversion(os.path.join(gdb_path, fc), sde_path, "CSCL_{}".format(fc))
                print("{} copy complete".format(fc))
                arcpy.ExportMetadata_conversion(os.path.join(sde_path, "CSCL_{}".format(fc)),
                                                translator,
                                                os.path.join(metadata_path, "{}.xml".format(fc)))
                print("Exporting metadata with geoprocessing history removed")
                arcpy.XSLTransform_conversion(os.path.join(metadata_path, "{}.xml".format(fc)),
                                              stylesheet,
                                              os.path.join(metadata_path, "{}_xslt.xml".format(fc)))
                print("Metadata exported")
                tree = ET.parse(os.path.join(metadata_path, "{}_xslt.xml".format(fc)))
                root = tree.getroot()
                print("Removing Publication Date since it is not currently maintained")
                for citeinfo in root.iter("citeinfo"):
                    for pubdate in citeinfo.findall("pubdate"):
                        citeinfo.remove(pubdate)
                print("Publication Date removed")
                print("Appending download date to metadata description")
                for descrip in root.iter("purpose"):
                    descrip.text = descrip.text + " Dataset Last Downloaded: {}".format(today_longform)
                tree.write(os.path.join(metadata_path, "{}_xslt_moded.xml".format(fc)))
                print("Download date appended to metadata description")
                print("Importing altered metadata to SDE")
                arcpy.MetadataImporter_conversion(os.path.join(metadata_path, "{}_xslt_moded.xml".format(fc)),
                                                  os.path.join(sde_path, "CSCL_{}".format(fc)))
                print("Metadata imported")
                arcpy.UpgradeMetadata_conversion(os.path.join(sde_path, "CSCL_{}".format(fc)), "FGDC_TO_ARCGIS")
                print("Metadata upgraded")

    # Define list of datasets based on their individual pull locations

    print("Setting desired Feature Class array")

    public_products_fcs = ["AddressPoint", "AssemblyDistrict", "Borough", "BusinessImprovementDistrict", "CensusBlock2000",
                           "CensusBlock2010", "CensusTract2000", "CensusTract2010", "CityCouncilDistrict",
                           "CommonPlace", "CommunityDistrict", "Complex", "CongressionalDistrict", "ElectionDistrict",
                           "FerryLanding", "FireCompany", "HealthArea", "HealthCenterDistrict", "HistoricDistrict",
                           "HurricaneEvacuationZone", "MunicipalCourtDistrict", "NamedIntersection", "Neighborhood",
                           "NYPDPrecinct", "RailStation", "SchoolDistrict", "StateSenateDistrict",
                           "TollBooth", "ZipCode"]
    public_products_tbls = ["ALTSEGMENTDATA", "StreetName"]
    public_cscl_products_fcs = ["Centerline", "MilePost", "NonStreetFeature", "Rail", "ReferenceMarker", "Subway"]
    citywide_cscl_products_fcs = ["AtomicPolygon", "Node", "Shoreline"]

    # Setting workspace to CSCL public geodatabase

    print("Setting environment workspace to temp CSCL geodatabase")
    arcpy.env.workspace = public_gdb_path

    # Parse Public CSCL geodatabase CSCL Feature Dataset feature classes [1]

    print("Getting total count for feature classes in public CSCL gdb CSCL Feature Dataset")
    count = 1
    for fc in arcpy.ListFeatureClasses(feature_dataset="CSCL"):
        print(fc, public_cscl_products_fcs)
        if fc in public_cscl_products_fcs:
            print("{} - {} of {}".format(fc, count, len(public_cscl_products_fcs)))
            copy_modify_fc(fc, public_gdb_path)
            count += 1

    print("Setting environment workspace to temp CSCL geodatabase")
    arcpy.env.workspace = public_gdb_path

    # Parse Public CSCL geodatabase feature classes [2]

    print("Getting total count for feature classes in public CSCL gdb")
    count = 1
    for fc in arcpy.ListFeatureClasses():
        print(fc, public_products_fcs)
        if fc in public_products_fcs:
            print("{} - {} of {}".format(fc, count, len(public_products_fcs)))
            copy_modify_fc(fc, public_gdb_path)
            count += 1

    print("Setting environment workspace to temp CSCL geodatabase")
    arcpy.env.workspace = public_gdb_path

    # Parse Public CSCL geodatabase tables [3]

    print("Getting total count for tables in public CSCL gdb")
    count = 1
    for tbl in arcpy.ListTables():
        print(tbl, public_products_fcs)
        if tbl in public_products_tbls and tbl is not "STREETNAME_A4":
            print("{} - {} of {}".format(tbl, count, len(public_products_tbls)))
            copy_modify_fc(tbl, public_gdb_path)
            count += 1

    # Setting workspace for CSCL citywide Geodatabase

    print("Setting environment workspace to temp CSCL geodatabase")
    arcpy.env.workspace = citywide_gdb_path

    print("Getting total count for feature classes in citywide CSCL gdb CSCL Feature Dataset")
    count = 1
    for fc in arcpy.ListFeatureClasses(feature_dataset="CSCL"):
        print(fc, citywide_cscl_products_fcs)
        if fc in citywide_cscl_products_fcs:
            print("{} - {} of {}".format(fc, count, len(citywide_cscl_products_fcs)))
            copy_modify_fc(fc, citywide_gdb_path)
            count += 1

    # Create required Relationship Classes

    arcpy.env.workspace = sde_path
    arcpy.env.overwriteOutput = True

    print("Creating CSCL_CenterlinesHaveAltAddresses Relationship Class")

    arcpy.CreateRelationshipClass_management("CSCL_Centerline",
                                             "CSCL_ALTSEGMENTDATA",
                                             "CSCL_CenterlinesHaveAltAddresses",
                                             "SIMPLE",
                                             "CSCL_ALTSEGMENTDATA",
                                             "CSCL_Centerline",
                                             "NONE",
                                             "ONE_TO_MANY",
                                             False,
                                             "PHYSICALID",
                                             "PHYSICALID")

    print("CSCL_CenterlinesHaveAltAddresses Relationship Class created")
    print("Creating CSCL_CenterlinesHaveNames Relationship Class")

    arcpy.CreateRelationshipClass_management("CSCL_Centerline",
                                             "CSCL_StreetName",
                                             "CSCL_CenterlinesHaveNames",
                                             "SIMPLE",
                                             "CSCL_StreetName",
                                             "CSCL_Centerline",
                                             "NONE",
                                             "ONE_TO_MANY",
                                             False,
                                             "B7SC",
                                             "B7SC")

    print("CSCL_CenterlinesHaveNames Relationship Class created")

    # Export metadata for each respective layer file

    sde_xml_dict = {"Address point (CSCL).lyr.xml": "CSCL_AddressPoint",
                    "Assembly district (CSCL).lyr.xml": "CSCL_AssemblyDistrict",
                    "Borough (CSCL).lyr.xml": "CSCL_Borough",
                    "Business improvement districts (CSCL).lyr.xml": "CSCL_BusinessImprovementDistrict",
                    "Census block - 2000 (CSCL).lyr.xml": "CSCL_CensusBlock2000",
                    "Census block - 2010 (CSCL).lyr.xml": "CSCL_CensusBlock2010",
                    "Census tract - 2000 (CSCL).lyr.xml": "CSCL_CensusTract2000",
                    "Census tract - 2010 (CSCL).lyr.xml": "CSCL_CensusTract2010",
                    "Centerline (CSCL).lyr.xml": "CSCL_Centerline",
                    "City council district (CSCL).lyr.xml": "CSCL_CityCouncilDistrict",
                    "Common place (CSCL).lyr.xml": "CSCL_CommonPlace",
                    "Community district (CSCL).lyr.xml": "CSCL_CommunityDistrict",
                    "Complex (CSCL).lyr.xml": "CSCL_Complex",
                    "Congressional district (CSCL).lyr.xml": "CSCL_CongressionalDistrict",
                    "Election district (CSCL).lyr.xml": "CSCL_ElectionDistrict",
                    "Ferry landing (CSCL).lyr.xml": "CSCL_FerryLanding",
                    "Fire company (CSCL).lyr.xml": "CSCL_FireCompany",
                    "Health area (CSCL).lyr.xml": "CSCL_HealthArea",
                    "Health center district (CSCL).lyr.xml": "CSCL_HealthCenterDistrict",
                    "Historic district (CSCL).lyr.xml": "CSCL_HistoricDistrict",
                    "Milepost (CSCL).lyr.xml": "CSCL_MilePost",
                    "Municipal court district (CSCL).lyr.xml": "CSCL_MunicipalCourtDistrict",
                    "Neighborhood (CSCL).lyr.xml": "CSCL_Neighborhood",
                    "Node (CSCL).lyr.xml": "CSCL_Node",
                    "Non-street feature (CSCL).lyr.xml": "CSCL_NonStreetFeature",
                    "NYPD precinct (CSCL).lyr.xml": "CSCL_NYPDPrecinct",
                    "Rail line (CSCL).lyr.xml": "CSCL_Rail",
                    "Rail station (CSCL).lyr.xml": "CSCL_RailStation",
                    "Reference marker (CSCL).lyr.xml": "CSCL_ReferenceMarker",
                    "School district (CSCL).lyr.xml": "CSCL_SchoolDistrict",
                    "Shoreline (CSCL).lyr.xml": "CSCL_Shoreline",
                    "State senate district (CSCL).lyr.xml": "CSCL_StateSenateDistrict",
                    "Subway route (CSCL).lyr.xml": "CSCL_Subway",
                    "Subway station (CSCL).lyr.xml": "CSCL_SubwayStation",
                    "Toll booth (CSCL).lyr.xml": "CSCL_TollBooth",
                    "ZIP code area (CSCL).lyr.xml": "CSCL_ZipCode"}

    xml_list = []

    for xml in os.listdir(m_drive_path):
        if xml.endswith(".xml"):
            xml_list.append(xml)

    arcpy.env.workspace = m_drive_path
    arcpy.env.overwriteOutput = True

    for xml in sde_xml_dict.keys():
        try:
            print("Exporting metadata from {} to {}".format(sde_path + r"\GISPROD.SDE.{}".format(sde_xml_dict[xml]),
                                                            os.path.join(m_drive_path, xml)))
            arcpy.ExportMetadata_conversion(sde_path + r"\GISPROD.SDE.{}".format(sde_xml_dict[xml]),
                                            translator,
                                            os.path.join(m_drive_path, xml))
        except Exception as e:
            print(e)

    # Reconnect SDE users

    arcpy.AcceptConnections(sde_path, True)

    EndTime = datetime.datetime.now().replace(microsecond=0)
    print("Script runtime: {}".format(EndTime - StartTime))

    log.write(str(StartTime) + "\t" + str(EndTime) + "\t" + str(EndTime - StartTime) + "\n")
    log.close()

except:

    # Reconnect SDE users and log errors that were thrown during script process
    arcpy.AcceptConnections(sde_path, True)

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