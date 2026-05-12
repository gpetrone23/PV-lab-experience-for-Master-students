from machine import ADC, mem32, Pin, PWM
import rp2
import array
import time

class MPPT:
    def __init__(self, step_size=0.03, initial_d=0.8):
        self.d = initial_d        # Current Duty Cycle (0.0 to 1.0)
        self.step = step_size     # The increment/decrement step
        self.p_prev = 0.0         # Power from the previous iteration
        self.v_prev = 0.0         # Voltage from the previous iteration

    def compute_duty(self, v_now, i_now):
        # 1. Calculate current power
        p_now = v_now * i_now
        
        # 2. Calculate variations
        delta_p = p_now - self.p_prev
        #delta_v = v_now - self.v_prev

        # 3. Perturb and Observe Logic
        #print(f"Delta PV power: {delta_p:3f}W")
        if delta_p != 0:
            if delta_p > 0:
                # Power is increasing, keep going in the same direction
                self.d += self.step #for Buck
            else:
                # Power is decreasing, reverse the direction
                self.d -= self.step
                # and reverse the direction of perturbation
                self.step=-self.step
        # 4. Safety Constraints (Clamp Duty Cycle between 10% and 90%)
        self.d = max(0.1, min(0.9, self.d))
        # 5. Store values for the next cycle
        self.p_prev = p_now
        self.v_prev = v_now
        return self.d

# Conversion factor for 16-bit (0-65535) to Voltage (0-3.3V)
conversion_factor = 3.3 / 65535
# Conversion factor for 12-bit (0-4095) to Voltage (0-3.3V)
#conversion_factor = 3.3 / 4095
# Voltage and Current Sensors Gain
v_gain=10.09
i_gain=8


# Configure the 3 ADC channels (GP26, GP27, GP28)
adc0 = ADC(Pin(26)) # Vpan+
adc1 = ADC(Pin(27)) # Vpan-   ADC in differential mode
adc2 = ADC(Pin(28)) # Ipan 

num_measurements = 10 # number of measurements

raw0 = [0] * num_measurements
raw1 = [0] * num_measurements
raw2 = [0] * num_measurements

#SETTING PWM MODULE
print("--- Setting PWM")
#Config. pin (es. GPIO 15)
pwm1 = PWM(Pin(15))
# Impostazione frequenza di commutazione e.g 10kHz=10000
frequency = 100000 
pwm1.freq(frequency)



# Configure a toggle pin to monitor ADC timing (GP6)
# Use an oscilloscope or logic analyzer on this pin
trigger_pin = Pin(6, Pin.OUT)

print("Starting ADC measurements with trigger pin on GP15...")

mppt_controller = MPPT(step_size=0.055)

while True:
    # --- START Measurement: Set Pin HIGH ---
    trigger_pin.value(1)
    
    
    # Perform the actual ADC reads
    for m in range(0, num_measurements):
            raw0[m] = adc0.read_u16()
            raw1[m] = adc1.read_u16()
            raw2[m] = adc2.read_u16()
    
    # --- END Measurement: Set Pin LOW ---
    trigger_pin.value(0)
    
    Vpan = (sum(raw1) -sum(raw0))/ len(raw1)*conversion_factor*v_gain
    Ipan = (sum(raw2)/ len(raw2)*conversion_factor-0.35)*i_gain
    Ppan=Vpan*Ipan
  
 
    duty_cycle = mppt_controller.compute_duty(v_now=Vpan, i_now=Ipan)
    # Conversione in valore u16 (0-65535) per MicroPython
    duty_u16 = int(duty_cycle * 65535)
    pwm1.duty_u16(duty_u16)
    
    print(f"Update Duty Cycle to: {duty_cycle:.4f}")
    print(f"PV Voltage:   {Vpan:.3f}V; PV current {Ipan:.3f}A")
    print(f"PV power: {Ppan:3f}W")
    print(f"Duty: {duty_cycle:2f}")
    # Delay for readability





