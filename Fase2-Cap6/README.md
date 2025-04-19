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

