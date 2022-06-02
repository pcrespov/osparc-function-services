from typing import Any

from ._utils import define_service


def JsonSchema(schema: dict[str, Any]) -> Any:
    pass


@define_service(
    version="0.2.0",
    # CHANGELOG
    # - 0.2.0: reverted order of first 5 outputs
    name="Demo Units",
    description="This service is for demo purposes.It takes base units as inputs and transform them in the outputs.",
    # authors =[PC, OM],
    # contact =PC.email,
    # thumbnail =create_fake_thumbnail_url("demo-units"),
    outputs={
        "mass": JsonSchema(
            {
                "title": "Mass",
                "minimum": 0,
                "x_unit": "kilo-gram",
                "type": "number",
            }
        ),
        "luminosity": JsonSchema(
            {
                "title": "Luminosity",
                "x_unit": "candela",
                "type": "number",
            }
        ),
        "current": JsonSchema(
            {
                "title": "Current",
                "x_unit": "milli-ampere",
                "type": "number",
            }
        ),
        "time": JsonSchema(
            {
                "title": "Time",
                "minimum": 0,
                "x_unit": "minute",
                "type": "number",
            }
        ),
        "length": JsonSchema(
            {
                "title": "Distance",
                "description": "Distance value converted",
                "x_unit": "milli-meter",
                "type": "number",
            }
        ),
        "substance": JsonSchema(
            {
                "title": "Substance",
                "minimum": 0,
                "x_unit": "mole",
                "type": "number",
            }
        ),
        "temperature": JsonSchema(
            {
                "title": "Temperature",
                "minimum": 0,
                "x_unit": "degree_Celsius",
                "type": "number",
            }
        ),
        "angle": JsonSchema(
            {
                "title": "Angle",
                "x_unit": "radian",
                "type": "number",
            }
        ),
        "velocity": JsonSchema(
            {
                "title": "Velo-city",
                "x_unit": "kilometer_per_hour",
                "type": "number",
            }
        ),
        "radiation": JsonSchema(
            {
                "title": "Radiation",
                "x_unit": "curie",
                "type": "number",
            }
        ),
    },
)
def main(
    length: float = JsonSchema(
        {
            "title": "Distance",
            "minimum": 0,
            "maximum": 10,
            "x_unit": "meter",
            "type": "number",
        }
    ),
    time: float = JsonSchema(
        {
            "title": "Time",
            "description": "Positive time",
            "minimum": 0,
            "x_unit": "micro-second",
            "type": "number",
        }
    ),
    current: float = JsonSchema(
        {
            "title": "Current",
            "x_unit": "ampere",
            "type": "number",
        }
    ),
    luminosity: float = JsonSchema(
        {
            "title": "Luminosity",
            "x_unit": "candela",
            "type": "number",
        }
    ),
    mass: float = JsonSchema(
        {
            "title": "Mass",
            "description": "Positive mass",
            "minimum": 0,
            "x_unit": "micro-gram",
            "type": "number",
        }
    ),
    substance: float = JsonSchema(
        {
            "title": "Substance",
            "minimum": 0,
            "x_unit": "milli-mole",
            "type": "number",
        }
    ),
    temperature: float = JsonSchema(
        {
            "title": "Temperature",
            "minimum": 0,
            "x_unit": "kelvin",
            "type": "number",
        }
    ),
    angle: float = JsonSchema(
        {
            "title": "Angle",
            "x_unit": "degree",
            "type": "number",
        }
    ),
    velocity: float = JsonSchema(
        {
            "title": "Velo-city",
            "x_unit": "meter_per_second",
            "type": "number",
        }
    ),
    entropy: float = JsonSchema(
        {
            "title": "Entropy",
            "x_unit": "m**2 kg/s**2/K",
            "type": "number",
        }
    ),
    radiation: float = JsonSchema(
        {
            "title": "Radiation",
            "x_unit": "rutherford",
            "type": "number",
        }
    ),
):
    # SEE https://github.com/hgrecco/pint/blob/master/pint/default_en.txt

    raise NotImplemented()


from pydantic import confloat, Field


def compute_speed(
    length: float = Field(x_unit="mm"), time: confloat(ge=0) = Field(x_unit="m")
):
    return length / time
