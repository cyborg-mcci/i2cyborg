#include <Wire.h>

#define SlaveAddres 0x45 
#define NumReg 4    //Number of registers

int registers[NumReg]; // Array to store register values

void setup() {
  Wire.begin(SlaveAddres); // Initialize I2C communication as a slave
  Wire.onRequest(requestEvent); // Register the requestEvent function to handle incoming requests
  Wire.onReceive(receiveEvent); // Register the receiveEvent function to handle incoming data
  Serial.begin(9600); // Initialize serial communication for debugging

  // Initialize register values
  for (int i = 0; i < NumReg; i++) {
    registers[i] = 0;
  }
}

void loop() {
  // Additional code for the main loop, if needed
}

void receiveEvent(int byteCount) {
  
  if (byteCount >= 2) {
    int registerIndex = Wire.read(); // Read the register index
    int value = Wire.read(); // Read the value to be written

    if (registerIndex >= 0 && registerIndex < NumReg) {
      registers[registerIndex] = value; // Store the value in the specified register

      Serial.println();
      Serial.print("Register: ");
      Serial.println(registerIndex);
      Serial.print("Data:");
      Serial.println(value);
      Serial.println();
    }
    else {
      Serial.println("Invalid register index");
    }
  }
}

void requestEvent() {
  
  if (Wire.available()) {
    int registerIndex = Wire.read(); // Read the register index

    if (registerIndex >= 0 && registerIndex < NumReg) {
      int value = registers[registerIndex]; // Get the value from the specified register

      Serial.println();
      Serial.print("Register:");
      Serial.println(registerIndex);
      Serial.print("Read:");
      Serial.println(value);
      Serial.println();

      Wire.write(value); // Send the value back to the master

      //Wire.endTransmission();

      // Manually send ACK after read operation
      
    }
    else {
      Serial.println("Invalid register index");
    }
  }
}
