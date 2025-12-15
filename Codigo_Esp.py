#include <WiFi.h>
#include "AdafruitIO_WiFi.h"

// ===================== CONFIGURAÇÃO WIFI =====================
#define WIFI_SSID   "RADIOMETRIA"
#define WIFI_PASS   "password"

// ===================== CONFIGURAÇÃO ADAFRUIT IO =====================
#define IO_USERNAME "valdemir669"
#define IO_KEY      "aio_VsCU172taTIoVIMHTgLD1cXhq3cx"

// ===================== PINOS DOS RELÉS =====================
int reles[4] = {22, 18, 19, 21};  // IN1, IN2, IN3, IN4

// ===================== FEEDS ADAFRUIT IO =====================
AdafruitIO_WiFi io(IO_USERNAME, IO_KEY, WIFI_SSID, WIFI_PASS);

AdafruitIO_Feed *lamp1 = io.feed("lampada-1");
AdafruitIO_Feed *lamp2 = io.feed("lampada-2");
AdafruitIO_Feed *lamp3 = io.feed("lampada-3");
AdafruitIO_Feed *lamp4 = io.feed("lampada-4");
AdafruitIO_Feed *lampTodas = io.feed("lampadas-todas");

// ===================== FUNÇÃO PARA LIGAR/DESLIGAR =====================
void controlaLampada(int idx, int valor){
  digitalWrite(reles[idx], valor == 1 ? LOW : HIGH);  // LOW = ligado, HIGH = desligado
  Serial.printf("Lampada %d -> %s\n", idx+1, valor ? "LIGADA" : "DESLIGADA");
}

// ===================== CALLBACKS ADAFRUIT =====================
void handleLamp1(AdafruitIO_Data *data){ controlaLampada(0, data->toInt()); }
void handleLamp2(AdafruitIO_Data *data){ controlaLampada(1, data->toInt()); }
void handleLamp3(AdafruitIO_Data *data){ controlaLampada(2, data->toInt()); }
void handleLamp4(AdafruitIO_Data *data){ controlaLampada(3, data->toInt()); }

void handleLampTodas(AdafruitIO_Data *data){
  int valor = data->toInt();
  for(int i=0;i<4;i++){
    controlaLampada(i, valor);
  }
}

// ===================== SETUP =====================
void setup(){
  Serial.begin(115200);

  // Configura os relés
  for(int i=0;i<4;i++){
    pinMode(reles[i], OUTPUT);
    digitalWrite(reles[i], HIGH); // começa desligado
  }

  Serial.println("Conectando ao Adafruit IO...");

  io.connect();

  lamp1->onMessage(handleLamp1);
  lamp2->onMessage(handleLamp2);
  lamp3->onMessage(handleLamp3);
  lamp4->onMessage(handleLamp4);
  lampTodas->onMessage(handleLampTodas);

  // Aguarda conexão com timeout
  unsigned long startTime = millis();
  while(io.status() < AIO_CONNECTED){
    Serial.print(".");
    delay(500);
    if(WiFi.status() != WL_CONNECTED){
      Serial.println("Wi-Fi não conectado, tentando...");
    }
    if(millis() - startTime > 15000){ // 15 segundos de timeout
      Serial.println("Erro: Não conectou ao Adafruit IO.");
      break;
    }
  }

  if(io.status() == AIO_CONNECTED){
    Serial.println("\nConectado ao Adafruit IO!");
    // Pega o último estado salvo na nuvem
    lamp1->get();
    lamp2->get();
    lamp3->get();
    lamp4->get();
    lampTodas->get();
  }
}

// ===================== LOOP =====================
void loop(){
  io.run(); // mantém a conexão com a nuvem ativa
}
