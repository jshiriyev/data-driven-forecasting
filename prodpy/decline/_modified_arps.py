import numpy as np


class ModifiedArps:
    """
    Modified Arps decline model that transitions from hyperbolic to exponential at a specified minimum decline rate.
    """

    def __init__(self, b, di, qi, d_min):
        """
        Initialize the Modified Arps model.

        Parameters
        ----------
        b : float
            Hyperbolic exponent.
        di : float
            Initial nominal decline rate.
        qi : float
            Initial production rate.
        d_min : float
            Minimum nominal decline rate where model switches to exponential.
        """
        if qi <= 0 or di <= 0 or d_min <= 0:
            raise ValueError("qi, di, and d_min must be positive.")
        if b < 0:
            raise ValueError("b must be non-negative.")

        self.b = b
        self.di = di
        self.qi = qi
        self.d_min = d_min

    def q(self, t):
        """
        Calculate production rate using the Modified Arps model.

        Parameters
        ----------
        t : float or array-like
            Time values.

        Returns
        -------
        q : float or ndarray
            Production rate at time t.
        """
        t = np.asarray(t, dtype=float)

        # Pure exponential case when b = 0
        if self.b == 0:
            return self.qi * np.exp(-self.di * t)

        # Time at which hyperbolic decline reaches d_min
        t_switch = (self.di / self.d_min - 1.0) / (self.b * self.di)

        # Rate at switch time
        q_switch = self.qi / (1.0 + self.b * self.di * t_switch) ** (1.0 / self.b)

        # Allocate output
        q = np.empty_like(t, dtype=float)

        # Hyperbolic part
        mask_hyp = t <= t_switch
        q[mask_hyp] = self.qi / (1.0 + self.b * self.di * t[mask_hyp]) ** (1.0 / self.b)

        # Exponential tail
        mask_exp = t > t_switch
        q[mask_exp] = q_switch * np.exp(-self.d_min * (t[mask_exp] - t_switch))

        return q

    def N_ec(self, qf):
        """
        Calculate EUR for Modified Arps given final rate qf.

        Parameters
        ----------
        qf : float
            Final/economic limit rate

        Returns
        -------
        eur : float
            Estimated ultimate recovery
        """
        if qf <= 0:
            raise ValueError("qf must be positive.")

        # pure exponential special case
        if self.b == 0:
            return (self.qi - qf) / self.di

        # switch time and switch rate
        t_sw = (self.di / self.d_min - 1.0) / (self.b * self.di)
        q_sw = self.qi / (1.0 + self.b * self.di * t_sw) ** (1.0 / self.b)

        # case 1: qf reached before switch
        if qf >= q_sw:
            if np.isclose(self.b, 1.0):
                eur = (self.qi / self.di) * np.log(self.qi / qf)
            else:
                eur = (self.qi / (self.di * (1.0 - self.b))) * (
                    1.0 - (qf / self.qi) ** (1.0 - self.b)
                )
            return eur

        # case 2: qf reached after switch
        if np.isclose(self.b, 1.0):
            np_hyp = (self.qi / self.di) * np.log(self.qi / q_sw)
        else:
            np_hyp = (self.qi / (self.di * (1.0 - self.b))) * (
                1.0 - (q_sw / self.qi) ** (1.0 - self.b)
            )

        np_exp = (q_sw - qf) / self.d_min

        return np_hyp + np_exp
