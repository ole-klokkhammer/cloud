#!/usr/bin/python3

from dataclasses import dataclass


@dataclass
class BatteryStatus:
    voltage: float
    percentage: int


@dataclass
class SensorData:
    humidity: float
    illuminance: int
    radon_1day_avg: int
    radon_longterm_avg: int
    temperature: float
    pressure: float
    co2: float
    voc: float 
    # Uncomment the following lines if extra fields are needed
    # extra1: float = None
    # extra2: float = None
