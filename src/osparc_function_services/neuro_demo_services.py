
from doctest import OutputChecker
import random
from numbers import Complex
from typing import Tuple
from enum import Enum

from scipy import rand

from pydantic import confloat, conint

# Units validated against https://github.com/hgrecco/pint/blob/master/pint/default_en.txt


######## This is a set of services intended for a "contextual" example of unit conversions ######
# Concept:
#   Heart function is affected by the autonomous nervous system via the parasympathetic (e.g. vagus)
#   and sympathetic systems. We can stimulate the vagus nerve with electrical stimulation of a 
#   particular amplitude and pulse width. 


# Instructions:
#   The pipeline is meant to be set up as follows:
#   1. 2 float parameters for stimulation amplitude (mA) and pulse width inputs to stimulate autonomic_model
#   2. 1 array float parameter for location of the center of electrode: dimension 1x3 (x,y,z coord)
#   3. autonomic_model gets inputs from parameters 1 and 2. Outputs acetylcholine, epinephrine and norepinephrine 
#       are connected to the inputs of sinoatrial_node. Output contractility is connected to cardiac_model.
#   4. sinoatrial_node gets inputs acetylcholine, epinephrine and norepinephrine  from autonomic_model. The Output 
#       heart rate is connected to the cardiac_model.
#   5. cardiac_model receives one input from sinoatrial_node (heart rate) and one input from autonomic model 
#       (contractility). It provides stroke volume and blood pressure as outputs, which can optionally be connected
#       to the pressure_monitor. 
#   6. pressure_monitor is an optional service that receives one input (blood pressure) from cardiac_model. 
#       It will fail dynamic validation.
#   
# Pipeline: 
#   electrode_loc_param --|
#   stim_amp_param --------> autonomic_model -------------------------> cardiac_model --?--> pressure_monitor
#   pulse_width_param-----|                  |---> sinoatrial_node---|
#
#
# Note:
#   Inputs and outputs are intentionally marked with different units (e.g. mM vs uM) to demonstrate conversions
#


class Exercise(str, Enum):
    REST = "Resting"
    LOW = "Low Activity"
    MEDIUM = "Moderate Exercise"
    HIGH = "Intense Exercise"


# @services.add(return_outputs=["acetylcholine [mM]", "epinephrine [mM]", "norepinephrine [mM], "stroke_volume [mL]", "mean_arterial_pressure [kPa]"])
def autonomic_model(
    *,
    stimulation_amp: confloat(ge=-1, le=1),                 # mA
    pulse_width: confloat(ge=0, multiple_of=0.1, le=50),    # ms 
    stim_location: list[confloat()],                        # list with units mm, of length==3 (x,y,z coordinate)
    exercise_level: Exercise = Exercise.REST.value          # string
) -> Tuple[float, float, float, float, float]:

    options = {
        Exercise.REST: 0.0,
        Exercise.LOW: 0.25,
        Exercise.MEDIUM: 0.5,
        Exercise.HIGH: 0.75
        }
    acetylcholine = abs(stimulation_amp)            # mM (molar is a unit of concentration)
    stroke_volume = random.randrange(40, 130)       # mL
    mean_arterial_pressure = random.randrange(12, 20) # kPa 
    epinephrine = options[exercise_level]           # mM 
    norepinephrine = options[exercise_level] +.25   # mM

    return acetylcholine, epinephrine, norepinephrine, stroke_volume, mean_arterial_pressure


# @services.add(return_outputs=["heart_rate [bpm or Hz]"])
def sinoatrial_node(
    *,
    acetylcholine: confloat(ge=0),  # uM (molar M is a unit of concentration)
    epinephrine: confloat(ge=0),    # uM 
    norepinephrine: confloat(ge=0)  # uM
) -> int:

    heart_rate = random.randint(0.5, 10)  # Hz

    return heart_rate 

# @services.add(return_outputs=["cardiac_output [L/min]", "blood_pressure [mmHg, mmHg]"])
def cardiac_model(
    *,
    heart_rate: conint(ge=40, le=200),                  # rpm (would prefer bpm but not in pint)
    stroke_volume: confloat(ge=0.004, le=0.130),        # L
    mean_arterial_pressure: confloat(ge=90, le= 151)    # mmHg
)-> Tuple[float, list]:

    factor = random.random()
    cardiac_output = factor*(20 - 4) + 4        # set output 4-20 L/min
    sys_blood_pressure = factor*(140-100) + 100 # set systolic blood pressure 100-140 mmHg
    dia_blood_pressure = factor*(90-70) + 70    # set diastolic blood pressure 70-90 mmHg
    pressure = [dia_blood_pressure, sys_blood_pressure]

    return(cardiac_output , pressure)


## this is an optional service that will fail during runtime when connected to the output of cardiac_model
# @services.add(return_outputs=["flag"])
def pressure_monitor(
    *,
    pressures: list[confloat(le=90)]    # array with unit Pa (also pressure)
)-> bool:

    return True

