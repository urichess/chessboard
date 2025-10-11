import time
import threading
import berserk
from berserk.exceptions import ResponseError
import chess
from datetime import datetime, timezone

class LichessConnector:
    def __init__(self, token: str):
        self.session = berserk.TokenSession(token)
        self.client = berserk.Client(session=self.session)
        # self.start_event_listener()

    def getUsername(self) -> str:
        account_info = self.client.account.get()
        return account_info["username"]

    def createGame(self):
        pass

    def findGame(self) -> 'LichessConnector.LichessGame':
        try:
            for event in self.client.board.stream_incoming_events():
                if event["type"] == "gameStart":
                    new_game_id = event["game"]["id"]
                    print(f"New game detected: {new_game_id}")
                    return self.LichessGame(self, event)
        except Exception as e:
            print(f"[findGame] event listener error {e}")
            return None

    def start_event_listener(self):
        def listen():
            print("[Event Listener] Listening to incoming events...")
            try:
                for event in self.client.board.stream_incoming_events():
                    print("[Lichess Event]", event)
            except Exception as e:
                print(f"[Event Listener Error] {e}")

        listener_thread = threading.Thread(target=listen, daemon=True)
        listener_thread.start()

    class LichessGame:
        def __init__(self, connector, event_start: dict):
            self.connector = connector
            self.event_start = event_start
            print(event_start)
            #{'type': 'gameStart', 'game': {'fullId': '9zQU8L09BUnp', 'gameId': '9zQU8L09', 'fen': 'r1bqkbnr/ppp2ppp/8/4Q3/2P5/4P3/PP1P2PP/RNB1KB1R b KQkq - 0 7', 'color': 'black', 'lastMove': 'h5e5', 'source': 'ai', 'status': {'id': 20, 'name': 'started'}, 'variant': {'key': 'standard', 'name': 'Standard'}, 'speed': 'correspondence', 'perf': 'correspondence', 'rated': False, 'hasMoved': True, 'opponent': {'id': None, 'username': 'Stockfish level 8', 'ai': 8}, 'isMyTurn': True, 'compat': {'bot': False, 'board': True}, 'id': '9zQU8L09'}}


            self.initialPosition = event_start["game"]["fen"]
            self.current_board = chess.Board(self.initialPosition)
            self.board_lock = threading.Lock()
            self.turn_event = threading.Event()

            if event_start["game"]["isMyTurn"] == True:
                self.isMyTurn = True
                self.myColor = self.current_board.turn

                print(self.current_board)
                print("Your turn")
            else:
                self.isMyTurn = False
                if self.current_board.turn == "white":
                    self.myColor = "black"
                else:
                    self.myColor = "white"

            self.finished = False


            self.game_id = event_start["game"]["id"]
            self.thread = threading.Thread(target=self._monitor_game, daemon=True)
            self.start()
            time.sleep(0.5)

        def start(self):
            #print(f"[LichessGame] Starting game state monitor for game {self.game_id}")
            self.thread.start()
            

        def finished(self):
            return self.finished


        def waitMyTurn(self) -> chess.Board:
            if not self.isMyTurn and self.finished == False:
                print("Opponent's turn. Wait.")
                self.turn_event.wait()  # Blocks until it's your turn

            with self.board_lock:
                if self.finished:
                    return None
                else:
                    return self.current_board.copy(stack=True)
                           


        def sendMove(self, move: str):
            try:
                
                with self.board_lock:
                    self.connector.client.board.make_move(self.game_id, move)
                    self.isMyTurn = False
                    self.turn_event.clear()
                    
                print(f"Move {move} sent to game {self.game_id}.")
            except ResponseError as e:
                print(f"Failed to send move {move} to game {self.game_id}: {e}")

        def _monitor_game(self):
            while True:
                try:
                    for event in self.connector.client.board.stream_game_state(self.game_id):
                        #print(f"[Game {self.game_id} Event]", event)
                        if event.get("state"):
                            self.processEventState(event["state"])
                        else:
                            if event["type"] == "gameState":
                                self.processEventState(event)
                    
                        
                except Exception as e:
                    print(f"[LichessGame Error] {e}")

        def print_game_state(self, game_state):
            def to_seconds(value):
                if isinstance(value, datetime):
                    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
                    return int((value - epoch).total_seconds())
                return int(value)

            def format_time(seconds):
                h = seconds // 3600
                m = (seconds % 3600) // 60
                s = seconds % 60
                return f"{h}:{m:02}:{s:02}"

            moves = game_state.get('moves', '').split()
            last_move = moves[-1] if moves else '(no moves)'

            wtime = to_seconds(game_state['wtime'])
            btime = to_seconds(game_state['btime'])
            winc = to_seconds(game_state['winc'])
            binc = to_seconds(game_state['binc'])

            print(
                f"[{game_state['status'].upper()}] Last: {last_move} | "
                f"W: {format_time(wtime)} (+{winc}s) | B: {format_time(btime)} (+{binc}s)"
            )

            

           

        def processEventState(self, event):
            lastGameEvent = event
        #{'type': 'gameState', 'moves': 'e2e4 c7c5 g1f3 d7d6 d2d3 e7e5 f1e2 f8e7', 'wtime': datetime.datetime(1970, 1, 25, 20, 31, 23, 647000, tzinfo=datetime.timezone.utc), 'btime': datetime.datetime(1970, 1, 25, 20, 31, 23, 647000, tzinfo=datetime.timezone.utc), 'winc': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'binc': datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc), 'status': 'started'}


            self.print_game_state(event)

            status = event.get("status", "started")
            if status != "started":
                print(f"Game ended or aborted with status: {status}")
                self.finished = True
                with self.board_lock:
                    self.turn_event.set()  # Notify waitMyTurn()
                    
            else:
                #board = chess.Board(self.initialPosition)
                board = chess.Board()
                moves = event["moves"].strip().split()
                for move in moves:
                    board.push_uci(move)

                if board.turn == self.myColor:
                    with self.board_lock:
                        self.current_board = board
                        self.isMyTurn = True
                        self.turn_event.set()  # Notify waitMyTurn()
#                else:
#                    print ("Waitting opponent's move")
