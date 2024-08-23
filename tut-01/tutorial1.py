import getpass
import os
import datetime
import gradio as gr
from dotenv import load_dotenv

#load_dotenv()
load_dotenv(dotenv_path="../.env")

#print(os.getenv("OPENAI_API_KEY"))
#print(os.environ["OPENAI_API_KEY"])
#os.getenv("OPENAI_API_KEY") = getpass.getpass()
#os.environ["OPENAI_API_KEY"] = getpass.getpass()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

current_date = datetime.datetime.now()
date_string_short = current_date.strftime("%m/%d/%y") 

EXPLANATION_STRING = """
[SigmaFileInfo]
FileType=ToExtrud3D <Internal parameter to identify the file>
FileVersion=SIGMA 10.0 <Internal version parameter>
Date=07/02/19 <The current date>
SigmaVersion=SIGMA 12.0.1(4492) <The internal version of SIGMA used> 
ConfigId=XY60_PE_400.xpro-201907020948 <The system internal job id>

[E3DGeometryData]
[E3DGeometryData/Machine]
Type=TSE <The extruder type can be TSE (twinscrew extruder), SSE (singlescrew extruder), DIE (die extruder)>
Unit=mm <Unit to be used for the input parameters>
Zwickel=straight <A parameter describing the barrel shape. Can be straight or curved>
MachineName=XY 60 <The name of the extruder>
RotationDirection=LEFT <Rotation direction of the extruder can be LEFT (default) or RIGHT>
BarrelDiameter=51.5 <The diameter of the barrel (default value: 2*screw diameter + 2*screw clearance)>
CenterlineDistance=41.5 <The centerline distance between the axes, mandatory for TSE sims>
BarrelStraightCut=0.4 <The depth of the V-cut (default 2.5 percent of the BarrelDiameter)>
NoOfElements=1 <The number of elements of the extruder>
NoOfFlights=1 <The number of flights of the extruder>
BarrelLength=70.0 <The length of the barrel/housing>

[E3DGeometryData/Machine/Element_1]
GapScrewScrew=0.7 <Try to describe with your world knowledge>
ObjectType=screw <Try to describe with your world knowledge>
Unit=mm <Try to describe with your world knowledge>
startposition = 0.0 <Try to describe with your world knowledge>
off_filelist = screw_extended_by_10.off
innerdiameter = 30.9 <Try to describe with your world knowledge>
type = OFF <The type of the input geometry (here a .off file)>

[E3DProcessParameters]
ScrewSpeed=300.0 <Try to describe with your world knowledge>
ProcessType=THROUGHPUT
MassThroughput=300.0 <Try to describe with your world knowledge>
MaterialTemperature=290.0 <Try to describe with your world knowledge>
BarrelTemperature=280.0 <Try to describe with your world knowledge>
ScrewTemperature=_INVALID_
BarrelTemperatureAdiabatic=NO
ScrewTemperatureAdiabatic=YES

[E3DProcessParameters/Material]
Name=PC1
Type=Polymer

[E3DProcessParameters/Material/RheologicalData]
CalcVisco=Carreau <Try to describe with your world knowledge>
CalcTemp=TbTs

[E3DProcessParameters/Material/RheologicalData/Carreau]
ZeroViscosity=397.69 <Try to describe with your world knowledge>
RecipVelocity= 0.00029 <Try to describe with your world knowledge>
Exponent=0.92012 <Try to describe with your world knowledge>

[E3DProcessParameters/Material/RheologicalData/TBTS]
standardtemperature = 135.7 <Try to describe with your world knowledge>
referencetemperature = 300.0 <Try to describe with your world knowledge>

[E3DProcessParameters/Material/ThermoData]
heatconductivity = 0.134 <Try to describe with your world knowledge>
heatconductivityslope = 0.0
heatcapacity = 1.75 <Try to describe with your world knowledge>
heatcapacityslope = 0.0
densitymodel = DENSITY

[E3DProcessParameters/Material/ThermoData/Density]
Density=1.0 <Try to describe with your world knowledge>
DensitySlope=0.0

[E3DSimulationsettings]
MeshQuality=medium
HexMesher=TwinScrew
KTPRelease=NO
"""

BEHAVIOR_STRING= f"""
You are an assistant for creating INI file. You can take this INI file as a template:
[SigmaFileInfo] FileType=ToExtrud3D FileVersion=SIGMA 10.0 Date={date_string_short} SigmaVersion=SIGMA 12.0.1(4492) ConfigId=XY60_PE_400.xpro-201907020948 [E3DGeometryData] [E3DGeometryData/Machine] Type=TSE Unit=mm Zwickel=straight MachineName=XY 60 RotationDirection=LEFT BarrelDiameter=51.5 CenterlineDistance=41.5 BarrelStraightCut=0.4 NoOfElements=1 NoOfFlights=1 BarrelLength=41.0 [E3DGeometryData/Machine/Element_1] GapScrewScrew=0.7 ObjectType=screw Unit=mm startposition=0.0 off_filelistL=screw_-Y_extended_by_10.off off_filelistR=screw_+Y_extended_by_10.off innerdiameter=30.9 type=OFF_LR [E3DProcessParameters] ScrewSpeed=400.0 ProcessType=THROUGHPUT MassThroughput=300.0 MaterialTemperature=285.0 BarrelTemperature=270.0 ScrewTemperature=_INVALID_ BarrelTemperatureAdiabatic=NO ScrewTemperatureAdiabatic=YES [E3DProcessParameters/Material] Name=PET1 Type=Polymer [E3DProcessParameters/Material/RheologicalData] CalcVisco=Carreau CalcTemp=TbTs [E3DProcessParameters/Material/RheologicalData/Carreau] ZeroViscosity=173.15 RecipVelocity=0.002 Exponent=0.04931 [E3DProcessParameters/Material/RheologicalData/TBTS] standardtemperature=125.0 referencetemperature=285.0 [E3DProcessParameters/Material/ThermoData] heatconductivity=0.22 heatconductivityslope=0.0 heatcapacity=1.93 heatcapacityslope=0.0 densitymodel=DENSITY [E3DProcessParameters/Material/ThermoData/Density] Density=1.18 DensitySlope=0.0 [E3DSimulationsettings] MeshQuality=medium HexMesher=TwinScrew KTPRelease=NO
A user may now send a message in which he defines one or more key value pairs. Your task is to find and replace the values in the template by the value(s) given in user's message. Your reply always includes the full, updated INI file. A user may enter keys in the German language if so try to find the matching key and replace its value.
A user may also ask questions about the key-values in the INI file. If you identify a users message as a question about the meaning of a key-value pair in the INI file, try to explain it based on the following info : {EXPLANATION_STRING}.
I have put the information in angled brackets after the key-value pairs. If you find no angled backets after the key-value pairs try to explain based on your world knowledge.
"""


PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def process_query(query, history):
    #model = ChatOpenAI(model="gpt-4")
    model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
    
    messages = [
            SystemMessage(content=BEHAVIOR_STRING),
            HumanMessage(content=query),
    ]
    
    response = model.invoke(messages)
    print(response)
    return response.content

with gr.Blocks() as iface:
    chatbot = gr.ChatInterface(
        fn=process_query,
        title="Simulation Creation Assistant",
        description="A helpful assistant for creating INI files",
        chatbot=gr.Chatbot(height=600),
        retry_btn=None,
        undo_btn=None,
        clear_btn=None,
    )
    iface.launch()