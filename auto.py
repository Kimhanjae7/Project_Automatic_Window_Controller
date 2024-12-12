#include <Servo.h>

// 핀 정의
#define WATER_LEVEL_PIN A2   // 수위 센서 핀 (아날로그 핀 2)
#define SERVO_PIN 9          // 서보 모터 핀
#define GAS_PIN A0           // 가스 감지 핀 (아날로그 핀 0)

Servo motor; // 서보 모터 객체 생성

// 주요 변수 초기화
int motorAngle = 0;          // 현재 서보 모터 각도
int targetAngle = 0;         // 목표 각도
unsigned long lastLevelCheckTime = 0; // 마지막 센서 확인 시간
const unsigned long levelCheckInterval = 2000; // 센서 확인 주기 (2초)
String mode = "auto";        // 초기 모드는 AUTO
bool isServoMoving = false;  // 서보 모터 이동 상태

void setup() {
  motor.attach(SERVO_PIN, 600, 2400); // 서보 모터 초기화 (펄스 폭 범위 설정)
  motor.write(motorAngle);           // 초기 각도를 0도로 설정
  pinMode(GAS_PIN, INPUT);           // 가스 센서 핀을 입력 모드로 설정
  Serial.begin(9600);                // Serial 통신 시작

  // 초기화 메시지 출력
  Serial.println("Starting system...");
  Serial.println("Enter 'auto' for automatic mode or 'manual' for manual mode:");
}

void loop() {
  // Serial 입력 확인
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n'); // 줄바꿈까지 입력 받기
    input.trim(); // 입력 값의 앞뒤 공백 제거
    handleInput(input); // 입력 처리
  }

  // 현재 모드에 따른 동작 수행
  if (mode == "auto" && !isServoMoving) {
    autoMode(); // AUTO 모드에서 자동 제어 수행
  }

  // 서보 모터 이동 처리
  if (isServoMoving) {
    moveServoStep(); // 목표 각도까지 이동 수행
  }
}

// 사용자 입력 처리 함수
void handleInput(String input) {
  if (input == "auto") {
    mode = "auto"; // AUTO 모드로 전환
    Serial.println("Switched to AUTO mode.");
  } else if (input == "manual") {
    mode = "manual"; // MANUAL 모드로 전환
    Serial.println("Switched to MANUAL mode. Enter 'open' or 'close':");
  } else if (mode == "manual") {
    if (input == "open") {
      setTargetAngle(180); // 서보를 180도로 이동
      Serial.println("Servo opened (180 degrees).");
    } else if (input == "close") {
      setTargetAngle(0); // 서보를 0도로 이동
      Serial.println("Servo closed (0 degrees).");
    } else {
      Serial.println("Invalid command in MANUAL mode. Use 'open' or 'close'.");
    }
  } else {
    Serial.println("Invalid input. Use 'auto' or 'manual'.");
  }
}

// AUTO 모드 동작 함수
void autoMode() {
  if (millis() - lastLevelCheckTime >= levelCheckInterval) { // 2초마다 센서 값 확인
    lastLevelCheckTime = millis(); // 마지막 확인 시간 갱신

    int waterLevel = analogRead(WATER_LEVEL_PIN); // 수위 센서 값 읽기
    int gasLevel = analogRead(GAS_PIN);          // 가스 센서 값 읽기

    // 센서 값 Serial 출력
    Serial.print("\uC218\uC704\uC13C\uC11C \uCE21\uC815\uAC12: ");
    Serial.println(waterLevel);
    Serial.print("\uAC00\uC2A4\uC13C\uC11C \uCE21\uC815\uAC12: ");
    Serial.println(gasLevel);

    // 우선순위에 따른 동작 결정
    if (gasLevel >= 40) {
      setTargetAngle(180); // 가스 감지 시 창문 열기
      Serial.println("High gas level detected! Opening window.");
    } else {
      if (waterLevel >= 500) {
        setTargetAngle(0); // 수위 높을 때 창문 닫기
        Serial.println("High water level detected! Closing window.");
      } else {
        setTargetAngle(180); // 수위 낮을 때 창문 열기
        Serial.println("Low water level detected! Opening window.");
      }
    }
  }
}

// 서보 모터 목표 각도 설정 함수
void setTargetAngle(int angle) {
  if (targetAngle != angle) { // 목표 각도가 변경된 경우에만 동작
    targetAngle = angle;
    isServoMoving = true; // 이동 상태 시작
  }
}

// 서보 모터 이동 함수 (단계적 이동)
void moveServoStep() {
  if (motorAngle < targetAngle) {
    motorAngle++; // 목표 각도보다 작으면 증가
  } else if (motorAngle > targetAngle) {
    motorAngle--; // 목표 각도보다 크면 감소
  } else {
    isServoMoving = false; // 목표 각도에 도달 시 이동 종료
    Serial.print("Servo reached target angle: ");
    Serial.println(motorAngle);
    return;
  }
  motor.write(motorAngle); // 서보 모터에 현재 각도 전달
  delay(15); // 부드러운 동작을 위한 딜레이
}
