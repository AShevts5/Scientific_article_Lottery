import csv
import math
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import chi2 as chi2_dist
from sklearn.cluster import DBSCAN

file = "Monte-Karlo_real.csv"
N, K = 45, 6
ALPHA = 0.05

# Загрузка данных 
draws = []
draw_ids = []
with open(file, encoding="utf-8-sig", newline="") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        nums = [int(x) for x in row[2].split(",")]
        assert len(set(nums)) == K, f"Тираж {row[0]}:"
        draws.append(nums)
        draw_ids.append(int(row[0]))

n = len(draws)
print(f"Загружено тиражей: {n}\n")

# Наблюдаемые и ожидаемые частоты
freq: dict[int, int] = Counter(x for d in draws for x in d)
expected = n * K / N

# Таблица для расчёта хи-квадрат
print(f"{'Число':>5} {'O':>5} {'E':>20} {'O-E':>20} {'(O-E)^2/E':>22}")
chi2 = 0.0
for i in range(1, N + 1):
    o = freq[i]
    part = (o - expected) ** 2 / expected
    chi2 += part
    print(f"{i:>5} {o:>5} {expected:>20.5f} {o - expected:>20.5f} {part:>22.5f}")
print(f"{'Итого':>5} {sum(freq.values()):>5} {expected * N:>20.5f} {'':>20} {chi2:>22.5f}\n")

# Критическое значение и p-значение 
df = N - 1
crit = float(chi2_dist.ppf(1 - ALPHA, df))
p_value = float(chi2_dist.sf(chi2, df))
print(f"Хи-квадрат = {chi2!r}")
print(f"df = {df}, критическое значение (alpha={ALPHA}) = {crit!r}")
print(f"p-значение = {p_value!r}")
print("Вывод:", "равномерность не отвергается" if chi2 < crit
      else "отклонение от равномерности значимо")
print("Чаще всего:", freq.most_common(3), " Реже всего:", freq.most_common()[-3:], "\n")

# Критерий серий, основанный на медиане выборки.
order = sorted(range(n), key=lambda i: draw_ids[i])
sums = [sum(draws[i]) for i in order]
ranked = sorted(sums)
series_n = len(ranked)
if series_n % 2 == 1:
    median_sum = ranked[series_n // 2]
else:
    median_sum = (ranked[series_n // 2 - 1] + ranked[series_n // 2]) / 2
signs = ["+" if value > median_sum else "-" for value in sums if value != median_sum]
runs = 1
longest = 1
current = 1
for i in range(1, len(signs)):
    if signs[i] == signs[i - 1]:
        current += 1
        longest = max(longest, current)
    else:
        current = 1
        runs += 1
runs_bound = math.floor(0.5 * (series_n + 1 - 1.96 * math.sqrt(series_n - 1)))
longest_bound = math.floor(3.3 * (math.log10(series_n) + 1))
no_trend = runs > runs_bound and longest < longest_bound

print("Критерий серий, основанный на медиане выборки")
print(f"n = {series_n}, медиана суммы = {median_sum}")
print(f"значений, равных медиане и пропущенных: {series_n - len(signs)}")
print(f"число серий v(n) = {runs}, порог целой части = {runs_bound}")
print(f"длина самой длинной серии tau = {longest}, порог целой части = {longest_bound}")
print("Вывод:", "гипотеза верна" if no_trend else "гипотеза об отсутствии тренда отвергается")
print()

''' DBSCAN группирует числа с близкой частотой.
Расстояние - разница частот; eps=2 означает, что числа попадают
в одну группу, если их частоты отличаются не больше чем на 2 '''
numbers = np.arange(1, N + 1)
observed = np.array([freq[i] for i in numbers], dtype=float)
labels = DBSCAN(eps=2, min_samples=2).fit_predict(observed.reshape(-1, 1))

cluster_ids = [lab for lab in sorted(set(labels)) if lab != -1]
core = max(cluster_ids, key=lambda lab: np.count_nonzero(labels == lab))
groups = {"чаще": [], "реже": [], "типичные": []}
for number, count, lab in zip(numbers, observed, labels):
    item = (int(number), int(count))
    if lab == core:
        groups["типичные"].append(item)
    elif count > expected:
        groups["чаще"].append(item)
    else:
        groups["реже"].append(item)

print("DBSCAN (eps=2, min_samples=2) по частоте выпадения")
for name in ("чаще", "реже"):
    items = sorted(groups[name], key=lambda item: item[1], reverse=(name == "чаще"))
    printable = ", ".join(f"{number} ({count})" for number, count in items)
    print(f"{name}: {printable}")

typical = sorted(groups["типичные"], key=lambda item: item[1])
print("типичные:")
per_line = 6
for start in range(0, len(typical), per_line):
    line = typical[start:start + per_line]
    print("  " + ", ".join(f"{number} ({count})" for number, count in line))
print()

colors = {"чаще": "#c0392b", "реже": "#2471a3", "типичные": "#95a5a6"}
bar_colors = []
for count, lab in zip(observed, labels):
    if lab == core:
        bar_colors.append(colors["типичные"])
    elif count > expected:
        bar_colors.append(colors["чаще"])
    else:
        bar_colors.append(colors["реже"])

fig, ax = plt.subplots(figsize=(12, 5))
ax.bar(numbers, observed, color=bar_colors, width=0.8)
ax.axhline(expected, color="#1a1a1a", linestyle="--", linewidth=1)
ax.set_xlabel("Число")
ax.set_ylabel("Сколько раз выпало")
ax.set_title("Частота чисел и группы DBSCAN")
ax.set_xticks(numbers)
ax.tick_params(axis="x", labelsize=8)
handles = [
    Line2D([0], [0], color="#1a1a1a", linestyle="--", linewidth=1,
           label=f"ожидаемая частота {expected:.2f}"),
    *(Patch(facecolor=color, edgecolor="none", label=name) for name, color in colors.items()),
]
ax.legend(handles=handles)
fig.tight_layout()
figure_path = Path(file).resolve().with_name("freq_dbscan.png")
fig.savefig(figure_path, dpi=150)
print(f"Столбчатая диаграмма сохранена: {figure_path}")
plt.show()
