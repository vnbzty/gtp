#!/usr/bin/env python

from subprocess import Popen, PIPE

from gtp import parse_vertex, gtp_move, gtp_color
from gtp import BLACK, WHITE, PASS, RESIGN


class GTPSubProcess(object):

    def __init__(self, label, args):
        self.label = label
        self.subprocess = Popen(args, stdin=PIPE, stdout=PIPE)
        print("{} subprocess created".format(label))

    def send(self, data):
        print("sending {}: {}".format(self.label, data))
        self.subprocess.stdin.write(data.encode())
        self.subprocess.stdin.flush()
        result = ""
        while True:
            data = self.subprocess.stdout.readline()
            if not data.strip():
                break
            result += str(data, encoding='utf-8')
        print("got: {}".format(result))
        return result

    def close(self):
        print("quitting {} subprocess".format(self.label))
        self.subprocess.communicate(b"quit\n")


class GTPFacade(object):

    def __init__(self, label, args):
        self.label = label
        self.gtp_subprocess = GTPSubProcess(label, args)

    def name(self):
        self.gtp_subprocess.send("name\n")

    def version(self):
        self.gtp_subprocess.send("version\n")

    def boardsize(self, boardsize):
        self.gtp_subprocess.send("boardsize {}\n".format(boardsize))

    def komi(self, komi):
        self.gtp_subprocess.send("komi {}\n".format(komi))

    def clear_board(self):
        self.gtp_subprocess.send("clear_board\n")

    def genmove(self, color):
        message = self.gtp_subprocess.send(
            "genmove {}\n".format(gtp_color(color)))
        assert message[0] == "="
        return parse_vertex(message[1:].strip())

    def showboard(self):
        self.gtp_subprocess.send("showboard\n")

    def play(self, color, vertex):
        self.gtp_subprocess.send("play {}\n".format(gtp_move(color, vertex)))

    def final_score(self):
        self.gtp_subprocess.send("final_score\n")

    def close(self):
        self.gtp_subprocess.close()


GNUGO = ["/home/research/zhangtianyubj/gnugo-3.8/interface/gnugo", "--mode", "gtp"]
GNUGO_LEVEL_ONE = ["/home/research/zhangtianyubj/gnugo-3.8/interface/gnugo", "--mode", "gtp", "--level", "1"]
GNUGO_MONTE_CARLO = ["/home/research/zhangtianyubj/gnugo-3.8/interface/gnugo", "--mode", "gtp", "--monte-carlo"]
KATAGO_B6C96 = ["/home/research/zhangtianyubj/KataGo/cpp/katago", "gtp", "-config", "/home/research/zhangtianyubj/KataGo/cpp/configs/gtp_example.cfg", "-model", "/home/research/zhangtianyubj/pygtp/gtp/models/g170-b6c96-s175395328-d26788732.bin.gz"]
KATAGO_B6C96_ZTY = ["/home/research/zhangtianyubj/KataGo/cpp/katago", "gtp", "-config", "/home/research/zhangtianyubj/KataGo/cpp/configs/gtp_example.cfg", "-model", "/home/research/zhangtianyubj/KataGo/0111/models/vnb-s156901184-d2213323/model.bin.gz"]


black = GTPFacade("black", GNUGO)
white = GTPFacade("white", KATAGO_B6C96)

black.name()
black.version()

white.name()
white.version()

black.boardsize(9)
white.boardsize(9)

black.komi(5.5)
white.komi(5.5)

black.clear_board()
white.clear_board()

first_pass = False

while True:
    vertex = black.genmove(BLACK)
    if vertex == PASS:
        if first_pass:
            break
        else:
            first_pass = True
    elif vertex == RESIGN:
        break
    else:
        first_pass = False

    black.showboard()

    white.play(BLACK, vertex)
    white.showboard()

    vertex = white.genmove(WHITE)
    if vertex == PASS:
        if first_pass:
            break
        else:
            first_pass = True
    elif vertex == RESIGN:
        break
    else:
        first_pass = False

    white.showboard()

    black.play(WHITE, vertex)
    black.showboard()

black.final_score()
white.final_score()

black.close()
white.close()

