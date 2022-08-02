#include <AccelStepper.h>
#define dirPin 8
#define stepPin 9
#define motorInterfaceType 1
// Create a new instance of the AccelStepper class:
AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);
char serialData;


void setup() {
  Serial.begin(9600);
  pinMode(7, OUTPUT);
  stepper.setMaxSpeed(200);
  stepper.setAcceleration(100);
  digitalWrite(7, HIGH);
}
void loop() 
{
  if(Serial.available() > 0)
  {
    serialData = Serial.read();
    Serial.print(serialData);
  }
  if(serialData == '1')
  {
    delay(5000);
    stepper.moveTo(4800);
    stepper.runToPosition();
  }
  else if(serialData == '0')
  {
    delay(1000);
    stepper.moveTo(0);
    stepper.runToPosition();
    delay(500);
  }
  else if(serialData == '2')
  {
    delay(500);
    digitalWrite(7, LOW);
  }
  else if(serialData == '3')
  {
    delay(500);
    digitalWrite(7,HIGH);
  }
}
