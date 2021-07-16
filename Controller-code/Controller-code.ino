#include <stdlib.h>
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <ESP8266WebServer.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

ESP8266WebServer server(80);

Adafruit_PWMServoDriver pwm1 = Adafruit_PWMServoDriver();




void direct_control();
void zone(Adafruit_PWMServoDriver);
void handleNotFound();




void setup() 
{
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.begin(9600);   // Serial comm

  for(int i=0; i<=50;i++)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
    delay(50);
  }
  
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());
  
  WiFi.begin("SSID", "password");                 // Connecting to wifi
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)           // Waiting for connection
  {   
    delay(400);
    digitalWrite(LED_BUILTIN, LOW);
    Serial.print(".");
    delay(50);
    digitalWrite(LED_BUILTIN, HIGH);
  }

  digitalWrite(LED_BUILTIN, LOW);
  Serial.print(" Connection established. IP address: ");  
  Serial.println(WiFi.localIP());

  if (MDNS.begin("esp8266"))                        // Start the mDNS responder for esp8266.local
  {
    Serial.println("mDNS responder started");
  } 
  else
  {
    Serial.println("Error setting up MDNS responder!");
  }

  
  server.on("/direct", HTTP_POST, direct_control);  // Call direct_control() after receiving a POST request on localhost/direct
  server.onNotFound(handleNotFound);                // Call handleNotFound() after receiving a request on an unknown URL
  
  pwm1.begin();
  pwm1.setPWMFreq(400);


  server.begin();
  Serial.println("HTTP server started.");
  delay(5000);
  digitalWrite(LED_BUILTIN, HIGH);
}




void loop()
{
  server.handleClient();
  
  /*
  pwm.setPWM(15, 0, PWMValue);

  PWMValue*=pow(2, 0.05);

  if(PWMValue>=4095)
    PWMValue=50;

  delay(30);
  */
}




void direct_control()
{
  Serial.println("Received direct control request");
  if (server.arg("pwm") == "1")     //add else if after adding another PCA PWM controller,
    if (server.hasArg("0"))
      zone(pwm1, 0);
    else if (server.hasArg("5"))
      zone(pwm1, 5);
    else if (server.hasArg("10"))
      zone(pwm1, 10);
    else
      server.send(400, "text/plain", "Invalid channel");
  else
  {
    server.send(400, "text/plain", "Invalid board");
    Serial.println("Responded: 400");
  }
}

void zone(Adafruit_PWMServoDriver pwm, int num)      // arguments: which board and with which channel the request starts (which zone - 0,5,10)
{
  digitalWrite(LED_BUILTIN, LOW);
  int temp;
  for(int i=num; i<num+5; i++)
  {
    temp = server.arg(String(i)).toInt();
    pwm.setPWM(i, 0, temp);
    //Serial.print(i);
    //Serial.print(": ");
    //Serial.println(temp);
  }
  server.send(200, "text/plain", "OK");
  Serial.println("Responded: 200");
  digitalWrite(LED_BUILTIN, HIGH);
}

void handleNotFound()
{
  server.send(404, "text/plain", "404: Not found");
  Serial.println("Responded: 404");
}
