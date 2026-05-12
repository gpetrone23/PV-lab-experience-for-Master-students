# TE4DE Laboratory activity - Photovoltaic MPPT System Testing

This repository contains the workflow and scripts for characterizing and testing a Maximum Power Point Tracking (MPPT) system based on the **Raspberry Pi RP2350** microcontroller. The system is designed to interface with a **6V / 25W nominal PV panel**.

## 🛠 Hardware Specifications
- **MCU:** Raspberry Pi RP2350 (Cortex-M33).
- **PV Source:** 6V / 25W (12-cell array) photovoltaic panel.
- **Irradiance Sensor:** Solarimeter LITEMETER PRO ($100 \Omega$ load)- (9-12)V power supply.
- **Converter:** DC-DC Power Stage (step-up).
- **Load:** 12V Lead acid battery
- **Tools:** Digital Oscilloscope, Multimeter, and Python-based Data Logger.

---

## 🧪 Experimental Phases

### Phase 1: Source Characterization (Static Test)
Establish the baseline performance of the PV panel under controlled irradiance conditions. A **matrir of different clored LED** is used to regulate the Irradiance level. 
- **Irradiance Calculation ($G$):** Measured via $G = 750 \cdot V_{sol} - 300$ $W/m^2$.
- **Static Metrics:** Measure $V_{oc}$ (Open Circuit Voltage) and $I_{sc}$ (Short Circuit Current).
- **Deliverable:** A baseline table correlating $W/m^2$ with photovoltaic electrical parameters.
This table establishes the PV panel's baseline performance under controlled irradiance from the LED matrix. Irradiance is calculated by measuring the output voltage (**$V_{sol}$**) of solarimeter and using the formula: $G = 750 \cdot V_{sol} - 300$ [$W/m^2$].


| # exp |LED current| $V_{sol}$ [V] | Irradiance ($G$) [$W/m^2$] | $V_{oc}$ [V] | $I_{sc}$ [A] |
| :---: | :---:| :---: | :---: | :---: | :---: |
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

> **Note:** PV cell temperature should be constant during testing to prevent thermal drift in $V_{oc}$ measurements.




### Phase 2: Hardware & Switching Analysis (Dynamic Test)
Verify photovoltaic voltage oscillations due to DC-DC converter dynamics and duty-cycle perturbation.
- **Script:** `main_set_Duty_on_demand.py`
- **Parameters:** 100kHz PWM frequency.
- **Procedure:** Execute a "Duty Step" from 80% to 85%.
- **Oscilloscope Configuration:** Trigger level at 2.8V. Single seq. visualization. A second order Voltage oscillation should be visible. Voltage switching ripple is also visible.

### Phase 3: I-V and P-V Curve Mapping (Scanning)
Experimentally identify the "Ground Truth" Maximum Power Point (MPP).
- **Script:** `main_IV_scan.py`
- **Protocols:**
  - **Fast Scan:** `num_steps=20`, `num_measurements=10` (Wiring validation).
  - **High-Res Scan:** `num_steps=50`, `num_measurements=200` (Curve plotting).
  - **Storage and Data transfer:** A .cvs file is saved on Raspberry Pi for each IV scan. Use Thonny IDE for Downloading Data on your PC. 
- **Deliverable:** Run the MATLAB script **PLOT_IV_curves.m** for reading the .csv files and generating the I-V and P-V plots to define the target for the MPPT algorithm.

### Phase 4: Control Loop Tuning (MPPT Performance)
Optimize tracking speed vs. steady-state stability using the RP2350's processing power.
- **Variables:**
  - **Step Size:** Compare 0.03 (Stable) vs. 0.075 (Aggressive).
  - **Sampling Time:** Stress test from 30ms down to 1ms.
- **Verification:** Analysis of convergence speed and oscillation ("hunting") around the peak power point.

---

## ⚡ Safety & Operation Notes
- **ADC Protection:** PV voltage $V_{pan}$ is reading trough a voltage sensor with a **10.1** attenuation factor to stay within the RP2350 3.3V limit. Current $I_{pan}$ is reading with a current sensor ganin of **8 A/V**.
- **Thermal Management:** DC-DC converter is not protected by over voltage and temperature sensors. Do NOT use it at high voltage (>20V input/output voltage) and high power (>30W). Monitoring of inductor and MOSFET temperatures could be usefull to guarantee safety conditions.

## 📂 Project Structure


| File | Description |
| :--- | :--- |
| `main_set_Duty_on_demand.py` | Manual PWM control for hardware validation. |
| `main_IV_scan.py` | Automated sweep to map panel characteristics. |
| `mppt_main.py` | Core MPPT algorithm based on Perturb and Observe (P&O) method. |
| `PLOT_IV_curves.m`|MATLAB script, reads .csv data, plots I-V and P-V curves|


---
Created by [@Giovanni Petrone](https://github.com)
