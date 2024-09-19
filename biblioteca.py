import sqlite3
import os
import csv
from pathlib import Path
from datetime import datetime
import shutil

# Diretórios
BASE_DIR = Path("meu_sistema_livraria")
BACKUP_DIR = BASE_DIR / "backups"
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"

# Arquivo do banco de dados
DB_PATH = DATA_DIR / "livraria.db"

# Criação da estrutura de diretórios se não existir
def criar_diretorios():
    for dir_path in [BACKUP_DIR, DATA_DIR, EXPORT_DIR]:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

# Função para criar a tabela 'livros'
def criar_tabela():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

# Função para fazer backup do banco de dados
def fazer_backup():
    backup_nome = f"backup_livraria_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.db"
    backup_path = BACKUP_DIR / backup_nome
    shutil.copy(DB_PATH, backup_path)
    print(f"Backup realizado: {backup_nome}")
    limpar_backups_antigos()

# Função para manter apenas os 5 backups mais recentes
def limpar_backups_antigos():
    backups = sorted(BACKUP_DIR.glob("*.db"), key=os.path.getmtime)
    while len(backups) > 5:
        backup_antigo = backups.pop(0)
        backup_antigo.unlink()
        print(f"Backup removido: {backup_antigo.name}")

# Função para adicionar um novo livro
def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('''
        INSERT INTO livros (titulo, autor, ano_publicacao, preco)
        VALUES (?, ?, ?, ?)
    ''', (titulo, autor, ano_publicacao, preco))
    conexao.commit()
    conexao.close()
    fazer_backup()

# Função para exibir todos os livros
def exibir_livros():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    for livro in livros:
        print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")
    conexao.close()

# Função para atualizar o preço de um livro
def atualizar_preco(titulo, novo_preco):
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('''
        UPDATE livros SET preco = ? WHERE titulo = ?
    ''', (novo_preco, titulo))
    conexao.commit()
    conexao.close()
    fazer_backup()

# Função para remover um livro
def remover_livro(titulo):
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('''
        DELETE FROM livros WHERE titulo = ?
    ''', (titulo,))
    conexao.commit()
    conexao.close()
    fazer_backup()

# Função para buscar livros por autor
def buscar_por_autor(autor):
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('''
        SELECT * FROM livros WHERE autor = ?
    ''', (autor,))
    livros = cursor.fetchall()
    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: {livro[4]}")
    else:
        print(f"Nenhum livro encontrado para o autor: {autor}")
    conexao.close()

# Função para exportar dados para CSV
def exportar_para_csv():
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conexao.close()

    csv_path = EXPORT_DIR / 'livros_exportados.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)
    print(f"Dados exportados para {csv_path}")

# Função para importar dados de um arquivo CSV
def importar_de_csv(csv_path):
    conexao = sqlite3.connect(DB_PATH)
    cursor = conexao.cursor()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Pula o cabeçalho
        for row in reader:
            cursor.execute('''
                INSERT INTO livros (titulo, autor, ano_publicacao, preco)
                VALUES (?, ?, ?, ?)
            ''', (row[1], row[2], int(row[3]), float(row[4])))
    conexao.commit()
    conexao.close()
    fazer_backup()

# Menu principal
def menu():
    criar_diretorios()
    criar_tabela()
    while True:
        print("\n1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano_publicacao, preco)
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            titulo = input("Título do livro para atualizar o preço: ")
            novo_preco = float(input("Novo preço: "))
            atualizar_preco(titulo, novo_preco)
        elif opcao == '4':
            titulo = input("Título do livro para remover: ")
            remover_livro(titulo)
        elif opcao == '5':
            autor = input("Autor: ")
            buscar_por_autor(autor)
        elif opcao == '6':
            exportar_para_csv()
        elif opcao == '7':
            csv_path = input("Caminho do arquivo CSV para importar: ")
            importar_de_csv(csv_path)
        elif opcao == '8':
            fazer_backup()
        elif opcao == '9':
            break
        else:
            print("Opção inválida!")

# Executar o menu
menu()
