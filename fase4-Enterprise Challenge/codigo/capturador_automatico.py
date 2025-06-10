import serial
import csv
import time
import datetime
import sys
import os

"""
Script Python para Geração Automática de CSV
Sistema de Monitoramento Industrial - Hermes Reply

FUNCIONALIDADES:
- Cria arquivo CSV automaticamente no computador
- Interpreta comandos especiais do ESP32
- Salva dados em tempo real
- Gera alertas em arquivo separado

COMO USAR:
1. Execute este script: python capturador_automatico.py
2. Execute o código do ESP32 no Wokwi
3. O arquivo CSV será criado automaticamente
4. Pressione Ctrl+C para parar

ARQUIVOS GERADOS:
- dados_monitoramento_hermes_reply.csv (dados principais)
- alertas_sistema.txt (alertas do sistema)
"""

# ===== CONFIGURAÇÕES =====
PORTA_SERIAL = 'COM3'  # Altere para sua porta (COM3, COM4, /dev/ttyUSB0, etc.)
BAUD_RATE = 115200
PASTA_DESTINO = os.getcwd()  # Pasta atual

# ===== VARIÁVEIS GLOBAIS =====
arquivo_csv_atual = None
writer_csv = None
arquivo_alertas = None

def processar_comando_csv(comando, dados=""):
    """Processa comandos CSV enviados pelo ESP32"""
    global arquivo_csv_atual, writer_csv, arquivo_alertas
    
    try:
        if comando == "CREATE_FILE":
            # Criar arquivo CSV
            caminho_arquivo = os.path.join(PASTA_DESTINO, dados)
            arquivo_csv_atual = open(caminho_arquivo, 'w', newline='', encoding='utf-8')
            writer_csv = csv.writer(arquivo_csv_atual)
            
            # Criar arquivo de alertas
            nome_alertas = dados.replace('.csv', '_alertas.txt')
            caminho_alertas = os.path.join(PASTA_DESTINO, nome_alertas)
            arquivo_alertas = open(caminho_alertas, 'w', encoding='utf-8')
            arquivo_alertas.write(f"=== ALERTAS DO SISTEMA - {datetime.datetime.now()} ===\n\n")
            arquivo_alertas.flush()
            
            print(f"✅ Arquivo CSV criado: {caminho_arquivo}")
            print(f"✅ Arquivo de alertas criado: {caminho_alertas}")
            
        elif comando == "WRITE_HEADER":
            # Escrever cabeçalho
            if writer_csv:
                colunas = dados.split(',')
                writer_csv.writerow(colunas)
                arquivo_csv_atual.flush()
                print(f"📋 Cabeçalho CSV escrito: {len(colunas)} colunas")
                
        elif comando == "WRITE_DATA":
            # Escrever dados
            if writer_csv:
                linha_dados = dados.split(',')
                writer_csv.writerow(linha_dados)
                arquivo_csv_atual.flush()
                
                # Mostrar progresso
                timestamp = linha_dados[0] if linha_dados else "N/A"
                temp = linha_dados[1] if len(linha_dados) > 1 else "N/A"
                status = linha_dados[-1] if linha_dados else "N/A"
                print(f"📊 Dados salvos: {timestamp}ms | {temp}°C | Status: {status}")
                
        elif comando == "WRITE_ALERT":
            # Escrever alerta
            if arquivo_alertas:
                timestamp_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                arquivo_alertas.write(f"[{timestamp_atual}] {dados}\n")
                arquivo_alertas.flush()
                print(f"🚨 ALERTA REGISTRADO: {dados}")
                
        elif comando == "FLUSH_FILE":
            # Forçar gravação
            if arquivo_csv_atual:
                arquivo_csv_atual.flush()
            if arquivo_alertas:
                arquivo_alertas.flush()
            print("💾 Arquivos sincronizados com disco")
            
    except Exception as e:
        print(f"❌ Erro ao processar comando {comando}: {e}")

def main():
    print("=== Capturador Automático de CSV - Hermes Reply ===")
    print(f"📁 Pasta de destino: {PASTA_DESTINO}")
    print(f"🔌 Porta serial: {PORTA_SERIAL}")
    print("🚀 Aguardando conexão com ESP32...")
    print("⏹️  Pressione Ctrl+C para parar\n")
    
    try:
        # Conectar à porta serial
        ser = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
        time.sleep(2)  # Aguardar conexão
        
        print("✅ Conectado! Aguardando dados do ESP32...\n")
        registros_salvos = 0
        sistema_iniciado = False
        
        while True:
            try:
                # Ler linha da serial
                linha = ser.readline().decode('utf-8').strip()
                
                if linha:
                    # Verificar início do sistema
                    if linha == "CSV_AUTO_START":
                        sistema_iniciado = True
                        print("🎯 Sistema ESP32 detectado e inicializado!")
                        continue
                    
                    # Processar comandos CSV
                    if linha.startswith("CSV_CMD:"):
                        partes = linha[8:].split(':', 2)  # Remove "CSV_CMD:"
                        comando = partes[0]
                        dados = partes[1] if len(partes) > 1 else ""
                        processar_comando_csv(comando, dados)
                        
                    # Mostrar logs do sistema
                    elif linha.startswith("LOG:"):
                        print(f"ℹ️  {linha[4:].strip()}")
                        
                    # Mostrar dados em tempo real
                    elif linha.startswith("DATA:"):
                        registros_salvos += 1
                        if registros_salvos % 5 == 0:  # Mostrar a cada 5 registros
                            print(f"📈 Total de registros salvos: {registros_salvos}")
                            
                    # Mostrar alertas
                    elif linha.startswith("ALERT:"):
                        print(f"🚨 {linha[6:].strip()}")
                        
            except UnicodeDecodeError:
                # Ignorar erros de decodificação
                pass
                
    except serial.SerialException as e:
        print(f"❌ Erro na porta serial: {e}")
        print(f"💡 Verifique se a porta {PORTA_SERIAL} está correta")
        print("💡 Portas comuns: COM3, COM4 (Windows) ou /dev/ttyUSB0 (Linux)")
        
    except KeyboardInterrupt:
        print(f"\n✅ Captura interrompida pelo usuário")
        print(f"📊 Total de registros salvos: {registros_salvos}")
        
        # Listar arquivos gerados
        print("\n📁 Arquivos gerados:")
        for arquivo in os.listdir(PASTA_DESTINO):
            if arquivo.startswith("dados_monitoramento") and (arquivo.endswith(".csv") or arquivo.endswith("_alertas.txt")):
                caminho_completo = os.path.join(PASTA_DESTINO, arquivo)
                tamanho = os.path.getsize(caminho_completo)
                print(f"   📄 {arquivo} ({tamanho} bytes)")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    finally:
        # Fechar arquivos
        try:
            if arquivo_csv_atual:
                arquivo_csv_atual.close()
            if arquivo_alertas:
                arquivo_alertas.close()
            ser.close()
        except:
            pass

if __name__ == "__main__":
    # Verificar se pyserial está instalado
    try:
        import serial
    except ImportError:
        print("❌ Biblioteca 'pyserial' não encontrada")
        print("💡 Instale com: pip install pyserial")
        sys.exit(1)
    
    main()

