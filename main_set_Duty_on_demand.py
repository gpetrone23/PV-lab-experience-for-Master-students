import sys
from machine import Pin, PWM

# Hardware Configuration
PWM_PIN = 15       # Any valid GPIO pin on Pico 2 (e.g., GP15)
FREQUENCY = 100000   # Signal frequency in Hz (50 kHz)

# Initialize pin in PWM mode
pwm_out = PWM(Pin(PWM_PIN))
pwm_out.freq(FREQUENCY)

print("--- Pico 2 On-Demand PWM Control ---")
print(f"Frequency set to: {FREQUENCY} Hz on GP{PWM_PIN}")
print("Enter a value between 0 and 100 to change the Duty Cycle.")
print("Type 'exit' to stop the script.")
print("-------------------------------------")

while True:
    try:
        # Wait for user input from the serial console
        user_input = input("\nEnter Duty Cycle (%): ").strip()
        
        if user_input.lower() == 'exit':
            print("Deactivating PWM and exiting.")
            pwm_out.deinit()  # Release PWM hardware resources
            break
            
        # Convert input string to a float
        duty_percent = float(user_input)
        
        # Validate data range
        if 0 <= duty_percent <= 100:
            # Calculate the 16-bit value (0 - 65535) required by MicroPython
            duty_u16 = int((duty_percent / 100) * 65535)
            
            # Apply the new duty cycle in real-time
            pwm_out.duty_u16(duty_u16)
            
            print(f"-> Success: Duty Cycle set to {duty_percent}% (U16 Value: {duty_u16})")
        else:
            print("-> Error: Value must be between 0 and 100.")
            
    except ValueError:
        print("-> Error: Invalid input. Enter numbers only or 'exit'.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Powering down PWM.")
        pwm_out.deinit()
        break
