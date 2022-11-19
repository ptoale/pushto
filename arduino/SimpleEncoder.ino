#include <QuadratureEncoder.h>
/*
Reads 2 rotary encoders and writes data every second.

The data consists of millis, count1, count2, error1, error2

N controls the write period:
N = 1000    T = 1s
N = 100     T = 100ms
N = 10      T = 10ms
N = 1       T = 1ms
*/


Encoders aziEncoder(2,4);
Encoders altEncoder(7,8);

unsigned long lastMilli = 0;
unsigned long N = 50;

void setup() {
  Serial.begin(9600);
  lastMilli = millis();
}

void loop() {
  if ((millis()-lastMilli) > N) {
    long currentAziCount = aziEncoder.getEncoderCount();
    long currentAltCount = altEncoder.getEncoderCount();
    long currentAziError = aziEncoder.getEncoderErrorCount();
    long currentAltError = altEncoder.getEncoderErrorCount();

    Serial.print(lastMilli);
    Serial.print(" ");
    Serial.print(currentAziCount);
    Serial.print(" ");
    Serial.print(currentAltCount);
    Serial.print(" ");
    Serial.print(currentAziError);
    Serial.print(" ");
    Serial.println(currentAltError);
    lastMilli = millis();
  }
}
