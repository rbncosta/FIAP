# Sistema de Rastreabilidade Agrícola

![GitHub](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.7%2B-blue) ![Oracle](https://img.shields.io/badge/database-Oracle-red) ![Status](https://img.shields.io/badge/status-active-success)

## Visão Geral
Sistema completo para gestão da cadeia produtiva agrícola com rastreabilidade desde o produtor até o transporte final dos produtos, garantindo transparência e conformidade.

## Funcionalidades
### Cadastros
- **Produtores**: Cadastro completo de fazendas/produtores
- **Plantios**: Registro de culturas agrícolas
- **Insumos**: Controle de insumos utilizados
- **Certificações**: Gestão de certificações
- **Transportes**: Rastreamento logístico

### Consultas
- Listagem completa de cadastros
- Consulta por código de rastreio
- Exportação para JSON

### Administração
- Exclusão seletiva de registros
- Limpeza total do banco (com confirmação)

## Tecnologias
- **Python 3.7+**
- **Oracle Database**
- Bibliotecas:
  - `oracledb` (conexão Oracle)
  - `python-dotenv` (gerenciamento de variáveis)
  - `logging` (registro de operações)

## Instalação
1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/rastreabilidade-agricola.git
cd rastreabilidade-agricola
Crie e ative ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Instale dependências:

```bash
pip install -r requirements.txt
Configuração
Crie um arquivo .env na raiz com:

ini
DB_HOST=localhost
DB_PORT=1521
SERVICE_NAME=ORCL
DB_USER=usuario
DB_PASSWORD=senha
Como Usar
Execute o sistema:

```bash
python sistema_rastreabilidade.py
Menu principal oferece:

Cadastros (produtores, plantios, insumos, etc.)

Consultas

Administração

Estrutura do Banco
Principais tabelas:

PRODUTORES (dados dos produtores)

PLANTIOS (informações de culturas)

INSUMOS (materiais utilizados)

CERTIFICACOES (certificações obtidas)

TRANSPORTE (dados logísticos)

Validações
Implementadas para:

CNPJ (formato XX.XXX.XXX/XXXX-XX)

Telefone ((XX) XXXX-XXXX)

E-mail (padrão RFC 5322)

Datas (DD/MM/AAAA)

Números positivos

Exemplos
Cadastro de Produtor
python
Nome da Fazenda: Fazenda Esperança
CNPJ: 12.345.678/0001-99
Localização: São Paulo/SP
Área: 150.5 hectares
Saída JSON
json
{
  "id_rastreio": "SP2023SOJA001",
  "produtor": "Fazenda Esperança",
  "cultura": "Soja",
  "data_plantio": "2023-03-15"
}
Licença
MIT - Veja LICENSE para detalhes.

Contato
Desenvolvido por [Seu Nome] - contato@exemplo.com
Repositório: github.com/seu-usuario/rastreabilidade-agricola

📌 Atualizado em: 20/04/2025
