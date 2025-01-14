import socket
import threading
import time
from hashlib import sha256
from trivia_service import fetch_questions
from trivia_provider import transform_questions
from database import Database

class TriviaServer:
    def __init__(self):
        self.clients = []
        self.max_clients = 4
        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.scores = {}
        self.db = Database()

    def start_server(self, host='0.0.0.0', port=12345):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(self.max_clients)
        print(f"Server started on {host}:{port}")

        def handle_client(client_socket):
            client_ip = client_socket.getpeername()[0]
            while True:
                try:
                    message = client_socket.recv(1024).decode('utf-8')
                    if not message:
                        break
                    print(f"Received message from {client_ip}: {message}")
                    if message.startswith("ANSWER:"):
                        self.answers[client_socket] = message.split(":")[1]
                        self.process_answers()
                    elif message.startswith("REGISTER:"):
                        self.handle_register(client_socket, message)
                    elif message.startswith("LOGIN:"):
                        self.handle_login(client_socket, message)
                    elif message == "START_GAME":
                        self.handle_start_game(client_socket)
                except ConnectionResetError:
                    break
            client_socket.close()
            self.clients.remove(client_socket)
            print(f"Client {client_ip} disconnected")
            
        while True:
            if len(self.clients) < self.max_clients:
                try:
                    client_socket, addr = server_socket.accept()
                    self.clients.append(client_socket)
                    self.scores[client_socket] = 0
                    print(f"Connection from {addr}")
                    client_handler = threading.Thread(target=handle_client, args=(client_socket,))
                    client_handler.start()
                except OSError:
                    break
            else:
                print("Server is full")

    def handle_register(self, client_socket, message):
        _, username, password = message.split(":")
        if self.db.get_user(username):
            client_socket.sendall("REGISTER_FAIL".encode('utf-8'))
        else:
            self.db.create_user(username, password)
            client_socket.sendall("REGISTER_SUCCESS".encode('utf-8'))

    def handle_login(self, client_socket, message):
        _, username, password = message.split(":")
        user = self.db.get_user(username)
        if user and user['password'] == password:
            client_socket.sendall("LOGIN_SUCCESS".encode('utf-8'))
        else:
            client_socket.sendall("LOGIN_FAIL".encode('utf-8'))

    def handle_start_game(self, client_socket):
        self.fetch_and_broadcast_questions(10, "Any Difficulty", "Any Type")
        for client in self.clients:
            client.sendall("START_GAME_SUCCESS".encode('utf-8'))

    def broadcast_question(self):
        if not self.clients:
            print("No clients connected. Terminating game.")
            self.end_game()
            return

        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            print(f"Broadcasting question: {question['question']}")
            for client in self.clients:
                client.sendall(f"QUESTION:{question['question']}".encode('utf-8'))
            for client in self.clients:
                for i, answer in enumerate(question['incorrect_answers'] + [question['correct_answer']]):
                    client.sendall(f"ANSWER_{i+1}:{answer}".encode('utf-8'))
            self.current_question_index += 1
            self.start_timer(question['difficulty'])

    def start_timer(self, difficulty):
        timer = 30 if difficulty == "hard" else 25 if difficulty == "medium" else 20
        for t in range(timer, 0, -1):
            for client in self.clients:
                client.sendall(f"TIMER:{t}".encode('utf-8'))
            time.sleep(1)
        self.process_answers()

    def process_answers(self):
        question = self.questions[self.current_question_index - 1]
        correct_answer = question['correct_answer']
        for client, answer in self.answers.items():
            if answer == correct_answer:
                self.scores[client] += 10 * (30 if question['difficulty'] == "hard" else 25 if question['difficulty'] == "medium" else 20)
        self.answers.clear()
        self.broadcast_leaderboard()
        time.sleep(5)
        if self.current_question_index < len(self.questions):
            self.broadcast_question()
        else:
            self.end_game()

    def broadcast_leaderboard(self):
        leaderboard = ",".join([f"{client.getpeername()[0]}:{score}" for client, score in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)])
        print(f"Broadcasting leaderboard: {leaderboard}")
        for client in self.clients:
            client.sendall(f"LEADERBOARD:{leaderboard}".encode('utf-8'))

    def end_game(self):
        winner = max(self.scores, key=self.scores.get)
        for client in self.clients:
            client.sendall(f"END_GAME:Winner is {winner.getpeername()[0]}".encode('utf-8'))
        self.save_game_data()
        time.sleep(5)
        self.reset_game()

    def save_game_data(self):
        for client in self.clients:
            username = client.getpeername()[0]
            score = self.scores[client]
            user_data = self.db.get_user(username)
            if user_data:
                total_points = user_data['totalPoints'] + score
                rounds_played = user_data['roundsPlayed'] + len(self.questions)
                games_played = user_data['gamesPlayed'] + 1
                self.db.update_user(username, total_points, rounds_played, games_played)

    def reset_game(self):
        self.current_question_index = 0
        self.scores.clear()
        self.answers.clear()
        self.fetch_and_broadcast_questions(10, "Any Difficulty", "Any Type")

    def fetch_and_broadcast_questions(self, amount, difficulty, qtype):
        self.questions = transform_questions(fetch_questions(amount, difficulty, qtype))
        self.broadcast_question()
