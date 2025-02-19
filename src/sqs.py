import os

class SQS_Client():

    currentQueue = ""
    client = None

    def __init__(self, object):
        self.client = object['client']

        links = {
            'select': self.selectQueue,
            'list': self.listQueues,
            'receive': self.receiveMessage,
            'create': self.createQueue,
            'send': self.sendMessage
        }
        menu = 'Menu\n' \
               '- "select"    --> Selectionner une file d\'attente\n' \
               '- "list"      --> Lister les files d\'attentes\n' \
               '- "create"    --> Créer une file d\'attentes\n' \
               '- "receive"   --> Lire message depuis la file d\'attente\n'\
               '- "send"      --> Envoyer message dans la file d\'attente\n'\
               '- "delete"    --> Effacer message dans une file d\'attente\n' \
               '- "exit"      --> Quitter le menu'

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Efface l'écran
            print('################ SQS ################')
            print(menu)
            print(f'Queue sélectionnée : {self.currentQueue}\n' if self.currentQueue else '', end='')
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

    def checkQueueSelected(self):
        if self.currentQueue == "":
            self.selectQueue()

    def selectQueue(self):
        self.currentQueue = '' + input('Queue à utiliser --> ')

    def listQueues(self):
        queues = self.client.list_queues()
        if queues['QueueUrls']:
            for queue in queues['QueueUrls']:
                print(queue)
        else:
            print('Pas de queue sur le SQS')
        input("Appuyez sur Entrée pour continuer...")

    def receiveMessage(self):
        self.checkQueueSelected()
        messages = self.client.receive_message(QueueUrl=self.currentQueue)
        print(messages)
        input("Appuyez sur Entrée pour continuer...")

    def sendMessage(self):
        self.checkQueueSelected()
        message = input('Quel est le message a envoyer sur le SQS ? --> ')
        self.client.send_message(QueueUrl=self.currentQueue, MessageBody=message)
        print('Le message a bien été envoyé !')
        input("Appuyez sur Entrée pour continuer...")

    def createQueue(self):
        queueName = input('Comment va s\'apeller la queue ? --> ')
        self.client.create_queue(QueueName=queueName)
        input("Appuyez sur Entrée pour continuer...")