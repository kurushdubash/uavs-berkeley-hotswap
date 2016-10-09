/*
  UAVs@Berkeley HotSwap Project
  This module is for the hexacopter landing pad.
  Written by:
  Kurush Dubash
*/

// LEDs will be used as on-board indicators
int LED_GREEN = 7; // Set green LED pin to 7
int LED_RED = 5; // Set red LED pin to 5

// Motor is used for screwing in our battery
int CMOTOR = 10; // Set motor pins to (CMOT) 10

// intialize the state of our robot, 0 = stop
char input = 0; 

// Optional: Ultra-sonic sensor for triggering when drone is in position
int trigPin = 12; // intialize trigPin to 12 & echoPin to 11
int echoPin = 11;

void setup()
{
  Serial.println("Booting up...")
  // start the serial monitor
  Serial.begin(9600);

  // initialize LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  // intialize motors 
  pinMode(CMOTOR, OUTPUT);

  /* optional: initalize Ultra-sonic sensor*/
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  
  Serial.println("Boot complete!"); 
}


void loop() {
  // this figures out the distance the ultrasonic sees in milimeters
  long duration;
  long distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) / 2.91; //74=inches, 29.1=cm, 2.91=mm

  Serial.print("Distance: ");
  Serial.println(distance);
}
