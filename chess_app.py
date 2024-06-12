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
        
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)
        
        self.selected_piece = None
        self.selected_square = None

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
                self.board.push(move)
                self.update_board()
                if not self.board.is_game_over():
                    self.computer_move()
            self.selected_piece = None
            self.selected_square = None

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