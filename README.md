# Production Forecasting for Oil & Gas Wells

[![PyPI version](https://img.shields.io/pypi/v/prodpy.svg)](https://pypi.org/project/prodpy/)
[![Python versions](https://img.shields.io/pypi/pyversions/prodpy.svg)](https://pypi.org/project/prodpy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Feature Highlights](#feature-highlights)
- [Testing](#testing)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

## Overview
`prodpy` is a production-forecasting toolkit for oil and gas wells. It streamlines production data analysis, decline-curve fitting, and time-series forecasting so engineers and data scientists can move from raw data to actionable insights quickly.

## Key Features
- Production-ready plotting templates for rapid well reviews.
- Configurable reservoir allocation utilities for multi-zone wells.
- Vectorized Arps decline-curve models with fitting and simulation helpers.
- Time-series analysis scaffolding for advanced forecasting workflows.

## Installation

### Quick Install (recommended)
```bash
python -m pip install -U pip
python -m pip install prodpy
```

### Optional Extras
Install the plotting extras when you need the OnePage figure templates:
```bash
python -m pip install "prodpy[plots]"
```

### From Source
```bash
git clone https://github.com/jshiriyev/data-driven-forecasting.git
cd data-driven-forecasting
python -m pip install -U pip
python -m pip install -e .
```

> Tip: Work inside a virtual environment to keep dependencies isolated.

## Quickstart

```python
import numpy as np
from prodpy.decline import Arps

# Instantiate three Arps models
m_exp = Arps(di=0.25, qi=120.0, mode="exponential")
m_har = Arps(di=0.25, qi=120.0, mode="harmonic")
m_hyp = Arps(di=0.25, qi=120.0, mode="hyperbolic", b=0.5)

# Time grid (consistent units with di)
t = np.linspace(0.0, 10.0, 201)

# Forecast rate and cumulative production
q_exp = m_exp.run(t)
n_exp = m_exp.run(t, cum=True)

# Shifted origin analysis (treat day 200 as new zero)
t2 = np.linspace(190.0, 220.0, 121)
q2 = m_har.run(t2, xi=200.0)

print(q_exp[:5])
print(n_exp[-1])
```

## Feature Highlights

### OnePage Production Dashboards
The `prodpy.onepage` module assembles compact, graphical summaries of multi-dimensional production data. Oil, gas, and water rates are plotted alongside perforation intervals, shut-ins, and completion events to support fast decision-making.

![OnePage production dashboard](img/customized_production_figures.png "Example production dashboard")

### Reservoir Allocation
Use `prodpy.Allocate` to distribute measured commingled production back to contributing layers. Configure weighting schemes with permeability, thickness, pressure, or historical trends to tailor allocations for multi-zone completions.

![Reservoir allocation workflow](img/reservoir_allocation_calculation.png "Reservoir allocation workflow")

### Decline-Curve Analysis
The `prodpy.decline` module implements exponential, harmonic, and hyperbolic models with a consistent API for linearized regression, non-linear fitting, and uncertainty sampling.

![Decline curve analysis equations](img/decline_curve_analysis_equations.png "Decline curve analysis equations")

```python
import numpy as np
from prodpy.decline import Arps

TRUE = dict(mode="hyperbolic", di=0.22, qi=150.0, b=0.6)

t = np.linspace(0.0, 8.0, 400)
true_model = Arps(**TRUE)
q_clean = true_model.run(t)

# Add multiplicative noise to mimic measurements
rng = np.random.default_rng(7)
q_obs = q_clean * (1.0 + 0.01 * rng.standard_normal(q_clean.shape))

fitr = true_model.fit(t, q_obs)
print(fitr)
print(Arps.reader(fitr))

lo = Arps.simulate(fitr, prc=5.0)
hi = Arps.simulate(fitr, prc=95.0)
print("(di, qi)@5%:", lo)
print("(di, qi)@95%:", hi)
```

## Testing
Install the test dependencies and run the suite:

```bash
python -m pip install pytest numpy scipy
pytest -q
# or parallel
pytest -n auto
```

Key checks in `tests/test_arps.py` verify mode-to-exponent mapping, rate and cumulative outputs, shifted-origin behavior, fit accuracy, linearization fidelity, and the helper utilities (`reader`, `simulate`).

## Requirements
- Python 3.9 or newer
- pandas
- numpy
- matplotlib
- scipy

## Contributing
Contributions are welcome! If you find a bug or want to improve the tool:
1. Fork the repository.
2. Create a descriptive branch (for example, `feature/new-dashboard`).
3. Open a pull request with context and testing notes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
