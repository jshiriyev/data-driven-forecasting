# Production Forecasting for Oil & Gas Wells

## Overview  
This repository is designed to offer comprehensive **production forecasting** solutions for oil and gas wells. It includes tools for **production data analysis**, **decline curve analysis**, and **time series analysis**, enabling users to make informed predictions about future production trends.

## Features
- **Data Extraction** – Read and structure production data from various formats, including Excel.
- **Production Data Analysis** – Process, clean, and visualize production data.
- **Graphical Templates** – Industry-standard visualizations for production trend analysis and interpretation.
- **Decline Curve Analysis** – Implement common decline models (Exponential, Harmonic, Hyperbolic).  
- **Time Series Analysis** – Utilize statistical methods and machine learning models for forecasting.
- **Customizable Workflow** – Modify or extend the tools to fit specific reservoir and well conditions.  

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
