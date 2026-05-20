from typing import Final

class UnitConversion:
    LBM_TO_KG: Final[float]             = 0.45359237
    FT_TO_M: Final[float]               = 0.3048
    DAY_TO_SEC: Final[float]            = 24.0 * 60.0 * 60.0
    LBMOL_TO_MOL: Final[float]          = 453.59237

    CP_TO_PA_SEC: Final[float]          = 0.001
    PSI_TO_PA: Final[float]             = 6894.757293168
    LBF_TO_N: Final[float]              = 4.4482216152605

    MD_TO_FT2: Final[float]             = 1.062314e-14
    MD_TO_M2: Final[float]              = 9.869233e-16
    ACRE_TO_FT2: Final[float]           = 43560
    ACRE_TO_M2: Final[float]            = 4046.8564224
    BBL_TO_FT3: Final[float]            = 5.614583333
    BBL_TO_M3: Final[float]             = 0.158987294928

    @staticmethod
    def f_to_c(value: float) -> float:
        """Convert Fahrenheit to Celsius."""
        return (value - 32.0) * 5.0 / 9.0

    @staticmethod
    def r_to_k(value: float) -> float:
        """Convert Rankine to Kelvin."""
        return value * 5.0 / 9.0
    
    @staticmethod
    def c_to_f(value: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return value * 9.0 / 5.0 + 32.0

    @staticmethod
    def k_to_r(value: float) -> float:
        """Convert Kelvin to Rankine."""
        return value * 9.0 / 5.0
    
    @staticmethod
    def c_to_k(value: float) -> float:
        """Convert Celsius to Kelvin."""
        return value + 273.15

    @staticmethod
    def k_to_c(value: float) -> float:
        """Convert Kelvin to Celsius."""
        return value - 273.15

    @staticmethod
    def f_to_r(value: float) -> float:
        """Convert Fahrenheit to Rankine."""
        return value + 459.67

    @staticmethod
    def r_to_f(value: float) -> float:
        """Convert Rankine to Fahrenheit."""
        return value - 459.67