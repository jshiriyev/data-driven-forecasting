# Production Forecasting for Oil & Gas Wells

## Overview  
This repository is designed to offer comprehensive **production forecasting** solutions for oil and gas wells. It includes tools for **production data analysis**, **decline curve analysis**, and **time series analysis**, enabling users to make informed predictions about future production trends.

## Features
- **Graphical Templates** – Industry-standard visualizations for production trend analysis and interpretation.

The `prodpy.onepage` module offers ready-to-use templates for generating compact, graphical summaries of multi-dimensional production data. These visualizations combine key metrics such as oil, gas, and water rates with operational details like active perforation intervals, shut-ins, and completion events - all in a single, easy-to-read figure. Designed for quick well reviews and communication between subsurface and operations teams, the OnePage layout enhances situational awareness and supports efficient decision-making.

<img src="img/customized_production_figures.png">

*Figure 1: A layout showing production rates alongside active intervals and well events.*

- **Customizable Workflow** – Modify or extend the tools to fit specific reservoir and well conditions.

The reservoir allocation function `prodpy.Allocate` provides a systematic method to distribute measured production volumes (oil, gas, and water) from commingled surface data back to individual reservoirs or layers. This is particularly useful in fields with multi-zone completions or shared infrastructure. The allocation algorithm uses layer properties such as permeability, thickness, pressure, or historical trends to estimate each zone's contribution to total production. The function supports customizable weighting schemes and can be integrated into full-field workflows for reservoir surveillance, history matching, or field development planning.

<img src="img/reservoir_allocation_calculation.png">

*Figure 2: A typical workflow where surface production is decomposed and allocated to contributing reservoir zones using input data from well tests and petrophysical properties.*

- **Decline Curve Analysis** – Implement common decline models (Exponential, Harmonic, Hyperbolic).

The `prodpy.decline` module provides analytical tools for fitting and forecasting production using classical decline curve models, including exponential, hyperbolic, and harmonic equations. These models are implemented with a consistent interface and allow estimation of key parameters such as decline rate, cumulative production, and well life. The module is ideal for rapid screening, reserves estimation, and performance diagnostics in conventional reservoirs.

<img src="img/decline_curve_analysis_equations.png">

*Table 1: The mathematical forms of the implemented decline models, highlighting their differences in rate behavior and cumulative production estimates.*

- **Time Series Analysis** – Utilize statistical methods and machine learning models for forecasting.

## Installation
Clone the repository and install the required dependencies:  

```bash
git clone https://github.com/jshiriyev/main-prodpy.git  
cd main-prodpy 
pip install -r requirements.txt  
```

## Usage  
Example usage of the **decline curve analysis** module:  

```python
from prodpy import dca

# Load production data (assumed to be a Pandas DataFrame)
dca = dca(production_data)

# Fit a hyperbolic decline model
dca.fit(model="hyperbolic")

# Plot the forecasted production trend
dca.plot_forecast()
```

## Dependencies  
The following libraries are required:  
- Python 3.x  
- `pandas`  
- `numpy`  
- `matplotlib`  
- `scipy`  

## Contributing  
Contributions are welcome! If you find a bug or want to improve the tool, feel free to:  
1. **Fork** the repository  
2. **Create a new branch** (`feature-branch`)  
3. **Submit a pull request**  

## License  
This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
