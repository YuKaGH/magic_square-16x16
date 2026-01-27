# тест работает для конкретной пары диагоналей 
# main_set = {2, 1, 13, 8} anti_set = {11, 5, 3, 6}
# можно оробовать оптимизировать
#
#
#
#
#
#
#
import numpy as np
from itertools import permutations

# Исходные блоки 2x2
blocks = [
    [[28, 21], [38, 43]],  # 0
    [[55, 58], [9, 8]],    # 1
    [[37, 44], [27, 22]],  # 2
    [[39, 42], [25, 24]],  # 3
    [[48, 33], [18, 31]],  # 4
    [[17, 32], [47, 34]],  # 5
    [[12, 5], [54, 59]],   # 6
    [[1, 16], [63, 50]],   # 7
    [[53, 60], [11, 6]],   # 8
    [[19, 30], [45, 36]],  # 9
    [[62, 51], [4, 13]],   # 10
    [[46, 35], [20, 29]],  # 11
    [[3, 14], [61, 52]],   # 12
    [[64, 49], [2, 15]],   # 13
    [[10, 7], [56, 57]],   # 14
    [[26, 23], [40, 41]]   # 15
]

TARGET = 260

# Вычисляем свойства каждого блока
block_props = []
for idx, block in enumerate(blocks):
    row1 = block[0][0] + block[0][1]
    row2 = block[1][0] + block[1][1]
    col1 = block[0][0] + block[1][0]
    col2 = block[0][1] + block[1][1]
    main_diag = block[0][0] + block[1][1]
    anti_diag = block[0][1] + block[1][0]

    block_props.append({
        'id': idx,
        'row1': row1, 'row2': row2,
        'col1': col1, 'col2': col2,
        'main_diag': main_diag, 'anti_diag': anti_diag,
        'matrix': block
    })

def build_8x8(grid_4x4):
    grid_8x8 = np.zeros((8, 8), dtype=int)
    for i in range(4):
        for j in range(4):
            block_idx = grid_4x4[i][j]
            block = blocks[block_idx]
            r_start, c_start = i*2, j*2
            grid_8x8[r_start:r_start+2, c_start:c_start+2] = block
    return grid_8x8

def is_solution(grid_8x8):
    for row in range(8):
        if np.sum(grid_8x8[row, :]) != TARGET:
            return False
    for col in range(8):
        if np.sum(grid_8x8[:, col]) != TARGET:
            return False
    if np.sum(np.diag(grid_8x8)) != TARGET:
        return False
    if np.sum(np.diag(np.fliplr(grid_8x8))) != TARGET:
        return False
    return True

def check_rows_and_cols(grid_4x4):
    for row in range(4):
        row_blocks = grid_4x4[row]
        top_sum = sum(block_props[b]['row1'] for b in row_blocks)
        bottom_sum = sum(block_props[b]['row2'] for b in row_blocks)
        if top_sum != TARGET or bottom_sum != TARGET:
            return False
    for col in range(4):
        col_blocks = [grid_4x4[row][col] for row in range(4)]
        left_sum = sum(block_props[b]['col1'] for b in col_blocks)
        right_sum = sum(block_props[b]['col2'] for b in col_blocks)
        if left_sum != TARGET or right_sum != TARGET:
            return False
    return True

def backtrack_fill(grid_4x4, used_blocks, pos, unique_solutions_set, solution_counter):
    if pos == 16:
        if check_rows_and_cols(grid_4x4):
            grid_8x8 = build_8x8(grid_4x4)
            if is_solution(grid_8x8):
                # Преобразуем сетку 4x4 в кортеж из 16 чисел (уникальный ключ)
                grid_tuple = tuple(grid_4x4[i][j] for i in range(4) for j in range(4))

                if grid_tuple not in unique_solutions_set:
                    unique_solutions_set.add(grid_tuple)
                    solution_counter[0] += 1

                    # Выводим решение сразу, как нашли
                    print(f"\nРешение #{solution_counter[0]}:")
                    #print("Сетка 4x4 (индексы блоков):")
                    #for row in grid_4x4:
                        #print("  " + " ".join(f"{idx:2d}" for idx in row))

                    print("Последовательность блоков (16 чисел):")
                    print("  " + " ".join(f"{idx:2d}" for idx in grid_tuple))

                    # Проверка сумм
                    row_sums = [np.sum(grid_8x8[i, :]) for i in range(8)]
                    col_sums = [np.sum(grid_8x8[:, i]) for i in range(8)]
                    main_diag_sum = np.sum(np.diag(grid_8x8))
                    anti_diag_sum = np.sum(np.diag(np.fliplr(grid_8x8)))

                    all_ok = (all(s == TARGET for s in row_sums) and 
                              all(s == TARGET for s in col_sums) and
                              main_diag_sum == TARGET and anti_diag_sum == TARGET)

                    #print(f"Проверка сумм: {'✓ ВСЕ суммы равны 260' if all_ok else '✗ Ошибка'}")
                    print("-"*60)
        return

    row, col = divmod(pos, 4)

    if grid_4x4[row][col] != -1:
        backtrack_fill(grid_4x4, used_blocks, pos + 1, unique_solutions_set, solution_counter)
        return

    for block_id in range(16):
        if not used_blocks[block_id]:
            grid_4x4[row][col] = block_id
            used_blocks[block_id] = True

            ok = True
            # Проверяем строку, если она полностью заполнена
            if all(cell != -1 for cell in grid_4x4[row]):
                row_blocks = grid_4x4[row]
                top_sum = sum(block_props[b]['row1'] for b in row_blocks)
                bottom_sum = sum(block_props[b]['row2'] for b in row_blocks)
                if top_sum != TARGET or bottom_sum != TARGET:
                    ok = False

            # Проверяем столбец, если он полностью заполнен
            if ok and all(grid_4x4[r][col] != -1 for r in range(4)):
                col_blocks = [grid_4x4[r][col] for r in range(4)]
                left_sum = sum(block_props[b]['col1'] for b in col_blocks)
                right_sum = sum(block_props[b]['col2'] for b in col_blocks)
                if left_sum != TARGET or right_sum != TARGET:
                    ok = False

            if ok:
                backtrack_fill(grid_4x4, used_blocks, pos + 1, unique_solutions_set, solution_counter)

            used_blocks[block_id] = False
            grid_4x4[row][col] = -1

# Конкретная пара диагоналей
main_set = {2, 1, 13, 8}
anti_set = {11, 5, 3, 6}

print("Запуск поиска УНИКАЛЬНЫХ решений для пары диагоналей:")
print(f"Главная диагональ: {sorted(main_set)}")
print(f"Побочная диагональ: {sorted(anti_set)}")

unique_solutions_set = set()
solution_counter = [0]  # Счетчик уникальных решений

main_perms = list(permutations(main_set))
anti_perms = list(permutations(anti_set))

total_placements = len(main_perms) * len(anti_perms)
print(f"Всего размещений диагоналей: {total_placements}")
print("="*60)

# Перебираем все размещения диагоналей
for i, main_perm in enumerate(main_perms):
    for j, anti_perm in enumerate(anti_perms):
        # Создаем сетку с диагоналями
        grid_4x4 = [[-1 for _ in range(4)] for _ in range(4)]
        for k in range(4):
            grid_4x4[k][k] = main_perm[k]
            grid_4x4[k][3-k] = anti_perm[k]

        used_blocks = [False] * 16
        for k in range(4):
            used_blocks[main_perm[k]] = True
            used_blocks[anti_perm[k]] = True

        # Запускаем backtracking
        backtrack_fill(grid_4x4, used_blocks, 0, unique_solutions_set, solution_counter)

print(f"\n{'='*60}")
print(f"ПОИСК ЗАВЕРШЕН!")
print(f"Найдено уникальных решений: {solution_counter[0]}")
print(f"Всего размещений диагоналей проверено: {total_placements}")

# Создаем список всех уникальных решений для дальнейшего использования
all_unique_solutions = []
for grid_tuple in unique_solutions_set:
    # Преобразуем кортеж обратно в сетку 4x4
    grid_4x4 = []
    for i in range(4):
        row = []
        for j in range(4):
            row.append(grid_tuple[i*4 + j])
        grid_4x4.append(row)

    all_unique_solutions.append({
        'grid_4x4': grid_4x4,
        'grid_8x8': build_8x8(grid_4x4)
    })

# Выводим все уникальные решения в более компактном виде
print(f"\nВсе уникальные решения ({solution_counter[0]} штук):")
for idx, solution in enumerate(all_unique_solutions, 1):
    print(f"\nУникальное решение #{idx}:")

    # Преобразуем сетку 4x4 в кортеж для вывода
    grid_tuple = tuple(solution['grid_4x4'][i][j] for i in range(4) for j in range(4))

    print(f"  Блоки (16 чисел): {' '.join(f'{num:2d}' for num in grid_tuple)}")

    # Сетка 4x4
    #print("  Сетка 4x4:")
    #for row in solution['grid_4x4']:
        #print("    " + " ".join(f"{idx:2d}" for idx in row))

# Сохраняем все уникальные решения в файл
with open("unique_solutions.txt", "w") as f:
    f.write(f"Всего уникальных решений: {solution_counter[0]}\n")
    f.write(f"Пара диагоналей: главная={sorted(main_set)}, побочная={sorted(anti_set)}\n\n")

    for sol_idx, grid_tuple in enumerate(unique_solutions_set, 1):
        f.write(f"Уникальное решение #{sol_idx}:\n")

        # Преобразуем кортеж обратно в сетку 4x4
        grid_4x4 = []
        for i in range(4):
            row = []
            for j in range(4):
                row.append(grid_tuple[i*4 + j])
            grid_4x4.append(row)

        f.write("Последовательность блоков (16 чисел):\n")
        f.write("  " + " ".join(f"{idx:2d}" for idx in grid_tuple) + "\n")

        f.write("Сетка 4x4 (индексы блоков):\n")
        for row in grid_4x4:
            f.write("  " + " ".join(f"{idx:2d}" for idx in row) + "\n")

        # Квадрат 8x8
        grid_8x8 = build_8x8(grid_4x4)
        f.write("Квадрат 8x8:\n")
        for i in range(8):
            row_str = "  ".join(f"{num:2d}" for num in grid_8x8[i])
            f.write(f"  {row_str}\n")

        # Проверка сумм
        row_sums = [np.sum(grid_8x8[i, :]) for i in range(8)]
        col_sums = [np.sum(grid_8x8[:, i]) for i in range(8)]
        main_diag_sum = np.sum(np.diag(grid_8x8))
        anti_diag_sum = np.sum(np.diag(np.fliplr(grid_8x8)))

        f.write("Проверка сумм:\n")
        f.write(f"  Строки: {row_sums}\n")
        f.write(f"  Столбцы: {col_sums}\n")
        f.write(f"  Главная диагональ: {main_diag_sum}\n")
        f.write(f"  Побочная диагональ: {anti_diag_sum}\n")

        f.write("\n" + "-"*50 + "\n\n")

print(f"\nВсе уникальные решения сохранены в файл 'unique_solutions.txt'")
