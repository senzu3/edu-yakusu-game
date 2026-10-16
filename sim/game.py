import random, sys
from functools import lru_cache

def make(N):
    pdiv = [0]*(N+1)  # bitmask of proper divisors (bit i = number i)
    for n in range(1, N+1):
        m = 0
        for d in range(1, n):
            if n % d == 0:
                m |= 1 << d
        pdiv[n] = m
    return pdiv

def popsum(mask):
    s = 0; i = 0
    while mask:
        if mask & 1: s += i
        mask >>= 1; i += 1
    return s

class Game:
    def __init__(self, N, leftover_to_stuck=True):
        self.N = N
        self.pdiv = make(N)
        self.full = sum(1 << i for i in range(1, N+1))
        self.leftover_to_stuck = leftover_to_stuck  # True: 質問6のルール(最後に打った人の相手が残りをもらう)
        self.dsum = [popsum(m) for m in self.pdiv]

    def legal(self, board):
        return [n for n in range(1, self.N+1) if (board >> n) & 1 and (self.pdiv[n] & board)]

    def gain(self, board, n):
        """(自分の得点, 相手の得点, 新しい盤面)"""
        given = self.pdiv[n] & board
        return n, popsum(given), board & ~(given | (1 << n))

    def leftover(self, board):
        return popsum(board)

# ---- 方策 ----
def greedy_move(g, board, rng, eps):
    mv = g.legal(board)
    if rng.random() < eps:
        return rng.choice(mv)
    best, bm = None, []
    for n in mv:
        a, b, _ = g.gain(board, n)
        v = a - b
        if best is None or v > best: best, bm = v, [n]
        elif v == best: bm.append(n)
    return rng.choice(bm)

def lookahead_move(g, board, rng):
    mv = g.legal(board)
    best, bm = None, []
    for n in mv:
        a, b, nb = g.gain(board, n)
        v = a - b
        rep = g.legal(nb)
        if rep:
            v -= max(g.gain(nb, m)[0] - g.gain(nb, m)[1] for m in rep)
        if best is None or v > best: best, bm = v, [n]
        elif v == best: bm.append(n)
    return rng.choice(bm)

POLICIES = {
    'ランダム': lambda g,b,r: r.choice(g.legal(b)),
    'よわい':   lambda g,b,r: greedy_move(g,b,r,0.5),
    'ふつう':   lambda g,b,r: greedy_move(g,b,r,0.2),
    'つよい':   lambda g,b,r: lookahead_move(g,b,r),
}

def play(g, p0, p1, rng):
    """p0が先手。戻り値: 先手の得点 - 後手の得点"""
    board = g.full
    score = [0, 0]
    turn = 0
    pol = [p0, p1]
    while True:
        mv = g.legal(board)
        if not mv:
            left = g.leftover(board)
            # turn は「手が打てない人」。最後に打った人は 1-turn
            if g.leftover_to_stuck: score[turn] += left
            else: score[1-turn] += left
            break
        n = pol[turn](g, board, rng)
        a, b, board = g.gain(board, n)
        score[turn] += a; score[1-turn] += b
        turn = 1 - turn
    return score[0] - score[1]
