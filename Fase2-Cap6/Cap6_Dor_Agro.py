"""
Sistema de Rastreabilidade Agrícola

Módulo principal para gestão de produtores, plantios, insumos, certificações e transportes agrícolas,
com integração a banco de dados Oracle.

Features:
- Cadastro completo da cadeia produtiva
- Validação de dados de entrada
- Geração de relatórios de rastreabilidade
- Interface baseada em menus console
"""
import oracledb
import re
import sys
import os
import logging
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, List, Union
from dotenv import load_dotenv

# --- CONFIGURAÇÕES INICIAIS ---
load_dotenv()  # Carrega variáveis do arquivo .env

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rastreabilidade.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# --- EXCEÇÕES PERSONALIZADAS ---
class DatabaseError(Exception):
    """Exceção base para erros de banco de dados."""
    pass

class ValidationError(Exception):
    """Exceção para erros de validação de dados."""
    pass

# --- FUNÇÕES COMPARTILHADAS ---
def formatar_titulo(titulo: str) -> None:
    """
    Exibe um título formatado centralizado com bordas.

    Args:
        titulo (str): Texto do título a ser formatado.
    """
    print("\n" + "=" * 50)
    print(titulo.center(50))
    print("=" * 50)

def input_inteiro_positivo(mensagem: str) -> int:
    """
    Solicita e valida entrada de um número inteiro positivo.

    Args:
        mensagem (str): Mensagem a ser exibida para o usuário.

    Returns:
        int: Valor inteiro positivo validado.
    """
    while True:
        try:
            valor = int(input(mensagem).strip())
            if valor > 0:
                return valor
            logger.warning("Valor deve ser maior que zero")
        except ValueError:
            logger.warning("Digite um número inteiro válido")

def input_decimal_positivo(mensagem: str, permite_zero: bool = False) -> Decimal:
    """
    Solicita e valida entrada de um número decimal positivo.

    Args:
        mensagem (str): Mensagem a ser exibida para o usuário.
        permite_zero (bool): Se True, aceita zero como valor válido.

    Returns:
        Decimal: Valor decimal positivo validado.
    """
    while True:
        valor = input(mensagem).strip().replace(',', '.')
        try:
            valor_dec = Decimal(valor)
            if valor_dec > 0 or (permite_zero and valor_dec >= 0):
                return valor_dec
            logger.warning(f"Valor deve ser {'maior ou igual a zero' if permite_zero else 'maior que zero'}")
        except:
            logger.warning("Digite um número decimal válido (ex: 10.5)")

def input_data(mensagem: str) -> datetime.date:
    """
    Solicita e valida entrada de uma data no formato DD/MM/AAAA.

    Args:
        mensagem (str): Mensagem a ser exibida para o usuário.

    Returns:
        datetime.date: Objeto de data validado.
    """
    while True:
        data_str = input(f"{mensagem} (dd/mm/aaaa): ").strip()
        try:
            return datetime.strptime(data_str, "%d/%m/%Y").date()
        except ValueError:
            logger.warning("Formato inválido! Use dd/mm/aaaa")

def input_opcao(mensagem: str, opcoes_validas: List[str]) -> str:
    """
    Solicita e valida entrada de uma opção dentre as possíveis.

    Args:
        mensagem (str): Mensagem a ser exibida para o usuário.
        opcoes_validas (List[str]): Lista de opções aceitáveis.

    Returns:
        str: Opção selecionada em maiúsculas.
    """
    while True:
        valor = input(mensagem).strip().upper()
        if valor in opcoes_validas:
            return valor
        logger.warning(f"Opções válidas: {', '.join(opcoes_validas)}")

def input_texto(mensagem: str, max_caracteres: Optional[int] = None, obrigatorio: bool = False) -> Optional[str]:
    """
    Solicita e valida entrada de texto.

    Args:
        mensagem (str): Mensagem a ser exibida para o usuário.
        max_caracteres (Optional[int]): Tamanho máximo permitido.
        obrigatorio (bool): Se True, não aceita string vazia.

    Returns:
        Optional[str]: Texto validado ou None se não obrigatório.
    """
    while True:
        valor = input(mensagem).strip()
        if not valor and obrigatorio:
            logger.warning("Campo obrigatório!")
            continue
        if valor and max_caracteres and len(valor) > max_caracteres:
            logger.warning(f"Máximo de {max_caracteres} caracteres!")
            continue
        return valor or None

def input_cnpj() -> str:
    """
    Solicita e valida entrada de CNPJ no formato XX.XXX.XXX/XXXX-XX.

    Returns:
        str: CNPJ formatado e validado.
    """
    while True:
        cnpj = input("CNPJ (XX.XXX.XXX/XXXX-XX): ").strip()
        if re.match(r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$', cnpj):
            return cnpj
        logger.warning("Formato inválido! Use XX.XXX.XXX/XXXX-XX")

def input_telefone() -> Optional[str]:
    """
    Solicita e valida entrada de telefone no formato (XX) XXXX-XXXX.

    Returns:
        Optional[str]: Telefone formatado ou None se vazio.
    """
    while True:
        telefone = input("Telefone (opcional): ").strip()
        if not telefone:
            return None
        if re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', telefone):
            return telefone
        logger.warning("Formato inválido! Use (XX) XXXX-XXXX ou (XX) XXXXX-XXXX")

def input_email() -> Optional[str]:
    """
    Solicita e valida entrada de e-mail.

    Returns:
        Optional[str]: E-mail validado ou None se vazio.
    """
    while True:
        email = input("E-mail (opcional): ").strip()
        if not email:
            return None
        if re.match(r'^[\w.-]+@[\w.-]+\.\w+$', email):
            return email
        logger.warning("Formato inválido! Use exemplo@dominio.com")

def executar_sql(
        conn: oracledb.Connection,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        operacao: str = 'insert'
) -> Union[int, Tuple[List[Tuple], List[str]], None]:
    """
    Executa operações SQL no banco de dados com tratamento de erros.

    Args:
        conn (oracledb.Connection): Conexão com o banco de dados.
        sql (str): Comando SQL a ser executado.
        params (Optional[Dict[str, Any]]): Parâmetros para o comando SQL.
        operacao (str): Tipo de operação ('insert', 'insert_returning', 'select_one', 'select_all').

    Returns:
        Union[int, Tuple[List[Tuple], List[str]], None]:
            - Para 'insert_returning': ID gerado (int)
            - Para 'select_all': (resultados, colunas)
            - Para outros: None

    Raises:
        DatabaseError: Em caso de falha na execução SQL.
    """
    cursor = None
    try:
        cursor = conn.cursor()

        if operacao == 'insert_returning':
            id_var = cursor.var(oracledb.NUMBER)
            if params is None:
                params = {}
            params['id'] = id_var
            cursor.execute(sql, params)
            conn.commit()
            logger.info(f"Operação realizada: {sql.split()[0]} com ID {id_var.getvalue()[0]}")
            return id_var.getvalue()[0]

        elif operacao == 'insert':
            cursor.execute(sql, params)
            conn.commit()
            logger.info(f"Operação realizada: {sql.split()[0]}")

        elif operacao == 'select_one':
            cursor.execute(sql, params)
            return cursor.fetchone()

        elif operacao == 'select_all':
            cursor.execute(sql, params)
            return cursor.fetchall(), [desc[0] for desc in cursor.description]

    except oracledb.DatabaseError as e:
        error, = e.args
        logger.error(f"Erro Oracle (ORA-{error.code}): {error.message}")
        conn.rollback()
        raise DatabaseError(f"Falha no banco de dados (ORA-{error.code})") from e
    finally:
        if cursor:
            cursor.close()

# --- FUNÇÃO DE CADASTRO ---
def cadastrar_produtores(conn: oracledb.Connection) -> None:
    """
    Realiza o cadastro completo de produtores rurais.

    Fluxo:
    1. Solicita dados do produtor com validações
    2. Insere no banco de dados
    3. Retorna feedback ao usuário

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CADASTRO DE PRODUTORES")
        logger.info("Iniciando cadastro de produtor")

        dados = {
            "nome_fazenda": input_texto("Nome da Fazenda: ", obrigatorio=True),
            "cnpj": input_cnpj(),
            "localizacao": input_texto("Localização (Cidade/Estado): ", obrigatorio=True),
            "area_hectares": input_decimal_positivo("Área (hectares): "),
            "telefone": input_telefone(),
            "email": input_email(),
            "biografia": input_texto("Biografia (opcional): ")
        }

        sql = """
        INSERT INTO Produtores (
            nome_fazenda, cnpj, localizacao, area_hectares, 
            telefone, email, biografia, data_cadastro
        ) VALUES (
            :nome, :cnpj, :local, :area, :tel, :email, :bio, SYSDATE
        )
        RETURNING id_produtor INTO :id
        """

        id_produtor = executar_sql(conn, sql, dados, 'insert_returning')
        print(f"\n✅ Produtor cadastrado com sucesso! ID: {id_produtor}")

    except DatabaseError:
        print("\n❌ Falha ao cadastrar produtor. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar produtor")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para voltar ao menu...")

def cadastrar_plantios(conn: oracledb.Connection) -> None:
    """
    Realiza o cadastro completo de plantios agrícolas.

    Inclui:
    - Dados básicos do plantio
    - Datas de plantio e colheita (opcionais)
    - Métodos agrícolas utilizados

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CADASTRO DE PLANTIOS")
        logger.info("Iniciando cadastro de plantio")

        dados = {
            "id_produtor": input_inteiro_positivo("ID do Produtor: "),
            "id_rastreio": input_texto("Código de Rastreio (20 caracteres): ", max_caracteres=20, obrigatorio=True),
            "cultura": input_texto("Cultura (50 caracteres): ", max_caracteres=50, obrigatorio=True),
            "data_plantio": input_data("Data de Plantio") if input_opcao("Incluir data de plantio? (S/N): ",
                                                                         ["S", "N"]) == "S" else None,
            "data_colheita": input_data("Data de Colheita") if input_opcao("Incluir data de colheita? (S/N): ",
                                                                           ["S", "N"]) == "S" else None,
            "solo_tipo": input_texto("Tipo de solo (50 caracteres, opcional): ", max_caracteres=50),
            "metodo_irrigacao": input_texto("Método de irrigação (50 caracteres, opcional): ", max_caracteres=50),
            "uso_agrotoxico": input_opcao("Usa agrotóxico? (S/N): ", ["S", "N"]),
            "descricao": input_texto("Descrição (400 caracteres, opcional): ", max_caracteres=400)
        }

        sql = """
        INSERT INTO Plantios (
            id_produtor, id_rastreio, cultura, data_plantio, data_colheita,
            solo_tipo, metodo_irrigacao, uso_agrotoxico, descricao
        ) VALUES (
            :id_produtor, :id_rastreio, :cultura, :data_plantio, :data_colheita,
            :solo_tipo, :metodo_irrigacao, :uso_agrotoxico, :descricao
        )
        RETURNING id_plantio INTO :id
        """

        id_plantio = executar_sql(conn, sql, dados, 'insert_returning')
        print(f"\n✅ Plantio cadastrado com sucesso! ID: {id_plantio}")

    except DatabaseError:
        print("\n❌ Falha ao cadastrar plantio. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar plantio")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para continuar...")

def cadastrar_insumos(conn: oracledb.Connection, dados=None) -> None:
    """
    Realiza o cadastro de insumos agrícolas utilizados nos plantios.

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CADASTRO DE INSUMOS")
        logger.info("Iniciando cadastro de insumo")

        dados = {
            "id_plantio": input_inteiro_positivo("ID do Plantio: "),
            "tipo": input_texto("Tipo de insumo (50 caracteres, ex: Fertilizante): ", max_caracteres=50,
                                obrigatorio=True),
            "nome": input_texto("Nome do insumo (100 caracteres, opcional): ", max_caracteres=100),
            "quantidade": input_decimal_positivo("Quantidade (ex: 10.5): ") if input_opcao(
                "Incluir quantidade? (S/N): ", ["S", "N"]) == "S" else None,
            "unidade": input_texto("Unidade (max 10 caracteres, ex: kg, L): ",
                                   max_caracteres=10) if "quantidade" in dados and dados[
                "quantidade"] is not None else None
        }

        # Obter próximo ID disponível
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_insumo), 0) + 1 FROM Insumos")
        proximo_id = cursor.fetchone()[0]
        cursor.close()

        sql = """
        INSERT INTO Insumos (
            id_insumo, id_plantio, tipo, nome, quantidade, unidade
        ) VALUES (
            :id_insumo, :id_plantio, :tipo, :nome, :quantidade, :unidade
        )
        """

        params = {
            "id_insumo": proximo_id,
            "id_plantio": dados["id_plantio"],
            "tipo": dados["tipo"],
            "nome": dados["nome"],
            "quantidade": float(dados["quantidade"]) if dados["quantidade"] is not None else None,
            "unidade": dados["unidade"]
        }

        executar_sql(conn, sql, params)
        print(f"\n✅ Insumo cadastrado com sucesso! ID: {proximo_id}")

    except DatabaseError:
        print("\n❌ Falha ao cadastrar insumo. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar insumo")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para continuar...")

def cadastrar_certificacoes(conn: oracledb.Connection) -> None:
    """
    Realiza o cadastro de certificações obtidas pelos produtores.

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CADASTRO DE CERTIFICAÇÕES")
        logger.info("Iniciando cadastro de certificação")

        dados = {
            "id_produtor": input_inteiro_positivo("ID do Produtor: "),
            "tipo": input_texto("Tipo de Certificação (100 caracteres, ex: Orgânico, Fair Trade): ", max_caracteres=100,
                                obrigatorio=True),
            "certificadora": input_texto("Certificadora (100 caracteres, opcional): ", max_caracteres=100),
            "data_validade": input_data("Data de Validade") if input_opcao("Incluir data de validade? (S/N): ",
                                                                           ["S", "N"]) == "S" else None,
            "codigo_certificado": input_texto("Código do Certificado (50 caracteres, opcional): ", max_caracteres=50)
        }

        # Obter próximo ID disponível
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_certificacao), 0) + 1 FROM Certificacoes")
        proximo_id = cursor.fetchone()[0]
        cursor.close()

        sql = """
        INSERT INTO Certificacoes (
            id_certificacao, id_produtor, tipo, certificadora, data_validade, codigo_certificado
        ) VALUES (
            :id_cert, :id_prod, :tipo, :certif, :data_val, :codigo
        )
        """

        executar_sql(conn, sql, {
            "id_cert": proximo_id,
            "id_prod": dados["id_produtor"],
            "tipo": dados["tipo"],
            "certif": dados["certificadora"],
            "data_val": dados["data_validade"],
            "codigo": dados["codigo_certificado"]
        })
        print(f"\n✅ Certificação cadastrada com sucesso! ID: {proximo_id}")

    except DatabaseError:
        print("\n❌ Falha ao cadastrar certificação. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar certificação")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para continuar...")

def cadastrar_transportes(conn: oracledb.Connection) -> None:
    """
    Realiza o cadastro de transportes de produtos agrícolas.

    Inclui:
    - Tipo de veículo
    - Distância percorrida
    - Emissão de CO2
    - Data e destino

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CADASTRO DE TRANSPORTES")
        logger.info("Iniciando cadastro de transporte")

        dados = {
            "id_plantio": input_inteiro_positivo("ID do Plantio: "),
            "tipo_veiculo": input_texto("Tipo de veículo (50 caracteres, opcional): ", max_caracteres=50),
            "distancia_km": input_decimal_positivo("Distância (km): ", permite_zero=True) if input_opcao(
                "Registrar distância em km? (S/N): ", ["S", "N"]) == "S" else None,
            "emissao_co2": input_decimal_positivo("Emissão de CO2 (kg): ", permite_zero=True) if input_opcao(
                "Registrar emissão de CO2? (S/N): ", ["S", "N"]) == "S" else None,
            "data_transporte": input_data("Data do Transporte") if input_opcao("Registrar data do transporte? (S/N): ",
                                                                               ["S", "N"]) == "S" else None,
            "destino": input_texto("Local de destino (200 caracteres, opcional): ", max_caracteres=200)
        }

        # Obter próximo ID disponível
        cursor = conn.cursor()
        cursor.execute("SELECT NVL(MAX(id_transporte), 0) + 1 FROM Transporte")
        proximo_id = cursor.fetchone()[0]
        cursor.close()

        sql = """
        INSERT INTO Transporte (
            id_transporte, id_plantio, tipo_veiculo, distancia_km, 
            emissao_co2, data_transporte, destino
        ) VALUES (
            :id_transp, :id_plant, :tipo_veic, :distancia,
            :emissao, :data_transp, :destino
        )
        """

        executar_sql(conn, sql, {
            "id_transp": proximo_id,
            "id_plant": dados["id_plantio"],
            "tipo_veic": dados["tipo_veiculo"],
            "distancia": float(dados["distancia_km"]) if dados["distancia_km"] is not None else None,
            "emissao": float(dados["emissao_co2"]) if dados["emissao_co2"] is not None else None,
            "data_transp": dados["data_transporte"],
            "destino": dados["destino"]
        })
        print(f"\n✅ Transporte cadastrado com sucesso! ID: {proximo_id}")

    except DatabaseError:
        print("\n❌ Falha ao cadastrar transporte. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar transporte")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para continuar...")

# --- FUNÇÃO PARA LISTAR CADASTROS ---
def listar_cadastro(conn: oracledb.Connection) -> None:
    """
    Exibe um menu secundário para listar registros de cadastros específicos.

    Permite ao usuário selecionar qual tabela deseja visualizar e mostra
    todos os registros no formato de tuplas.

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        while True:
            formatar_titulo("LISTAGEM DE CADASTROS")
            print("\nSelecione o cadastro que deseja listar:")
            print("1. PRODUTORES")
            print("2. PLANTIOS")
            print("3. INSUMOS")
            print("4. CERTIFICAÇÕES")
            print("5. TRANSPORTES")
            print("0. Voltar ao menu principal")

            opcao = input("\nOpção: ").strip()

            if opcao == '0':
                return

            tabelas = {
                '1': {'nome': 'PRODUTORES', 'titulo': 'PRODUTORES CADASTRADOS'},
                '2': {'nome': 'PLANTIOS', 'titulo': 'PLANTIOS CADASTRADOS'},
                '3': {'nome': 'INSUMOS', 'titulo': 'INSUMOS CADASTRADOS'},
                '4': {'nome': 'CERTIFICACOES', 'titulo': 'CERTIFICAÇÕES CADASTRADAS'},
                '5': {'nome': 'TRANSPORTE', 'titulo': 'TRANSPORTES CADASTRADOS'}
            }

            if opcao not in tabelas:
                print("\n❌ Opção inválida! Digite um número entre 1 e 5 ou 0 para voltar.")
                input("Pressione Enter para continuar...")
                continue

            tabela = tabelas[opcao]

            try:
                # Executa o SELECT na tabela escolhida
                sql = f"SELECT * FROM {tabela['nome']}"
                resultados, colunas = executar_sql(conn, sql, operacao='select_all')

                if not resultados:
                    print(f"\nℹ️ Nenhum registro encontrado na tabela {tabela['nome']}.")
                    input("\nPressione Enter para continuar...")
                    continue

                # Exibe os resultados
                formatar_titulo(tabela['titulo'])
                print(f"\nColunas: {', '.join(colunas)}\n")

                for i, registro in enumerate(resultados, 1):
                    print(f"Registro #{i}:")
                    for coluna, valor in zip(colunas, registro):
                        print(f"  {coluna}: {valor}")
                    print("-" * 40)

                print(f"\nTotal de registros encontrados: {len(resultados)}")

            except DatabaseError:
                print("\n❌ Falha ao acessar o banco de dados. Consulte o log para detalhes.")
            except Exception as e:
                logger.exception("Erro inesperado ao listar cadastros")
                print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")

            input("\nPressione Enter para continuar...")

    except Exception as e:
        logger.exception("Erro na função de listagem")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
        input("\nPressione Enter para voltar ao menu principal...")

# --- FUNÇÃO DE CONSULTA E EXCLUSÃO ---
def excluir_registros(conn: oracledb.Connection) -> None:
    """
    Interface para exclusão segura de registros do sistema.

    Permite selecionar a tabela e verifica a existência do registro
    antes de realizar a exclusão.

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    TABELAS = {
        1: {'nome': 'PRODUTORES', 'id': 'id_produtor', 'nome_id': 'ID Produtor'},
        2: {'nome': 'PLANTIOS', 'id': 'id_plantio', 'nome_id': 'ID Plantio'},
        3: {'nome': 'INSUMOS', 'id': 'id_insumo', 'nome_id': 'ID Insumo'},
        4: {'nome': 'CERTIFICACOES', 'id': 'id_certificacao', 'nome_id': 'ID Certificação'},
        5: {'nome': 'TRANSPORTE', 'id': 'id_transporte', 'nome_id': 'ID Transporte'}
    }

    try:
        while True:
            formatar_titulo("EXCLUSÃO DE REGISTROS")
            print("\nSelecione a tabela:")
            for opcao, tabela in TABELAS.items():
                print(f"{opcao}. {tabela['nome'].capitalize()}")
            print("0. Voltar ao menu principal")

            try:
                opcao = int(input("\nOpção: ").strip())
                if opcao == 0:
                    return
                tabela = TABELAS.get(opcao)
                if not tabela:
                    print("Opção inválida!")
                    continue
            except ValueError:
                print("Digite um número válido!")
                continue

            try:
                id_registro = int(input(f"\nInforme o {tabela['nome_id']} para exclusão: ").strip())
            except ValueError:
                print("ID deve ser um número inteiro!")
                continue

            try:
                # Verifica existência
                sql_verifica = f"SELECT * FROM {tabela['nome']} WHERE {tabela['id']} = :id"
                resultado, colunas = executar_sql(conn, sql_verifica, {'id': id_registro}, 'select_all')

                if not resultado:
                    print(f"\n❌ Registro não encontrado!")
                    continue

                # Mostra registro
                formatar_titulo(f"REGISTRO ENCONTRADO - {tabela['nome']}")
                for linha in resultado:
                    for coluna, valor in zip(colunas, linha):
                        print(f"{coluna:20}: {valor}")

                # Confirmação
                if input_opcao("\nConfirmar exclusão? (S/N): ", ["S", "N"]) == "S":
                    sql_exclui = f"DELETE FROM {tabela['nome']} WHERE {tabela['id']} = :id"
                    executar_sql(conn, sql_exclui, {'id': id_registro})
                    print("\n✅ Registro excluído com sucesso!")

            except DatabaseError:
                print("\n❌ Falha ao excluir registro. Consulte o log para detalhes.")
            except Exception as e:
                logger.exception("Erro inesperado ao excluir registro")
                print("\n❌ Ocorreu um erro inesperado.")

            input("\nPressione Enter para continuar...")

    except Exception as e:
        logger.exception("Erro na função de exclusão")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")

def excluir_tudo(conn: oracledb.Connection) -> None:
    """
    Realiza a exclusão total de todos os registros do sistema com confirmação.

    Reseta todas as sequências de IDs para 1.
    ATENÇÃO: Esta operação é irreversível!

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("EXCLUSÃO TOTAL E RESET DE SEQUÊNCIAS")
        print("\n⚠️ ATENÇÃO: Esta operação irá:")
        print("- Remover TODOS os registros do sistema")
        print("- Resetar todas as sequências de ID para 1")

        if input_opcao("\nTem CERTEZA que deseja continuar? (Digite 'CONFIRMAR' para prosseguir): ",
                       ["CONFIRMAR"]) != "CONFIRMAR":
            print("\nOperação cancelada pelo usuário.")
            input("Pressione Enter para voltar ao menu...")
            return

        # Ordem de exclusão CRÍTICA (respeitando FKs)
        tabelas = ['CERTIFICACOES', 'TRANSPORTE', 'INSUMOS', 'PLANTIOS', 'PRODUTORES']

        for tabela in tabelas:
            try:
                executar_sql(conn, f"DELETE FROM {tabela}")
                print(f"✓ {tabela}: Registros excluídos")
            except DatabaseError:
                print(f"\n❌ Falha ao excluir registros de {tabela}")
                raise

        # Resetar sequências
        sequencias = {
            'PRODUTORES': 'SEQ_PRODUTORES',
            'PLANTIOS': 'SEQ_PLANTIOS',
            'INSUMOS': 'SEQ_INSUMOS',
            'CERTIFICACOES': 'SEQ_CERTIFICACOES',
            'TRANSPORTE': 'SEQ_TRANSPORTE'
        }

        for tabela, seq in sequencias.items():
            try:
                executar_sql(conn, f"DROP SEQUENCE {seq}")
            except:
                pass  # Ignora se a sequência não existir
            executar_sql(conn, f"CREATE SEQUENCE {seq} START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE")
            print(f"✓ Sequência {seq}: Resetada para 1")

        print("\n✅ Banco de dados totalmente limpo e sequências resetadas!")

    except DatabaseError:
        print("\n❌ Falha na limpeza do banco. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado ao limpar banco")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para voltar ao menu...")

def consultar_rastreabilidade(conn: oracledb.Connection) -> None:
    """
    Consulta completa de rastreabilidade de produtos agrícolas.

    Mostra toda a cadeia desde o produtor até o transporte,
    com opção de salvar resultado em arquivo JSON.

    Args:
        conn (oracledb.Connection): Conexão ativa com o banco de dados.
    """
    try:
        formatar_titulo("CONSULTA DE RASTREABILIDADE")
        id_rastreio = input("\nInforme o ID de Rastreio: ").strip()

        sql = """
        SELECT 
            p.nome_fazenda, p.localizacao,
            pl.id_rastreio, pl.cultura, pl.data_plantio,
            c.tipo AS certificacao,
            t.emissao_co2
        FROM 
            Produtores p
        JOIN Plantios pl ON p.id_produtor = pl.id_produtor
        LEFT JOIN Certificacoes c ON p.id_produtor = c.id_produtor
        LEFT JOIN Transporte t ON pl.id_plantio = t.id_plantio
        WHERE 
            pl.id_rastreio = :id_rastreio
        """

        resultados, colunas = executar_sql(conn, sql, {"id_rastreio": id_rastreio}, 'select_all')

        if not resultados:
            print("\n❌ Nenhum registro encontrado com este ID de Rastreio!")
            input("\nPressione Enter para continuar...")
            return

        formatar_titulo("RESULTADO DA CONSULTA")
        for registro in resultados:
            for coluna, valor in zip(colunas, registro):
                print(f"{coluna:15}: {valor}")
            print("-" * 50)

        if input_opcao("\nDeseja salvar esta consulta em JSON? (S/N): ", ["S", "N"]) == "S":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"rastreio_{id_rastreio}_{timestamp}.json"

            dados = [dict(zip(colunas, registro)) for registro in resultados]

            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=4, default=str)

            print(f"\n✅ Arquivo salvo como: {nome_arquivo}")

    except DatabaseError:
        print("\n❌ Falha na consulta. Consulte o log para detalhes.")
    except Exception as e:
        logger.exception("Erro inesperado na consulta")
        print("\n❌ Ocorreu um erro inesperado. Consulte o log para detalhes.")
    finally:
        input("\nPressione Enter para continuar...")

# --- CONEXÃO COM BANCO DE DADOS ---
def conectar_oracle() -> oracledb.Connection:
    """
    Estabelece conexão com o banco de dados Oracle.

    Utiliza configurações do arquivo .env:
    - DB_HOST: Endereço do servidor
    - DB_PORT: Porta de conexão
    - SERVICE_NAME: Nome do serviço Oracle
    - DB_USER: Nome de usuário
    - DB_PASSWORD: Senha

    Returns:
        oracledb.Connection: Objeto de conexão ativa.

    Raises:
        DatabaseError: Se a conexão falhar.
    """
    try:
        # Configuração via variáveis de ambiente
        dsn = oracledb.makedsn(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "1522")),
            service_name=os.getenv("SERVICE_NAME", "ORCLPDB")
        )

        conn = oracledb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            dsn=dsn
        )

        logger.info("Conexão com o banco de dados estabelecida com sucesso")
        return conn

    except oracledb.DatabaseError as e:
        error, = e.args
        logger.error(f"Falha na conexão (ORA-{error.code}): {error.message}")
        raise DatabaseError(f"Falha na conexão com o Oracle (ORA-{error.code})") from e
    except Exception as e:
        logger.exception("Erro inesperado ao conectar ao banco")
        raise DatabaseError("Erro inesperado ao conectar ao banco") from e

# --- MENU PRINCIPAL ---
def exibir_menu() -> None:
    """Exibe o menu principal do sistema com todas as opções disponíveis."""
    formatar_titulo("SISTEMA DE RASTREABILIDADE AGRÍCOLA")
    print("1. Cadastrar PRODUTORES")
    print("2. Cadastrar PLANTIOS")
    print("3. Cadastrar INSUMOS")
    print("4. Cadastrar CERTIFICAÇÕES")
    print("5. Cadastrar TRANSPORTES")
    print("6. Listar CADASTROS")
    print("7. Excluir REGISTROS")
    print("8. Excluir TUDO (CUIDADO!)")
    print("9. Consultar RASTREABILIDADE")
    print("0. SAIR")
    print("=" * 50)

def main() -> None:
    """
    Função principal que inicia o sistema.

    Fluxo:
    1. Configura cliente Oracle
    2. Estabelece conexão com o banco
    3. Exibe menu interativo
    4. Gerencia todas as operações
    5. Encerra conexão ao sair
    """
    try:
        # Configuração inicial do cliente Oracle
        try:
            oracledb.init_oracle_client(lib_dir=None)
            logger.info("Cliente Oracle inicializado")
        except Exception as e:
            logger.warning(f"Cliente Oracle não encontrado, usando modo thin: {e}")

        # Conecta ao banco
        conn = conectar_oracle()

        # Menu principal
        while True:
            exibir_menu()
            opcao = input("Digite o número da opção desejada: ").strip()

            if opcao == '1':
                cadastrar_produtores(conn)
            elif opcao == '2':
                cadastrar_plantios(conn)
            elif opcao == '3':
                cadastrar_insumos(conn)
            elif opcao == '4':
                cadastrar_certificacoes(conn)
            elif opcao == '5':
                cadastrar_transportes(conn)
            elif opcao == '6':
                listar_cadastro(conn)
            elif opcao == '7':
                excluir_registros(conn)
            elif opcao == '8':
                excluir_tudo(conn)
            elif opcao == '9':
                consultar_rastreabilidade(conn)
            elif opcao == '0':
                print("\nEncerrando conexão com o banco de dados...")
                break
            else:
                print("\nOpção inválida! Digite um número entre 0 e 8.")
                input("Pressione Enter para tentar novamente...")

    except DatabaseError:
        print("\n❌ Erro fatal de banco de dados. Verifique os logs e tente novamente.")
        sys.exit(1)
    except Exception as e:
        logger.exception("Erro inesperado na aplicação")
        print("\n❌ Erro inesperado. Verifique os logs para detalhes.")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("Conexão com o banco encerrada")
        print("\nObrigado por usar o sistema! Até logo!")

if __name__ == "__main__":
    main()