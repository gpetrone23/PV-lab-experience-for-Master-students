from machine import ADC, mem32, Pin, PWM
import rp2
import array
import time

FILENAME_OUT = "IVscanG375W.csv"

num_steps=50 # number of duty cycle steps
num_measurements = 200 # number of measurements for each point

Vpan=[0]*num_steps
Ipan=[0]*num_steps
Ppan=[0]*num_steps
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
# Duty cycle valore tra 0 e 1

print("Starting IV scan")
duty_steps=0.85/num_steps
for s in range(0, num_steps):

    duty_cycle =max(0.1,min(0.1+s*duty_steps,0.95))
    # Conversion in u16 (0-65535) for MicroPython
    pwm1.duty_u16(int(duty_cycle * 65535))
    time.sleep(0.5)
    # Perform the actual ADC reads
    for m in range(0, num_measurements):
            raw0[m] = adc0.read_u16()
            raw1[m] = adc1.read_u16()
            raw2[m] = adc2.read_u16()
    # Calculate the average values
    Vpan[s] = (sum(raw1) -sum(raw0))/ len(raw1)*conversion_factor*v_gain
    Ipan[s] = (sum(raw2)/ len(raw2)*conversion_factor-0.35)*i_gain
    Ppan[s]=Vpan[s]*Ipan[s]
  
    
    print(f"Update Duty Cycle to: {duty_cycle:.4f}")
    # Print results
    #print(f"CH0: {volts0:.3f}V | CH1: {volts1:.3f}V | CH2: {volts2:.3f}V")
    print(f"PV Voltage:   {Vpan[s]:.3f}V; PV current {Ipan[s]:.3f}A")
    print(f"PV power: {Ppan[s]:3f}W")
    print(f"Duty: {duty_cycle:2f}")
    # Delay for readability



"""

FILENAME_INPUT="EIS_input.csv"
FILENAME_OUT = "Data_Stored.csv"
LOG_FILE = "data_log.txt"


print("Project MPPT P&O for single Photovoltaic Panel")
print("UNISA - EE4DE")
print("\n")
print("OPERATING LIMITS")
print("max PV voltage 15V")
print("max PV current 10A")
print("max Output Voltage 30V")
"""

"""
print("--- Setting the Analogue to digital Front-End Module (FEM)")
print("\n")

# 1. Correct Raspberry Pi Pico 2 (RP2350) Address Configuration - check GP in datasheet
ADC_BASE = 0x400a0000
ADC_CS   = ADC_BASE + 0x00  # Control and Status
ADC_FIFO = ADC_BASE + 0x0c  # FIFO Data Register (Where DMA reads from)
ADC_FCS  = ADC_BASE + 0x08  # FIFO Control (DREQ/Threshold configuration)
ADC_DIV  = ADC_BASE + 0x10  # Clock Divider (Sampling interval)
ADC_INTR = ADC_BASE + 0x14  # Interrupts
#ADC_RROBIN = ADC_BASE + 0x18 # Round Robin (Multiple channel selection)

# 2. Sampling Parameters
RING_BITS = 5 # 2^10 = 1024 bytes (if size=1, these are 512 16-bit samples)
BUFFER_SIZE = 1 << RING_BITS
NSAMPLES = BUFFER_SIZE 
FREQ = 100000  # 10 kHz
div_val = int(48000000 / FREQ) - 1
#adc = ADC(27) 
adc1=ADC(Pin(27))
adc2=ADC(Pin(26))
# 3. Configure ADC FIFO for DMA
# Bit 0: EN, Bit 3: DREQ_EN, Bits 10-23: THRESHOLD (Threshold = 1)
mem32[ADC_DIV] = div_val << 8  # The divider uses bits 8-31 (integer part)
#mem32[ADC_FCS] = (1 << 0) | (1 << 3) | (1 << 10) # EN, DREQ_EN, Threshold=1
mem32[ADC_FCS] = (1 << 0) | (1 << 3) | (1 << 24) # EN, DREQ_EN, Threshold=1

# Aggiungendo (1 << 1) i campioni diventano 8-bit, compatibili con dma size=1
#mem32[ADC_FCS] = (1 << 0) | (1 << 1) | (1 << 3) | (1 << 24)

# 1. Enable Round Robin for Channel 0 (bit 16) and Channel 1 (bit 17)
# This tells the ADC: "Sample 0, then 1, then 0..."
mask = (1 << 0) | (1 << 1)
mem32[ADC_CS] = (mem32[ADC_CS] & ~(0x1f << 16)) | (mask << 16)


# 4. Buffer and DMA Setup
adc_buff = array.array('H', [0] * NSAMPLES)
dma = rp2.DMA()
#ctrl = dma.pack_ctrl(size=1, inc_read=False, inc_write=True, treq_sel=36)
ctrl = dma.pack_ctrl(size=1, inc_read=False, inc_write=True, treq_sel=48)
# SET treq_sel=48 for ADC channel in Pi Pico 2 (RP2350)
# SET treq_sel=36 for ADC channel in Pi Pico (RP2040)
dma.config(read=ADC_FIFO, write=adc_buff, count=NSAMPLES, ctrl=ctrl, trigger=True)

# 5. Activate ADC in "Free Running" mode (Bit 1 of the CS register)
# This tells the ADC to sample continuously at the set frequency
#mem32[ADC_CS] = mem32[ADC_CS] | (1 << 1)
#Da datasheet 
mem32[ADC_CS] = mem32[ADC_CS] | (1 << 3)
#mem32[ADC_CS] = mem32[ADC_CS] & ~(1 << 3) # Turn off Free Running
# 6. Now the DMA receives data and dma.active() will work
print("Sampling in progress...")
while dma.active():
    pass 

# 7. Stop the ADC and read the data
#mem32[ADC_CS] = mem32[ADC_CS] & ~(1 << 1) # Turn off Free Running
mem32[ADC_CS] = mem32[ADC_CS] & ~(1 << 3) # Turn off Free Running
data_list = list(adc_buff)


    

#print(f"Completed! First 50 values: {data_list[:100]}")


def analyze_data(buffer, adc_cs_reg):
    # 1. Check for Hardware Errors (Bit 3 of ADC_CS)
    # 0x08 is (1 << 3). If this bit is 1, an error occurred during sampling.
    err_flag = mem32[adc_cs_reg] & 0x08
    if err_flag:
        print("⚠️ WARNING: ADC Error detected (FIFO Overflow or Conversion Error)!")
    
    if not buffer:
        print("Buffer is empty!")
        return

    # 2. Basic Statistics
    v_max = max(buffer)
    v_min = min(buffer)
    avg = sum(buffer) / len(buffer)
    
    # 3. Voltage Conversion (12-bit ADC = 4095 steps, 3.3V reference)
    v_avg = (avg * 3.3) / 4095
    
    print("-" * 30)
    print(f"Samples analyzed: {len(buffer)}")
    print(f"Max Value: {v_max}")
    print(f"Min Value: {v_min}")
    print(f"Average:   {avg:.2f} ({v_avg:.3f} V)")
    print("-" * 30)

# Call this after the sampling is finished
analyze_data(adc_buff, ADC_CS)

Vch1= [adc_buff[i] for i in range(0, len(adc_buff), 2)]
Vch2= [adc_buff[i] for i in range(1, len(adc_buff), 2)]

print(Vch1[0:10])
print(Vch2[0:10])

v_gain=10.09
Vavg = (sum(Vch1)-sum(Vch2)) / len(Vch2)*3.3/4095*v_gain
print(f"{Vch1[3]*3.3/4095}")
print(f"{Vch2[3]*3.3/4095}")

print(f"{Vavg}")


"""

def save_vectors_to_csv(Vpan,Ipan,Ppan):
    try:
        with open(FILENAME_OUT, "w") as f:
            # Scrittura Intestazione (opzionale)
            f.write("Vpan,Ipan,Ppan\n")
            
            # Iteriamo sul buffer a passi di 2 per separare i canali
            for i in range(0, len(Vpan), 1):
                # Salvataggio in formato CSV (3 colonne)
                f.write(f"{Vpan[i]},{Ipan[i]},{Ppan[i]}\n")
                
        print(f"--- Data successfully saved to {FILENAME_OUT}")
    except OSError as e:
        print(f"Errore disco: {e}")
        
save_vectors_to_csv(Vpan,Ipan,Ppan)


def get_formatted_time():
    """Returns timestamp in YYYYMMDD-HH:MM:SS format."""
    t = utime.localtime()
    # Format: YYYYMMDD-HH:MM:SS
    return "{:04d}{:02d}{:02d}-{:02d}:{:02d}:{:02d}".format(
        t[0], t[1], t[2], t[3], t[4], t[5]
    )