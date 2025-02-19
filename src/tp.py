import os
import boto3
import datetime
from botocore.exceptions import ClientError


class TP_Program():

    def __init__(self, ENDPOINT_URL, REGION):
        self.ENDPOINT_URL = ENDPOINT_URL
        self.REGION = REGION
        self.queue_url = None  # Sera initialisé lors de la vérification de SQS
        links = {
            'lancer': self.lancer,
        }
        menu = ('Menu\n'
                '- "lancer" --> Lancer le script\n'
                '- "exit" --> Quitter le menu')

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('################ TP ################')
            print(menu)
            user_choice = input('--> ')
            match user_choice:
                case 'exit':
                    break
                case choice if user_choice in links:
                    print('\n')
                    links[choice]()
                    input("\nAppuyez sur Entrée pour continuer...")
                case _:
                    print('Choix non reconnu...')
                    input("Appuyez sur Entrée pour continuer...")

    # Fonction principale
    def lancer(self):
        file_name = input("Entrez le nom du fichier à traiter: ")

        print("\nVérification des ressources...")
        self.check_and_create_bucket()
        self.check_and_create_queue()
        self.check_and_create_table()

        print(f"\nDébut du traitement pour {file_name}")
        self.upload_file_to_s3(file_name)
        self.retrieve_file_from_s3(file_name)
        self.add_dynamodb_entry(file_name)
        self.read_dynamodb_entries()
        self.send_sqs_message(file_name)

    def check_and_create_bucket(self):
        s3 = boto3.client(
            's3',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        bucket_name = 'data'
        try:
            s3.head_bucket(Bucket=bucket_name)
            print(f"- Bucket '{bucket_name}' exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"- Creating bucket {bucket_name}...")
                try:
                    if self.REGION == 'us-east-1':
                        s3.create_bucket(Bucket=bucket_name)
                    else:
                        s3.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={
                                'LocationConstraint': self.REGION
                            }
                        )
                    print(f"✓ Bucket '{bucket_name}' created")
                except Exception as create_error:
                    print(f"Error creating bucket: {create_error}")
                    raise

    def check_and_create_queue(self):
        sqs = boto3.client(
            'sqs',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        queue_name = 'processQueue'
        try:
            response = sqs.get_queue_url(QueueName=queue_name)
            self.queue_url = response['QueueUrl']
            print(f"- Queue '{queue_name}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                print(f"- Creating queue {queue_name}...")
                try:
                    response = sqs.create_queue(QueueName=queue_name)
                    self.queue_url = response['QueueUrl']
                    print(f"✓ Queue '{queue_name}' created")
                except Exception as create_error:
                    print(f"Error creating queue: {create_error}")
                    raise
            else:
                raise

    def check_and_create_table(self):
        dynamodb = boto3.client(
            'dynamodb',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        table_name = 'dataTracker'
        try:
            if table_name not in dynamodb.list_tables()['TableNames']:
                print(f"- Creating table {table_name}...")
                dynamodb.create_table(
                    TableName=table_name,
                    KeySchema=[{'AttributeName': 'FileName', 'KeyType': 'HASH'}],
                    AttributeDefinitions=[
                        {'AttributeName': 'FileName', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                waiter = dynamodb.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                print(f"✓ Table '{table_name}' created")
            else:
                print(f"- Table '{table_name}' exists")
        except Exception as e:
            print(f"Error checking/creating table: {e}")
            raise

    def upload_file_to_s3(self, file_name):
        s3 = boto3.client(
            's3',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        try:
            s3.upload_file(file_name, 'data', file_name)
            print(f"✓ Fichier {file_name} uploadé vers S3")
        except Exception as e:
            print(f"Erreur upload S3: {e}")
            raise

    def retrieve_file_from_s3(self, file_name):
        s3 = boto3.client(
            's3',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        try:
            s3.head_object(Bucket='data', Key=file_name)
            print(f"✓ Fichier {file_name} trouvé dans S3")
        except Exception as e:
            print(f"Erreur accès fichier S3: {e}")
            raise

    def add_dynamodb_entry(self, file_name):
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        table = dynamodb.Table('dataTracker')
        try:
            table.put_item(
                Item={
                    'FileName': file_name,
                    'Timestamp': datetime.datetime.now().isoformat(),
                    'Status': 'UPLOADED'
                }
            )
            print(f"✓ Entrée DynamoDB ajoutée")
        except Exception as e:
            print(f"Erreur écriture DynamoDB: {e}")
            raise

    def read_dynamodb_entries(self):
        dynamodb = boto3.resource(
            'dynamodb',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        table = dynamodb.Table('dataTracker')
        try:
            response = table.scan()
            print("\nContenu de la table DynamoDB:")
            for item in response['Items']:
                print(f"- {item['FileName']} ({item['Timestamp']})")
        except Exception as e:
            print(f"Erreur lecture DynamoDB: {e}")
            raise

    def send_sqs_message(self, file_name):
        sqs = boto3.client(
            'sqs',
            endpoint_url=self.ENDPOINT_URL,
            region_name=self.REGION
        )
        try:
            sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=f"Traitement requis pour {file_name}"
            )
            print("✓ Message envoyé à SQS")
        except Exception as e:
            print(f"Erreur envoi SQS: {e}")
            raise