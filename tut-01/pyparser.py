import configparser

# Helper function to convert string to upper case and trim whitespaces
def inip_toupper_replace(value):
    return value.strip().upper()

# Initialize the configparser
config = configparser.ConfigParser()

# Reading from the INI file
filename = "cE3Dfile.ini"
config.read(filename)

# Variables initialization
myProcess = {"iInd": 0, "Rotation": ""}
mySigma = {
    "ScrewCylinderRendering": False,
    "cType": "",
    "DIE_Start": 0.0,
    "DIE_Length": 0.0,
    "DIE_SymmetryBC": "",
    "Dz_out": 0.0,
    "W": 0.0,
    "Dzz": 0.0,
    "cZwickel": "",
    "Dz_in": 0.0,
    "InnerDiamNParam": 0,
    "InnerDiamDParam": [],
    "InnerDiamZParam": [],
    "L": 0.0,
    "L0": 0.0,
    "NumberOfSeg": 0,
    "GANGZAHL": 0,
    "bOnlyBarrelAdaptation": False,
    "RotationAxis": "",
    "a": 0.0,
    "RotAxisAngle": 0.0,
    "RotAxisCenter": 0.0
}

dSizeScale = 1.0
myInf = float('inf')
cRotation = ""
cUnit = ""
cSCR = ""
cauxD = ""
cauxZ = ""
cOnlyBarrelAdaptation = ""

# Helper function to safely get values from the config
def get_value(section, key, default_value):
    if config.has_option(section, key):
        return config.get(section, key)
    return default_value

# Helper function to safely get numeric values from the config
def get_value_double(section, key, default_value):
    if config.has_option(section, key):
        return config.getfloat(section, key)
    return default_value

def get_value_int(section, key, default_value):
    if config.has_option(section, key):
        return config.getint(section, key)
    return default_value

# Process RotationType
cRotation = get_value("E3DGeometryData/Machine", "RotationType", 'co')
cRotation = inip_toupper_replace(cRotation)
myProcess["iInd"] = 1
if cRotation in ["COUNTER", "COUNTERROTATING"]:
    myProcess["iInd"] = -1

# Process RotationDirection
cRotation = get_value("E3DGeometryData/Machine", "RotationDirection", 'NoRotation')
cRotation = inip_toupper_replace(cRotation)
if cRotation in ["R", "RECHTS", "RIGHT"]:
    myProcess["ind"] = 1
elif cRotation in ["LINKS", "LEFT", "L"]:
    myProcess["ind"] = -1
else:
    myProcess["ind"] = 0

myProcess["Rotation"] = cRotation
if myProcess["ind"] == 0:
    print("rotation direction is not defined")
    print(f'"{myProcess["Rotation"]}"')

# Process Unit
cUnit = get_value("E3DGeometryData/Machine", "Unit", 'MM')
cUnit = inip_toupper_replace(cUnit)
if cUnit not in ['MM', 'CM', 'DM', 'M']:
    print("Unit type is invalid. Only MM, CM, DM or 'M' units are allowed ", cUnit)
    cUnit = 'MM'

dSizeScale = {
    'MM': 0.1,
    'CM': 1.0,
    'DM': 10.0,
    'M': 100.0
}.get(cUnit, 1.0)

# Process ScrewCylinderRendering
cSCR = get_value("E3DGeometryData/Machine", "ScrewCylinderRendering", 'YES')
cSCR = inip_toupper_replace(cSCR)
mySigma["ScrewCylinderRendering"] = cSCR in ["YES", "ON"]

# Process Machine Type
mySigma["cType"] = get_value("E3DGeometryData/Machine", "Type", 'SSE')
mySigma["cType"] = inip_toupper_replace(mySigma["cType"])

if mySigma["cType"] not in ["SSE", "TSE", "DIE", "XSE", "NETZSCH"]:
    print("not a valid Extruder type:", mySigma["cType"])
    raise ValueError("Invalid Extruder Type")

# Continue processing other parameters in a similar fashion

# Process GeometryStart
mySigma["GeometryStart"] = get_value("E3DGeometryData/Machine", "GeometryStart", '_INVALID_')
mySigma["GeometryStart"] = inip_toupper_replace(mySigma["GeometryStart"])
if mySigma["GeometryStart"] != '_INVALID_':
    try:
        mySigma["DIE_Start"] = dSizeScale * float(mySigma["GeometryStart"])
    except ValueError:
        print("   Wrong DIE start has been set:", mySigma["GeometryStart"])
        raise ValueError("Invalid DIE Start Value")

# Continue similarly for GeometryLength, GeometrySymmetryBC, and others...

# This pattern follows for other sections of the original Fortran code.
