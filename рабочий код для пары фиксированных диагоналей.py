import numpy as np
import time

start_time = time.time()

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
    [[62, 51], [4, 13]],   # 10 A
    [[46, 35], [20, 29]],  # 11 B
    [[3, 14], [61, 52]],   # 12 C
    [[64, 49], [2, 15]],   # 13 D
    [[10, 7], [56, 57]],   # 14 E
    [[26, 23], [40, 41]]   # 15 F
]

TARGET = 260

# Функция для преобразования числа в 16-ричный символ (0-9, A-F)
def to_hex_digit(num):
    if 0 <= num <= 9:
        return str(num)
    elif 10 <= num <= 15:
        return chr(ord('A') + num - 10)
    else:
        return '?'

# Функция для преобразования последовательности блоков в 16-ричную строку
def blocks_to_hex(block_sequence):
    return ''.join(to_hex_digit(b) for b in block_sequence)

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

# Глобальная переменная для хранения прогресса
progress_counter = [0]

def backtrack_fill(grid_4x4, used_blocks, pos, solutions_hex_set):
    """Backtracking, который сохраняет решения в 16-ричном формате"""
    if pos == 16:
        if check_rows_and_cols(grid_4x4):
            grid_8x8 = build_8x8(grid_4x4)
            if is_solution(grid_8x8):
                # Преобразуем сетку 4x4 в последовательность из 16 чисел
                grid_tuple = tuple(grid_4x4[i][j] for i in range(4) for j in range(4))

                # Конвертируем в 16-ричную строку
                hex_code = blocks_to_hex(grid_tuple)

                # Добавляем в множество (уникальность гарантируется)
                if hex_code not in solutions_hex_set:
                    solutions_hex_set.add(hex_code)

                    # Увеличиваем счетчик прогресса
                    progress_counter[0] += 1

                    # Выводим прогресс каждые 10 решений
                    if progress_counter[0] % 10 == 0:
                        print(f"  Найдено решений: {progress_counter[0]}")

        return

    row, col = divmod(pos, 4)

    if grid_4x4[row][col] != -1:
        backtrack_fill(grid_4x4, used_blocks, pos + 1, solutions_hex_set)
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
                backtrack_fill(grid_4x4, used_blocks, pos + 1, solutions_hex_set)

            used_blocks[block_id] = False
            grid_4x4[row][col] = -1

# Основная программа
main_set = {2, 1, 13, 8}
anti_set = {11, 5, 3, 6}

print("=" * 70)
print("ПОИСК УНИКАЛЬНЫХ РЕШЕНИЙ В 16-РИЧНОМ ФОРМАТЕ")
print("=" * 70)

# ФИКСИРОВАННОЕ РАСПОЛОЖЕНИЕ ДИАГОНАЛЕЙ
fixed_main_diag = [2, 1, 13, 8]   # Порядок на главной диагонали
fixed_anti_diag = [11, 5, 3, 6]   # Порядок на побочной диагонали

print(f"Главная диагональ (2,1,13,8): {blocks_to_hex(fixed_main_diag)}")
print(f"Побочная диагональ (11,5,3,6): {blocks_to_hex(fixed_anti_diag)}")
print()

# Создаем сетку с фиксированными диагоналями
grid_4x4 = [[-1 for _ in range(4)] for _ in range(4)]
for k in range(4):
    grid_4x4[k][k] = fixed_main_diag[k]          # Главная диагональ
    grid_4x4[k][3-k] = fixed_anti_diag[k]        # Побочная диагональ

# Отмечаем использованные блоки (8 блоков на диагоналях)
used_blocks = [False] * 16
for k in range(4):
    used_blocks[fixed_main_diag[k]] = True
    used_blocks[fixed_anti_diag[k]] = True

print("Начинаем поиск уникальных решений...")
print("(Прогресс отображается каждые 10 найденных решений)")
print("-" * 70)

# Множество для хранения уникальных решений в 16-ричном формате
solutions_hex_set = set()

# Сбрасываем счетчик прогресса
progress_counter = [0]

# Запускаем backtracking
backtrack_fill(grid_4x4, used_blocks, 0, solutions_hex_set)

print("-" * 70)
print(f"Поиск завершен!")
print(f"Найдено уникальных решений: {len(solutions_hex_set)}")
print()

# Преобразуем множество в отсортированный список
sorted_solutions = sorted(solutions_hex_set)

# Выводим все решения в консоль
print("ВСЕ УНИКАЛЬНЫЕ РЕШЕНИЯ (в 16-ричном формате):")
print("=" * 70)

for idx, hex_code in enumerate(sorted_solutions, 1):
    # Форматируем вывод для лучшей читаемости
    formatted_code = ' '.join([hex_code[i:i+4] for i in range(0, 16, 4)])
    print(f"#{idx:3d}: {hex_code}  {formatted_code}")
    #print(f"#{idx:3d}: {hex_code}  ")
print("=" * 70)

# Сохраняем в файл
output_filename = "unique_solutions_hex.txt"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("=" * 70 + "\n")
    f.write("УНИКАЛЬНЫЕ РЕШЕНИЯ МАГИЧЕСКОГО КВАДРАТА (16-ричный формат)\n")
    f.write("=" * 70 + "\n\n")

    f.write(f"Пара диагоналей:\n")
    f.write(f"  Главная: {blocks_to_hex(fixed_main_diag)} (2,1,13,8)\n")
    f.write(f"  Побочная: {blocks_to_hex(fixed_anti_diag)} (11,5,3,6)\n\n")

    f.write(f"Всего уникальных решений: {len(sorted_solutions)}\n\n")

    f.write("Список решений (отсортированный):\n")
    f.write("-" * 50 + "\n")

    for idx, hex_code in enumerate(sorted_solutions, 1):
        # Разбиваем код на группы по 4 символа для читаемости
        formatted_code = ' '.join([hex_code[i:i+4] for i in range(0, 16, 4)])
        f.write(f"#{idx:4d}: {hex_code}  ({formatted_code})\n")

    f.write("\n" + "=" * 70 + "\n")
    f.write("ПРИМЕЧАНИЕ: Каждое решение - это 16 символов, представляющих\n")
    f.write("номера блоков в сетке 4x4 (по строкам слева направо).\n")
    f.write("Символы: 0-9 = блоки 0-9, A=10, B=11, C=12, D=13, E=14, F=15\n")
    f.write("=" * 70 + "\n")

print(f"\nВсе решения сохранены в файл '{output_filename}'")

# Также создаем файл с более подробной информацией
detail_filename = "solutions_details.txt"
with open(detail_filename, "w", encoding="utf-8") as f:
    f.write("ПОДРОБНАЯ ИНФОРМАЦИЯ О РЕШЕНИЯХ\n")
    f.write("=" * 70 + "\n\n")

    for idx, hex_code in enumerate(sorted_solutions, 1):
        f.write(f"Решение #{idx}:\n")
        f.write(f"  16-ричный код: {hex_code}\n")

        # Преобразуем обратно в числовую последовательность
        def hex_to_blocks(hex_str):
            result = []
            for char in hex_str:
                if '0' <= char <= '9':
                    result.append(int(char))
                else:
                    result.append(10 + ord(char) - ord('A'))
            return result

        block_seq = hex_to_blocks(hex_code)
        f.write(f"  Числовая последовательность: {' '.join(f'{b:2d}' for b in block_seq)}\n")

        # Восстанавливаем сетку 4x4
        grid_4x4_detail = []
        for i in range(4):
            row = block_seq[i*4:(i+1)*4]
            grid_4x4_detail.append(row)

        f.write(f"  Сетка 4x4:\n")
        for row in grid_4x4_detail:
            f.write(f"    {' '.join(f'{b:2d}' for b in row)}\n")

        # Проверяем решение
        grid_8x8 = build_8x8(grid_4x4_detail)
        is_valid = is_solution(grid_8x8)
        f.write(f"  Проверка: {'ВЕРНО' if is_valid else 'ОШИБКА'}\n")
        f.write("-" * 50 + "\n\n")

print(f"Подробная информация сохранена в файл '{detail_filename}'")

end_time = time.time()

elapsed_time = end_time - start_time

print(f"The task took {elapsed_time:.2f} seconds to complete.")    