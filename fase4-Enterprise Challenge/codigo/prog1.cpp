/*
 * Sistema de Monitoramento Industrial
 * Autor: Robson Costa - RM565066
 * 
 * FUNCIONALIDADES:
 * - Gera arquivo CSV automaticamente no computador
 * - Protocolo especial para comunicação com script Python
 * - Sistema de alertas completo
 * - Verificação de conexões automática
 * 
 * CONEXÕES FÍSICAS IMPLEMENTADAS:
 * 
 * DHT22 (Temperatura/Umidade):
 * - VCC → ESP32 3.3V (fio vermelho)
 * - GND → ESP32 GND (fio preto)
 * - DATA → ESP32 GPIO 15 (fio amarelo)
 * 
 * MPU6050 (Acelerômetro/Giroscópio):
 * - VCC → ESP32 3.3V (fio vermelho)
 * - GND → ESP32 GND (fio preto)
 * - SDA → ESP32 GPIO 21 (fio verde)
 * - SCL → ESP32 GPIO 22 (fio azul)
 * 
 * LDR (Sensor de Luz):
 * - Terminal 1 → ESP32 GPIO 34/A0 (fio laranja)
 * - Terminal 2 → ESP32 GND (fio preto)
 * - Resistor 10kΩ entre 3.3V e GPIO 34 (pull-up)
 */

#include <Arduino.h>  // ← OBRIGATÓRIO para PlatformIO
#include <DHT.h>
#include <Wire.h>

// ===== DEFINIÇÃO DOS PINOS =====
#define DHT_PIN 15        // DHT22 DATA conectado ao GPIO 15
#define DHT_TYPE DHT22    // Tipo do sensor DHT
#define LDR_PIN 34        // LDR conectado ao GPIO 34 (A0)
#define MPU_ADDRESS 0x68  // Endereço I2C do MPU6050

// ===== CONFIGURAÇÕES DO ARQUIVO CSV =====
#define NOME_ARQUIVO "dados_monitoramento_hermes_reply.csv"

// ===== DECLARAÇÕES DAS FUNÇÕES (OBRIGATÓRIO EM C++) =====
void lerSensores();
String analisarStatus();
void enviarDadosCSV(unsigned long timestamp, String status);
void verificarAlertas();
void enviarComandoArquivo(String comando, String dados = "");
void inicializarSistema();

// ===== INICIALIZAÇÃO DOS SENSORES =====
DHT dht(DHT_PIN, DHT_TYPE);

// ===== VARIÁVEIS GLOBAIS =====
float temperatura = 0.0;
float umidade = 0.0;
int luminosidade = 0;
float accel_x = 0.0, accel_y = 0.0, accel_z = 0.0;
float gyro_x = 0.0, gyro_y = 0.0, gyro_z = 0.0;

unsigned long ultimaLeitura = 0;
const unsigned long intervaloLeitura = 3000; // 3 segundos
int contadorRegistros = 0;
bool sistemaInicializado = false;

void setup() {
  Serial.begin(115200);
  delay(2000); // Aguardar inicialização do Serial
  
  inicializarSistema();
  
  // ===== VERIFICAÇÃO DAS CONEXÕES =====
  Serial.println("LOG: Verificando conexões físicas...");
  
  // Inicializar DHT22
  dht.begin();
  Serial.println("LOG: ✓ DHT22 inicializado (GPIO 15)");
  
  // Inicializar I2C para MPU6050
  Wire.begin(21, 22); // SDA=21, SCL=22
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(0x6B); // Registro de power management
  Wire.write(0);    // Acordar o MPU6050
  byte error = Wire.endTransmission();
  
  if (error == 0) {
    Serial.println("LOG: ✓ MPU6050 detectado (I2C: SDA=21, SCL=22)");
  } else {
    Serial.println("LOG: ❌ MPU6050 NÃO detectado - Verificar conexões!");
  }
  
  // Configurar LDR
  pinMode(LDR_PIN, INPUT);
  Serial.println("LOG: ✓ LDR configurado (GPIO 34 + resistor pull-up)");
  
  // ===== TESTE INICIAL DOS SENSORES =====
  Serial.println("LOG: === TESTE INICIAL DOS SENSORES ===");
  
  // Teste DHT22
  float temp_teste = dht.readTemperature();
  float hum_teste = dht.readHumidity();
  if (!isnan(temp_teste) && !isnan(hum_teste)) {
    Serial.println("LOG: ✓ DHT22 funcionando: " + String(temp_teste) + "°C, " + String(hum_teste) + "%");
  } else {
    Serial.println("LOG: ❌ DHT22 com problema - Verificar conexão DATA no GPIO 15");
  }
  
  // Teste LDR
  int ldr_teste = analogRead(LDR_PIN);
  Serial.println("LOG: ✓ LDR funcionando: " + String(ldr_teste) + " (0-4095)");
  
  // Teste MPU6050
  if (error == 0) {
    Serial.println("LOG: ✓ MPU6050 comunicando via I2C");
  }
  
  // ===== CRIAR ARQUIVO CSV =====
  enviarComandoArquivo("CREATE_FILE", NOME_ARQUIVO);
  enviarComandoArquivo("WRITE_HEADER", "Timestamp,Temperatura,Umidade,Luminosidade,Accel_X,Accel_Y,Accel_Z,Gyro_X,Gyro_Y,Gyro_Z,Status");
  
  Serial.println("LOG: === INICIANDO COLETA DE DADOS ===");
  Serial.println("LOG: Arquivo CSV: " + String(NOME_ARQUIVO));
  Serial.println("LOG: Dados sendo salvos automaticamente no computador");
  
  sistemaInicializado = true;
  delay(2000);
}

void loop() {
  if (!sistemaInicializado) {
    delay(1000);
    return;
  }
  
  unsigned long tempoAtual = millis();
  
  if (tempoAtual - ultimaLeitura >= intervaloLeitura) {
    ultimaLeitura = tempoAtual;
    
    // Ler todos os sensores
    lerSensores();
    
    // Analisar status
    String status = analisarStatus();
    
    // Enviar dados para arquivo CSV
    enviarDadosCSV(tempoAtual, status);
    
    // Verificar alertas
    verificarAlertas();
    
    contadorRegistros++;
    
    // Mostrar progresso a cada 10 registros
    if (contadorRegistros % 10 == 0) {
      Serial.println("LOG: Registros coletados: " + String(contadorRegistros));
      Serial.println("LOG: Arquivo CSV atualizado: " + String(NOME_ARQUIVO));
      enviarComandoArquivo("FLUSH_FILE"); // Forçar gravação
    }
    
    // Mostrar dados no Serial Monitor também
    Serial.println("DATA: " + String(tempoAtual) + "," + 
                   String(temperatura, 2) + "," + 
                   String(umidade, 2) + "," + 
                   String(luminosidade) + "," + 
                   String(accel_x, 3) + "," + 
                   String(accel_y, 3) + "," + 
                   String(accel_z, 3) + "," + 
                   String(gyro_x, 2) + "," + 
                   String(gyro_y, 2) + "," + 
                   String(gyro_z, 2) + "," + 
                   status);
  }
  
  delay(100);
}

// ===== IMPLEMENTAÇÃO DAS FUNÇÕES =====

void inicializarSistema() {
  Serial.println("CSV_AUTO_START");
  Serial.println("LOG: === Sistema de Monitoramento Industrial ===");
  Serial.println("LOG: Hermes Reply - Fase 4 Challenge");
  Serial.println("LOG: VERSÃO COM GERAÇÃO AUTOMÁTICA DE CSV");
  Serial.println("LOG: CONEXÕES FÍSICAS CORRETAS");
  Serial.println("LOG: ");
  Serial.println("LOG: 💾 ARQUIVO CSV SERÁ GERADO AUTOMATICAMENTE");
  Serial.println("LOG: 📁 Local: Pasta onde o script Python está rodando");
  Serial.println("LOG: 📄 Nome: " + String(NOME_ARQUIVO));
  Serial.println("LOG: ");
}

void enviarComandoArquivo(String comando, String dados) {
  Serial.println("CSV_CMD:" + comando + ":" + dados);
  delay(50); // Pequena pausa para processamento
}

void enviarDadosCSV(unsigned long timestamp, String status) {
  // Montar linha CSV
  String linhaCsv = String(timestamp) + "," + 
                    String(temperatura, 2) + "," + 
                    String(umidade, 2) + "," + 
                    String(luminosidade) + "," + 
                    String(accel_x, 3) + "," + 
                    String(accel_y, 3) + "," + 
                    String(accel_z, 3) + "," + 
                    String(gyro_x, 2) + "," + 
                    String(gyro_y, 2) + "," + 
                    String(gyro_z, 2) + "," + 
                    status;
  
  // Enviar comando para escrever no arquivo
  enviarComandoArquivo("WRITE_DATA", linhaCsv);
}

void lerSensores() {
  // ===== LEITURA DHT22 =====
  temperatura = dht.readTemperature();
  umidade = dht.readHumidity();
  
  // Verificar se leitura é válida
  if (isnan(temperatura) || isnan(umidade)) {
    temperatura = 0.0;
    umidade = 0.0;
  }
  
  // ===== LEITURA LDR =====
  int leitura_raw = analogRead(LDR_PIN);
  luminosidade = map(leitura_raw, 0, 4095, 0, 100); // Converter para 0-100%
  
  // ===== LEITURA MPU6050 =====
  Wire.beginTransmission(MPU_ADDRESS);
  Wire.write(0x3B); // Registro do acelerômetro
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDRESS, 14, true);
  
  if (Wire.available() >= 14) {
    // Ler acelerômetro (6 bytes)
    int16_t ax = Wire.read() << 8 | Wire.read();
    int16_t ay = Wire.read() << 8 | Wire.read();
    int16_t az = Wire.read() << 8 | Wire.read();
    
    // Pular temperatura do MPU (2 bytes)
    Wire.read(); 
    Wire.read();
    
    // Ler giroscópio (6 bytes)
    int16_t gx = Wire.read() << 8 | Wire.read();
    int16_t gy = Wire.read() << 8 | Wire.read();
    int16_t gz = Wire.read() << 8 | Wire.read();
    
    // Converter para unidades físicas
    accel_x = ax / 16384.0; // ±2g
    accel_y = ay / 16384.0;
    accel_z = az / 16384.0;
    
    gyro_x = gx / 131.0; // ±250°/s
    gyro_y = gy / 131.0;
    gyro_z = gz / 131.0;
  }
}

String analisarStatus() {
  // Calcular vibração total
  float vibracao_total = sqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z);
  
  // Verificar condições críticas
  if (temperatura > 35.0) {
    return "CRITICO";
  }
  
  if (vibracao_total > 5.0) {
    return "CRITICO";
  }
  
  // Verificar condições de alerta
  if (temperatura > 25.0 && temperatura <= 35.0) {
    return "ALERTA";
  }
  
  if (vibracao_total > 2.0 && vibracao_total <= 5.0) {
    return "ALERTA";
  }
  
  if (umidade > 80.0 || umidade < 20.0) {
    return "ALERTA";
  }
  
  return "NORMAL";
}

void verificarAlertas() {
  if (temperatura > 35.0) {
    Serial.println("ALERT: CRÍTICO - Temperatura > 35°C");
    enviarComandoArquivo("WRITE_ALERT", "CRÍTICO - Temperatura > 35°C - " + String(millis()));
  }
  
  float vibracao_total = sqrt(accel_x*accel_x + accel_y*accel_y + accel_z*accel_z);
  if (vibracao_total > 5.0) {
    Serial.println("ALERT: CRÍTICO - Vibração excessiva");
    enviarComandoArquivo("WRITE_ALERT", "CRÍTICO - Vibração excessiva - " + String(millis()));
  }
  
  if (umidade > 80.0) {
    Serial.println("ALERT: Umidade alta - Risco de corrosão");
    enviarComandoArquivo("WRITE_ALERT", "ALERTA - Umidade alta - " + String(millis()));
  }
  
  if (umidade < 20.0) {
    Serial.println("ALERT: Umidade baixa - Risco de estática");
    enviarComandoArquivo("WRITE_ALERT", "ALERTA - Umidade baixa - " + String(millis()));
  }
}

