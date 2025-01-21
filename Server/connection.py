import socket
import threading
import time
import json
from hashlib import sha256
from trivia_service import fetch_questions
from trivia_provider import transform_questions
from database import Database
import random

class TriviaServer:
    def __init__(self):
        self.clients = []
        self.max_clients = 4
        self.questions = []
        self.current_question_index = 0
        self.answers = {}
        self.scores = {}
        self.db = Database()
        self.game_ongoing = False
        self.received_answers = []
        self.logged_in_clients = {}

    def start_server(self, host='0.0.0.0', port=12346):
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
                    self.handle_message(client_socket, message)
                except ConnectionResetError:
                    break
            client_socket.close()
            self.clients.remove(client_socket)
            self.scores.pop(client_socket, None)
            self.logged_in_clients.pop(client_socket, None)
            print(f"Client {client_ip} disconnected")
            
        while True:
            if len(self.clients) < self.max_clients and not self.game_ongoing:
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
                client_socket, addr = server_socket.accept()
                if self.game_ongoing:
                    print("Game is ongoing, new connections are not allowed.")
                    client_socket.sendall("GAME_ONGOING".encode('utf-8'))
                else:
                    print("Server is full")
                    client_socket.sendall("SERVER_FULL".encode('utf-8'))
                client_socket.close()

    def handle_message(self, client_socket, message):
        if message.startswith("ANSWER:"):
            self.received_answers.append((client_socket, message.split(":")[1]))
        elif message.startswith("REGISTER:"):
            self.handle_register(client_socket, message)
        elif message.startswith("LOGIN:"):
            self.handle_login(client_socket, message)
        elif message.startswith("START_GAME:"):
            settings = json.loads(message.split(":", 1)[1])
            self.handle_start_game(client_socket, settings)
        elif message.startswith("GET_LEADERBOARD:"):
            order_by = message.split(":")[1]
            self.handle_get_leaderboard(client_socket, order_by)
        elif message.startswith("GET_USERNAMES"):
            self.handle_get_usernames(client_socket)

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
            self.db.update_user_ip(username, client_socket.getpeername()[0], time.strftime('%Y-%m-%d %H:%M:%S'))
            client_socket.sendall("LOGIN_SUCCESS".encode('utf-8'))
            self.logged_in_clients[client_socket] = username
        else:
            client_socket.sendall("LOGIN_FAIL".encode('utf-8'))

    def handle_start_game(self, client_socket, settings):
        self.game_ongoing = True 
        amount = settings.get("amount", 10)
        difficulty = settings.get("difficulty", "Any Difficulty")
        qtype = settings.get("type", "Any Type")
        self.notify_game_start()
        threading.Thread(target=self.fetch_and_broadcast_questions, args=(amount, difficulty, qtype)).start()

    def notify_game_start(self):
        for client in self.clients:
            client.sendall("GAME_START".encode('utf-8'))

    def broadcast_question(self):
        if not self.clients:
            print("No clients connected. Terminating game.")
            self.end_game()
            return

        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            print(f"Broadcasting question: {question['question']}")
            answers = question['incorrect_answers'] + [question['correct_answer']]
            random.shuffle(answers) 

            for client in self.clients:
                client.sendall(f"QUESTION:{question['difficulty'].capitalize()} | {question['question']}".encode('utf-8'))
                for i, answer in enumerate(answers):
                    client.sendall(f"ANSWER_{i+1}:{answer}".encode('utf-8'))
            self.current_question_index += 1
            threading.Thread(target=self.start_timer, args=(question['difficulty'],)).start()

    def start_timer(self, difficulty):
        timer = 30 if difficulty == "hard" else 25 if difficulty == "medium" else 20
        if not self.clients:
            print("No clients connected. Terminating game.")
            self.end_game()
            return
        for t in range(timer, -1, -1):
            for client in self.clients:
                client.sendall(f"TIMER:{t}".encode('utf-8'))
            if t > 0:
                time.sleep(1)
            else:
                self.process_received_answers()
                threading.Thread(target=self.start_next_round).start()
    
    def start_next_round(self):
        time.sleep(5)
        if self.current_question_index < len(self.questions):
            self.broadcast_question()
        else:
            self.end_game()

    def process_received_answers(self):
        question = self.questions[self.current_question_index - 1]
        correct_answer = question['correct_answer']
        print(f"Processing answers for question: {question['question']}")
        print(f"Correct answer: {correct_answer}")
        print(f"Received answers: {self.received_answers}")
        if not self.clients:
            print("No clients connected. Terminating game.")
            self.end_game()
            return
        if not self.received_answers:
            print("No answers received.")
        for client, answer in self.received_answers:
            print(f"Client {client.getpeername()[0]} answered: {answer}")
            if answer == correct_answer:
                self.scores[client] += 10 * (30 if question['difficulty'] == "hard" else 25 if question['difficulty'] == "medium" else 20)
        for client in self.clients:
            client.sendall(f"ANSWER_RESULT:correct:{correct_answer}".encode('utf-8'))
        self.received_answers.clear()
        self.broadcast_leaderboard()

    def broadcast_leaderboard(self):
        valid_clients = [client for client in self.clients if client.fileno() != -1]
        leaderboard = ",".join([f"{self.db.get_user_by_ip(client.getpeername()[0])['username']}:{score}" for client, score in sorted(self.scores.items(), key=lambda item: item[1], reverse=True) if client in valid_clients])
        print(f"Broadcasting leaderboard: {leaderboard}")
        for client in valid_clients:
            client.sendall(f"LEADERBOARD:{leaderboard}".encode('utf-8'))

    def end_game(self):
        if self.clients and self.scores:
            winner = max(self.scores, key=self.scores.get)
            winner_username = self.db.get_user_by_ip(winner.getpeername()[0])['username']
            self.save_game_data()
            for client in self.clients:
                client.sendall(f"END_GAME:Winner is {winner_username}!".encode('utf-8'))
                self.scores[client] = 0
        else:
            print("No clients or scores available to determine a winner.")
        print("Ending game...")
        time.sleep(2)
        self.send_players_to_lobby()
        self.game_ongoing = False

    def send_players_to_lobby(self):
        for client in self.clients:
            client.sendall("RETURN_TO_LOBBY".encode('utf-8'))
        self.reset_game()

    def reset_game(self):
        self.current_question_index = 0
        self.answers.clear()
        self.questions.clear()

    def save_game_data(self):
        for client in self.clients:
            score = self.scores[client]
            user_data = self.db.get_user_by_ip(client.getpeername()[0])
            print(f"Saving game data for {user_data['username']} with score {score}")
            if user_data:
                total_points = user_data['totalPoints'] + score
                rounds_played = user_data['roundsPlayed'] + len(self.questions)
                games_played = user_data['gamesPlayed'] + 1
                print(f"Updating user {user_data['username']}: totalPoints={total_points}, roundsPlayed={rounds_played}, gamesPlayed={games_played}")
                self.db.update_user(user_data['username'], total_points, rounds_played, games_played)
            else:
                print(f"No user data found for {user_data['username']}")

    def fetch_and_broadcast_questions(self, amount, difficulty, qtype):
        self.questions = transform_questions(fetch_questions(amount, difficulty, qtype))
        print(f"Broadcasting {len(self.questions)} questions")
        self.broadcast_question()

    def handle_get_leaderboard(self, client_socket, order_by):
        print(f"Fetching leaderboard for {order_by}...")
        leaderboard_data = self.db.get_leaderboard(order_by)
        print(f"Sending leaderboard data: {leaderboard_data}")
        message = ','.join([f'{entry[0]}:{entry[1]}' for entry in leaderboard_data])
        client_socket.sendall(f"{message}".encode('utf-8'))

    def handle_get_usernames(self, client_socket):
        usernames = []
        for client in self.logged_in_clients:
            if client.fileno() != -1:
                usernames.append(self.logged_in_clients[client])
        usernames_str = ",".join(usernames)
        client_socket.sendall(f"{usernames_str}".encode('utf-8'))
