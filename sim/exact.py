import random, sys
from game import *

class Solver:
    def __init__(self, N, stuck=True):
        self.g = Game(N, stuck); self.memo = {}; self.stuck = stuck
    def val(self, board):
        m = self.memo
        if board in m: return m[board]
        g = self.g
        mv = g.legal(board)
        if not mv:
            left = g.leftover(board); v = left if self.stuck else -left
        else:
            v = max(g.gain(board,n)[0]-g.gain(board,n)[1]-self.val(g.gain(board,n)[2]) for n in mv)
        m[board] = v; return v
    def best_moves(self, board):
        g = self.g; mv = g.legal(board); best=None; bm=[]
        for n in mv:
            a,b,nb = g.gain(board,n); q = a-b-self.val(nb)
            if best is None or q>best: best,bm=q,[n]
            elif q==best: bm.append(n)
        return bm

def exact_policy(S, eps):
    def f(g, board, rng):
        if rng.random() < eps: return rng.choice(g.legal(board))
        return rng.choice(S.best_moves(board))
    return f

if __name__ == '__main__':
    rng = random.Random(3); G = 2000
    for N in (12, 30):
        S = Solver(N, True); g = S.g
        tiers = {'ランダム': exact_policy(S,1.0), 'A(でたらめ60%)': exact_policy(S,0.6),
                 'B(でたらめ30%)': exact_policy(S,0.3), 'C(でたらめ10%)': exact_policy(S,0.1),
                 '完全': exact_policy(S,0.0)}
        names = list(tiers)
        print(f"\n=== 盤面 1〜{N}: 総当たり 行=自分の勝率%(先後平均) ===")
        print(" "*16 + "".join(f"{n:>16s}" for n in names))
        for a in names:
            row=[]
            for b in names:
                w=0
                for i in range(G):
                    if i%2==0: r=play(g,lambda g,bd,r_:tiers[a](g,bd,r_),lambda g,bd,r_:tiers[b](g,bd,r_),rng); w+=(r>0)+0.5*(r==0)
                    else:      r=play(g,lambda g,bd,r_:tiers[b](g,bd,r_),lambda g,bd,r_:tiers[a](g,bd,r_),rng); w+=(r<0)+0.5*(r==0)
                row.append(100*w/G)
            print(f"{a:16s}"+"".join(f"{v:16.1f}" for v in row))
        # 同じ強さどうしの先手勝率
        print(f"\n--- 同じ強さどうしの先手勝率 ---")
        for a in names:
            w=0
            for i in range(G):
                r=play(g,lambda g,bd,r_:tiers[a](g,bd,r_),lambda g,bd,r_:tiers[a](g,bd,r_),rng); w+=(r>0)+0.5*(r==0)
            print(f"  {a:16s} {100*w/G:5.1f}%")
