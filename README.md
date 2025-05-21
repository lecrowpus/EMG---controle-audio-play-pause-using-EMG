

---

# EMG Control Audio Play/Pause Using EMG

Triggering play/pause commands based on EMG signals.

## Requirements

### Hardware
- **1x Muscle BioAmp Shield**
- **1x Arduino Uno**
- **1x BioAmp Cable**
- **1x Nuprep Skin Preparation Gel**
- **1x Muscle BioAmp Band**
- **Hardware form:** [Upside Down Labs](https://upsidedownlabs.tech/)

### Circuit diagram
![image](https://github.com/user-attachments/assets/e561d17a-45f4-47ce-8f31-deeade34bec2)

### Software
- **Arduino IDE v1.8.19 (legacy IDE)**
- **VS Code**
- **Python (newest version available)**

## Installation

1. **Copy everything up to step 7 (except step 6) from the Upside Down Labs documentation**:
   - Link: [Upside Down Labs Documentation](https://docs.upsidedownlabs.tech/hardware/bioamp/muscle-bioamp-shield/index.html#id24)

2. **Step 8**: Install the `requirements.txt` `pip install -r requirements.txt` and close the Arduino IDE (if open). 

3. **Step 9**: Change the COM port to your specific one.
   - ![image](https://github.com/user-attachments/assets/bf30f4d8-c597-4527-a5ba-cb5bb491f011)

4. **Step 10**: Run the script `python main.py`


### Code Explanation

```python
import serial
import time
import keyboard

# Configure the serial connection
PORT = 'COM3'  # Replace with the correct port
BAUD_RATE = 115200  # Define correct baud rate
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
```

### Explanation:

1. **Serial Configuration**:
   - `PORT` specifies the serial port (e.g., `COM3` on Windows, `/dev/ttyUSB0` on Linux/Mac).
   - `BAUD_RATE` defines the speed of data transmission. It should match the baud rate set on the Arduino.
   - `TIMEOUT` sets the timeout for the serial read operation.

2. **Data Processing**:
   - The script reads data from the Arduino in a loop. It waits for data with `arduino.in_waiting > 0`.
   - `arduino.readline()` reads a line of data from the serial input.
   - Data is split into signal and envelope values using `split(',')`. The threshold value for triggering is defined by `TRIGGER_THRESHOLD`.

3. **Trigger Mechanism**:
   - When the envelope (a measure of muscle signal strength) exceeds the `TRIGGER_THRESHOLD`, it triggers the play/pause command.
   - A cooldown period (`COOLDOWN_TIME`) ensures the play/pause command is not triggered too frequently.
   - `keyboard.press_and_release('play/pause media')` sends a play/pause command to the system. Replace this with your specific audio control command or script.

4. **Error Handling**:
   - `serial.SerialException` catches issues with the serial connection.
   - `KeyboardInterrupt` allows clean exit when the script is stopped.
   - In the `finally` block, the serial connection is safely closed if it is open.

### Usage:

- Ensure the hardware is properly connected to the Arduino.
- Upload the sketch to the Arduino using the **Arduino IDE**.
- Run the Python script on your computer. Replace the serial port, baud rate, and audio control command as needed.
- Monitor the serial data as the script reads and triggers audio play/pause based on EMG signals.



---

![image](https://github.com/user-attachments/assets/68bf19a9-9890-4f9f-8d0d-54b8e69812a2)


### Code Explanation:

```cpp
#define SAMPLE_RATE 500
#define BAUD_RATE 115200
#define INPUT_PIN A0
#define BUFFER_SIZE 128

int circular_buffer[BUFFER_SIZE];
int data_index, sum;
// LED pin numbers in-order
int led_bar[] = {4, 5, 6, 7, 8, 9, 10, 11, 12};
int total_leds = sizeof(led_bar) / sizeof(led_bar[0]);

void setup() {
  // Serial connection begin
  Serial.begin(BAUD_RATE);
  // Initialize all the led_bar
  for (int i = 0; i < total_leds; i++) {
    pinMode(led_bar[i], OUTPUT);
  }
}

void loop() {
  // Calculate elapsed time
  static unsigned long past = 0;
  unsigned long present = micros();
  unsigned long interval = present - past;
  past = present;

  // Run timer
  static long timer = 0;
  timer -= interval;

  // Sample and get envelop
  if(timer < 0) {
    timer += 1000000 / SAMPLE_RATE;
    int sensor_value = analogRead(INPUT_PIN);
    int signal = EMGFilter(sensor_value);
    int envelop = getEnvelop(abs(signal));

    // Update LED bar graph
    for(int i = 0; i<=total_leds; i++){
      if(i>(envelop-1)){
        digitalWrite(led_bar[i], LOW);
      } else {
        digitalWrite(led_bar[i], HIGH);
      }
    }

    Serial.print(signal);
    Serial.print(",");
    Serial.println(envelop);
  }
}

// Envelop detection algorithm
int getEnvelop(int abs_emg){
  sum -= circular_buffer[data_index];
  sum += abs_emg;
  circular_buffer[data_index] = abs_emg;
  data_index = (data_index + 1) % BUFFER_SIZE;
  return (sum/BUFFER_SIZE) * 2;
}

// Band-Pass Butterworth IIR digital filter, generated using filter_gen.py.
// Sampling rate: 500.0 Hz, frequency: [74.5, 149.5] Hz.
// Filter is order 4, implemented as second-order sections (biquads).
float EMGFilter(float input)
{
  float output = input;
  {
    static float z1, z2; // filter section state
    float x = output - 0.05159732*z1 - 0.36347401*z2;
    output = 0.01856301*x + 0.03712602*z1 + 0.01856301*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -0.53945795*z1 - 0.39764934*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - 0.47319594*z1 - 0.70744137*z2;
    output = 1.00000000*x + 2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  {
    static float z1, z2; // filter section state
    float x = output - -1.00211112*z1 - 0.74520226*z2;
    output = 1.00000000*x + -2.00000000*z1 + 1.00000000*z2;
    z2 = z1;
    z1 = x;
  }
  return output;
}
```

### Explanation:

1. **Hardware Configuration**:
   - The code uses an Arduino connected to a BioAmp Shield to capture EMG signals from a muscle.
   - `INPUT_PIN` is configured as an analog input to read the EMG signal.
   - LEDs are connected to digital pins 4 to 12 to form a bar graph.

2. **Sampling Rate and Serial Communication**:
   - `SAMPLE_RATE` is set to 500 Hz, indicating how often the microcontroller reads the EMG signal.
   - `BAUD_RATE` is set to 115200 for serial communication.
   - The serial connection is initialized to display data.

3. **LED Bar Graph Logic**:
   - The code uses an array `led_bar` to hold the pins for the LEDs in the bar graph.
   - `getEnvelop(abs(signal))` processes the absolute EMG signal to calculate the envelope, which is then mapped to the LED bar graph.
   - LEDs are turned on or off based on the calculated envelope, showing the strength of the muscle signal.

4. **Envelop Detection Algorithm**:
   - `getEnvelop(int abs_emg)` uses a circular buffer to smooth out the EMG signal over time.
   - The buffer size is defined as `BUFFER_SIZE`, which is 128 in this case.
   - `sum` accumulates the values from the buffer, and the envelope is calculated as `(sum/BUFFER_SIZE) * 2`.

5. **EMG Filtering**:
   - `EMGFilter(float input)` applies a band-pass Butterworth IIR filter to the raw EMG signal.
   - The filter is implemented as second-order sections and helps in removing noise and focusing on the relevant frequency range.
   - Multiple sections of the filter are applied to smooth the signal and maintain a clean representation of the EMG data.

6. **Error Handling and Optimization**:
   - The `circular_buffer` and `data_index` are used to manage the buffer efficiently.
   - The loop ensures the LEDs are updated only when necessary, minimizing power consumption.

7. **License and Support**:
   - The code is open-source under the **MIT License**, allowing users to modify and distribute it.
   - Upside Down Labs encourages users to support their work by purchasing hardware products.

---


