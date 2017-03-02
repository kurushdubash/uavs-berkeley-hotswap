  #include <Stepper.h>
#include <QueueArray.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"
/*
  UAVs@Berkeley HotSwap Project
  This module is for the hexacopter landing pad.
*/

// MOTOR SHIELD (1)
Adafruit_MotorShield AFMS_bottom(0x60);
Adafruit_MotorShield AFMS_top(0x61);


// LEDs will be used as on-board indicators
int LED_GREEN = 7; // Set green LED pin to 7
int LED_RED = 5; // Set red LED pin to 5

// Motor is used for screwing in our battery
int steps_per_rev = 200;
Adafruit_StepperMotor *stepper;
Adafruit_DCMotor *treadmill_dc;
Adafruit_DCMotor *belt_dc;
Adafruit_DCMotor *battery_mover_dc;

//directions and pwm's
int treadmill_dc_dir = 0;
int treadmill_dc_pwm = 0;
int belt_dc_dir = 0;
int belt_dc_pwm = 0;

//initializing the speed at which each motor will run
int treadmill_dc_speed = 100;
int belt_dc_speed = 100;
int battery_mover_dc_speed = 100;

// Ultra-sonic sensor for triggering when drone is in position
int trigPin = 11; // intialize trig Pin to 12 & echoPin to 11
int echoPin = 12;

// electromagnet
int emPin = 8; 

//speed constants
int STEPPER_UNSCREW_SPEED = 200;
int BELT_MOVE_SPEED = 100;
int TREADMILL_SPEED = 100;

//time constants
int LANDING_DELAY = 1000;
int BELT_MOVE_TIME = 1000;
int TREADMILL_WAIT_TIME = 2000;
int SCREW_DELAY = 1000;
int POST_SWAP_DELAY = 10000;

QueueArray <double> distances;
double SONAR_DIST_THRESH = 3.0;

void setup()
{
  
  // intialize motors 
  AFMS_bottom.begin();
  AFMS_top.begin();
  stepper = AFMS_bottom.getStepper(768, 2);
  stepper->setSpeed(STEPPER_UNSCREW_SPEED);
  treadmill_dc = AFMS_bottom.getMotor(1);
  belt_dc = AFMS_bottom.getMotor(2);
  battery_mover_dc = AFMS_top.getMotor(1);

  //set motors to run at their corresponding speeds
  treadmill_dc->setSpeed(treadmill_dc_speed);
  belt_dc->setSpeed(belt_dc_speed);
  battery_mover_dc->setSpeed(battery_mover_dc_speed);
  
  Serial.print("Booting up...");
  // start the serial monitor
  Serial.begin(9600);

  // initialize LEDs
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_RED, OUTPUT);

//  pinMode(belt_dc_dir, OUTPUT);
//  pinMode(treadmill_dc_dir, OUTPUT);
//  pinMode(belt_dc_pwm, OUTPUT);
//  pinMode(treadmill_dc_pwm, OUTPUT);
//  
  // initalize Ultra-sonic sensor
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // electromagnets
  pinMode(emPin, OUTPUT);
  digitalWrite(emPin, LOW);
  
  Serial.println("BOOT COMPLETE."); 
  Serial.print("Looking for quad...");

//  performSwap();
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

  
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if(quadInRange(distance)){
    performSwap();
  }
  else{
    digitalWrite(emPin, LOW);
  }
  
}

boolean quadInRange(int distance){
  if (distances.count() < 15){ // Not enough data stored yet
    distances.enqueue(distance);
    return false;      
  }
  distances.enqueue(distance); // Store new distance
  distances.dequeue(); // Pop oldest item

  double tempDistances[15];
  int count = 0;
  double average = 0;
  while (count < 15){ // Calculate average
    double value = distances.dequeue();
    average += value;
    tempDistances[count] = value; 
    count++;
  }
  average = average / 15.0;
  count = 0;
  while (count < 15){ // Store items again
    distances.enqueue(tempDistances[count]);
    count++;
  }
  
  if (average < SONAR_DIST_THRESH){
    Serial.print("QUAD IN RANGE. ");
    Serial.print(average);
    Serial.println(" cm");
    return true;
  }
  return false; 
}

boolean quadHasLanded(){
  // Read Pressure sensor data here:
  // If pressure = quad has landed
  Serial.println("LANDED.");
  // return true
  return true;
}

void performSwap(){

  /* Electromagnets engage, move on when pressure sensors sense landing */
    Serial.print("Turning on electro magnets...");
    digitalWrite(emPin, HIGH);
    Serial.println("ON.");
    Serial.print("Waiting for quad to land...");
//    while(!quadHasLanded());
    delay(LANDING_DELAY);
  /* Landing happens now -- DEFINITELY */

  /* Push in stepper motor with belt_dc */
    Serial.print("Pushing in stepper motor...");
//    digitalWrite(belt_dc_dir, HIGH); //clockwise
//    analogWrite(belt_dc_pwm, BELT_MOVE_SPEED); //in
    belt_dc->run(FORWARD);
    delay(BELT_MOVE_TIME);
//    analogWrite(belt_dc_pwm, 0);
    belt_dc->run(RELEASE);
    Serial.println("PUSHED.");
  
  /* Stepper motor unscrews */
    Serial.print("Unscrewing...");
    stepper->step(2*steps_per_rev, BACKWARD, DOUBLE);
    delay(SCREW_DELAY);
    Serial.println("UNSCREWED.");
      
  /* Push out stepper motor with belt_dc */
    Serial.print("Pushing out stepper motor...");
//    digitalWrite(belt_dc_dir, LOW); //counter clockwise
//    analogWrite(belt_dc_pwm, BELT_MOVE_SPEED); //out
    belt_dc->run(BACKWARD);
    delay(BELT_MOVE_TIME);
//    analogWrite(belt_dc_pwm, 0);
    belt_dc->run(RELEASE);
    Serial.println("ON.");

  /* Magazine loads new pack on treadmill */
  
  /* DC motor treadmill slide battery in */
    Serial.print("Sliding in battery...");
//    digitalWrite(treadmill_dc_dir, HIGH);
//    analogWrite(treadmill_dc_pwm, TREADMILL_SPEED); //moves treadmill
    treadmill_dc->run(FORWARD);
    delay(TREADMILL_WAIT_TIME);
//    analogWrite(treadmill_dc_pwm, 0);
    treadmill_dc->run(RELEASE);
    Serial.println("IN.");

  /* Push in stepper motor with belt_dc */
    Serial.print("Push in stepper motor...");
//    digitalWrite(belt_dc_dir, HIGH); //clockwise
//    analogWrite(belt_dc_pwm, BELT_MOVE_SPEED);
    belt_dc->run(FORWARD);
    delay(BELT_MOVE_TIME);
//    analogWrite(belt_dc_pwm, 0);
    belt_dc->run(RELEASE);
    Serial.println("PUSHED.");

  /* Stepper motor screws in */
    Serial.print("Screwing in...");
    stepper->step(2*steps_per_rev, FORWARD, DOUBLE); //two rotations
    delay(SCREW_DELAY);
    Serial.println("IN.");

  /* Push out stepper motor with belt_dc */
    Serial.print("Pushing out stepper motor...");
//    digitalWrite(belt_dc_dir, LOW); //counter-clockwise
//    analogWrite(belt_dc_pwm, BELT_MOVE_SPEED);
    belt_dc->run(BACKWARD);
    delay(BELT_MOVE_TIME);
//    analogWrite(belt_dc_pwm, 0);
    belt_dc->run(RELEASE);
    Serial.println("OUT.");

  /* Electromagnets disengage */
    Serial.print("Turning off electro magnets...");
    digitalWrite(emPin, LOW);

    battery_mover_dc->run(FORWARD);
    delay(1000);
    battery_mover_dc->run(RELEASE);
    
    Serial.println("OFF.");
    delay(POST_SWAP_DELAY); // Sleep 10 seconds to start our search
    Serial.print("Looking for quad..."); // Restart our loop
  /* Take off */
}
