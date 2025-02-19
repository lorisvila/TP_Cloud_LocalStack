import os
import boto3

ENDPOINT_URL = 'http://localhost:4566'
REGION = 'us-east-1'

class App():
    def __init__(self):
        import s3
        import sqs
        import db
        import tp
        print('Lancement du script AWS')
        links = {
            's3': {
                'class': s3.S3_Client,
                'client': boto3.client(endpoint_url=ENDPOINT_URL, service_name='s3', region_name=REGION)
            },
            'sqs': {
                'class': sqs.SQS_Client,
                'client': boto3.client(endpoint_url=ENDPOINT_URL, service_name='sqs', region_name=REGION)
            },
            'db': {
                'class': db.DynamoDB_Client,
                'client': boto3.client(endpoint_url=ENDPOINT_URL, service_name='dynamodb', region_name=REGION),
                'ressource': boto3.resource(endpoint_url=ENDPOINT_URL, service_name='dynamodb', region_name=REGION)
            },
            'tp': {
                'class': tp.TP_Program
            }
        }
        menu = 'Menu\n' \
               '- "s3"     --> Utiliser le bucket local S3\n' \
               '- "sqs"    --> Utiliser la file d\'attente locale SQS\n'\
               '- "db"     --> Utiliser la base de donnée local DynamoDB\n'\
               '- "tp"     --> Ce que le TP demande, quand même...'

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Efface l'écran
            print('##################################')
            print(menu)
            user_choice = input('--> ')
            match(user_choice):
                case 'tp':
                    links[user_choice]['class'](ENDPOINT_URL, REGION)
                case choice if user_choice in links:
                    links[choice]['class'](links[choice])
                case _:
                    print('!...Choix non reconnu...!\n\n')
                    input("Appuyez sur Entrée pour continuer...")

if __name__ == '__main__':
    App()