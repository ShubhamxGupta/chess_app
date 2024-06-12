import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import chess
import chess.pgn
import chess.engine

class ChessApp:
    def __init__(self, root, engine_path):
        self.root = root
        self.root.title("Chess App")
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        
        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.pack(side=tk.LEFT)
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        
        self.selected_piece = None
        self.selected_square = None
        self.highlight_squares = []
        self.last_move = None
        self.ai_difficulty = tk.IntVar(value=2) 

        self.move_list = tk.Listbox(root, height=20, width=30)
        self.move_list.pack(side=tk.RIGHT)

        self.undo_button = tk.Button(root, text="Undo", command=self.undo_move)
        self.undo_button.pack()

        self.save_button = tk.Button(root, text="Save Game", command=self.save_game)
        self.save_button.pack()

        self.load_button = tk.Button(root, text="Load Game", command=self.load_game)
        self.load_button.pack()

        self.difficulty_menu = tk.OptionMenu(root, self.ai_difficulty, 1, 2, 3, 4, 5)
        self.difficulty_menu.pack()

        self.update_board()

    def draw_board(self):
        colors = ["#f0d9b5", "#b58863"]
        for row in range(8):
            for col in range(8):
                x1 = col * 60
                y1 = row * 60
                x2 = x1 + 60
                y2 = y1 + 60
                color = colors[(row + col) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
                
        if self.last_move:
            self.highlight_square(self.last_move.from_square, "#aaf")
            self.highlight_square(self.last_move.to_square, "#aaf")

    def draw_pieces(self):
        piece_symbols = {
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔'
        }
        for square, piece in self.board.piece_map().items():
            row = 7 - (square // 8)
            col = square % 8
            x = col * 60 + 30
            y = row * 60 + 30
            self.canvas.create_text(x, y, text=piece_symbols[piece.symbol()], font=("Arial", 32), fill="black", tags="piece")

    def highlight_square(self, square, color):
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)
        x1 = col * 60
        y1 = row * 60
        x2 = x1 + 60
        y2 = y1 + 60
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color, stipple="gray50")

    def update_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.draw_pieces()

    def on_click(self, event):
        col = event.x // 60
        row = 7 - (event.y // 60)
        self.selected_square = chess.square(col, row)
        piece = self.board.piece_at(self.selected_square)
        if piece:
            self.selected_piece = piece
            self.canvas.tag_raise("piece")
            self.highlight_squares = [move.to_square for move in self.board.legal_moves if move.from_square == self.selected_square]
            self.update_board()
            for square in self.highlight_squares:
                self.highlight_square(square, "#afa")

    def on_drag(self, event):
        if self.selected_piece:
            self.canvas.delete("selected_piece")
            self.canvas.create_text(event.x, event.y, text=self.selected_piece.symbol().upper() if self.selected_piece.color else self.selected_piece.symbol().lower(), font=("Arial", 32), fill="red", tags="selected_piece")

    def on_drop(self, event):
        if self.selected_piece:
            col = event.x // 60
            row = 7 - (event.y // 60)
            target_square = chess.square(col, row)
            move = chess.Move(self.selected_square, target_square)
            if move in self.board.legal_moves:
                if chess.Move.from_uci(f"{chess.square_name(self.selected_square)}{chess.square_name(target_square)}q") in self.board.legal_moves and self.selected_piece.piece_type == chess.PAWN and (row == 0 or row == 7):
                    piece = simpledialog.askstring("Promotion", "Promote to (q, r, b, n):", initialvalue="q")
                    if piece in ["q", "r", "b", "n"]:
                        move = chess.Move(self.selected_square, target_square, promotion=chess.Piece.from_symbol(piece).piece_type)
                self.board.push(move)
                self.last_move = move
                self.update_board()
                self.update_move_list()
                if not self.board.is_game_over():
                    self.computer_move()
                else:
                    self.display_game_over()
            self.selected_piece = None
            self.selected_square = None
            self.highlight_squares = []
            self.update_board()

    def computer_move(self):
        try:
            depth = self.ai_difficulty.get()
            result = self.engine.play(self.board, chess.engine.Limit(depth=depth))
            self.board.push(result.move)
            self.last_move = result.move
            self.update_board()
            self.update_move_list()
            if self.board.is_game_over():
                self.display_game_over()
        except Exception as e:
            print(f"Error in computer move: {e}")
            tk.messagebox.showerror("Error", "An error occurred while making the computer move.")

    def update_move_list(self):
        self.move_list.delete(0, tk.END)
        temp_board = chess.Board()
        for move in self.board.move_stack:
            try:
                san_move = temp_board.san(move)
                temp_board.push(move)
                self.move_list.insert(tk.END, san_move)
            except Exception as e:
                print(f"Error updating move list: {e}")

    def undo_move(self):
        if len(self.board.move_stack) > 1:
            self.board.pop()
            self.board.pop()
            self.update_board()
            self.update_move_list()

    def display_game_over(self):
        result = self.board.result()
        if self.board.is_checkmate():
            message = "Checkmate! "
        elif self.board.is_stalemate():
            message = "Stalemate! "
        elif self.board.is_insufficient_material():
            message = "Insufficient material! "
        elif self.board.is_seventyfive_moves():
            message = "75-move rule! "
        elif self.board.is_fivefold_repetition():
            message = "Fivefold repetition! "
        elif self.board.is_variant_draw():
            message = "Draw! "
        else:
            message = "Game over! "
        message += f"Result: {result}"
        print(message)
        tk.messagebox.showinfo("Game Over", message)

    def save_game(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pgn", filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "w") as f:
                exporter = chess.pgn.StringExporter()
                game = chess.pgn.Game.from_board(self.board)
                game.accept(exporter)
                f.write(str(exporter))

    def load_game(self):
        file_path = filedialog.askopenfilename(filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "r") as f:
                    game = chess.pgn.read_game(f)
                    self.board = game.board()
                    for move in game.mainline_moves():
                        self.board.push(move)
                    self.update_board()
                    self.update_move_list()
            except Exception as e:
                print(f"Error loading game: {e}")
                tk.messagebox.showerror("Error", "An error occurred while loading the game.")

    def __del__(self):
        self.engine.quit()

if __name__ == "__main__":
    engine_path = r"stockfish\stockfish-windows-x86-64-avx2.exe"
    root = tk.Tk()
    app = ChessApp(root, engine_path)
    root.mainloop()
