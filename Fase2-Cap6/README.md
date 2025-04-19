Sistema de Rastreabilidade Agrícola
GitHub
Python
Oracle
Status

📑 Índice
🔍 Visão Geral

✨ Funcionalidades

🛠️ Tecnologias

📥 Instalação

⚙️ Configuração

🚀 Como Usar

🗃️ Estrutura do Banco

🔒 Validações

📋 Exemplos

📄 Licença

🔍 Visão Geral
Sistema completo para gestão da cadeia produtiva agrícola com rastreabilidade desde o produtor até o transporte final dos produtos, garantindo transparência e conformidade com regulamentações.

✨ Funcionalidades
🏷️ Cadastros
Módulo	Descrição
Produtores	Cadastro completo de fazendas
Plantios	Registro de culturas e plantações
Insumos	Controle de insumos utilizados
Certificações	Gestão de certificações obtidas
Transportes	Rastreamento de logística
🔎 Consultas
Listagem completa de todos os cadastros

Consulta detalhada por código de rastreio

Exportação de dados para JSON

⚠️ Administração
Exclusão seletiva de registros

Limpeza total do banco (com múltiplas confirmações)

Reset de sequências de IDs

🛠️ Tecnologias
Linguagem Principal:

Python 3.7+

Banco de Dados:

Oracle Database

Bibliotecas:

python
oracledb==1.0.0
python-dotenv==0.19.0
Ferramentas:

Logging nativo para auditoria

JSON para exportação de dados

📥 Instalação
Clone o repositório:

bash
git clone https://github.com/seu-usuario/rastreabilidade-agricola.git
cd rastreabilidade-agricola
Crie um ambiente virtual (recomendado):

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
Instale as dependências:

bash
pip install -r requirements.txt
⚙️ Configuração
Crie um arquivo .env na raiz do projeto:

ini
DB_HOST=seu_servidor_oracle
DB_PORT=1521
SERVICE_NAME=ORCL
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
Configuração opcional:

Edite logging.ini para ajustar níveis de log

Configure config.json para parâmetros adicionais

🚀 Como Usar
Iniciando o sistema:

bash
python sistema_rastreabilidade.py
Fluxo típico:

Cadastre um produtor

Adicione plantios associados

Registre insumos utilizados

Inclua certificações

Cadastre transportes

Consulte a rastreabilidade completa

Comandos disponíveis:

text
1 - Cadastrar Produtor
2 - Cadastrar Plantio
3 - Cadastrar Insumo
4 - Cadastrar Certificação
5 - Cadastrar Transporte
6 - Listar Cadastros
7 - Excluir Registros
8 - Limpar Banco (CUIDADO!)
9 - Consultar Rastreabilidade
0 - Sair
🗃️ Estrutura do Banco
Diagrama Relacional
Diagram
Code









Esquema Completo
sql
CREATE TABLE PRODUTORES (
    id_produtor NUMBER PRIMARY KEY,
    nome_fazenda VARCHAR2(100) NOT NULL,
    cnpj VARCHAR2(18) UNIQUE,
    localizacao VARCHAR2(100) NOT NULL,
    area_hectares NUMBER,
    telefone VARCHAR2(15),
    email VARCHAR2(100),
    biografia VARCHAR2(400),
    data_cadastro DATE DEFAULT SYSDATE
);
-- Demais tabelas disponíveis na documentação técnica
🔒 Validações
Tipos de Validação
Dados Obrigatórios

Campos marcados como NOT NULL

Validação programática

Formatos Específicos

python
# CNPJ
r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$'

# Telefone
r'^\(\d{2}\) \d{4,5}-\d{4}$'

# Email
r'^[\w.-]+@[\w.-]+\.\w+$'
Intervalos Válidos

Datas: DD/MM/AAAA entre 1900-2100

Números: Positivos com limites específicos

📋 Exemplos
Cadastro de Produtor
python
>>> Nome da Fazenda: Fazenda Verde
>>> CNPJ: 12.345.678/0001-99
>>> Localização: Minas Gerais/MG
>>> Área (hectares): 350.25
✅ Produtor cadastrado com sucesso! ID: 42
Saída de Consulta
json
{
  "id_rastreio": "MG2023CAFE001",
  "produtor": "Fazenda Verde",
  "cultura": "Café Arábica",
  "data_plantio": "2023-03-15",
  "certificacoes": ["Orgânico", "Fair Trade"],
  "transportes": [
    {
      "data": "2023-08-20",
      "destino": "São Paulo/SP",
      "emissao_co2": 150.5
    }
  ]
}
📄 Licença
Este projeto está licenciado sob a licença MIT. Consulte o arquivo LICENSE para detalhes completos.

text
Copyright 2025 Seu Nome

Permissão é concedida, gratuitamente, a qualquer pessoa que obtenha uma cópia
deste software e arquivos de documentação associados (o "Software"), para lidar
no Software sem restrição, incluindo, sem limitação, os direitos de usar, copiar,
modificar, mesclar, publicar, distribuir, sublicenciar e/ou vender cópias do
Software, e para permitir que as pessoas a quem o Software é fornecido o façam...
📧 Contato
Para suporte ou contribuições:

Email: contato@rastreabilidadeagricola.com

Repositório: github.com/seu-usuario/rastreabilidade-agricola

Documentação Completa: docs.rastreabilidadeagricola.com