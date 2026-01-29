"""
Script para executar pipelines do br_me_cnpj e salvar no PostgreSQL
Uso:
  python run_br_me_cnpj_postgres.py                    # Executa todas as tabelas
  python run_br_me_cnpj_postgres.py --table empresas   # Executa apenas empresas
  python run_br_me_cnpj_postgres.py --table estabelecimentos
"""

import argparse
import sys
from pathlib import Path

from pipelines.datasets.br_me_cnpj.tasks import get_data_source_max_date, main
from pipelines.utils.tasks_postgres import load_data_to_postgres
from pipelines.utils.utils import log

# Lista completa de tabelas disponíveis
AVAILABLE_TABLES = ["Empresas", "Socios", "Estabelecimentos", "Simples"]


def process_table(
    table: str, max_folder_date: str, max_last_modified_date: str
) -> bool:
    """
    Processa uma tabela específica

    Args:
        table: Nome da tabela (ex: Empresas, Socios, etc)
        max_folder_date: Data máxima da pasta
        max_last_modified_date: Data máxima de modificação

    Returns:
        bool: True se bem-sucedida, False caso contrário
    """
    try:
        log(f"{'=' * 60}")
        log(f"Processando tabela: {table}")
        log(f"{'=' * 60}")

        # Executa o download e processamento dos dados
        output_path = main.run(
            [table], max_folder_date, max_last_modified_date
        )

        log(f"Dados processados. Caminho de saída: {output_path}")

        # Verifica se há arquivos CSV no caminho (incluindo subpastas)
        output_path_obj = Path(output_path)
        csv_files = list(output_path_obj.glob("*.csv")) + list(
            output_path_obj.glob("**/*.csv")
        )

        if not csv_files:
            log(
                f"AVISO: Nenhum arquivo CSV encontrado em {output_path}",
                level="warning",
            )
            # Debug: listar conteúdo do diretório
            try:
                import os

                contents = os.listdir(output_path)
                log(f"Conteúdo da pasta: {contents}", level="warning")
            except Exception as e:
                log(f"Erro ao listar conteúdo: {e}", level="warning")
            return False

        log(f"Encontrados {len(csv_files)} arquivo(s) CSV")

        # Define o nome da tabela no banco (em minúsculo)
        table_id = table.lower()

        # Carrega os dados para o PostgreSQL
        log(f"Carregando dados para PostgreSQL: br_me_cnpj.{table_id}")
        success = load_data_to_postgres.run(
            data_path=output_path,
            dataset_id="br_me_cnpj",
            table_id=table_id,
            dump_mode="replace",  # Substitui a tabela se existir
            schema="public",  # Schema padrão do PostgreSQL
        )

        if success:
            log(f"✓ Tabela {table_id} carregada com sucesso no PostgreSQL")
            return True
        else:
            log(f"✗ Erro ao carregar tabela {table_id}", level="error")
            return False

    except Exception as e:
        log(f"✗ Erro ao processar tabela {table}: {e!s}", level="error")
        import traceback

        log(f"Traceback: {traceback.format_exc()}", level="error")
        return False


def run_br_me_cnpj_pipelines(tables: list[str] = None):
    """
    Executa pipelines do br_me_cnpj e salva os dados no PostgreSQL

    Args:
        tables: Lista de tabelas a processar. Se None, processa todas.
    """
    try:
        # Obtém as datas mais recentes dos dados
        log("Obtendo datas mais recentes da API de CNPJ...")
        max_folder_date, max_last_modified_date = (
            get_data_source_max_date.run()
        )
        log(f"Data máxima da pasta: {max_folder_date}")
        log(f"Data máxima de modificação: {max_last_modified_date}")

        # Define quais tabelas processar
        if tables is None:
            tables = AVAILABLE_TABLES
        else:
            # Valida tabelas solicitadas
            for table in tables:
                if table.capitalize() not in AVAILABLE_TABLES:
                    log(
                        f"ERRO: Tabela '{table}' não encontrada. "
                        f"Tabelas disponíveis: {', '.join(AVAILABLE_TABLES)}",
                        level="error",
                    )
                    return False
            # Capitaliza os nomes
            tables = [t.capitalize() for t in tables]

        successful_tables = []
        failed_tables = []

        for table in tables:
            success = process_table(
                table, max_folder_date, max_last_modified_date
            )
            if success:
                successful_tables.append(table)
            else:
                failed_tables.append(table)

        # Resumo final
        log(f"{'=' * 60}")
        log("RESUMO DA EXECUÇÃO")
        log(f"{'=' * 60}")
        log(f"Tabelas processadas com sucesso: {len(successful_tables)}")
        if successful_tables:
            for t in successful_tables:
                log(f"  ✓ {t}")

        if failed_tables:
            log(f"Tabelas com erro: {len(failed_tables)}", level="warning")
            for t in failed_tables:
                log(f"  ✗ {t}")
            return False

        return True

    except Exception as e:
        log(f"ERRO CRÍTICO na execução do pipeline: {e!s}", level="error")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Executa pipelines do br_me_cnpj e salva no PostgreSQL"
    )

    parser.add_argument(
        "--table",
        "-t",
        type=str,
        nargs="+",
        help=f"Tabela(s) a processar. Disponíveis: {', '.join(AVAILABLE_TABLES)}. "
        "Se não informado, processa todas.",
    )

    args = parser.parse_args()

    success = run_br_me_cnpj_pipelines(tables=args.table)
    sys.exit(0 if success else 1)
