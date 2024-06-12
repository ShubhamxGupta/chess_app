import tkinter as tk
import chess
import chess.engine

class ChessApp:
    def __init__(self, root, engine_path):
        self.root = root
        self.root.title("Chess App")
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        
        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.pack()
        
        self.update_board()
        
        self.move_entry = tk.Entry(root)
        self.move_entry.pack()
        
        self.move_button = tk.Button(root, text="Make Move", command=self.make_move)
        self.move_button.pack()

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
            self.canvas.create_text(x, y, text=piece_symbols[piece.symbol()], font=("Arial", 32), fill="black")

    def update_board(self):
        self.canvas.delete("all")
        self.draw_board()
        self.draw_pieces()
        
    def make_move(self):
        move = self.move_entry.get()
        try:
            self.board.push_san(move)
            self.update_board()
            if not self.board.is_game_over():
                self.computer_move()
        except ValueError:
            print("Invalid move")
    
    def computer_move(self):
        result = self.engine.play(self.board, chess.engine.Limit(time=2.0))
        self.board.push(result.move)
        self.update_board()
        if self.board.is_game_over():
            print("Game over!")
            print("Result: ", self.board.result())

    def __del__(self):
        self.engine.quit()

if __name__ == "__main__":
    engine_path = r"D:\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
    root = tk.Tk()
    app = ChessApp(root, engine_path)
    root.mainloop()