# Sistema de Gerenciamento de Dados Agrícolas

Este projeto implementa um sistema de gerenciamento de dados agrícolas que simula o armazenamento e manipulação de informações sobre culturas, sensores, medições, sugestões e aplicações em um banco de dados SQL.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
projeto_banco_agricola/
├── csv_data/                  # Arquivos CSV com dados de exemplo
│   ├── t_culturas.csv         # Dados de culturas agrícolas
│   ├── t_sensores.csv         # Dados de sensores
│   ├── t_medicoes.csv         # Dados de medições
│   ├── t_sugestoes.csv        # Dados de sugestões
│   └── t_aplicacoes.csv       # Dados de aplicações
├── python_code/               # Código Python para operações CRUD
│   └── agricola_db_manager.py # Classe principal para gerenciamento do banco de dados
├── SCRIPT_DDL_PROJETO_FASE2_CAP1.SQL  # Script SQL para criação das tabelas
├── justificativa_estrutura.md # Justificativa da estrutura de dados e relação com o MER
└── README.md                  # Este arquivo
```

## Modelo Relacional

O sistema é baseado no seguinte modelo relacional:

![Modelo Relacional](Modelo_Relacional.png)

O modelo consiste em cinco tabelas principais:

1. **T_CULTURAS**: Armazena informações sobre as culturas agrícolas.
2. **T_SENSORES**: Registra os sensores instalados e suas características.
3. **T_MEDICOES**: Contém as medições realizadas pelos sensores.
4. **T_SUGESTOES**: Armazena sugestões baseadas nas medições.
5. **T_APLICACOES**: Registra as aplicações realizadas com base nas sugestões.

## Relação com o MER da Fase 2

O banco de dados implementado segue fielmente o Modelo Entidade-Relacionamento (MER) desenvolvido na Fase 2 do projeto. As principais correspondências são:

### Entidades e Tabelas

Cada entidade do MER foi mapeada para uma tabela correspondente no banco de dados:

- A entidade **Cultura** é representada pela tabela `T_CULTURAS`
- A entidade **Sensor** é representada pela tabela `T_SENSORES`
- A entidade **Medição** é representada pela tabela `T_MEDICOES`
- A entidade **Sugestão** é representada pela tabela `T_SUGESTOES`
- A entidade **Aplicação** é representada pela tabela `T_APLICACOES`

### Relacionamentos

Os relacionamentos do MER foram implementados através de chaves estrangeiras:

- Um sensor pertence a uma cultura: `T_SENSORES.cod_cultura` referencia `T_CULTURAS.cod_cultura`
- Uma medição é realizada por um sensor: `T_MEDICOES.cod_sensor` referencia `T_SENSORES.cod_sensor`
- Uma sugestão é baseada em uma medição: `T_SUGESTOES.cod_medicao` e `T_SUGESTOES.cod_sensor` referenciam `T_MEDICOES.cod_medicao` e `T_MEDICOES.cod_sensor`
- Uma aplicação é baseada em uma sugestão: `T_APLICACOES.cod_sugestao`, `T_APLICACOES.cod_medicao` e `T_APLICACOES.cod_sensor` referenciam `T_SUGESTOES.cod_sugestao`, `T_SUGESTOES.cod_medicao` e `T_SUGESTOES.cod_sensor`
- Uma aplicação é realizada em uma cultura: `T_APLICACOES.cod_cultura` referencia `T_CULTURAS.cod_cultura`

Para uma análise mais detalhada da relação entre o MER e a implementação, consulte o arquivo [justificativa_estrutura.md](justificativa_estrutura.md).

## Arquivos CSV de Exemplo

Os arquivos CSV contêm dados de exemplo para cada tabela do modelo relacional:

### t_culturas.csv

Contém informações sobre diferentes culturas agrícolas, como soja, milho e café, incluindo tamanho e data prevista de colheita.

### t_sensores.csv

Contém dados de sensores instalados, incluindo tipo (umidade, pH, temperatura), fabricante, modelo e localização.

### t_medicoes.csv

Registra medições realizadas pelos sensores, com data/hora, valor e unidade de medida.

### t_sugestoes.csv

Contém sugestões baseadas nas medições, como irrigação ou aplicação de fertilizantes.

### t_aplicacoes.csv

Registra aplicações realizadas com base nas sugestões, incluindo produto utilizado, quantidade e responsável.

## Operações CRUD Implementadas

O sistema implementa operações CRUD (Create, Read, Update, Delete) para todas as tabelas do modelo relacional:

### Create (Criar)

Métodos para inserir novos registros em cada tabela:

- `create_cultura()`: Insere uma nova cultura
- `create_sensor()`: Insere um novo sensor
- `create_medicao()`: Insere uma nova medição
- `create_sugestao()`: Insere uma nova sugestão
- `create_aplicacao()`: Insere uma nova aplicação

### Read (Ler)

Métodos para recuperar dados das tabelas:

- `read_cultura()`: Recupera dados de culturas
- `read_sensor()`: Recupera dados de sensores
- `read_medicao()`: Recupera dados de medições
- `read_sugestao()`: Recupera dados de sugestões
- `read_aplicacao()`: Recupera dados de aplicações

### Update (Atualizar)

Métodos para atualizar registros existentes:

- `update_cultura()`: Atualiza dados de uma cultura
- `update_sensor()`: Atualiza dados de um sensor
- `update_medicao()`: Atualiza dados de uma medição
- `update_sugestao()`: Atualiza dados de uma sugestão
- `update_aplicacao()`: Atualiza dados de uma aplicação

### Delete (Excluir)

Métodos para remover registros:

- `delete_cultura()`: Remove uma cultura
- `delete_sensor()`: Remove um sensor
- `delete_medicao()`: Remove uma medição
- `delete_sugestao()`: Remove uma sugestão
- `delete_aplicacao()`: Remove uma aplicação

Todas as operações CRUD implementam verificações de integridade referencial para garantir a consistência dos dados.

## Consultas Analíticas

Além das operações CRUD básicas, o sistema implementa consultas analíticas para obter insights dos dados:

- `get_medicoes_by_cultura()`: Recupera medições associadas a uma cultura específica
- `get_aplicacoes_by_cultura()`: Recupera aplicações associadas a uma cultura específica
- `get_sugestoes_by_sensor()`: Recupera sugestões associadas a um sensor específico

## Como Usar o Sistema

### Pré-requisitos

- Python 3.6 ou superior
- SQLite3

### Configuração

1. Clone o repositório ou extraia os arquivos para uma pasta local
2. Certifique-se de que o script SQL e os arquivos CSV estão nos locais corretos

### Execução

1. Execute o script Python principal:

```bash
python agricola_db_manager.py
```

2. O script irá:
   - Criar o banco de dados SQLite
   - Importar os dados dos arquivos CSV
   - Demonstrar operações CRUD básicas
   - Executar consultas analíticas de exemplo

### Personalização

Você pode modificar o script principal para:

- Adicionar novas culturas, sensores, medições, etc.
- Implementar consultas personalizadas
- Exportar resultados para arquivos CSV ou outros formatos

## Justificativa da Estrutura de Dados

A estrutura de dados escolhida (SQLite) oferece um equilíbrio ideal entre simplicidade, desempenho e fidelidade ao modelo entidade-relacionamento original. As principais vantagens incluem:

1. **Portabilidade**: O banco de dados inteiro é armazenado em um único arquivo
2. **Simplicidade**: Não requer configuração de servidor
3. **Compatibilidade com Python**: Integração nativa através da biblioteca sqlite3
4. **Suporte completo a SQL**: Permite implementar todas as operações necessárias
5. **Integridade referencial**: Garante a consistência dos dados

Para uma análise mais detalhada da estrutura de dados e sua relação com o MER, consulte o arquivo [justificativa_estrutura.md](justificativa_estrutura.md).

## Conclusão

Este sistema demonstra a implementação de um banco de dados relacional para gerenciamento de dados agrícolas, seguindo fielmente o modelo entidade-relacionamento definido na Fase 2 do projeto. A implementação em Python, com a classe `AgricolaDatabaseManager`, fornece uma interface clara e consistente para manipulação dos dados, permitindo operações CRUD completas e consultas analíticas.
