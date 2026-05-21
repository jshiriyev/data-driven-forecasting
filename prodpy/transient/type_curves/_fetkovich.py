import numpy as np

class Fetkovich:

    @staticmethod
    def qD2qDd(qD, reD):
        """
        Convert qD to Fetkovich decline dimensionless rate qDd.
        """
        return qD * (np.log(reD) - 0.5)
    
    @staticmethod
    def qDd2qD(qDd, reD):
        """
        Convert Fetkovich decline dimensionless rate qDd to qD.
        """
        return qDd / (np.log(reD) - 0.5)

    @staticmethod
    def tD2tDd(tD, reD):
        """
        Convert tD to Fetkovich decline dimensionless time tDd.
        """
        return tD / Fetkovich._time_scale(reD)
    
    @staticmethod
    def tDd2tD(tDd, reD):
        """
        Convert Fetkovich decline dimensionless time tDd to tD.
        """
        return tDd * Fetkovich._time_scale(reD)
    
    @staticmethod
    def _time_scale(reD):
        """
        Fetkovich time scaling factor.

        tDd = tD / scale

        where:

            scale = 0.5 * (reD**2 - 1) * [ln(reD) - 0.5]

        """
        reD = float(reD)

        if reD <= 1:
            raise ValueError("reD must be greater than 1.")

        return 0.5 * (reD**2 - 1.0) * (np.log(reD) - 0.5)