import math

from typing import Iterable

from ._constraint import Constraint


class Boundary:
    """
    Boundary/fault object with face metadata and scheduled constraints.

    ``Boundary`` is the boundary-side analogue of :class:`Borehole`: it stores
    location/orientation information for a reservoir face and owns one or more
    time-windowed :class:`Constraint` objects. Constraint intervals are treated
    as half-open intervals:

        start <= t < stop

    Therefore, adjacent constraints are allowed, but overlapping constraints
    are rejected.

    Parameters
    ----------
    face : str
        Reservoir boundary face. Accepted values are ``"xmin"``, ``"xmax"``,
        ``"ymin"``, ``"ymax"``, ``"zmin"``, and ``"zmax"``.
    constraints : iterable of Constraint, optional
        Initial iterable of non-overlapping boundary constraints.
    **kwargs
        Convenience keyword arguments used to create an initial ``Constraint``.
        For example:

            Boundary("xmin", start=0, stop=30, press=3000)

    Notes
    -----
    A boundary can be created without constraints. This is useful for inactive
    or no-flow faces where no explicit pressure/rate condition is scheduled.
    """

    FACE_TO_ID = {
        "xmin": 0,
        "xmax": 1,
        "ymin": 2,
        "ymax": 3,
        "zmin": 4,
        "zmax": 5,
    }
    ID_TO_FACE = {value: key for key, value in FACE_TO_ID.items()}

    FACE_TO_AXIS = {
        "xmin": "x",
        "xmax": "x",
        "ymin": "y",
        "ymax": "y",
        "zmin": "z",
        "zmax": "z",
    }
    FACE_TO_SIDE = {
        "xmin": "min",
        "xmax": "max",
        "ymin": "min",
        "ymax": "max",
        "zmin": "min",
        "zmax": "max",
    }
    FACE_TO_NORMAL = {
        "xmin": (-1, 0, 0),
        "xmax": (1, 0, 0),
        "ymin": (0, -1, 0),
        "ymax": (0, 1, 0),
        "zmin": (0, 0, -1),
        "zmax": (0, 0, 1),
    }

    def __init__(
        self,
        face: str,
        *,
        constraints: Iterable[Constraint] | None = None,
        **kwargs,
    ):
        self._face = None
        self._constraints: list[Constraint] = []

        self.face = face

        if constraints is not None:
            for constraint in constraints:
                self.add_constraint(constraint)

        if kwargs:
            self.add_constraint(**kwargs)

    @property
    def face(self) -> str:
        """Boundary face name."""
        return self.ID_TO_FACE[self._face]

    @face.setter
    def face(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("face must be a string.")

        value = value.lower()

        if value not in self.FACE_TO_ID:
            raise ValueError(
                f"face must be one of {list(self.FACE_TO_ID.keys())}; got {value!r}."
            )

        self._face = self.FACE_TO_ID[value]

    @property
    def axis(self) -> str:
        """Coordinate axis normal to the boundary face."""
        return self.FACE_TO_AXIS[self.face]

    @property
    def axis_id(self) -> int:
        """Integer axis id: x -> 0, y -> 1, z -> 2."""
        return {"x": 0, "y": 1, "z": 2}[self.axis]

    @property
    def side(self) -> str:
        """Boundary side along its axis: ``"min"`` or ``"max"``."""
        return self.FACE_TO_SIDE[self.face]

    @property
    def normal(self) -> tuple[int, int, int]:
        """Outward unit-normal direction in grid-index convention."""
        return self.FACE_TO_NORMAL[self.face]

    @property
    def normal_direction(self) -> int:
        """Signed direction along ``axis``: -1 for min faces and +1 for max faces."""
        return -1 if self.side == "min" else 1

    @property
    def constraints(self) -> tuple[Constraint, ...]:
        """
        Constraints sorted by start time.

        A tuple is returned to prevent accidental list-level modification.
        """
        return tuple(self._constraints)

    @property
    def constraint(self) -> Constraint:
        """
        Return the sole constraint.

        This convenience property keeps simple single-condition usage readable.
        For scheduled boundaries, use ``constraints`` or ``active_constraint``.
        """
        if len(self._constraints) != 1:
            raise ValueError(
                "Boundary has "
                f"{len(self._constraints)} constraints; expected exactly one."
            )

        return self._constraints[0]

    # ------------------------------------------------------------------
    # Single-constraint convenience proxies
    # ------------------------------------------------------------------
    @property
    def start(self) -> float:
        """Start time of the sole boundary constraint, days."""
        return self.constraint.start

    @property
    def stop(self) -> float | None:
        """Stop time of the sole boundary constraint, days."""
        return self.constraint.stop

    @property
    def mode(self) -> str:
        """Control mode of the sole boundary constraint."""
        return self.constraint.mode

    @property
    def limit(self) -> float:
        """Limit value of the sole boundary constraint in oilfield units."""
        return self.constraint.limit

    @property
    def prod(self):
        """Boundary transmissibility/productivity of the sole constraint."""
        return self.constraint.prod

    @prod.setter
    def prod(self, value):
        self.constraint.prod = value

    def set_limit(self, **kwargs) -> None:
        """
        Set or replace the limit on a single-constraint boundary.

        If the boundary has no constraints, a new one is created. If it has one,
        that constraint's limit is replaced. Multi-constraint schedules should
        be edited through the individual ``Constraint`` objects.
        """
        if not self._constraints:
            self.add_constraint(**kwargs)
            return

        self.constraint.set_limit(**kwargs)

    def is_active(self, time_days: float) -> bool:
        """Check whether the sole boundary constraint is active."""
        return self.constraint.is_active(time_days)

    # ------------------------------------------------------------------
    # Constraint management
    # ------------------------------------------------------------------
    def add_constraint(self, constraint: Constraint | None = None, **kwargs) -> Constraint:
        """
        Add a new boundary constraint.

        Parameters
        ----------
        constraint : Constraint, optional
            Existing Constraint object.
        **kwargs
            Keyword arguments used to create a Constraint if ``constraint`` is
            not provided. For example:

                add_constraint(start=0, stop=30, press=3000)

        Returns
        -------
        Constraint
            The added Constraint object.
        """
        if constraint is None:
            constraint = Constraint(**kwargs)
        elif kwargs:
            raise ValueError(
                "Provide either an existing Constraint object or keyword "
                "arguments to create one, not both."
            )

        self._check_constraint_type(constraint)
        self._check_no_overlap(constraint)

        self._constraints.append(constraint)
        self._constraints.sort(key=lambda item: item.start)

        return constraint

    def remove_constraint(self, constraint: Constraint) -> None:
        """Remove a constraint from the boundary."""
        self._constraints.remove(constraint)

    def clear_constraints(self) -> None:
        """Remove all constraints from the boundary."""
        self._constraints.clear()

    def active_constraint(self, time_days: float) -> Constraint | None:
        """
        Return the active boundary constraint at a given time.

        Parameters
        ----------
        time_days : float
            Time in days.
        """
        try:
            time_days = float(time_days)
        except Exception as exc:
            raise ValueError(f"time_days must be convertible to float; got {time_days!r}.") from exc

        active = [constraint for constraint in self._constraints if constraint.is_active(time_days)]

        if len(active) > 1:
            raise RuntimeError(
                "More than one active constraint was found. "
                "The boundary schedule is internally inconsistent."
            )

        return active[0] if active else None

    def validate_schedule(self) -> bool:
        """
        Validate that all stored constraints are non-overlapping.

        Returns
        -------
        bool
            True if the schedule is valid.
        """
        sorted_constraints = sorted(self._constraints, key=lambda item: item.start)

        for previous, current in zip(sorted_constraints[:-1], sorted_constraints[1:]):
            if self._constraints_overlap(previous, current):
                raise ValueError(
                    "Overlapping constraints detected:\n"
                    f"  Existing: {self._format_constraint(previous)}\n"
                    f"  Current : {self._format_constraint(current)}"
                )

        return True

    # ------------------------------------------------------------------
    # Schedule helpers
    # ------------------------------------------------------------------
    def schedule(self):
        """
        Return the boundary constraint schedule.

        Returns
        -------
        pandas.DataFrame or list[dict]
            If pandas is available, returns a DataFrame. Otherwise, returns a
            list of dictionaries.
        """
        rows = []

        for i, constraint in enumerate(self._constraints):
            rows.append(
                {
                    "index": i,
                    "face": self.face,
                    "axis": self.axis,
                    "side": self.side,
                    "start_days": constraint.start,
                    "stop_days": constraint.stop,
                    "mode": constraint.mode,
                    "limit": constraint.limit,
                    "unit": self._unit_for_mode(constraint.mode),
                }
            )

        try:
            import pandas as pd

            return pd.DataFrame(rows)
        except ImportError:
            return rows

    def change_times(self) -> list[float]:
        """
        Return all finite start and stop times where the schedule changes.
        """
        times = []

        for constraint in self._constraints:
            times.append(constraint.start)
            if constraint.stop is not None:
                times.append(constraint.stop)

        return sorted(set(times))

    # ------------------------------------------------------------------
    # Plotting methods
    # ------------------------------------------------------------------
    def plot_schedule(self, ax=None, max_time: float | None = None, show_labels: bool = True):
        """
        Plot boundary constraint intervals as a Gantt-style schedule.
        """
        if not self._constraints:
            raise ValueError("No constraints available to plot.")

        import matplotlib.pyplot as plt

        if ax is None:
            height = max(2.5, 0.55 * len(self._constraints) + 1.5)
            fig, ax = plt.subplots(figsize=(9, height))
        else:
            fig = ax.figure

        x_max = self._plot_horizon(max_time=max_time)

        for i, constraint in enumerate(self._constraints):
            start = constraint.start
            stop = x_max if constraint.stop is None else constraint.stop
            width = stop - start

            if width <= 0:
                continue

            ax.broken_barh([(start, width)], (i - 0.35, 0.7))

            if show_labels:
                label = (
                    f"{constraint.mode} = {constraint.limit:g} "
                    f"{self._unit_for_mode(constraint.mode)}"
                )
                ax.text(start + 0.01 * max(x_max, 1.0), i, label, va="center")

        ax.set_xlabel("Time, days")
        ax.set_ylabel("Constraint")
        ax.set_yticks(range(len(self._constraints)))
        ax.set_yticklabels([f"{i}: {c.mode}" for i, c in enumerate(self._constraints)])
        ax.set_xlim(left=0, right=x_max)
        ax.grid(True, axis="x", alpha=0.3)
        ax.set_title(f"Boundary constraint schedule: {self.face}")

        return fig, ax

    def plot_limits(self, mode: str | None = None, ax=None, max_time: float | None = None):
        """
        Plot boundary constraint limit versus time for one constraint mode.
        """
        if not self._constraints:
            raise ValueError("No constraints available to plot.")

        modes = {constraint.mode for constraint in self._constraints}

        if mode is None:
            if len(modes) != 1:
                raise ValueError(
                    f"Multiple constraint modes exist: {sorted(modes)}. "
                    "Pass mode='press', 'orate', etc. to plot one mode."
                )
            mode = next(iter(modes))

        if mode not in Constraint.VALID_MODES:
            raise ValueError(f"Invalid mode: {mode!r}. Must be one of {Constraint.VALID_MODES}.")

        selected = [constraint for constraint in self._constraints if constraint.mode == mode]

        if not selected:
            raise ValueError(f"No constraints found for mode={mode!r}.")

        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots(figsize=(9, 4))
        else:
            fig = ax.figure

        x_max = self._plot_horizon(max_time=max_time)

        for constraint in selected:
            start = constraint.start
            stop = x_max if constraint.stop is None else constraint.stop

            ax.hlines(
                y=constraint.limit,
                xmin=start,
                xmax=stop,
                linewidth=2,
            )

            ax.plot([start, stop], [constraint.limit, constraint.limit], marker="o")

        ax.set_xlabel("Time, days")
        ax.set_ylabel(f"{mode} limit, {self._unit_for_mode(mode)}")
        ax.set_xlim(left=0, right=x_max)
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{mode} boundary limits: {self.face}")

        return fig, ax

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _check_constraint_type(constraint: Constraint) -> None:
        if not isinstance(constraint, Constraint):
            raise TypeError(
                "constraint must be a Constraint object. "
                f"Got {type(constraint).__name__}."
            )

    def _check_no_overlap(self, new_constraint: Constraint) -> None:
        for existing in self._constraints:
            if self._constraints_overlap(existing, new_constraint):
                raise ValueError(
                    "New constraint overlaps with an existing constraint:\n"
                    f"  Existing: {self._format_constraint(existing)}\n"
                    f"  New     : {self._format_constraint(new_constraint)}"
                )

    @staticmethod
    def _constraints_overlap(first: Constraint, second: Constraint) -> bool:
        """
        Check whether two half-open intervals overlap.
        """
        first_start = first.start
        first_stop = math.inf if first.stop is None else first.stop

        second_start = second.start
        second_stop = math.inf if second.stop is None else second.stop

        return first_start < second_stop and second_start < first_stop

    @staticmethod
    def _format_constraint(constraint: Constraint) -> str:
        stop = "None" if constraint.stop is None else f"{constraint.stop:g}"

        return (
            f"[{constraint.start:g}, {stop}) "
            f"{constraint.mode}={constraint.limit:g}"
        )

    @staticmethod
    def _unit_for_mode(mode: str) -> str:
        units = {
            "press": "psi",
            "lrate": "bbl/day",
            "orate": "bbl/day",
            "wrate": "bbl/day",
            "grate": "ft3/day",
        }
        return units.get(mode, "")

    def _plot_horizon(self, max_time: float | None = None) -> float:
        if max_time is not None:
            try:
                max_time = float(max_time)
            except Exception as exc:
                raise ValueError(f"max_time must be convertible to float; got {max_time!r}.") from exc

            if max_time <= 0:
                raise ValueError("max_time must be positive.")

            return max_time

        finite_stops = [
            constraint.stop for constraint in self._constraints if constraint.stop is not None
        ]
        max_start = max(constraint.start for constraint in self._constraints)

        if finite_stops:
            x_max = max(max(finite_stops), max_start)
        else:
            x_max = max_start

        if any(constraint.stop is None for constraint in self._constraints):
            x_max = max(x_max, max_start + max(1.0, 0.10 * max(max_start, 1.0)))

        return max(1.0, 1.05 * x_max)

    def __repr__(self) -> str:
        return (
            f"Boundary(face={self.face!r}, "
            f"axis={self.axis!r}, "
            f"side={self.side!r}, "
            f"constraints={len(self._constraints)})"
        )


if __name__ == "__main__":
    bcond = Boundary("xmin", press=500)

    print(bcond.limit)
    print(bcond.face)
    print(bcond.axis)
    print(bcond.mode)
