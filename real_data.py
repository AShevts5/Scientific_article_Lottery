import csv
from math import comb
from collections import Counter

file = "D:/Downloads/Monte-Karlo_real.csv"   
N, K = 45, 6
CHI2_CRIT = 60.48   

# Загрузка данных
draws = []
with open(file, encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    next(reader)                                   
    for row in reader:
        nums = [int(x) for x in row[2].split(",")]
        assert len(set(nums)) == K, f"Тираж {row[0]}:"
        draws.append(nums)
 
n = len(draws)
print(f"Загружено тиражей: {n}\n")

# Равномерность: как часто выпадал каждый номер
freq = Counter(x for d in draws for x in d)
expected = n * K / N                               
chi2 = sum((freq[i] - expected) ** 2 / expected for i in range(1, N + 1))
print(f"Ожидаемая частота каждого номера: {expected:.1f}")
print(f"Хи-квадрат = {chi2:.2f} (критическое значение {CHI2_CRIT})")
print("Вывод:", "равномерность не отвергается" if chi2 < CHI2_CRIT
      else "отклонение от равномерности значимо")
print("Чаще всего:", freq.most_common(3), " Реже всего:", freq.most_common()[-3:], "\n")


# Совпадения фиксированного билета с реальными тиражами
def theory(k):
    return comb(K, k) * comb(N - K, K - k) / comb(N, K)


def match_table(ticket, label):
    counts = [0] * (K + 1)
    for d in draws:
        counts[len(set(ticket) & set(d))] += 1
    print(f"Билет {label}: {sorted(ticket)}")
    print(f"{'k':>2} {'Факт':>8} {'Ожидалось':>10} {'Теория P':>10}")
    for k in range(K, -1, -1):
        if k == 2:
            break
        print(f"{k:>2} {counts[k]:>8} {n * theory(k):>10.1f} {theory(k):>10.6f}")
    print(f"Выигрышных (k >= 3): {sum(counts[3:])} из {n}, "
          f"теория: {sum(theory(k) for k in range(3, K + 1)) * n:.1f}\n")


match_table(range(1, K + 1), "1-2-3-4-5-6")
match_table([7, 14, 21, 28, 35, 42], "кратных 7")

