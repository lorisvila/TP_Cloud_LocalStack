import os


class S3_Client():

    currentBucket = ""
    client = None

    def __init__(self, object):
        self.client = object['client']

        links = {
            'select': self.selectBucket,
            'create': self.createBucket,
            'list': self.listFiles,
            'listBuckets': self.listBuckets,
            'upload': self.uploadFile,
            'download': self.downloadFile
        }
        menu = 'Menu\n' \
               '- "select"      --> Selectionner un bucket\n' \
               '- "create"      --> Créer un bucket S3\n' \
               '- "list"        --> Lister les fichiers sur le bucket sélectionné\n' \
               '- "listBuckets" --> Uploader un fichier vers le bucket S3\n' \
               '- "upload"      --> Uploader un fichier vers le bucket S3\n' \
               '- "download"    --> Télécharger un fichier depuis le bucket S3\n'\
               '- "exit"      --> Quitter le menu'

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Efface l'écran
            print('################ S3 Bucket ################')
            print(menu)
            print(f'Bucket sélectionné : {self.currentBucket}\n' if self.currentBucket else '', end='')
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

    def checkBucketSelected(self):
        if self.currentBucket == "":
            self.selectBucket()

    def selectBucket(self):
        self.currentBucket = input('Bucket à utiliser --> ')

    def createBucket(self):
        bucket_name = input('Quel est le nom du bucket à créer ? --> ')
        self.client.create_bucket(Bucket=bucket_name)
        print(f"Le bucket {bucket_name} a bien été crée !")
        input("Appuyez sur Entrée pour continuer...")

    def listBuckets(self):
        buckets = self.client.list_buckets()
        if buckets['Buckets']:
            print('Liste des buckets présent sur le S3 :')
            for bucket in buckets['Buckets']:
                print(bucket)
        else:
            print("Il n'y a pas de bucket actuellement sur le S3")
        input("Appuyez sur Entrée pour continuer...")

    def listFiles(self):
        self.checkBucketSelected()
        files = self.client.list_objects(Bucket=self.currentBucket)
        if files:
            print(f'Liste des fichiers sur le Bucket {self.currentBucket} S3 :')
            for file in files['Contents']:
                print(file)
        else:
            print("Il n'y a pas de fichier actuellement sur le Bucket")
        input("Appuyez sur Entrée pour continuer...")

    def uploadFile(self):
        self.checkBucketSelected()
        path = input('Chemin d\'accès du fichier ? --> ')
        nomFichier = path.split('/')[-1]
        self.client.upload_file(path, Bucket=self.currentBucket, Key=nomFichier)
        print(f'Le fichier a bien été uploadé sur le bucket {self.currentBucket}')
        input("Appuyez sur Entrée pour continuer...")

    def downloadFile(self):
        self.checkBucketSelected()
        nomFichierDistant = input('Nom du fichier sur le bucket --> ')
        self.client.download_file(Key=nomFichierDistant, Bucket=self.currentBucket, Filename=nomFichierDistant)
        input("Appuyez sur Entrée pour continuer...")
