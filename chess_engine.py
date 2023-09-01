import copy


class Piece:

    def __init__(self, color: int, file_path: str = None):
        self.color = color
        self.file_path = file_path

    def get_moves(self, position: tuple[int, int], chessboard) -> list[tuple[int, int]]:
        raise NotImplementedError("Subclasses must implement get_moves()")

    def get_symbol(self):
        return ""


class Square:

    def __init__(self, piece=None):
        self.piece = piece

    def is_empty(self) -> bool:
        return self.piece is None

    def get_piece(self) -> Piece | None:
        return self.piece


class ChessBoard:
    def __init__(self):

        self.board = [
            [Square() for _ in range(8)] for _ in range(8)
        ]

    def get_square(self, rank: int, file: int) -> Square:
        return self.board[rank][file]

    def get_piece(self, rank: int, file: int) -> Piece | None:
        return self.board[rank][file].piece

    def starting_position(self):
        self.generate_position_from_fen(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

    def empty_board(self):
        self.board = [
            [Square() for _ in range(8)] for _ in range(8)
        ]

    def generate_position_from_fen(self, fen: str):
        self.empty_board()

        rank = 0
        file = 0

        pieces = {
            "p": Pawn(0), "q": Queen(0), "r": Rook(0), "k": King(0), "n": Knight(0), "b": Bishop(0),
            "P": Pawn(1), "Q": Queen(1), "R": Rook(1), "K": King(1), "N": Knight(1), "B": Bishop(1)
        }

        for c in fen:
            if c.isnumeric():
                file += int(c)
            elif c == "/":
                rank += 1
                file = 0
            else:
                self.board[rank][file] = Square(pieces[c])
                file += 1

    def print_board(self):
        for row in self.board:
            row_str = ""
            for square in row:
                piece = square.get_piece()
                if piece is None:
                    row_str += " -"
                else:
                    row_str += " " + piece.get_symbol()
            print(row_str)

    def move_piece(self, starting_square: tuple[int, int], dest_square: tuple[int, int], no_check: bool = False):
        piece = self.get_square(*starting_square).get_piece()

        if not piece:
            return
        color = piece.color

        if no_check:
            self.board[dest_square[0]][dest_square[1]
                                       ] = self.board[starting_square[0]][starting_square[1]]
            self.board[starting_square[0]][starting_square[1]] = Square()
            return

        legal_moves = self.get_all_legal_moves(color)
        if dest_square in legal_moves[starting_square]:
            self.board[dest_square[0]][dest_square[1]
                                       ] = self.board[starting_square[0]][starting_square[1]]
            self.board[starting_square[0]][starting_square[1]] = Square()

    def check_for_checks(self, color: int):
        king_pos = None
        for rank in range(8):
            for file in range(8):
                piece = self.get_square(rank, file).get_piece()
                if not piece:
                    continue
                if type(piece) == King and piece.color == color:
                    king_pos = rank, file

        legal_moves = self.get_all_legal_moves(
            0 if color else 1, no_check=True, to_list=True)

        if king_pos in legal_moves:
            return True

        return False

    def get_all_legal_moves(self, color: int, no_check: bool = False, to_list: bool = False) \
            -> dict[tuple[int, int], list[tuple[int, int]]] | list[tuple[int, int]]:
        moves = {}

        for rank in range(8):
            for file in range(8):
                piece = self.get_square(rank, file).get_piece()
                if piece and piece.color == color:
                    moves[(rank, file)] = piece.get_moves(
                        position=(rank, file), chessboard=self)

        if no_check:
            if to_list:
                moves_list = []
                for i in moves.values():
                    moves_list.extend(i)

                return moves_list
            return moves

        legal_moves = {}

        for starting_square in moves.keys():
            legal_moves[starting_square] = []
            for dest_square in moves[starting_square]:
                temp = ChessBoard()
                temp.board = copy.deepcopy(self.board)
                temp.move_piece(starting_square, dest_square, True)
                if not temp.check_for_checks(color):
                    legal_moves[starting_square].append(dest_square)

        if to_list:
            moves_list = []
            for i in legal_moves.values():
                moves_list.extend(i)
            return moves_list

        return legal_moves

    def get_moves(self, square: tuple[int, int]) -> list[tuple[int, int]]:
        piece = self.get_square(*square).get_piece()

        if not piece:
            return []

        color = piece.color

        legal_moves = self.get_all_legal_moves(color)

        return legal_moves[square]

    def checkmate(self) -> int:

        white_moves = self.get_all_legal_moves(1, to_list=True)
        black_moves = self.get_all_legal_moves(0, to_list=True)

        if not white_moves:
            return 0
        if not black_moves:
            return 1

        return -1


class Pawn(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}p.png"

    def get_moves(self, position: tuple[int, int], chessboard: ChessBoard) -> list[tuple[int, int]]:
        rank, file = position
        moves = []
        two_places_row_limit = 6 if self.color else 1

        if self.color:
            push_moves = [(-1, 0), (-2, 0)]
            capture_moves = [(-1, -1), (-1, 1)]
        else:
            push_moves = [(1, 0), (2, 0)]
            capture_moves = [(1, -1), (1, 1)]

        if rank != two_places_row_limit:
            push_moves = [push_moves[0]]
        if file == 0:
            capture_moves = [capture_moves[1]]
        if file == 7:
            capture_moves = [capture_moves[0]]

        for move in push_moves:
            pos_rank, pos_file = tuple(
                map(lambda x, y: x + y, move, (rank, file)))

            if pos_rank not in range(8) or pos_file not in range(8):
                break

            if chessboard.get_square(pos_rank, pos_file).get_piece():
                break
            moves += [(pos_rank, pos_file)]

        for move in capture_moves:
            pos_rank, pos_file = tuple(
                map(lambda x, y: x + y, move, (rank, file)))

            if pos_rank not in range(8) or pos_file not in range(8):
                break

            piece_on_capture_pos = chessboard.get_square(
                pos_rank, pos_file).get_piece()
            if piece_on_capture_pos and piece_on_capture_pos.color != self.color:
                moves += [(pos_rank, pos_file)]

        return moves

    def get_symbol(self):
        return "P" if self.color else 'p'


class Rook(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}r.png"

    def get_moves(self, chessboard: ChessBoard, position: tuple[int, int]) -> list[tuple[int, int]]:
        rank, file = position
        moves = []

        for j in range(4):
            for i in range(1, 8):
                if j == 0:
                    pos_rank, pos_file = rank + i, file
                elif j == 1:
                    pos_rank, pos_file = rank - i, file
                elif j == 2:
                    pos_rank, pos_file = rank, file + i
                else:
                    pos_rank, pos_file = rank, file - i

                if pos_file not in range(8) or pos_rank not in range(8):
                    break

                pos_piece = chessboard.get_square(
                    pos_rank, pos_file).get_piece()
                if pos_piece:
                    if pos_piece.color != self.color:
                        moves += [(pos_rank, pos_file)]
                    break

                moves += [(pos_rank, pos_file)]

        return moves

    def get_symbol(self):
        return "R" if self.color else 'r'


class Bishop(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}b.png"

    def get_moves(self, chessboard: ChessBoard, position: tuple[int, int]) -> list[tuple[int, int]]:
        rank, file = position
        moves = []

        for j in range(4):
            for i in range(1, 8):
                if j == 0:
                    pos_rank, pos_file = rank + i, file + i
                elif j == 1:
                    pos_rank, pos_file = rank + i, file - i
                elif j == 2:
                    pos_rank, pos_file = rank - i, file + i
                else:
                    pos_rank, pos_file = rank - i, file - i

                if pos_file not in range(8) or pos_rank not in range(8):
                    break

                pos_piece = chessboard.get_square(
                    pos_rank, pos_file).get_piece()
                if pos_piece:
                    if pos_piece.color != self.color:
                        moves += [(pos_rank, pos_file)]
                    break

                moves += [(pos_rank, pos_file)]
        return moves

    def get_symbol(self):
        return "B" if self.color else 'b'


class Queen(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}q.png"

    def get_moves(self, chessboard: ChessBoard, position: tuple[int, int]) -> list[tuple[int, int]]:
        moves = []

        rook = Rook(self.color)
        bishop = Bishop(self.color)

        moves += rook.get_moves(chessboard, position)
        moves += bishop.get_moves(chessboard, position)
        return moves

    def get_symbol(self):
        return "Q" if self.color else 'q'


class Knight(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}n.png"

    def get_moves(self, chessboard: ChessBoard, position: tuple[int, int]) -> list[tuple[int, int]]:
        rank, file = position
        moves = []

        for i in [-2, -1, 1, 2]:
            for j in [-2, -1, 1, 2]:
                if abs(i) == abs(j):
                    continue

                pos_rank, pos_file = rank + i, file + j

                if pos_rank not in range(8) or pos_file not in range(8):
                    continue

                piece = chessboard.get_square(pos_rank, pos_file).get_piece()
                if piece:
                    if piece.color != self.color:
                        moves += [(pos_rank, pos_file)]
                    continue
                moves += [(pos_rank, pos_file)]

        return moves

    def get_symbol(self):
        return "N" if self.color else 'n'


class King(Piece):

    def __init__(self, color: int):
        super().__init__(color)
        self.file_path = f"./pieces/{'w' if self.color else 'b'}k.png"

    def get_moves(self, chessboard: ChessBoard, position: tuple[int, int]) -> list[tuple[int, int]]:
        rank, file = position
        moves = []
        legal_moves = []

        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == j == 0:
                    continue

                pos_rank, pos_file = rank + i, file + j

                if pos_rank not in range(8) or pos_file not in range(8):
                    continue

                piece = chessboard.get_square(pos_rank, pos_file).get_piece()
                if piece:
                    if piece.color != self.color:
                        moves += [(pos_rank, pos_file)]
                    continue
                moves += [(pos_rank, pos_file)]

        return moves

    def get_symbol(self):
        return "K" if self.color else 'k'
