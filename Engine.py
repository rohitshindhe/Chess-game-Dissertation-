from copy import deepcopy
from random import choice
from time import sleep, time

COLOR_MASK = 1 << 3
WHITE = 0 << 3
BLACK = 1 << 3

ENDGAME_COIN_COUNT = 7

COIN_MASK = 0b111  # Binary 7 (1:2:4 = 001:010:100)
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6

COIN_TYPES = [EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]
COIN_VALUES = {EMPTY: 0, PAWN: 100, KNIGHT: 300, BISHOP: 300, ROOK: 500, QUEEN: 900, KING: 42000}

FILES = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
RANKS = ['1', '2', '3', '4', '5', '6', '7', '8']

CASTLE_KINGSIDE_WHITE = 0b1 << 0
CASTLE_QUEENSIDE_WHITE = 0b1 << 1
CASTLE_KINGSIDE_BLACK = 0b1 << 2
CASTLE_QUEENSIDE_BLACK = 0b1 << 3

FULL_CASTLING_RIGHTS = CASTLE_KINGSIDE_WHITE | CASTLE_QUEENSIDE_WHITE | CASTLE_KINGSIDE_BLACK | CASTLE_QUEENSIDE_BLACK

# COIN AND COLOR BITMASK = 0bCPPP. Cap C for color and small c for coins. Here the pgm uses little endian rank file

ALL_SQUARES = 0xFFFFFFFFFFFFFFFF  # Access violation reading location in hexadecimal, 18446744073709551615 decimal
FILE_A = 0x0101010101010101  # 72340172838076673 decimal, 100000001000000010000000100000001000000010000000100000001 bin
FILE_B = 0x0202020202020202  # 144680345676153346
FILE_C = 0x0404040404040404  # 289360691352306692
FILE_D = 0x0808080808080808
FILE_E = 0x1010101010101010
FILE_F = 0x2020202020202020
FILE_G = 0x4040404040404040
FILE_H = 0x8080808080808080
RANK_1 = 0x00000000000000FF  # 255, 11111111 binary
RANK_2 = 0x000000000000FF00  # 65280
RANK_3 = 0x0000000000FF0000
RANK_4 = 0x00000000FF000000
RANK_5 = 0x000000FF00000000
RANK_6 = 0x0000FF0000000000
RANK_7 = 0x00FF000000000000
RANK_8 = 0xFF00000000000000
DIAG_A1H8 = 0x8040201008040201
ANTI_DIAG_H1A8 = 0x0102040810204080
LIGHT_SQUARES = 0x55AA55AA55AA55AA
DARK_SQUARES = 0xAA55AA55AA55AA55

FILE_MASKS = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H]
RANK_MASKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8]

# bit_boards = 0b(h8)(g8)...(b1)(a1)
# board = [ a1, b1, ..., g8, h8 ]

INITIAL_BOARD = [ROOK | WHITE, KNIGHT | WHITE, BISHOP | WHITE, QUEEN | WHITE, KING | WHITE, BISHOP | WHITE,
                 KNIGHT | WHITE, ROOK | WHITE,
                 PAWN | WHITE, PAWN | WHITE, PAWN | WHITE, PAWN | WHITE, PAWN | WHITE, PAWN | WHITE,
                 PAWN | WHITE, PAWN | WHITE,
                 EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                 PAWN | BLACK, PAWN | BLACK, PAWN | BLACK, PAWN | BLACK, PAWN | BLACK, PAWN | BLACK,
                 PAWN | BLACK, PAWN | BLACK,
                 ROOK | BLACK, KNIGHT | BLACK, BISHOP | BLACK, QUEEN | BLACK, KING | BLACK, BISHOP | BLACK,
                 KNIGHT | BLACK, ROOK | BLACK]

EMPTY_BOARD = [EMPTY for _ in range(64)]

INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
STROKES_YOLO = '1k6/2b1p3/Qp4N1/4r2P/2B2q2/1R6/2Pn2K1/8 w - - 0 1'

COIN_CODES = {KING | WHITE: 'K',
               QUEEN | WHITE: 'Q',
               ROOK | WHITE: 'R',
               BISHOP | WHITE: 'B',
               KNIGHT | WHITE: 'N',
               PAWN | WHITE: 'P',
               KING | BLACK: 'k',
               QUEEN | BLACK: 'q',
               ROOK | BLACK: 'r',
               BISHOP | BLACK: 'b',
               KNIGHT | BLACK: 'n',
               PAWN | BLACK: 'p',
               EMPTY: '.'}
COIN_CODES.update({v: k for k, v in COIN_CODES.items()})

DOUBLED_PAWN_PENALTY = 5
ISOLATED_PAWN_PENALTY = 10
BACKWARDS_PAWN_PENALTY = 4
PASSED_PAWN_TABLE = 10
ROOK_SEMI_OPEN_FILE_TABLE = 5
ROOK_OPEN_FILE_TABLE = 8
ROOK_ON_SEVENTH_TABLE = 10

PAWN_TABLE = [0, 0, 0, 0, 0, 0, 0, 0,
              50, 50, 50, 50, 50, 50, 50, 50,
              10, 10, 20, 30, 30, 20, 10, 10,
              5, 5, 10, 25, 25, 10, 5, 5,
              0, 0, 0, 20, 20, 0, 0, 0,
              5, -5, -10, 0, 0, -10, -5, 5,
              5, 10, 10, -20, -20, 10, 10, 5,
              0, 0, 0, 0, 0, 0, 0, 0]

KNIGHT_TABLE = [-50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -90, -30, -30, -30, -30, -90, -50]

BISHOP_TABLE = [-20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -90, -10, -10, -90, -10, -20]

KING_TABLE = [-30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -30, -40, -40, -50, -50, -40, -40, -30,
              -20, -30, -30, -40, -40, -30, -30, -20,
              -10, -20, -20, -20, -20, -20, -20, -10,
              20, 20, 0, 0, 0, 0, 20, 20,
              20, 30, 10, 0, 0, 10, 30, 20]

KING_ENDGAME_TABLE = [-50, -40, -30, -20, -20, -30, -40, -50,
                      -30, -20, -10, 0, 0, -10, -20, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 30, 40, 40, 30, -10, -30,
                      -30, -10, 20, 30, 30, 20, -10, -30,
                      -30, -30, 0, 0, 0, 0, -30, -30,
                      -50, -30, -30, -30, -30, -30, -30, -50]

verbose = False


# ========== CHESS GAME ==========

class Game:
    def __init__(self, FEN=''):
        self.board = INITIAL_BOARD
        self.to_move = WHITE
        self.ep_square = 0
        self.castling_rights = FULL_CASTLING_RIGHTS  # CASTLING BITMASK = 0bqkQK
        self.halfmove_clock = 0
        self.fullmove_number = 1

        self.position_history = []
        if FEN != '':
            self.load_FEN(FEN)
            self.position_history.append(FEN)
        else:
            self.position_history.append(INITIAL_FEN)

        self.move_history = []

    def get_move_list(self):
        return ' '.join(self.move_history)

    def to_FEN(self):
        FEN_str = ''

        for i in range(len(RANKS)):
            first = len(self.board) - 8 * (i + 1)
            empty_sqrs = 0
            for file in range(len(FILES)):
                coin = self.board[first + file]
                if coin & COIN_MASK == EMPTY:
                    empty_sqrs += 1
                else:
                    if empty_sqrs > 0:
                        FEN_str += '{}'.format(empty_sqrs)
                    FEN_str += '{}'.format(coin2str(coin))
                    empty_sqrs = 0
            if empty_sqrs > 0:
                FEN_str += '{}'.format(empty_sqrs)
            FEN_str += '/'
        FEN_str = FEN_str[:-1] + ' '

        if self.to_move == WHITE:
            FEN_str += 'w '
        if self.to_move == BLACK:
            FEN_str += 'b '

        if self.castling_rights & CASTLE_KINGSIDE_WHITE: # castling code K
            FEN_str += 'K'
        if self.castling_rights & CASTLE_QUEENSIDE_WHITE: # castling code Q
            FEN_str += 'Q'
        if self.castling_rights & CASTLE_KINGSIDE_BLACK: # castling code k
            FEN_str += 'k'
        if self.castling_rights & CASTLE_QUEENSIDE_BLACK: # castling code q
            FEN_str += 'q'
        if self.castling_rights == 0:
            FEN_str += '-'
        FEN_str += ' '

        if self.ep_square == 0:
            FEN_str += '-'
        else:
            FEN_str += bb2str(self.ep_square)

        FEN_str += ' {}'.format(self.halfmove_clock)
        FEN_str += ' {}'.format(self.fullmove_number)
        return FEN_str

    def load_FEN(self, FEN_str):
        FEN_list = FEN_str.split(' ')

        board_str = FEN_list[0]
        rank_list = board_str.split('/')
        rank_list.reverse()
        self.board = []

        for rank in rank_list:
            rank_coins = []
            for p in rank:
                if p.isdigit():
                    for _ in range(int(p)):
                        rank_coins.append(EMPTY)
                else:
                    rank_coins.append(str2coin(p))
            self.board.extend(rank_coins)

        to_move_str = FEN_list[1].lower()
        if to_move_str == 'w':
            self.to_move = WHITE
        if to_move_str == 'b':
            self.to_move = BLACK

        castling_rights_str = FEN_list[2]
        self.castling_rights = 0
        if castling_rights_str.find('K') >= 0:
            self.castling_rights |= CASTLE_KINGSIDE_WHITE
        if castling_rights_str.find('Q') >= 0:
            self.castling_rights |= CASTLE_QUEENSIDE_WHITE
        if castling_rights_str.find('k') >= 0:
            self.castling_rights |= CASTLE_KINGSIDE_BLACK
        if castling_rights_str.find('q') >= 0:
            self.castling_rights |= CASTLE_QUEENSIDE_BLACK

        ep_str = FEN_list[3]
        if ep_str == '-':
            self.ep_square = 0
        else:
            self.ep_square = str2bb(ep_str)

        self.halfmove_clock = int(FEN_list[4])
        self.fullmove_number = int(FEN_list[5])


# ================================


def get_coin(board, bitboard):
    return board[bb2index(bitboard)]


def bb2index(bitboard):
    for i in range(64):
        if bitboard & (0b1 << i):
            return i


def str2index(position_str):
    file = FILES.index(position_str[0].lower())
    rank = RANKS.index(position_str[1])
    return 8 * rank + file


def bb2str(bitboard):
    for i in range(64):
        if bitboard & (0b1 << i):
            file = i % 8
            rank = int(i / 8)
            return '{}{}'.format(FILES[file], RANKS[rank])


def str2bb(position_str):
    return 0b1 << str2index(position_str)


def move2str(move):
    return bb2str(move[0]) + bb2str(move[1])


def single_gen(bitboard):
    for i in range(64):
        bit = 0b1 << i
        if bitboard & bit:
            yield bit


def coin_gen(board, coin_code):
    for i in range(64):
        if board[i] & COIN_MASK == coin_code:
            yield 0b1 << i


def colored_coin_gen(board, coin_code, color):
    for i in range(64):
        if board[i] == coin_code | color:
            yield 0b1 << i


def opposing_color(color):
    if color == WHITE:
        return BLACK
    if color == BLACK:
        return WHITE


def coin2str(coin):
    return COIN_CODES[coin]


def str2coin(string):
    return COIN_CODES[string]


def print_board(board):
    print('')
    for i in range(len(RANKS)):
        rank_str = str(8 - i) + ' '
        first = len(board) - 8 * (i + 1)
        for file in range(len(FILES)):
            rank_str += '{} '.format(coin2str(board[first + file]))
        print(rank_str)
    print('  a b c d e f g h')


def print_rotated_board(board):
    r_board = rotate_board(board)
    print('')
    for i in range(len(RANKS)):
        rank_str = str(i + 1) + ' '
        first = len(r_board) - 8 * (i + 1)
        for file in range(len(FILES)):
            rank_str += '{} '.format(coin2str(r_board[first + file]))
        print(rank_str)
    print('  h g f e d c b a')


def print_bitboard(bitboard):
    print('')
    for rank in range(len(RANKS)):
        rank_str = str(8 - rank) + ' '
        for file in range(len(FILES)):
            if (bitboard >> (file + (7 - rank) * 8)) & 0b1:
                rank_str += '# '
            else:
                rank_str += '. '
        print(rank_str)
    print('  a b c d e f g h')


def lsb(bitboard):          # least significant bit
    for i in range(64):
        bit = (0b1 << i)
        if bit & bitboard:
            return bit


def msb(bitboard):          # most significant bit
    for i in range(64):
        bit = (0b1 << (63 - i))
        if bit & bitboard:
            return bit


def get_colored_coins(board, color):
    return list2int([(i != EMPTY and i & COLOR_MASK == color) for i in board])


def empty_squares(board):
    return list2int([i == EMPTY for i in board])


def occupied_squares(board):
    return nnot(empty_squares(board))


def list2int(lst):
    rev_list = lst[:]
    rev_list.reverse()
    return int('0b' + ''.join(['1' if i else '0' for i in rev_list]), 2)


def nnot(bitboard):
    return ~bitboard & ALL_SQUARES


def rotate_board(board):
    rotated_board = deepcopy(board)
    rotated_board.reverse()
    return rotated_board


def flip_board_v(board):
    flip = [56, 57, 58, 59, 60, 61, 62, 63,
            48, 49, 50, 51, 52, 53, 54, 55,
            40, 41, 42, 43, 44, 45, 46, 47,
            32, 33, 34, 35, 36, 37, 38, 39,
            24, 25, 26, 27, 28, 29, 30, 31,
            16, 17, 18, 19, 20, 21, 22, 23,
            8, 9, 10, 11, 12, 13, 14, 15,
            0, 1, 2, 3, 4, 5, 6, 7]

    return deepcopy([board[flip[i]] for i in range(64)])


def east_one(bitboard):
    return (bitboard << 1) & nnot(FILE_A)


def west_one(bitboard):
    return (bitboard >> 1) & nnot(FILE_H)


def north_one(bitboard):
    return (bitboard << 8) & nnot(RANK_1)


def south_one(bitboard):
    return (bitboard >> 8) & nnot(RANK_8)


def NE_one(bitboard):
    return north_one(east_one(bitboard))


def NW_one(bitboard):
    return north_one(west_one(bitboard))


def SE_one(bitboard):
    return south_one(east_one(bitboard))


def SW_one(bitboard):
    return south_one(west_one(bitboard))


def move_coin(board, move):
    new_board = deepcopy(board)
    new_board[bb2index(move[1])] = new_board[bb2index(move[0])]
    new_board[bb2index(move[0])] = EMPTY
    return new_board


def make_move(game, move):
    new_game = deepcopy(game)
    leaving_position = move[0]
    arriving_position = move[1]

    # update_clocks
    new_game.halfmove_clock += 1
    if new_game.to_move == BLACK:
        new_game.fullmove_number += 1

    # reset clock if capture
    if get_coin(new_game.board, arriving_position) != EMPTY:
        new_game.halfmove_clock = 0

    # for pawns: reset clock, removed captured ep, set new ep, promote
    if get_coin(new_game.board, leaving_position) & COIN_MASK == PAWN:
        new_game.halfmove_clock = 0

        if arriving_position == game.ep_square:
            new_game.board = remove_captured_ep(new_game)

        if is_double_push(leaving_position, arriving_position):
            new_game.ep_square = new_ep_square(leaving_position)

        if arriving_position & (RANK_1 | RANK_8):
            new_game.board[bb2index(leaving_position)] = new_game.to_move | QUEEN

    # reset ep square if not updated
    if new_game.ep_square == game.ep_square:
        new_game.ep_square = 0

    # update castling rights for rook moves
    if leaving_position == str2bb('a1'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_QUEENSIDE_WHITE)
    if leaving_position == str2bb('h1'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_WHITE)
    if leaving_position == str2bb('a8'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_QUEENSIDE_BLACK)
    if leaving_position == str2bb('h8'):
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_BLACK)

    # castling
    if get_coin(new_game.board, leaving_position) == WHITE | KING:
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_WHITE | CASTLE_QUEENSIDE_WHITE)
        if leaving_position == str2bb('e1'):
            if arriving_position == str2bb('g1'):
                new_game.board = move_coin(new_game.board, [str2bb('h1'), str2bb('f1')])
            if arriving_position == str2bb('c1'):
                new_game.board = move_coin(new_game.board, [str2bb('a1'), str2bb('d1')])

    if get_coin(new_game.board, leaving_position) == BLACK | KING:
        new_game.castling_rights = remove_castling_rights(new_game, CASTLE_KINGSIDE_BLACK | CASTLE_QUEENSIDE_BLACK)
        if leaving_position == str2bb('e8'):
            if arriving_position == str2bb('g8'):
                new_game.board = move_coin(new_game.board, [str2bb('h8'), str2bb('f8')])
            if arriving_position == str2bb('c8'):
                new_game.board = move_coin(new_game.board, [str2bb('a8'), str2bb('d8')])

    # update positions and next to move
    new_game.board = move_coin(new_game.board, (leaving_position, arriving_position))
    new_game.to_move = opposing_color(new_game.to_move)

    # update history
    new_game.move_history.append(move2str(move))
    new_game.position_history.append(new_game.to_FEN())
    return new_game


def unmake_move(game):
    if len(game.position_history) < 2:
        return deepcopy(game)

    new_game = Game(game.position_history[-2])
    new_game.move_history = deepcopy(game.move_history)[:-1]
    new_game.position_history = deepcopy(game.position_history)[:-1]
    return new_game


def get_rank(rank_num):
    rank_num = int(rank_num)
    return RANK_MASKS[rank_num]


def get_file(file_str):
    file_str = file_str.lower()
    file_num = FILES.index(file_str)
    return FILE_MASKS[file_num]


def get_filter(filter_str):
    if filter_str in FILES:
        return get_file(filter_str)
    if filter_str in RANKS:
        return get_rank(filter_str)


# ========== PAWN ==========

def get_all_pawns(board):
    return list2int([i & COIN_MASK == PAWN for i in board])


def get_pawns(board, color):
    return list2int([i == color | PAWN for i in board])


def pawn_moves(moving_coin, game, color):
    return pawn_pushes(moving_coin, game.board, color) | pawn_captures(moving_coin, game, color)


def pawn_captures(moving_coin, game, color):
    return pawn_simple_captures(moving_coin, game, color) | pawn_ep_captures(moving_coin, game, color)


def pawn_pushes(moving_coin, board, color):
    return pawn_simple_pushes(moving_coin, board, color) | pawn_double_pushes(moving_coin, board, color)


def pawn_simple_captures(attacking_coin, game, color):
    return pawn_attacks(attacking_coin, game.board, color) & get_colored_coins(game.board, opposing_color(color))


def pawn_ep_captures(attacking_coin, game, color):
    if color == WHITE:
        ep_squares = game.ep_square & RANK_6
    if color == BLACK:
        ep_squares = game.ep_square & RANK_3
    return pawn_attacks(attacking_coin, game.board, color) & ep_squares


def pawn_attacks(attacking_coin, board, color):
    return pawn_east_attacks(attacking_coin, board, color) | pawn_west_attacks(attacking_coin, board, color)


def pawn_simple_pushes(moving_coin, board, color):
    if color == WHITE:
        return north_one(moving_coin) & empty_squares(board)
    if color == BLACK:
        return south_one(moving_coin) & empty_squares(board)


def pawn_double_pushes(moving_coin, board, color):
    if color == WHITE:
        return north_one(pawn_simple_pushes(moving_coin, board, color)) & (empty_squares(board) & RANK_4)
    if color == BLACK:
        return south_one(pawn_simple_pushes(moving_coin, board, color)) & (empty_squares(board) & RANK_5)


def pawn_east_attacks(attacking_coin, board, color):
    if color == WHITE:
        return NE_one(attacking_coin & get_colored_coins(board, color))
    if color == BLACK:
        return SE_one(attacking_coin & get_colored_coins(board, color))


def pawn_west_attacks(attacking_coin, board, color):
    if color == WHITE:
        return NW_one(attacking_coin & get_colored_coins(board, color))
    if color == BLACK:
        return SW_one(attacking_coin & get_colored_coins(board, color))


def pawn_double_attacks(attacking_coin, board, color):
    return pawn_east_attacks(attacking_coin, board, color) & pawn_west_attacks(attacking_coin, board, color)


def is_double_push(leaving_square, target_square):
    return (leaving_square & RANK_2 and target_square & RANK_4) or \
           (leaving_square & RANK_7 and target_square & RANK_5)


def new_ep_square(leaving_square):
    if leaving_square & RANK_2:
        return north_one(leaving_square)
    if leaving_square & RANK_7:
        return south_one(leaving_square)


def remove_captured_ep(game):
    new_board = deepcopy(game.board)
    if game.ep_square & RANK_3:
        new_board[bb2index(north_one(game.ep_square))] = EMPTY
    if game.ep_square & RANK_6:
        new_board[bb2index(south_one(game.ep_square))] = EMPTY
    return new_board


# ========== KNIGHT ==========

def get_knights(board, color):
    return list2int([i == color | KNIGHT for i in board])


def knight_moves(moving_coin, board, color):
    return knight_attacks(moving_coin) & nnot(get_colored_coins(board, color))


def knight_attacks(moving_coin):
    return knight_NNE(moving_coin) | \
           knight_ENE(moving_coin) | \
           knight_NNW(moving_coin) | \
           knight_WNW(moving_coin) | \
           knight_SSE(moving_coin) | \
           knight_ESE(moving_coin) | \
           knight_SSW(moving_coin) | \
           knight_WSW(moving_coin)


def knight_WNW(moving_coin):
    return moving_coin << 6 & nnot(FILE_G | FILE_H)


def knight_ENE(moving_coin):
    return moving_coin << 10 & nnot(FILE_A | FILE_B)


def knight_NNW(moving_coin):
    return moving_coin << 15 & nnot(FILE_H)


def knight_NNE(moving_coin):
    return moving_coin << 17 & nnot(FILE_A)


def knight_ESE(moving_coin):
    return moving_coin >> 6 & nnot(FILE_A | FILE_B)


def knight_WSW(moving_coin):
    return moving_coin >> 10 & nnot(FILE_G | FILE_H)


def knight_SSE(moving_coin):
    return moving_coin >> 15 & nnot(FILE_A)


def knight_SSW(moving_coin):
    return moving_coin >> 17 & nnot(FILE_H)


def knight_fill(moving_coin, n):
    fill = moving_coin
    for _ in range(n):
        fill |= knight_attacks(fill)
    return fill


def knight_distance(pos1, pos2):
    init_bitboard = str2bb(pos1)
    end_bitboard = str2bb(pos2)
    fill = init_bitboard
    dist = 0
    while fill & end_bitboard == 0:
        dist += 1
        fill = knight_fill(init_bitboard, dist)
    return dist


# ========== KING ==========

def get_king(board, color):
    return list2int([i == color | KING for i in board])


def king_moves(moving_coin, board, color):
    return king_attacks(moving_coin) & nnot(get_colored_coins(board, color))


def king_attacks(moving_coin):
    king_atks = moving_coin | east_one(moving_coin) | west_one(moving_coin)
    king_atks |= north_one(king_atks) | south_one(king_atks)
    return king_atks & nnot(moving_coin)


def can_castle_kingside(game, color):
    if color == WHITE:
        return (game.castling_rights & CASTLE_KINGSIDE_WHITE) and \
               game.board[str2index('f1')] == EMPTY and \
               game.board[str2index('g1')] == EMPTY and \
               (not is_attacked(str2bb('e1'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('f1'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('g1'), game.board, opposing_color(color)))
    if color == BLACK:
        return (game.castling_rights & CASTLE_KINGSIDE_BLACK) and \
               game.board[str2index('f8')] == EMPTY and \
               game.board[str2index('g8')] == EMPTY and \
               (not is_attacked(str2bb('e8'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('f8'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('g8'), game.board, opposing_color(color)))


def can_castle_queenside(game, color):
    if color == WHITE:
        return (game.castling_rights & CASTLE_QUEENSIDE_WHITE) and \
               game.board[str2index('b1')] == EMPTY and \
               game.board[str2index('c1')] == EMPTY and \
               game.board[str2index('d1')] == EMPTY and \
               (not is_attacked(str2bb('c1'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('d1'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('e1'), game.board, opposing_color(color)))
    if color == BLACK:
        return (game.castling_rights & CASTLE_QUEENSIDE_BLACK) and \
               game.board[str2index('b8')] == EMPTY and \
               game.board[str2index('c8')] == EMPTY and \
               game.board[str2index('d8')] == EMPTY and \
               (not is_attacked(str2bb('c8'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('d8'), game.board, opposing_color(color))) and \
               (not is_attacked(str2bb('e8'), game.board, opposing_color(color)))


def castle_kingside_move(game):
    if game.to_move == WHITE:
        return str2bb('e1'), str2bb('g1')
    if game.to_move == BLACK:
        return str2bb('e8'), str2bb('g8')


def castle_queenside_move(game):
    if game.to_move == WHITE:
        return str2bb('e1'), str2bb('c1')
    if game.to_move == BLACK:
        return str2bb('e8'), str2bb('c8')


def remove_castling_rights(game, removed_rights):
    return game.castling_rights & ~removed_rights


# ========== BISHOP ==========

def get_bishops(board, color):
    return list2int([i == color | BISHOP for i in board])


def bishop_rays(moving_coin):
    return diagonal_rays(moving_coin) | anti_diagonal_rays(moving_coin)


def diagonal_rays(moving_coin):
    return NE_ray(moving_coin) | SW_ray(moving_coin)


def anti_diagonal_rays(moving_coin):
    return NW_ray(moving_coin) | SE_ray(moving_coin)


def NE_ray(moving_coin):
    ray_atks = NE_one(moving_coin)
    for _ in range(6):
        ray_atks |= NE_one(ray_atks)
    return ray_atks & ALL_SQUARES


def SE_ray(moving_coin):
    ray_atks = SE_one(moving_coin)
    for _ in range(6):
        ray_atks |= SE_one(ray_atks)
    return ray_atks & ALL_SQUARES


def NW_ray(moving_coin):
    ray_atks = NW_one(moving_coin)
    for _ in range(6):
        ray_atks |= NW_one(ray_atks)
    return ray_atks & ALL_SQUARES


def SW_ray(moving_coin):
    ray_atks = SW_one(moving_coin)
    for _ in range(6):
        ray_atks |= SW_one(ray_atks)
    return ray_atks & ALL_SQUARES


def NE_attacks(single_coin, board, color):
    blocker = lsb(NE_ray(single_coin) & occupied_squares(board))
    if blocker:
        return NE_ray(single_coin) ^ NE_ray(blocker)
    else:
        return NE_ray(single_coin)


def NW_attacks(single_coin, board, color):
    blocker = lsb(NW_ray(single_coin) & occupied_squares(board))
    if blocker:
        return NW_ray(single_coin) ^ NW_ray(blocker)
    else:
        return NW_ray(single_coin)


def SE_attacks(single_coin, board, color):
    blocker = msb(SE_ray(single_coin) & occupied_squares(board))
    if blocker:
        return SE_ray(single_coin) ^ SE_ray(blocker)
    else:
        return SE_ray(single_coin)


def SW_attacks(single_coin, board, color):
    blocker = msb(SW_ray(single_coin) & occupied_squares(board))
    if blocker:
        return SW_ray(single_coin) ^ SW_ray(blocker)
    else:
        return SW_ray(single_coin)


def diagonal_attacks(single_coin, board, color):
    return NE_attacks(single_coin, board, color) | SW_attacks(single_coin, board, color)


def anti_diagonal_attacks(single_coin, board, color):
    return NW_attacks(single_coin, board, color) | SE_attacks(single_coin, board, color)


def bishop_attacks(moving_coin, board, color):
    atks = 0
    for coin in single_gen(moving_coin):
        atks |= diagonal_attacks(coin, board, color) | anti_diagonal_attacks(coin, board, color)
    return atks


def bishop_moves(moving_coin, board, color):
    return bishop_attacks(moving_coin, board, color) & nnot(get_colored_coins(board, color))


# ========== ROOK ==========

def get_rooks(board, color):
    return list2int([i == color | ROOK for i in board])


def rook_rays(moving_coin):
    return rank_rays(moving_coin) | file_rays(moving_coin)


def rank_rays(moving_coin):
    return east_ray(moving_coin) | west_ray(moving_coin)


def file_rays(moving_coin):
    return north_ray(moving_coin) | south_ray(moving_coin)


def east_ray(moving_coin):
    ray_atks = east_one(moving_coin)
    for _ in range(6):
        ray_atks |= east_one(ray_atks)
    return ray_atks & ALL_SQUARES


def west_ray(moving_coin):
    ray_atks = west_one(moving_coin)
    for _ in range(6):
        ray_atks |= west_one(ray_atks)
    return ray_atks & ALL_SQUARES


def north_ray(moving_coin):
    ray_atks = north_one(moving_coin)
    for _ in range(6):
        ray_atks |= north_one(ray_atks)
    return ray_atks & ALL_SQUARES


def south_ray(moving_coin):
    ray_atks = south_one(moving_coin)
    for _ in range(6):
        ray_atks |= south_one(ray_atks)
    return ray_atks & ALL_SQUARES


def east_attacks(single_coin, board, color):
    blocker = lsb(east_ray(single_coin) & occupied_squares(board))
    if blocker:
        return east_ray(single_coin) ^ east_ray(blocker)
    else:
        return east_ray(single_coin)


def west_attacks(single_coin, board, color):
    blocker = msb(west_ray(single_coin) & occupied_squares(board))
    if blocker:
        return west_ray(single_coin) ^ west_ray(blocker)
    else:
        return west_ray(single_coin)


def rank_attacks(single_coin, board, color):
    return east_attacks(single_coin, board, color) | west_attacks(single_coin, board, color)


def north_attacks(single_coin, board, color):
    blocker = lsb(north_ray(single_coin) & occupied_squares(board))
    if blocker:
        return north_ray(single_coin) ^ north_ray(blocker)
    else:
        return north_ray(single_coin)


def south_attacks(single_coin, board, color):
    blocker = msb(south_ray(single_coin) & occupied_squares(board))
    if blocker:
        return south_ray(single_coin) ^ south_ray(blocker)
    else:
        return south_ray(single_coin)


def file_attacks(single_coin, board, color):
    return north_attacks(single_coin, board, color) | south_attacks(single_coin, board, color)


def rook_attacks(moving_coin, board, color):
    atks = 0
    for single_coin in single_gen(moving_coin):
        atks |= rank_attacks(single_coin, board, color) | file_attacks(single_coin, board, color)
    return atks


def rook_moves(moving_coin, board, color):
    return rook_attacks(moving_coin, board, color) & nnot(get_colored_coins(board, color))


# ========== QUEEN ==========

def get_queen(board, color):
    return list2int([i == color | QUEEN for i in board])


def queen_rays(moving_coin):
    return rook_rays(moving_coin) | bishop_rays(moving_coin)


def queen_attacks(moving_coin, board, color):
    return bishop_attacks(moving_coin, board, color) | rook_attacks(moving_coin, board, color)


def queen_moves(moving_coin, board, color):
    return bishop_moves(moving_coin, board, color) | rook_moves(moving_coin, board, color)


def is_attacked(target, board, attacking_color):
    return count_attacks(target, board, attacking_color) > 0


def is_check(board, color):
    return is_attacked(get_king(board, color), board, opposing_color(color))


def get_attacks(moving_coin, board, color):
    coin = board[bb2index(moving_coin)]

    if coin & COIN_MASK == PAWN:
        return pawn_attacks(moving_coin, board, color)
    elif coin & COIN_MASK == KNIGHT:
        return knight_attacks(moving_coin)
    elif coin & COIN_MASK == BISHOP:
        return bishop_attacks(moving_coin, board, color)
    elif coin & COIN_MASK == ROOK:
        return rook_attacks(moving_coin, board, color)
    elif coin & COIN_MASK == QUEEN:
        return queen_attacks(moving_coin, board, color)
    elif coin & COIN_MASK == KING:
        return king_attacks(moving_coin)


def get_moves(moving_coin, game, color):
    coin = game.board[bb2index(moving_coin)]

    if coin & COIN_MASK == PAWN:
        return pawn_moves(moving_coin, game, color)
    elif coin & COIN_MASK == KNIGHT:
        return knight_moves(moving_coin, game.board, color)
    elif coin & COIN_MASK == BISHOP:
        return bishop_moves(moving_coin, game.board, color)
    elif coin & COIN_MASK == ROOK:
        return rook_moves(moving_coin, game.board, color)
    elif coin & COIN_MASK == QUEEN:
        return queen_moves(moving_coin, game.board, color)
    elif coin & COIN_MASK == KING:
        return king_moves(moving_coin, game.board, color)


def count_attacks(target, board, attacking_color):
    attack_count = 0

    for index in range(64):
        coin = board[index]
        if coin != EMPTY and coin & COLOR_MASK == attacking_color:
            pos = 0b1 << index

            if get_attacks(pos, board, attacking_color) & target:
                attack_count += 1

    return attack_count


def material_sum(board, color):
    material = 0
    for coin in board:
        if coin & COLOR_MASK == color:
            material += COIN_VALUES[coin & COIN_MASK]
    return material


def material_balance(board):
    return material_sum(board, WHITE) - material_sum(board, BLACK)


def mobility_balance(game):
    return count_legal_moves(game, WHITE) - count_legal_moves(game, BLACK)


def evaluate_game(game):
    if game_ended(game):
        return evaluate_end_node(game)
    else:
        return material_balance(game.board) + positional_balance(game)  # + 10*mobility_balance(game)


def evaluate_end_node(game):
    if is_checkmate(game, game.to_move):
        return win_score(game.to_move)
    elif is_stalemate(game) or \
            has_insufficient_material(game) or \
            is_under_75_move_rule(game):
        return 0


def positional_balance(game):
    return positional_table(game, WHITE) - positional_table(game, BLACK)


def positional_table(game, color):
    table = 0

    if color == WHITE:
        board = game.board
    elif color == BLACK:
        board = flip_board_v(game.board)

    for index in range(64):
        coin = board[index]

        if coin != EMPTY and coin & COLOR_MASK == color:
            coin_type = coin & COIN_MASK

            if coin_type == PAWN:
                table += PAWN_TABLE[index]
            elif coin_type == KNIGHT:
                table += KNIGHT_TABLE[index]
            elif coin_type == BISHOP:
                table += BISHOP_TABLE[index]

            elif coin_type == ROOK:
                position = 0b1 << index

                if is_open_file(position, board):
                    table += ROOK_OPEN_FILE_TABLE
                elif is_semi_open_file(position, board):
                    table += ROOK_SEMI_OPEN_FILE_TABLE

                if position & RANK_7:
                    table += ROOK_ON_SEVENTH_TABLE

            elif coin_type == KING:
                if is_endgame(board):
                    table += KING_ENDGAME_TABLE[index]
                else:
                    table += KING_TABLE[index]

    return table


def is_endgame(board):
    return count_coins(occupied_squares(board)) <= ENDGAME_COIN_COUNT


def is_open_file(bitboard, board):
    for f in FILES:
        rank_filter = get_file(f)
        if bitboard & rank_filter:
            return count_coins(get_all_pawns(board) & rank_filter) == 0


def is_semi_open_file(bitboard, board):
    for f in FILES:
        rank_filter = get_file(f)
        if bitboard & rank_filter:
            return count_coins(get_all_pawns(board) & rank_filter) == 1


def count_coins(bitboard):
    return bin(bitboard).count("1")


def win_score(color):
    if color == WHITE:
        return -10 * COIN_VALUES[KING]
    if color == BLACK:
        return 10 * COIN_VALUES[KING]


def pseudo_legal_moves(game, color):
    for index in range(64):
        coin = game.board[index]

        if coin != EMPTY and coin & COLOR_MASK == color:
            coin_pos = 0b1 << index

            for target in single_gen(get_moves(coin_pos, game, color)):
                yield (coin_pos, target)

    if can_castle_kingside(game, color):
        yield (get_king(game.board, color), east_one(east_one(get_king(game.board, color))))
    if can_castle_queenside(game, color):
        yield (get_king(game.board, color), west_one(west_one(get_king(game.board, color))))


def legal_moves(game, color):
    for move in pseudo_legal_moves(game, color):
        if is_legal_move(game, move):
            yield move


def is_legal_move(game, move):
    new_game = make_move(game, move)
    return not is_check(new_game.board, game.to_move)


def count_legal_moves(game, color):
    move_count = 0
    for _ in legal_moves(game, color):
        move_count += 1
    return move_count


def is_stalemate(game):
    for _ in legal_moves(game, game.to_move):
        return False
    return not is_check(game.board, game.to_move)


def is_checkmate(game, color):
    for _ in legal_moves(game, game.to_move):
        return False
    return is_check(game.board, color)


def is_same_position(FEN_a, FEN_b):
    FEN_a_list = FEN_a.split(' ')
    FEN_b_list = FEN_b.split(' ')
    return FEN_a_list[0] == FEN_b_list[0] and \
           FEN_a_list[1] == FEN_b_list[1] and \
           FEN_a_list[2] == FEN_b_list[2] and \
           FEN_a_list[3] == FEN_b_list[3]


def has_threefold_repetition(game):
    current_pos = game.position_history[-1]
    position_count = 0
    for position in game.position_history:
        if is_same_position(current_pos, position):
            position_count += 1
    return position_count >= 3


def is_under_50_move_rule(game):
    return game.halfmove_clock >= 100


def is_under_75_move_rule(game):
    return game.halfmove_clock >= 150


def has_insufficient_material(game):  # TODO: other insufficient positions
    if material_sum(game.board, WHITE) + material_sum(game.board, BLACK) == 2 * COIN_VALUES[KING]:
        return True
    if material_sum(game.board, WHITE) == COIN_VALUES[KING]:
        if material_sum(game.board, BLACK) == COIN_VALUES[KING] + COIN_VALUES[KNIGHT] and \
                (get_knights(game.board, BLACK) != 0 or get_bishops(game.board, BLACK) != 0):
            return True
    if material_sum(game.board, BLACK) == COIN_VALUES[KING]:
        if material_sum(game.board, WHITE) == COIN_VALUES[KING] + COIN_VALUES[KNIGHT] and \
                (get_knights(game.board, WHITE) != 0 or get_bishops(game.board, WHITE) != 0):
            return True
    return False


def game_ended(game):
    return is_checkmate(game, WHITE) or \
           is_checkmate(game, BLACK) or \
           is_stalemate(game) or \
           has_insufficient_material(game) or \
           is_under_75_move_rule(game)


def random_move(game, color):
    return choice(legal_moves(game, color))


def evaluated_move(game, color):
    best_score = win_score(color)
    best_moves = []

    for move in legal_moves(game, color):
        evaluation = evaluate_game(make_move(game, move))

        if is_checkmate(make_move(game, move), opposing_color(game.to_move)):
            return [move, evaluation]

        if (color == WHITE and evaluation > best_score) or \
                (color == BLACK and evaluation < best_score):
            best_score = evaluation
            best_moves = [move]
        elif evaluation == best_score:
            best_moves.append(move)

    return [choice(best_moves), best_score]


def minimax(game, color, depth=1):
    if game_ended(game):
        return [None, evaluate_game(game)]

    [simple_move, simple_evaluation] = evaluated_move(game, color)

    if depth == 1 or \
            simple_evaluation == win_score(opposing_color(color)):
        return [simple_move, simple_evaluation]

    best_score = win_score(color)
    best_moves = []

    for move in legal_moves(game, color):
        his_game = make_move(game, move)

        if is_checkmate(his_game, his_game.to_move):
            return [move, win_score(his_game.to_move)]

        [_, evaluation] = minimax(his_game, opposing_color(color), depth - 1)

        if evaluation == win_score(opposing_color(color)):
            return [move, evaluation]

        if (color == WHITE and evaluation > best_score) or \
                (color == BLACK and evaluation < best_score):
            best_score = evaluation
            best_moves = [move]
        elif evaluation == best_score:
            best_moves.append(move)

    return [choice(best_moves), best_score]


def alpha_beta(game, color, depth, alpha=-float('inf'), beta=float('inf')):
    if game_ended(game):
        return [None, evaluate_game(game)]

    [simple_move, simple_evaluation] = evaluated_move(game, color)

    if depth == 1 or \
            simple_evaluation == win_score(opposing_color(color)):
        return [simple_move, simple_evaluation]

    best_moves = []

    if color == WHITE:
        for move in legal_moves(game, color):
            if verbose:
                print('\t' * depth + str(depth) + '. evaluating ' + COIN_CODES[
                    get_coin(game.board, move[0])] + move2str(move))

            new_game = make_move(game, move)
            [_, score] = alpha_beta(new_game, opposing_color(color), depth - 1, alpha, beta)

            if verbose:
                print('\t' * depth + str(depth) + '. ' + str(score) + ' [{},{}]'.format(alpha, beta))

            if score == win_score(opposing_color(color)):
                return [move, score]

            if score == alpha:
                best_moves.append(move)
            if score > alpha:  # white maximizes her score
                alpha = score
                best_moves = [move]
                if alpha > beta:  # alpha-beta cutoff
                    if verbose:
                        print('\t' * depth + 'cutoff')
                    break
        if best_moves:
            return [choice(best_moves), alpha]
        else:
            return [None, alpha]

    if color == BLACK:
        for move in legal_moves(game, color):
            if verbose:
                print('\t' * depth + str(depth) + '. evaluating ' + COIN_CODES[
                    get_coin(game.board, move[0])] + move2str(move))

            new_game = make_move(game, move)
            [_, score] = alpha_beta(new_game, opposing_color(color), depth - 1, alpha, beta)

            if verbose:
                print('\t' * depth + str(depth) + '. ' + str(score) + ' [{},{}]'.format(alpha, beta))

            if score == win_score(opposing_color(color)):
                return [move, score]

            if score == beta:
                best_moves.append(move)
            if score < beta:  # black minimizes his score
                beta = score
                best_moves = [move]
                if alpha > beta:  # alpha-beta cutoff
                    if verbose:
                        print('\t' * depth + 'cutoff')
                    break
        if best_moves:
            return [choice(best_moves), beta]
        else:
            return [None, beta]


def parse_move_code(game, move_code):
    move_code = move_code.replace(" ", "")
    move_code = move_code.replace("x", "")

    if move_code.upper() == 'O-O' or move_code == '0-0':
        if can_castle_kingside(game, game.to_move):
            return castle_kingside_move(game)

    if move_code.upper() == 'O-O-O' or move_code == '0-0-0':
        if can_castle_queenside(game, game.to_move):
            return castle_queenside_move(game)

    if len(move_code) < 2 or len(move_code) > 4:
        return False

    if len(move_code) == 4:
        filter_squares = get_filter(move_code[1])
    else:
        filter_squares = ALL_SQUARES

    destination_str = move_code[-2:]
    if destination_str[0] in FILES and destination_str[1] in RANKS:
        target_square = str2bb(destination_str)
    else:
        return False

    if len(move_code) == 2:
        coin = PAWN
    else:
        coin_code = move_code[0]
        if coin_code in FILES:
            coin = PAWN
            filter_squares = get_filter(coin_code)
        elif coin_code in COIN_CODES:
            coin = COIN_CODES[coin_code] & COIN_MASK
        else:
            return False

    valid_moves = []
    for move in legal_moves(game, game.to_move):
        if move[1] & target_square and \
                move[0] & filter_squares and \
                get_coin(game.board, move[0]) & COIN_MASK == coin:
            valid_moves.append(move)

    if len(valid_moves) == 1:
        return valid_moves[0]
    else:
        return False


def get_player_move(game):
    move = None
    while not move:
        move = parse_move_code(game, input())
        if not move:
            print('Invalid move!')
    return move


def get_AI_move(game, depth=2):
    if verbose:
        print('Searching best move for white...' if game.to_move == WHITE else 'Searching best move for black...')
    start_time = time()

    if find_in_guide(game):
        move = get_guide_move(game)
    else:
        # move = minimax(game, game.to_move, depth)[0]
        move = alpha_beta(game, game.to_move, depth)[0]

    end_time = time()
    if verbose:
        print('Found move ' + COIN_CODES[get_coin(game.board, move[0])] + ' from ' + str(
            bb2str(move[0])) + ' to ' + str(bb2str(move[1])) + ' in {:.3f} seconds'.format(
            end_time - start_time) + ' ({},{})'.format(evaluate_game(game), evaluate_game(make_move(game, move))))
    return move


def print_outcome(game):
    print(get_outcome(game))


def get_outcome(game):
    if is_stalemate(game):
        return 'Draw by stalemate'
    if is_checkmate(game, WHITE):
        return 'BLACK wins!'
    if is_checkmate(game, BLACK):
        return 'WHITE wins!'
    if has_insufficient_material(game):
        return 'Draw by insufficient material!'
    if is_under_75_move_rule(game):
        return 'Draw by 75-move rule!'


def play_as_white(game=Game()):
    print('Playing as white!')
    while True:
        print_board(game.board)
        if game_ended(game):
            break

        game = make_move(game, get_player_move(game))

        print_board(game.board)
        if game_ended(game):
            break

        game = make_move(game, get_AI_move(game))
    print_outcome(game)


def play_as_black(game=Game()):
    print('Playing as black!')
    while True:
        print_rotated_board(game.board)
        if game_ended(game):
            break

        game = make_move(game, get_AI_move(game))

        print_rotated_board(game.board)
        if game_ended(game):
            break

        game = make_move(game, get_player_move(game))
    print_outcome(game)


def watch_AI_game(game=Game(), sleep_seconds=0):
    print('Watching AI-vs-AI game!')
    while True:
        print_board(game.board)
        if game_ended(game):
            break

        game = make_move(game, get_AI_move(game))
        sleep(sleep_seconds)
    print_outcome(game)


def play_as(color):
    if color == WHITE:
        play_as_white()
    if color == BLACK:
        play_as_black()


def play_random_color():
    color = choice([WHITE, BLACK])
    play_as(color)


def find_in_guide(game):
    if game.position_history[0] != INITIAL_FEN:
        return False

    openings = []
    guide_file = open("guide.txt")
    for line in guide_file:
        if line.startswith(game.get_move_list()) and line.rstrip() > game.get_move_list():
            openings.append(line.rstrip())
    guide_file.close()
    return openings


def get_guide_move(game):
    openings = find_in_guide(game)
    chosen_opening = choice(openings)
    next_moves = chosen_opening.replace(game.get_move_list(), '').lstrip()
    move_str = next_moves.split(' ')[0]
    move = [str2bb(move_str[:2]), str2bb(move_str[-2:])]
    return move
