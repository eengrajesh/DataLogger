# GPIO Wiring Diagram for DataLogger Pi5

## 🔌 **Raspberry Pi 5 GPIO Pinout Used**

```
     3.3V  [ 1] [2 ] 5V     
   GPIO 2  [ 3] [4 ] 5V     
   GPIO 3  [ 5] [6 ] GND    
   GPIO 4  [ 7] [8 ] GPIO 14
      GND  [ 9] [10] GPIO 15
  GPIO 17  [11] [12] GPIO 18
  GPIO 27  [13] [14] GND    
  GPIO 22  [15] [16] GPIO 23
     3.3V  [17] [18] GPIO 24
  GPIO 10  [19] [20] GND    
   GPIO 9  [21] [22] GPIO 25
  GPIO 11  [23] [24] GPIO 8 
      GND  [25] [26] GPIO 7 
   GPIO 0  [27] [28] GPIO 1 
   GPIO 5  [29] [30] GND    
   GPIO 6  [31] [32] GPIO 12
  GPIO 13  [33] [34] GND    
  GPIO 19  [35] [36] GPIO 16
  GPIO 26  [37] [38] GPIO 20
      GND  [39] [40] GPIO 21
```

---

## 🎛️ **Pin Assignments**

### **BUTTONS (Input with Pull-up resistors):**
- **GPIO 17** (Pin 11) → 🟢 **START/STOP Button** (Green)
- **GPIO 27** (Pin 13) → 🔴 **SHUTDOWN Button** (Red)  
- **GPIO 22** (Pin 15) → 🔵 **EXPORT Button** (Blue)
- **GPIO 23** (Pin 16) → 🟡 **WIFI RESET Button** (Yellow)

### **LEDs (Output with 220Ω resistors):**
- **GPIO 18** (Pin 12) → 🟢 **SYSTEM Status LED** (Green)
- **GPIO 24** (Pin 18) → 🔴 **ERROR Status LED** (Red)
- **GPIO 25** (Pin 22) → 🔵 **NETWORK Status LED** (Blue)  
- **GPIO 5**  (Pin 29) → 🟡 **LOGGING Status LED** (Yellow)

### **POWER & GROUND:**
- **3.3V** (Pin 1 or 17) → All button pull-ups
- **GND** (Pin 6, 9, 14, 20, 25, 30, 34, 39) → All common grounds

---

## ⚡ **Detailed Wiring Connections**

### **BUTTON WIRING (with internal pull-up):**
```
BUTTON SCHEMATIC (per button):

Pi GPIO Pin ----[Button]---- GND
     |
 (Internal Pull-up 
  enabled in software)
```

**Physical Connections:**
1. **START Button (Green):**
   - One terminal → **GPIO 17** (Pin 11)
   - Other terminal → **GND** (Pin 14)

2. **SHUTDOWN Button (Red):**
   - One terminal → **GPIO 27** (Pin 13)  
   - Other terminal → **GND** (Pin 14)

3. **EXPORT Button (Blue):**
   - One terminal → **GPIO 22** (Pin 15)
   - Other terminal → **GND** (Pin 20)

4. **WIFI Button (Yellow):**
   - One terminal → **GPIO 23** (Pin 16)
   - Other terminal → **GND** (Pin 20)

### **LED WIRING (with current limiting resistors):**
```
LED SCHEMATIC (per LED):

Pi GPIO Pin ----[220Ω Resistor]----[LED Anode(+)]
                                       |
                                   [LED Cathode(-)]
                                       |
                                     GND
```

**Physical Connections:**
1. **SYSTEM LED (Green):**
   - **GPIO 18** (Pin 12) → 220Ω resistor → LED **Anode (+)**
   - LED **Cathode (-)** → **GND** (Pin 14)

2. **ERROR LED (Red):**
   - **GPIO 24** (Pin 18) → 220Ω resistor → LED **Anode (+)**
   - LED **Cathode (-)** → **GND** (Pin 20)

3. **NETWORK LED (Blue):**
   - **GPIO 25** (Pin 22) → 220Ω resistor → LED **Anode (+)**
   - LED **Cathode (-)** → **GND** (Pin 25)

4. **LOGGING LED (Yellow):**
   - **GPIO 5** (Pin 29) → 220Ω resistor → LED **Anode (+)**
   - LED **Cathode (-)** → **GND** (Pin 30)

---

## 📋 **Step-by-Step Wiring Instructions**

### **Step 1: Prepare Components**
1. Identify GPIO pins on Pi5 using pinout diagram above
2. Prepare 8 female-to-male jumper wires for connections
3. Connect 220Ω resistors to LED anodes (+ side)

### **Step 2: Connect Buttons**
1. Connect **START button** between GPIO 17 (Pin 11) and GND (Pin 14)
2. Connect **SHUTDOWN button** between GPIO 27 (Pin 13) and GND (Pin 14)  
3. Connect **EXPORT button** between GPIO 22 (Pin 15) and GND (Pin 20)
4. Connect **WIFI button** between GPIO 23 (Pin 16) and GND (Pin 20)

### **Step 3: Connect LEDs** 
1. Connect **SYSTEM LED**: GPIO 18 (Pin 12) → 220Ω → Green LED (+) → GND (Pin 14)
2. Connect **ERROR LED**: GPIO 24 (Pin 18) → 220Ω → Red LED (+) → GND (Pin 20)
3. Connect **NETWORK LED**: GPIO 25 (Pin 22) → 220Ω → Blue LED (+) → GND (Pin 25)  
4. Connect **LOGGING LED**: GPIO 5 (Pin 29) → 220Ω → Yellow LED (+) → GND (Pin 30)

### **Step 4: Test Connections**
1. Power on Pi5
2. Run GPIO test script (provided with software)
3. Verify all LEDs light up when tested
4. Verify all buttons register presses

---

## 🎨 **Physical Layout Suggestions**

### **Panel Layout:**
```
┌─────────────────────────┐
│  ENERTHERM DATALOGGER   │
├─────────────────────────┤
│                         │
│  ●🟢 SYSTEM    ●🔴 ERROR  │
│  ●🔵 NETWORK   ●🟡 LOG    │  
│                         │
│ [🟢START] [🔴SHUTDOWN]   │
│ [🔵EXPORT] [🟡WIFI]      │
│                         │
└─────────────────────────┘
```

### **Breadboard Layout:**
```
    Pi5 GPIO Header
         |
    [Breadboard]
    Buttons | LEDs
      🟢🔴    🟢🔴
      🔵🟡    🔵🟡
```

---

## ⚠️ **Safety & Testing Notes**

### **Before Powering On:**
- ✅ Double-check all ground connections
- ✅ Verify no short circuits between power and ground  
- ✅ Ensure LEDs are connected with correct polarity (+/-)
- ✅ Confirm resistors are in series with LEDs

### **Testing Checklist:**
- [ ] All 4 buttons register presses (software will show)
- [ ] All 4 LEDs can be controlled (turn on/off)
- [ ] No shorts or overheating
- [ ] GPIO pins not damaged (3.3V max)

### **Troubleshooting:**
- **LED not lighting:** Check polarity and resistor connection
- **Button not working:** Check ground connection and pull-up
- **Multiple issues:** Check power connections (3.3V/GND)

---

## 🔧 **Optional Enhancements**

### **Professional Mounting:**
- Use panel-mount buttons and LEDs
- Drill holes in project box for clean installation
- Add labels next to buttons and LEDs

### **Extended Features:**
- Add buzzer for audio alerts (GPIO 6)  
- Add rotary encoder for menu navigation (GPIO 19/20)
- Add small OLED display for status (I2C)

---

This wiring is **beginner-friendly** and uses **safe low voltages**. All connections are clearly documented and tested!