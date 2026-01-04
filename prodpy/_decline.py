from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal, TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from matplotlib.axes import Axes

# Use your internal modules (fallback friendly if importing locally)
try:
    from prodpy import Schedule
    from prodpy.decline import Arps, FitResult
except Exception:
    from ._schedule import Schedule
    from .decline._arps import Arps, FitResult

DeclineMode = Literal['exponential', 'hyperbolic', 'harmonic', 'exp', 'hyp', 'har']

@dataclass
class DCA:
    '''
    Decline Curve Analysis front-end that couples:
      - Schedule: robust time handling & elapsed days
      - Arps:     model selection + fitting (exp/hyp/har)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain a datetime column and a rate column.
    date_col : str, default "date"
        Name of the datetime-like column.
    rate_col : str, default "rate"
        Name of the production rate column (e.g., oil rate).
    '''

    df: pd.DataFrame
    date_col: str = 'date'
    rate_col: str = 'rate'

    # --- internal state after fit ---
    _sched: Optional[Schedule] = None
    _t_days: Optional[np.ndarray] = None
    _q_obs: Optional[np.ndarray] = None
    _fit: Optional[FitResult] = None
    _arps_hat: Optional[Arps] = None

    # ---------------- API ----------------
    def fit(
        self,
        model: DeclineMode = 'hyperbolic',
        *,
        b: Optional[float] = None,
        fit_start: Optional[pd.Timestamp | str] = None,
        fit_end: Optional[pd.Timestamp | str] = None,
        xi: float = 0.0,
    ) -> 'DCA':
        '''
        Fit an Arps decline model to the data.

        Parameters
        ----------
        model : {'exponential','hyperbolic','harmonic','exp','hyp','har'}
            Model family to use. (Hyperbolic can accept a fixed `b`.)
        b : float, optional
            Hyperbolic exponent (0<=b<=1). If None, uses Arps default mapping.
        fit_start, fit_end : optional
            Limit the fit window in calendar time (inclusive).
        xi : float, default 0.0
            Start time shift (in days) for model evaluation (e.g., to ignore early time).
        '''
        # 1) Build schedule & elapsed days
        s = Schedule(pd.to_datetime(self.df[self.date_col]))
        t_all = s.days_since_start()  # float days since first date (robust & vectorized)

        # 2) Select fit window (by calendar dates) if provided
        mask = np.ones(s.size, dtype=bool)
        if fit_start is not None or fit_end is not None:
            start = fit_start if fit_start is not None else s.mindate
            end = fit_end if fit_end is not None else s.maxdate
            mask = s.isbetween(start, end, inclusive='both')

        # 3) Pull observed rates, ensure numeric/finite
        q_all = pd.to_numeric(self.df[self.rate_col], errors='coerce').to_numpy()
        good = mask & np.isfinite(q_all) & (q_all > 0)

        t = t_all[good]
        q = q_all[good]

        if t.size < 3:
            raise ValueError('Not enough valid (t, q) points to fit (need >= 3).')

        # 4) Configure Arps orchestrator with chosen mode/b
        #    Arps maps mode<->b and instantiates correct model class under the hood.
        mode_name, b_eff = Arps.option(mode=model.lower(), b=b)
        arps = Arps(di=1.0, qi=float(np.nanmax(q)), b=b_eff, mode=mode_name)

        # 5) Fit (linearized init + non-linear curve_fit refinement, returns FitResult)
        self._fit = arps.fit(t, q, xi=xi)

        self._arps_hat = Arps(di=self._fit.di, qi=self._fit.qi, b=self._fit.b)

        # 6) Cache for plotting/forecasting
        self._sched, self._t_days, self._q_obs = s, t_all, q_all

        return self

    def run(
        self,
        *,
        periods: Optional[int] = None,
        horizon_days: Optional[int] = 365,
        econ_rate: Optional[float] = None,
    ) -> pd.DataFrame:
        '''
        Build a forecast DataFrame at the natural cadence of the input.

        Parameters
        ----------
        periods : int, optional
            Number of *additional* samples after last history. If None, infer from horizon_days.
        horizon_days : int, optional
            If periods is None, extend by this many days beyond last history (default 365).
        econ_rate : float, optional
            If provided, stop forecast once q(t) drops below this rate.

        Returns
        -------
        DataFrame with columns: ['date','t_days','q_hist','q_fit','q_forecast','N_forecast'].
        '''
        if self._sched is None or self._fit is None:
            raise RuntimeError('Call .fit(...) before forecasting.')

        s = self._sched
        t_all = self._t_days
        q_all = self._q_obs

        # Historical cadence (median dt in days)
        if t_all.size >= 2:
            dt = float(np.median(np.diff(t_all)))
            if not np.isfinite(dt) or dt <= 0:
                dt = 1.0
        else:
            dt = 1.0

        # Build future time grid
        t_last = float(t_all[-1]) if t_all.size else 0.0
        if periods is None:
            horizon = float(horizon_days or 365)
            periods = max(1, int(np.ceil(horizon / dt)))

        t_future = t_last + dt * np.arange(1, periods + 1, dtype=float)
        t_grid = np.concatenate([t_all, t_future])

        # Evaluate model on full grid (rate & cum) using Arps orchestrator
        q_fit_full = self._arps_hat.run(t_grid, xi=self._fit.xi, cum=False)
        N_full = self._arps_hat.run(t_grid, xi=self._fit.xi, cum=True)

        # Economic cutoff (optional)
        if econ_rate is not None and np.nanmin(q_fit_full) <= econ_rate:
            cut_idx = np.argmax(q_fit_full < econ_rate)
            if cut_idx > 0:
                q_fit_full[cut_idx:] = np.nan
                N_full[cut_idx:] = np.nan

        # Assemble DataFrame on calendar time using Schedule + original + extended dates
        # Extend calendar using last date and the same cadence
        last_date = s.series.iloc[-1]
        future_dates = last_date + pd.to_timedelta(np.round((t_future - t_last), 9), unit='D')
        date_full = pd.Index(s.series).append(pd.Index(future_dates))

        df = pd.DataFrame({
            'date': date_full.to_numpy(),
            't_days': t_grid,
            'q_hist': np.pad(q_all.astype(float), (0, t_future.size), constant_values=np.nan),
            'q_fit': q_fit_full,
        })
        # separate column for the model's forecasted segment only
        df['q_forecast'] = df['q_fit'].where(df.index >= (len(t_all) - 1), np.nan)
        df['N_forecast'] = N_full
        
        return df

    def plot(
        self,
        *,
        periods: Optional[int] = None,
        horizon_days: Optional[int] = 365,
        show: bool = True,
        ax: Optional[Axes] = None,
        title: Optional[str] = None,
    ) -> Axes:
        '''
        Quick visualization: history vs fitted+forecasted trend on linear axes.
        '''
        if self._fit is None:
            raise RuntimeError('Call .fit(...) before plotting.')

        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise ImportError('Plotting requires matplotlib. Install prodpy[plots].') from exc

        fdf = self.run(periods=periods, horizon_days=horizon_days)

        if ax is None:
            _, ax = plt.subplots(figsize=(8.5, 5.0))

        # History
        ax.scatter(fdf['date'], fdf['q_hist'], s=14, alpha=0.7, label='Observed')

        # Fitted + forecast (continuous curve)
        ax.plot(fdf['date'], fdf['q_fit'], lw=2.0, label='Fitted model')

        # Cosmetic
        ttl = title or f"DCA Forecast ({self._arps_hat.mode}, b={self._fit.b:.3g})"
        ax.set_title(ttl)
        ax.set_xlabel('Date')
        ax.set_ylabel(self.rate_col)
        ax.grid(True, alpha=0.3)
        ax.legend()

        if show:
            plt.tight_layout()
            plt.show()
        return ax
