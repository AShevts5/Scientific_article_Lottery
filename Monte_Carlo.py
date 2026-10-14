import random
from math import comb, sqrt

N = 45
K = 6
trials = 500_000
Seed = 42         

def simulate(trials, Seed=None):
    rng = random.Random(Seed)
    ticket = set(range(1, K + 1))
    numbers = range(1, N + 1)          
    counts = [0] * (K + 1)             

    for i in range(trials):
        draw = rng.sample(numbers, K)  
        matches = len(ticket.intersection(draw))
        counts[matches] += 1
    return counts

def chance(k):
    return comb(K, k) * comb(N - K, K - k) / comb(N, K)


counts = simulate(trials, Seed)

print(f"Число испытаний: {trials:,}".replace(",", " "))
print(f"{'k':>2} {'Частота':>10} {'P (Монте-Карло)':>17} {'P (теория)':>13} {'Погрешность 95%':>16}")

for k in range(K, -1, -1):
    if k == 2:
        break
    p_mc = counts[k] / trials
    p_c = chance(k)
    err = 1.96 * sqrt(p_c * (1 - p_c) / trials)   
    print(f"{k:>2} {counts[k]:>10} {p_mc:>17.8f} {p_c:>13.8f} {err:>16.8f}")

p_win_mc = sum(counts[3:]) / trials
p_win_c = sum(chance(k) for k in range(3, K + 1))
print(f"\nP(угадать не менее 3): Монте-Карло = {p_win_mc:.5f}, теория = {p_win_c:.5f}")








