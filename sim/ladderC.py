import random, sys
sys.argv = ['x']
from game import *
import exact

class SolverNone(exact.Solver):
    def val(self, board):
        m = self.memo
        if board in m: return m[board]
        g = self.g; mv = g.legal(board)
        if not mv: v = 0
        else:
            v = max(g.gain(board,n)[0]-g.gain(board,n)[1]-self.val(g.gain(board,n)[2]) for n in mv)
        m[board] = v; return v

def play_none(g, p0, p1, rng):
    board = g.full; score=[0,0]; turn=0; pol=[p0,p1]
    while g.legal(board):
        n = pol[turn](g, board, rng); a,b,board = g.gain(board,n)
        score[turn]+=a; score[1-turn]+=b; turn=1-turn
    return score[0]-score[1]

rng = random.Random(21)
for N in (20, 30):
    S = SolverNone(N, True); g = S.g
    tiers = {'ランダム':exact.exact_policy(S,1.0),'よわい60%':exact.exact_policy(S,0.6),
             'ふつう30%':exact.exact_policy(S,0.3),'つよい10%':exact.exact_policy(S,0.1)}
    names = list(tiers); G = 2000
    print(f"\n=== 盤面 1〜{N}(ルールC)2戦1組での勝率%(同点は0.5勝) 行=自分 列=相手 ===")
    print(" "*10 + "".join(f"{n:>12s}" for n in names))
    for a in names:
        row=[]
        for b in names:
            w=0
            for _ in range(G):
                t = play_none(g,tiers[a],tiers[b],rng) - play_none(g,tiers[b],tiers[a],rng)
                w += (t>0)+0.5*(t==0)
            row.append(100*w/G)
        print(f"{a:10s}"+"".join(f"{v:12.1f}" for v in row))
    # 引き分け率(同じ強さどうし、2戦1組)
    print("  2戦1組の引き分け率(同じ強さどうし): ", end="")
    for a in names:
        d=0
        for _ in range(G):
            t = play_none(g,tiers[a],tiers[a],rng) - play_none(g,tiers[a],tiers[a],rng)
            d += (t==0)
        print(f"{a} {100*d/G:.0f}%  ", end="")
    print()
