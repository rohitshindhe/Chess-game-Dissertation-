import pygame, Engine
from random import choice
from traceback import format_exc
from sys import stderr
from time import strftime
from copy import deepcopy

pygame.init()

SQ_SIDE = 50
AI_SEARCH_DEPTH = 2

RED_CHECK = (240, 150, 150)  # when check sq becomes red
GRAY_LIGHT = (240, 240, 240)
GRAY_DARK = (200, 200, 200)
CHESSWEBSITE_LIGHT = (212, 202, 190)
CHESSWEBSITE_DARK = (100, 92, 89)

BOARD_COLORS = [(GRAY_LIGHT, GRAY_DARK), (CHESSWEBSITE_LIGHT, CHESSWEBSITE_DARK)]
BOARD_COLOR = choice(BOARD_COLORS)

BK = pygame.image.load('Coins/BK.png')
BQ = pygame.image.load('Coins/BQ.png')
BR = pygame.image.load('Coins/BR.png')
BB = pygame.image.load('Coins/BB.png')
BN = pygame.image.load('Coins/BN.png')
BP = pygame.image.load('Coins/BP.png')

WK = pygame.image.load('Coins/WK.png')
WQ = pygame.image.load('Coins/WQ.png')
WR = pygame.image.load('Coins/WR.png')
WB = pygame.image.load('Coins/WB.png')
WN = pygame.image.load('Coins/WN.png')
WP = pygame.image.load('Coins/WP.png')

CLOCK = pygame.time.Clock()
CLOCK_TICK = 10

SCREEN = pygame.display.set_mode((8 * SQ_SIDE, 8 * SQ_SIDE), pygame.RESIZABLE)
SCREEN_TITLE = 'Chess Game'

pygame.display.set_icon(pygame.image.load('Coins/Chess logo.ico'))
pygame.display.set_caption(SCREEN_TITLE)


def resize_screen(sq_side_len):
    global SQ_SIDE
    global SCREEN
    SCREEN = pygame.display.set_mode((8 * sq_side_len, 8 * sq_side_len), pygame.RESIZABLE)
    SQ_SIDE = sq_side_len


def print_empty_board():
    SCREEN.fill(BOARD_COLOR[0])
    paint_dark_squares(BOARD_COLOR[1])


def paint_sq(sq, sq_color):
    col = Engine.FILES.index(sq[0])
    row = 7 - Engine.RANKS.index(sq[1])
    pygame.draw.rect(SCREEN, sq_color, (SQ_SIDE * col, SQ_SIDE * row, SQ_SIDE, SQ_SIDE), 0)


def paint_dark_squares(sq_color):
    for position in Engine.single_gen(Engine.DARK_SQUARES):
        paint_sq(Engine.bb2str(position), sq_color)


def get_sq_rect(sq):
    col = Engine.FILES.index(sq[0])
    row = 7 - Engine.RANKS.index(sq[1])
    return pygame.Rect((col * SQ_SIDE, row * SQ_SIDE), (SQ_SIDE, SQ_SIDE))


def coord2str(position, color=Engine.WHITE):
    if color == Engine.WHITE:
        file_index = int(position[0] / SQ_SIDE)
        rank_index = 7 - int(position[1] / SQ_SIDE)
        return Engine.FILES[file_index] + Engine.RANKS[rank_index]
    if color == Engine.BLACK:
        file_index = 7 - int(position[0] / SQ_SIDE)
        rank_index = int(position[1] / SQ_SIDE)
        return Engine.FILES[file_index] + Engine.RANKS[rank_index]


def print_board(board, color=Engine.WHITE):
    if color == Engine.WHITE:
        printed_board = board
    if color == Engine.BLACK:
        printed_board = Engine.rotate_board(board)

    print_empty_board()

    if Engine.is_check(board, Engine.WHITE):
        paint_sq(Engine.bb2str(Engine.get_king(printed_board, Engine.WHITE)), RED_CHECK)
    if Engine.is_check(board, Engine.BLACK):
        paint_sq(Engine.bb2str(Engine.get_king(printed_board, Engine.BLACK)), RED_CHECK)

    for position in Engine.colored_coin_gen(printed_board, Engine.KING, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BK, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.QUEEN, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BQ, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.ROOK, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BR, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.BISHOP, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BB, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.KNIGHT, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BN, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.PAWN, Engine.BLACK):
        SCREEN.blit(pygame.transform.scale(BP, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))

    for position in Engine.colored_coin_gen(printed_board, Engine.KING, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WK, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.QUEEN, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WQ, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.ROOK, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WR, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.BISHOP, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WB, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.KNIGHT, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WN, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))
    for position in Engine.colored_coin_gen(printed_board, Engine.PAWN, Engine.WHITE):
        SCREEN.blit(pygame.transform.scale(WP, (SQ_SIDE, SQ_SIDE)),
                    get_sq_rect(Engine.bb2str(position)))

    pygame.display.flip()


def set_title(title):
    pygame.display.set_caption(title)
    pygame.display.flip()


def make_AI_move(game, color):
    set_title(SCREEN_TITLE + " - Machine Playing...")
    new_game = Engine.make_move(game, Engine.get_AI_move(game, AI_SEARCH_DEPTH))
    set_title(SCREEN_TITLE)
    print_board(new_game.board, color)
    return new_game


def try_move(game, attempted_move):
    for move in Engine.legal_moves(game, game.to_move):
        if move == attempted_move:
            game = Engine.make_move(game, move)
    return game


def play_as(game, color):
    run = True
    ongoing = True

    try:
        while run:
            CLOCK.tick(CLOCK_TICK)
            print_board(game.board, color)

            if Engine.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + Engine.get_outcome(game))
                ongoing = False

            if ongoing and game.to_move == Engine.opposing_color(color):
                game = make_AI_move(game, color)

            if Engine.game_ended(game):
                set_title(SCREEN_TITLE + ' - ' + Engine.get_outcome(game))
                ongoing = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    leaving_sq = coord2str(event.pos, color)

                if event.type == pygame.MOUSEBUTTONUP:
                    arriving_sq = coord2str(event.pos, color)

                    if ongoing and game.to_move == color:
                        move = (Engine.str2bb(leaving_sq), Engine.str2bb(arriving_sq))
                        game = try_move(game, move)
                        print_board(game.board, color)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == 113:
                        run = False
                    if event.key == 104 and ongoing:  # H key
                        game = make_AI_move(game, color)
                    if event.key == 117:  # U key
                        game = Engine.unmake_move(game)
                        game = Engine.unmake_move(game)
                        set_title(SCREEN_TITLE)
                        print_board(game.board, color)
                        ongoing = True
                    if event.key == 99:  # C key
                        global BOARD_COLOR
                        new_colors = deepcopy(BOARD_COLORS)
                        new_colors.remove(BOARD_COLOR)
                        BOARD_COLOR = choice(new_colors)
                        print_board(game.board, color)
                    if event.key == 112 or event.key == 100:  # P or D key
                        print(game.get_move_list() + '\n')
                        print('\n'.join(game.position_history))
                    if event.key == 101:  # E key
                        print('eval = ' + str(Engine.evaluate_game(game) / 100))

                if event.type == pygame.VIDEORESIZE:
                    if SCREEN.get_height() != event.h:
                        resize_screen(int(event.h / 8.0))
                    elif SCREEN.get_width() != event.w:
                        resize_screen(int(event.w / 8.0))
                    print_board(game.board, color)
    except:
        print(format_exc(), file=stderr)
        bug_file = open('bug_report.txt', 'a')
        bug_file.write('----- ' + strftime('%x %X') + ' -----\n')
        bug_file.write(format_exc())
        bug_file.write('\nPlaying as WHITE:\n\t' if color == Engine.WHITE else '\nPlaying as BLACK:\n\t')
        bug_file.write(game.get_move_list() + '\n\t')
        bug_file.write('\n\t'.join(game.position_history))
        bug_file.write('\n-----------------------------\n\n')
        bug_file.close()


def play_as_black(game=Engine.Game()):
    return play_as(game, Engine.BLACK)


def play_as_white(game=Engine.Game()):
    return play_as(game, Engine.WHITE)


def play_random_color(game=Engine.Game()):          # This is to select random color to start the game
    color = choice([Engine.WHITE, Engine.BLACK])
    play_as(game, color)


play_random_color()
