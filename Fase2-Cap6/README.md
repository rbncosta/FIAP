# Sistema de Rastreabilidade Agrícola

![GitHub](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.7%2B-blue)

Sistema completo para gestão da cadeia produtiva agrícola, com rastreabilidade desde o produtor até o transporte dos produtos.

## 📌 Funcionalidades

- ✅ Cadastro completo da cadeia produtiva
- ✅ Validação rigorosa de dados de entrada
- ✅ Geração de relatórios de rastreabilidade
- ✅ Interface intuitiva baseada em menus console
- ✅ Integração com banco de dados Oracle
- ✅ Logging detalhado de operações
- ✅ Exportação de consultas em JSON

## 🗃️ Módulos Principais

### 1. Cadastros
- **Produtores**: Cadastro de fazendas/produtores rurais
- **Plantios**: Registro de culturas e plantações
- **Insumos**: Controle de insumos agrícolas utilizados
- **Certificações**: Gestão de certificações obtidas
- **Transportes**: Rastreamento de transporte de produtos

### 2. Consultas
- Listagem completa de cadastros
- Consulta de rastreabilidade por ID
- Exportação de dados para JSON

### 3. Administração
- Exclusão seletiva de registros
- Limpeza total do banco (com confirmação)

## 🛠️ Tecnologias Utilizadas

- Python 3.7+
- Oracle Database
- Biblioteca `oracledb`
- Logging nativo do Python
- JSON para exportação de dados

## ⚙️ Configuração

### Pré-requisitos
- Python 3.7 ou superior
- Banco de dados Oracle configurado
- Biblioteca `oracledb` instalada
- Arquivo `.env` com credenciais

### Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com:

```ini
DB_HOST=endereco_servidor
DB_PORT=porta_oracle
SERVICE_NAME=nome_servico
DB_USER=usuario
DB_PASSWORD=senha