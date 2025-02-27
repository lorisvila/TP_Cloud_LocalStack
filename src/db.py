import os

import botocore
from botocore.client import BaseClient


class DynamoDB_Client():

    currentTable = ""
    client = None

    def __init__(self, object):
        self.client = object['client']
        self.ressource = object['ressource']

        links = {
            'select': self.selectTable,
            'listTables': self.listTables,
            'createTable': self.createTable,
            'list': self.listFromTable,
            'add': self.addDataToTable
        }
        menu = 'Menu\n' \
               '- "select"       --> Selectionner une table\n' \
               '- "list"         --> Lister toutes les valeurs d\'une table\n'\
               '- "add"          --> Ajouter un élement dans la table\n'\
               '- "listTables"   --> Lister les tables\n' \
               '- "createTable"  --> Créer une table\n'\
               '- "exit"         --> Quitter le menu'

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Efface l'écran
            print('################ Dynamo DB ################')
            print(menu)
            print(f'Table sélectionnée : {self.currentTable}\n' if self.currentTable else '', end='')
            user_choice = input('--> ')
            if user_choice == "exit":
                break
            elif links.__contains__(user_choice):
                print('\n')
                links[user_choice]()
                print('\n')
            else:
                print('Choix non reconnu...')
                input("Appuyez sur Entrée pour continuer...")

    def checkTableSelected(self):
        if self.currentTable == "":
            self.selectTable()

    def selectTable(self):
        self.currentTable = '' + input('Table à utiliser --> ')

    def listTables(self):
        tables = self.client.list_tables()
        if tables['TableNames']:
            for table in tables['TableNames']:
                print(table)
        else:
            print('Pas de tables présentes dans la base de données')
        input("Appuyez sur Entrée pour continuer...")

    def createTable(self):
        tableName = str(input('Table name --> '))
        indexName = str(input('Index column name --> '))
        self.client.create_table(
            TableName=tableName,
            KeySchema=[
                {
                    'AttributeName': indexName,  # Partition key is often used as the Primary key
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': indexName,
                    'AttributeType': 'N'  # N for Number (int)
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table created successfully")
        input("Appuyez sur Entrée pour continuer...")

    def listFromTable(self):
        self.checkTableSelected()
        table = self.ressource.Table(self.currentTable)
        response = table.scan()
        if not response['Items']:
            print("La table est vide...")
            input("Appuyez sur Entrée pour continuer...")
            return
        for item in response['Items']:
            print(item)
        input("Appuyez sur Entrée pour continuer...")


    def addDataToTable(self):
        self.checkTableSelected()
        print(self.get_key_schema(self.currentTable))
        item = {}
        while True:
            print('Choix :\n'
                  '- "add" --> Ajouter une nouvelle clé\n'
                  '- "exit" --> Quitter le menu d\'ajout d\'élements\n'
                  '- "send" --> Envoyer la requête')
            print(f'Item à envoyer : {item}')
            choice = str(input('--> '))
            match choice:
                case 'add':
                    key = input('Key name --> ')
                    value = input('Value --> ')
                    type =  input('Type (S = string, N = numeric) --> ')
                    item[key] = {type: value}
                case 'exit':
                    return
                case 'send':
                    if not item:
                        print("Il faut au moins une clé pour l'envoi de la requête.")
                        continue
                    self.client.put_item(TableName=self.currentTable, Item=item)
                    print("L'élement a bien été rajouté dans la table")
                    break
                case _:
                    print('...Choix non reconnu...')
        input("Appuyez sur Entrée pour continuer...")

    def get_key_schema(self, table_name):
        try:
            table = self.ressource.Table(table_name)
            return table.key_schema
        except botocore.errorfactory.ResourceNotFoundException:
            return "!!!! - The table doesn't exist... - !!!!"

