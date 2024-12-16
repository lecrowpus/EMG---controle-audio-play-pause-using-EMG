import serial
import time
import keyboard

# Configure the serial connection
PORT = 'COM3'  # Replace with the correct port
BAUD_RATE = 115200 # Define correct baud rate
TIMEOUT = 1 
COOLDOWN_TIME = 1.0  

last_trigger_time = 0 

# Define the red light threshold
TRIGGER_THRESHOLD = 22

try:
    # Open serial connection
    arduino = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"Connected to {PORT} at {BAUD_RATE} baud.")

    # Allow time for Arduino to reset and start
    time.sleep(2)

    # Read and process data
    while True:
        current_time = time.time()
        if arduino.in_waiting > 0:  # Check if data is available
            raw_data = arduino.readline().decode('utf-8').strip()  # Read a line and decode it
            if raw_data:
                try:
                    # Split signal and envelope
                    signal, envelop = map(int, raw_data.split(','))
                    print(f"Signal: {signal}, Envelope: {envelop}")

                    # Trigger command when the red light threshold is met
                    if envelop >= TRIGGER_THRESHOLD:
                        if current_time - last_trigger_time > COOLDOWN_TIME:
                            last_trigger_time = current_time
                            print("Playing or pausing the audio")
                            # Play?Pause audio
                            keyboard.press_and_release('play/pause media')  # Replace with your command/script
                            
                            pass
                        else:
                            print("Cooldown in effect, no trigger.")
                except ValueError:
                    print(f"Invalid data received: {raw_data}")
except serial.SerialException as e:
    print(f"Serial error: {e}")
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
        print("Serial connection closed.")
