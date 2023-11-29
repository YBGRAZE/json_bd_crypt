import json
import os
import base64

class SimpleEncryptor:
    def __init__(self, key):
        self.key = key

    def encrypt(self, data):
        key_bytes = self.key.encode('utf-8')
        data_bytes = data.encode('utf-8')

        encrypted_bytes = bytearray()
        for i in range(len(data_bytes)):
            encrypted_bytes.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return base64.b64encode(encrypted_bytes).decode('utf-8')

    def decrypt(self, encrypted_data):
        key_bytes = self.key.encode('utf-8')
        encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))

        decrypted_bytes = bytearray()
        for i in range(len(encrypted_bytes)):
            decrypted_bytes.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])

        return decrypted_bytes.decode('utf-8')

class JSONDatabase:
    def __init__(self, filename, pin=None):
        self.filename = filename
        self.key = self.generate_key(pin)
        self.encryptor = SimpleEncryptor(self.key)
        self.load_from_file()

    def generate_key(self, pin):
        return base64.b64encode(pin.encode('utf-8')).decode('utf-8')

    def encrypt(self, data):
        return self.encryptor.encrypt(data)

    def decrypt(self, data):
        return self.encryptor.decrypt(data)

    def set_value(self, *args, value):
        current_node = self.data

        for arg in args[:-1]:
            if arg not in current_node:
                current_node[arg] = {}
            current_node = current_node[arg]

        current_node[args[-1]] = value
        self.save_to_file()

    def edit_value(self, *args, new_value):
        current_node = self.data

        for arg in args[:-1]:
            if arg not in current_node:
                raise KeyError(f"Path {'/'.join(args)} not found in the database.")

            current_node = current_node[arg]

        if args[-1] not in current_node:
            raise KeyError(f"Key '{args[-1]}' not found in the path {'/'.join(args)}.")

        current_node[args[-1]] = new_value
        self.save_to_file()

    def read_value(self, *args):
        current_node = self.data

        for arg in args:
            if arg not in current_node:
                current_node[arg] = {}
            current_node = current_node[arg]

        return current_node

    def save_to_file(self):
        directory = os.path.dirname(self.filename)
        os.makedirs(directory, exist_ok=True)

        encrypted_data = self.encrypt(json.dumps(self.data))
        with open(self.filename, 'w') as file:
            file.write(encrypted_data)

    def load_from_file(self):
        try:
            with open(self.filename, 'r') as file:
                encrypted_data = file.read()

            decrypted_data = self.decrypt(encrypted_data)
            self.data = json.loads(decrypted_data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

# Пример использования:


db = JSONDatabase(pin="123456", filename="./database.json") # Инициализация бд с использованием пина(ставьте на свое усмотрение, можно до бесконечности наверное)

db.set_value("ram", value=1000) # Установка значения без создания подкаталогов

db.set_value("storage", "ssd", value=256) # Установка значения с созданием подкаталогов

db.edit_value("storage", "ssd", new_value=512) # Изменение значения

# Чтение значения из подкаталога ssd
value = db.read_value("storage", "ssd")
print(value)
