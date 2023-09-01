import pygame as pg
from chess_engine import ChessBoard, Piece


class ChessGraphics:
    def __init__(self, height: int, width: int, chessboard: ChessBoard = ChessBoard(), flipped: bool = False):
        pg.init()
        pg.display.set_caption("Chess")

        self.font = pg.font.Font("./Poppins/Poppins-SemiBold.ttf", 20)
        self.LIGHT_SQUARE_COLOR = (238, 238, 210)
        self.DARK_SQUARE_COLOR = (119, 150, 87)
        self.DARK_SELECTED_COL = 0xBBCA2A
        self.LIGHT_SELECTED_COL = 0xF6F669
        self.screen = pg.display.set_mode((width, height))
        self.HEIGHT = height
        self.WIDTH = width
        self.CELL_SIDE = height // 8
        self.flipped = flipped
        self.chessboard = chessboard
        # if self.flipped:
        #     chessboard.flip()

        self.chessboard.starting_position()
        # self.chessboard.generate_position_from_fen("1k1r2nr/1pp2ppp/3b/1P3q/2Pp1B/5Q1P/RP3PP/5RK/")
        # self.chessboard.generate_position_from_fen("rnb1kb1r/pp3ppp/2p2n/4q/4N/3Q/PPPB1PPP/2KR1BNR")
        # self.chessboard.generate_position_from_fen("3r1k1N/pq4pp/4B3/2p5/5B3/1PbP1RK1/P5PP/8")
        self.selected_piece = None
        self.board_changed = True
        self.selected_piece_moves = None
        self.legal_moves = []
        self.turn = 1
        # self.chessboard.move_piece((6, 4), (4, 4))

    def __draw_square(self, color: int, pos_x: int, pos_y: int):
        color = self.LIGHT_SQUARE_COLOR if color else self.DARK_SQUARE_COLOR
        rectangle = pg.Rect(pos_x, pos_y, self.CELL_SIDE, self.CELL_SIDE)
        pg.draw.rect(self.screen, color, rectangle)
        return rectangle

    def __render_text(self, color: int, text: str, position: tuple[int, int]):
        color = self.LIGHT_SQUARE_COLOR if not color else self.DARK_SQUARE_COLOR
        self.screen.blit(self.font.render(text, True, color), position)
        pg.display.update()

    def __render_piece(self, rect: pg.Rect, file_path: str):
        image = pg.transform.smoothscale(pg.image.load(
            file_path), (self.CELL_SIDE, self.CELL_SIDE))
        self.screen.blit(image, rect)

    def __draw_selected_square(self, color: int, pos_x: int, pos_y: int):
        color = self.LIGHT_SELECTED_COL if color else self.DARK_SELECTED_COL
        rectangle = pg.Rect(pos_x, pos_y, self.CELL_SIDE, self.CELL_SIDE)
        pg.draw.rect(self.screen, color, rectangle)
        return rectangle

    def __handle_render_text(self, rank: int, file: int, color: int):

        position_offsets = [
            (.05 * self.CELL_SIDE, 0),  # top left of a cell
            (.83 * self.CELL_SIDE, .75 * self.CELL_SIDE)  # bottom right of a cell
        ]

        files = ["a", "b", "c", "d", "e", "f", "g", "h"]

        if rank == 7:
            if not self.flipped:
                self.__render_text(color, files[file], (
                    position_offsets[1][0] + self.CELL_SIDE * file,
                    position_offsets[1][1] + self.CELL_SIDE * rank
                ))
            else:
                self.__render_text(color, files[7 - file], (
                    position_offsets[1][0] + self.CELL_SIDE * file,
                    position_offsets[1][1] + self.CELL_SIDE * rank
                ))
        if file == 0:
            if not self.flipped:
                self.__render_text(color, f"{8 - rank}", (
                    position_offsets[0][0] + self.CELL_SIDE * file,
                    position_offsets[0][1] + self.CELL_SIDE * rank
                ))
            else:
                self.__render_text(color, f"{rank + 1}", (
                    position_offsets[0][0] + self.CELL_SIDE * file,
                    position_offsets[0][1] + self.CELL_SIDE * rank
                ))

    def __draw_circle(self, piece, rectangle):
        surface = pg.Surface((self.CELL_SIDE, self.CELL_SIDE), pg.SRCALPHA)
        center = (self.CELL_SIDE // 2, self.CELL_SIDE // 2)
        if not piece:
            pg.draw.circle(surface, (0, 0, 0, 50), center,
                           (self.CELL_SIDE * 0.15))
        else:
            pg.draw.circle(surface, (0, 0, 0, 50), center,
                           self.CELL_SIDE // 2, self.CELL_SIDE // 10)
        self.screen.blit(surface, rectangle)

    def __draw_piece_move_square(self, piece: Piece, rect: pg.Rect):
        surface = pg.Surface((self.CELL_SIDE, self.CELL_SIDE), pg.SRCALPHA)
        if not piece:
            square_color = (84, 144, 240, 70)
        else:
            square_color = (240, 84, 84, 70)

        pg.draw.rect(surface, square_color, pg.Rect(
            0, 0, self.CELL_SIDE, self.CELL_SIDE))
        self.screen.blit(surface, rect)

    def __handle_selected_piece_move_squares(self, rank: int, file: int, piece: Piece, rectangle: pg.Rect):
        if self.selected_piece_moves and ((rank, file) in self.selected_piece_moves):
            self.__draw_piece_move_square(piece, rectangle)

    def __handle_selected_piece_move_circles(self, rank: int, file: int, piece: Piece, rectangle: pg.Rect):
        if self.selected_piece_moves and ((rank, file) in self.selected_piece_moves):
            self.__draw_circle(piece, rectangle)

    def draw_board(self):

        for rank in range(8):
            for file in range(8):
                color = 1 if (rank + file) % 2 == 0 else 0
                square_rank = 7 - rank if self.flipped else rank
                square_file = 7 - file if self.flipped else file

                # Rendering square of desired color
                if (rank, file) == self.selected_piece:
                    rectangle = self.__draw_selected_square(color, square_file * self.CELL_SIDE,
                                                            square_rank * self.CELL_SIDE)
                else:
                    rectangle = self.__draw_square(
                        color, square_file * self.CELL_SIDE, square_rank * self.CELL_SIDE)

                piece = self.chessboard.get_square(rank, file).get_piece()

                # Handle selected piece moves
                # self.__handle_selected_piece_move_squares(
                #     rank, file, piece, rectangle)

                self.__handle_selected_piece_move_circles(
                    rank, file, piece, rectangle)

                # Rendering Piece

                if piece:
                    self.__render_piece(rectangle, piece.file_path)

                # Rendering rank and file numbers
                self.__handle_render_text(
                    square_rank, square_file, color)

        pg.display.update()

    def __handle_selected_piece(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        file, rank = mouse_x // self.CELL_SIDE, mouse_y // self.CELL_SIDE

        file, rank = (file, rank) if not self.flipped else (7 - file, 7 - rank)

        if (rank, file) == self.selected_piece:
            self.selected_piece = self.selected_piece_moves = None
            return

        if not (file in range(8) and rank in range(8)):
            return

        if self.selected_piece and (rank, file) in self.selected_piece_moves and self.chessboard.get_piece(*self.selected_piece).color == self.turn:
            self.chessboard.move_piece(self.selected_piece, (rank, file))
            self.turn = 1 - self.turn
            self.selected_piece = self.selected_piece_moves = None
            return

        piece = self.chessboard.get_square(rank, file).get_piece()

        if piece:
            self.selected_piece = (rank, file)
            self.selected_piece_moves = self.chessboard.get_moves(
                self.selected_piece)
        else:
            self.selected_piece = None
            self.selected_piece_moves = None

    def game_loop(self):
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_f:
                        self.flipped = not self.flipped
                        self.selected_piece = None
                        self.board_changed = True
                        self.selected_piece_moves = None

                    if event.key == pg.K_r:
                        self.chessboard.starting_position()
                        self.selected_piece = None
                        self.selected_piece_moves = None
                        self.board_changed = True

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.__handle_selected_piece()
                    self.board_changed = True

            if self.board_changed:
                self.chessboard.check_for_checks(0)
                self.chessboard.check_for_checks(1)
                # self.legal_moves = self.chessboard.get_all_legal_moves(0, to_list=True)

                self.draw_board()
                self.board_changed = False
                mate = self.chessboard.checkmate()
                if mate == 0:
                    print("Black Wins")
                elif mate == 1:
                    print("White Wins")

        pg.display.flip()
