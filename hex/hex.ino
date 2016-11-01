#include <Stepper.h>
#include <QueueArray.h>
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
// initialize the stepper library on pins 8 through 11:
int steps_per_rev = 200;
Stepper stepper_motor(steps_per_rev, 8, 9, 10, 11); //change for actual stepper

//directions and pwm's
int treadmill_dc_dir = 0; 
int treadmill_dc_pwm = 0;
int belt_dc_dir = 0;
int belt_dc_pwm = 0;

// intialize the state of our robot
int stage = 0;

// Optional: Ultra-sonic sensor for triggering when drone is in position
int trigPin = 12; // intialize trigPin to 12 & echoPin to 11
int echoPin = 11;

//electromagnet
int emPin = 0; // change port

int SONAR_ENGAGE_DIST = 10; //mm

void setup()
{
  Serial.println("Booting up...");
  // start the serial monitor
  Serial.begin(9600);

  // initialize LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  // intialize motors 
  stepper_motor.setSpeed(60);
  pinMode(belt_dc_dir, OUTPUT);
  pinMode(treadmill_dc_dir, OUTPUT);
  pinMode(belt_dc_pwm, OUTPUT);
  pinMode(treadmill_dc_pwm, OUTPUT);
  
  /* optional: initalize Ultra-sonic sensor*/
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  //electromagnets
  pinMode(emPin, OUTPUT);
  digitalWrite(emPin, LOW);
  
  Serial.println("Boot complete!"); 

  stage = 0;
}


void loop() {
  // this figures out the distance the ultrasonic sees in milimeters
  long duration;
  double distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) / 29.1; //74=inches, 29.1=cm, 2.91=mm

  // Serial.print("Distance: ");
  // Serial.print(distance);
  // Serial.println(" cm");

  if(quadInRange(distance)){
    performSwap();
  }
  // delay(1000);
}

QueueArray <double> distances;
double SONOAR_DIST_THRESH = 16;
boolean quadInRange(int distance){
  if (distances.count() < 10){ // Not enough data stored yet
    distances.enqueue(distance);
    return false;      
  }
  distances.enqueue(distance);
  distances.dequeue();

  double tempDistances[10];
  int count = 0;
  double average = 0;
  while (count < 10){
    double value = distances.dequeue();
    average += value;
    tempDistances[count] = value; 
    count++;
  }
  average = average / 10;
  count = 0;
  while (count < 10){
    distances.enqueue(tempDistances[count]);
    count++;
  }
  if (average < SONOAR_DIST_THRESH){
    Serial.print("Quad in range...");
    Serial.print(average);
    Serial.println(" cm");
    return true;
  }
  return false; 
}

boolean quadHasLanded(){
  // Read Pressure sensor data here:
  // If pressure = quad has landed
  // return true
  return false;
}

void performSwap(){

  /* Electromagnets engage, move on when pressure sensors sense landing */
    digitalWrite(emPin, HIGH);
    delay(1000); // for now just wait a second, instead of pressure sensors
    while(!quadHasLanded());
  /* Landing happens now -- DEFINITELY */

  /* Push in stepper motor with belt_dc */
    digitalWrite(belt_dc_dir, HIGH); //clockwise
    analogWrite(belt_dc_pwm, 100); //in
    delay(500);
    analogWrite(belt_dc_pwm, 0);
  
  /* Stepper motor unscrews */
    stepper_motor.step(-2*steps_per_rev);
    delay(500);
      
  /* Push out stepper motor with belt_dc */
    digitalWrite(belt_dc_dir, LOW); //counter clockwise
    analogWrite(belt_dc_pwm, 100); //out
    delay(500);
    analogWrite(belt_dc_pwm, 0);
  /* Magazine loads new pack on treadmill */
  
  /* DC motor treadmill slide battery in */
    digitalWrite(treadmill_dc_dir, HIGH);
    analogWrite(treadmill_dc_pwm, 80); //moves treadmill
    delay(1000);
    analogWrite(treadmill_dc_pwm, 0);

  /* Push in stepper motor with belt_dc */
    digitalWrite(belt_dc_dir, HIGH); //clockwise
    analogWrite(belt_dc_pwm, 100);
    delay(500);
    analogWrite(belt_dc_pwm, 0);

  /* Stepper motor screws in */
    stepper_motor.step(2*steps_per_rev); //two rotations
    delay(500);

  /* Push out stepper motor with belt_dc */
    digitalWrite(belt_dc_dir, LOW); //counter-clockwise
    analogWrite(belt_dc_pwm, 100);
    delay(500);
    analogWrite(belt_dc_pwm, 0);

  /* Electromagnets disengage */
    digitalWrite(emPin, LOW);
  /* Take off */
}

