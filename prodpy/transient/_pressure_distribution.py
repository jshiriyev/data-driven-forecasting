import numpy as np

class PressureDistribution:
    """
    Store analytical pressure solutions over one or more times and nodes.

    Public properties use oilfield units:
    times : days
    nodes : feet
    press : psi

    Internal underscored arrays use SI units:
    _times : seconds, shaped (n_times, 1)
    _nodes : meters, shaped (1, n_nodes)
    _press : pascals, shaped (n_times, n_nodes)

    The coordinate axes and backing pressure matrix are fixed after
    construction. Pressure values may be populated through :meth:`set_pressure`
    or row-by-row through :meth:`set_pressure_at_time`.

    """
    PSI_TO_PA = 6894.757293168
    DAY_TO_SEC = 24 * 60 * 60
    FT_TO_METER = 0.3048

    _IMMUTABLE_FIELDS = frozenset({"_times", "_nodes", "_press"})

    def __init__(self, times: np.ndarray, nodes: np.ndarray) -> None:
        self._times = self._set_times(times) * self.DAY_TO_SEC
        self._nodes = self._set_nodes(nodes) * self.FT_TO_METER
        self._press = np.empty((self._times.size, self._nodes.size), dtype=float)

        self._times.flags.writeable = False
        self._nodes.flags.writeable = False
        self._press.flags.writeable = False

    def __repr__(self):
        """Return a concise representation using public units."""
        return (
            f"{type(self).__name__}("
            f"times={self._repr_array(self.times.ravel())} days, "
            f"nodes={self._repr_array(self.nodes.ravel())} ft, "
            f"press_shape={self._press.shape})"
        )

    def __setattr__(self, name, value):
        """Prevent replacement of the internal storage arrays after construction."""
        if name in self._IMMUTABLE_FIELDS and hasattr(self, name):
            raise AttributeError(f"{name} is immutable after construction.")
        super().__setattr__(name, value)

    @staticmethod
    def _set_times(times: np.typing.ArrayLike):
        return PressureDistribution._as_vector(
            times, name="times"
            ).reshape((-1, 1))
    
    @staticmethod
    def _set_nodes(nodes: np.typing.ArrayLike):
        return PressureDistribution._as_vector(
            nodes, name="nodes"
            ).reshape((1, -1))

    @staticmethod
    def _as_vector(values: np.ndarray, *, name: str) -> np.ndarray:
        """Normalize a non-scalar array-like input to a one-dimensional float array."""
        arr = np.asarray(values, dtype=float)

        if arr.ndim == 0:
            raise TypeError(f"{name} must be array-like, not scalar.")

        arr = arr.ravel()

        if arr.size == 0:
            raise ValueError(f"{name} cannot be empty.")

        return arr

    @staticmethod
    def _repr_array(values: np.ndarray) -> str:
        """Format scalar and array values compactly for ``__repr__``."""
        arr = np.asarray(values)

        if arr.size == 1:
            return repr(float(arr.ravel()[0]))

        return (
            "np.array("
            + np.array2string(
                arr,
                precision=6,
                separator=", ",
                threshold=8,
                edgeitems=2,
            )
            + ")"
        )

    @property
    def times(self):
        """Time values in days."""
        return self._times / self.DAY_TO_SEC

    @property
    def nodes(self):
        """Node positions in feet."""
        return self._nodes / self.FT_TO_METER

    @property
    def press(self):
        """Pressure values in psi."""
        return self._press / self.PSI_TO_PA

    def set_pressure_at_time(
        self,
        time: float,
        values: np.ndarray,
        si_unit_flag: bool = False,
    ) -> None:
        """
        Set one pressure row for the requested public-unit time.

        Parameters
        ----------
        time : float
            Time in days. Must match exactly one stored time within floating-point
            tolerance.
        values : np.ndarray
            Pressure values for all nodes. Values are interpreted as psi by
            default and as pascals when ``si_unit_flag=True``.
        si_unit_flag : bool, optional
            Whether ``values`` are already in SI pressure units (Pa).
        """
        try:
            time = float(time)
        except (TypeError, ValueError) as exc:
            raise TypeError("time must be convertible to float.") from exc

        if not np.isfinite(time):
            raise ValueError("time must be a finite value.")

        matches = np.flatnonzero(np.isclose(self.times.ravel(), time))

        if matches.size == 0:
            raise ValueError(f"time {time} days is not present in this PressureDistribution.")

        if matches.size > 1:
            raise ValueError(
                f"time {time} days matches multiple stored times; times must be unique."
            )

        values = self._as_vector(values, name="values")

        if values.size != self._nodes.size:
            raise ValueError(
                f"values must contain one pressure per node; expected {self._nodes.size}, "
                f"got {values.size}."
            )

        if not si_unit_flag:
            values = values * self.PSI_TO_PA

        self._press.flags.writeable = True
        try:
            self._press[matches.item(), :] = values
        finally:
            self._press.flags.writeable = False
    
    def set_pressure(self, values: np.ndarray, si_unit_flag: bool = False):
        """
        Set the full pressure matrix without replacing the backing array.

        Parameters
        ----------
        values : np.ndarray
            Two-dimensional pressure array shaped ``(n_times, n_nodes)``.
            Values are interpreted as psi by default and as pascals when
            ``si_unit_flag=True``.
        si_unit_flag : bool, optional
            Whether ``values`` are already in SI pressure units (Pa).
        """
        values = np.asarray(values, dtype=float)

        if values.ndim != 2:
            raise ValueError("values must be a two-dimensional pressure array.")

        if values.shape != self._press.shape:
            raise ValueError(
                f"values shape must match pressure shape {self._press.shape}; "
                f"got {values.shape}."
            )

        if not si_unit_flag:
            values = values * self.PSI_TO_PA

        self._press.flags.writeable = True
        try:
            self._press[:, :] = values
        finally:
            self._press.flags.writeable = False

    def _plot_time_indices(self, max_lines: int = 10) -> np.ndarray:
        """Return time-row indices to plot, always including first and last."""
        time_count = self._times.size

        if time_count <= max_lines:
            return np.arange(time_count)

        indices = np.round(np.linspace(0, time_count - 1, max_lines)).astype(int)
        indices[0] = 0
        indices[-1] = time_count - 1

        return np.unique(indices)

    def plot(self, ax=None, max_lines: int = 10, **kwargs):
        """
        Plot pressure distribution versus node position for selected times.

        If more than ``max_lines`` time values are available, uniformly selected
        time rows are plotted while always including the first and last times.
        Axis values and labels use public oilfield units: feet, days, and psi.

        Parameters
        ----------
        ax : matplotlib.axes.Axes, optional
            Existing axes to draw on. If omitted, a new figure and axes are
            created.
        max_lines : int, optional
            Maximum number of time lines to plot.
        **kwargs
            Additional keyword arguments passed to ``Axes.plot``.

        Returns
        -------
        matplotlib.axes.Axes
            The axes containing the pressure-distribution plot.
        """
        if max_lines < 2:
            raise ValueError("max_lines must be at least 2.")

        if ax is None:
            import matplotlib.pyplot as plt

            _, ax = plt.subplots()

        indices = self._plot_time_indices(max_lines=max_lines)
        nodes = self.nodes.ravel()
        times = self.times.ravel()
        press = self.press

        for index in indices:
            time = times[index]
            label = f"t = {time:g} day" if np.isclose(time, 1.0) else f"t = {time:g} days"
            ax.plot(nodes, press[index, :], label=label, **kwargs)

        ax.set_xlabel("Node position, ft")
        ax.set_ylabel("Pressure, psi")
        ax.legend()

        return ax
