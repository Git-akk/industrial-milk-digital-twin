# Industrial Digital Twin: Ayran & Irimshik Production Simulation

## 📌 Overview
This project is a high-fidelity **Digital Twin** for dairy production (Ayran and Irimshik). It combines mathematical modeling, synthetic data generation, and interactive SCADA-like visualizations to monitor and predict industrial food processing stages.

## 🚀 Key Technical Features
* **Synthetic Data Engine (`DB.py`):** Instead of static data, the system uses custom mathematical models (Logarithmic and Exponential growth/decay) to simulate pH levels, viscosity, and microbiological activity.
* **Predictive Analytics:** Implements **Scikit-learn (Linear Regression)** to predict the "Target Point" for fermentation and moisture levels in real-time.
* **Custom SCADA Visualization:** A bespoke industrial dashboard built with **Streamlit** and custom **HTML/CSS/SVG** to visualize the technological flow (Pasteurization -> Fermentation -> Cooling).
* **3D Response Surface Modeling:** Advanced visualization of how time, temperature, and additives affect the final product quality using **Matplotlib 3D**.

## 🛠 Tech Stack
* **Core:** Python 3.x
* **Frontend:** Streamlit (Multi-page Architecture)
* **Data Science:** Pandas, NumPy, Scikit-learn
* **Visualization:** Matplotlib, Seaborn, Plotly, Custom HTML/CSS
* **Data Layer:** Simulation-driven CSV Generation

## 📂 Project Structure
* `main.py`: The central dashboard with KPI cards and predictive monitoring.
* `DB.py`: The simulation engine that generates the industrial datasets.
* `pages/`: Specialized modules for SCADA views, regression analysis, and 3D modeling.

## 📈 Industry 4.0 Impact
This system demonstrates how traditional food production can be optimized through:
1. **Precision Timing:** Avoiding "over-fermentation" through predictive modeling.
2. **Resource Optimization:** Modeling moisture loss in Irimshik production to save energy.
3. **Quality Assurance:** Real-time "Traffic Light" status (✅ Normal / ⚠️ Warning) based on model predictions.

## ⚙️ How to Run
1. Clone the repo:
   ```bash
   git clone [https://github.com/Git-akk/industrial-milk-digital-twin.git](https://github.com/Git-akk/industrial-milk-digital-twin.git)

2.Run the application:
  ```bash
   streamlit run main.py


