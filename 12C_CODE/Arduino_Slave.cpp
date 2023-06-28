#include <Wire.h>

#define SLAVE_ADDRESS 0x45 // Choose an appropriate slave address
unsigned int addr, data, reg0, reg1, reg2, reg3;

void setup() {
Wire.begin(SLAVE_ADDRESS); // Initialize I2C communication as a slave
Wire.onRequest(requestEvent); // Register the requestEvent function to handle incoming requests
Wire.onReceive(receiveEvent); // Register the receiveEvent function to handle incoming data
Serial.begin(9600); // Initialize serial communication for debugging
}

void loop() {
// Additional code for the main loop, if needed
}

void receiveEvent(int byteCount) {
// Handle incoming I2C data from the master
// This function will be called when the master sends data to the slave
// You can read the received data using the Wire.read() function
addr = Wire.read();
data = Wire.read();

Serial.print("Sub-Address:");
Serial.println(addr);

Serial.print("Data: ");
Serial.println(data);


switch(addr) {
case 0 :
reg0 = data;
Serial.println(reg0, HEX);
break;

case 1 :
reg1 = data;
Serial.println(reg1, HEX);

break;

case 2 :
reg2 = data;
Serial.println(reg2, HEX);
break;

case 3 :
reg3 = data;
Serial.println(reg3, HEX);
break;

default:
Serial.println("Invalid Address");
break;

}
Serial.println();
//Serial.println(x, HEX);
//Serial.println(Wire.read());
}

void requestEvent() {
// Handle I2C requests from the master
// This function will be called when the master requests data from the slave
// You can send data back to the master using the Wire.write() function
Wire.write(data);
}