import numpy as np
import time
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

# Функции для преобразования в 16-ричный формат
def to_hex_digit(num):
    if 0 <= num <= 9:
        return str(num)
    elif 10 <= num <= 15:
        return chr(ord('A') + num - 10)
    return '?'

def blocks_to_hex(block_sequence):
    return ''.join(to_hex_digit(b) for b in block_sequence)

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

def backtrack_fill_with_hex(grid_4x4, used_blocks, pos, solutions_set, hex_solutions_set, progress_counter, print_every=100):
    """Backtracking, который собирает все решения в виде 16-ричных строк"""
    if pos == 16:
        if check_rows_and_cols(grid_4x4):
            grid_8x8 = build_8x8(grid_4x4)
            if is_solution(grid_8x8):
                # Преобразуем сетку 4x4 в кортеж для проверки уникальности
                grid_tuple = tuple(grid_4x4[i][j] for i in range(4) for j in range(4))
                
                if grid_tuple not in solutions_set:
                    solutions_set.add(grid_tuple)
                    
                    # Преобразуем в 16-ричную строку
                    hex_solution = blocks_to_hex(grid_tuple)
                    
                    if hex_solution not in hex_solutions_set:
                        hex_solutions_set.add(hex_solution)
                        progress_counter[0] += 1
                        
                        # Выводим прогресс
                        if progress_counter[0] % print_every == 0:
                            print(f"  Найдено решений: {progress_counter[0]}")
        return

    row, col = divmod(pos, 4)

    if grid_4x4[row][col] != -1:
        backtrack_fill_with_hex(grid_4x4, used_blocks, pos + 1, solutions_set, hex_solutions_set, progress_counter, print_every)
        return

    for block_id in range(16):
        if not used_blocks[block_id]:
            grid_4x4[row][col] = block_id
            used_blocks[block_id] = True

            ok = True
            # Ранняя проверка строки
            if all(cell != -1 for cell in grid_4x4[row]):
                row_blocks = grid_4x4[row]
                top_sum = sum(block_props[b]['row1'] for b in row_blocks)
                bottom_sum = sum(block_props[b]['row2'] for b in row_blocks)
                if top_sum != TARGET or bottom_sum != TARGET:
                    ok = False

            # Ранняя проверка столбца
            if ok and all(grid_4x4[r][col] != -1 for r in range(4)):
                col_blocks = [grid_4x4[r][col] for r in range(4)]
                left_sum = sum(block_props[b]['col1'] for b in col_blocks)
                right_sum = sum(block_props[b]['col2'] for b in col_blocks)
                if left_sum != TARGET or right_sum != TARGET:
                    ok = False

            if ok:
                backtrack_fill_with_hex(grid_4x4, used_blocks, pos + 1, solutions_set, hex_solutions_set, progress_counter, print_every)

            used_blocks[block_id] = False
            grid_4x4[row][col] = -1

def find_all_solutions_for_fixed_diagonals(main_diag_fixed, anti_diag_fixed):
    """Находит все решения для фиксированной расстановки диагоналей"""
    print("="*80)
    print("ПОИСК ВСЕХ РЕШЕНИЙ ДЛЯ ФИКСИРОВАННЫХ ДИАГОНАЛЕЙ")
    print("="*80)
    
    # Создаем сетку с фиксированными диагоналями
    grid_4x4 = [[-1 for _ in range(4)] for _ in range(4)]
    
    # Заполняем главную диагональ в указанном порядке
    for i in range(4):
        grid_4x4[i][i] = main_diag_fixed[i]
    
    # Заполняем побочную диагональ в указанном порядке
    for i in range(4):
        grid_4x4[i][3-i] = anti_diag_fixed[i]
    
    print(f"Фиксированная расстановка диагоналей:")
    print(f"  Главная диагональ (порядок): {main_diag_fixed}")
    print(f"  Побочная диагональ (порядок): {anti_diag_fixed}")
    
    # Проверяем, что диагонали не пересекаются
    main_set = set(main_diag_fixed)
    anti_set = set(anti_diag_fixed)
    
    if len(main_set.intersection(anti_set)) > 0:
        print("ОШИБКА: Диагонали пересекаются!")
        return [], []
    
    # Отмечаем использованные блоки
    used_blocks = [False] * 16
    for block_id in main_diag_fixed:
        used_blocks[block_id] = True
    for block_id in anti_diag_fixed:
        used_blocks[block_id] = True
    
    print(f"\nИспользованные блоки на диагоналях: {sorted(main_diag_fixed + anti_diag_fixed)}")
    print(f"Осталось блоков для заполнения: {16 - len(main_diag_fixed) - len(anti_diag_fixed)}")
    print("\nЗапуск поиска всех решений...")
    
    # Наборы для хранения решений
    solutions_set = set()  # Для проверки уникальности по кортежам
    hex_solutions_set = set()  # Для хранения 16-ричных представлений
    progress_counter = [0]
    
    start_time = time.time()
    
    # Запускаем поиск
    backtrack_fill_with_hex(grid_4x4, used_blocks, 0, solutions_set, hex_solutions_set, progress_counter, print_every=100)
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("ПОИСК ЗАВЕРШЕН")
    print(f"{'='*80}")
    
    # Преобразуем set в отсортированный список
    hex_solutions_list = sorted(list(hex_solutions_set))
    
    print(f"Найдено уникальных решений: {len(hex_solutions_list)}")
    print(f"Время выполнения: {elapsed_time:.2f} сек")
    print(f"Среднее время на решение: {elapsed_time/len(hex_solutions_list) if len(hex_solutions_list) > 0 else 0:.4f} сек")
    
    # Выводим первые 10 решений для проверки
    if len(hex_solutions_list) > 0:
        print(f"\nПервые 10 решений (всего {len(hex_solutions_list)}):")
        for i, hex_sol in enumerate(hex_solutions_list[:10], 1):
            print(f"{i:4d}. {hex_sol}")
    
    # Сохраняем все решения в файл
    if len(hex_solutions_list) > 0:
        save_solutions_to_file(hex_solutions_list, main_diag_fixed, anti_diag_fixed, elapsed_time)
    
    return hex_solutions_list, solutions_set

def save_solutions_to_file(hex_solutions_list, main_diag, anti_diag, elapsed_time):
    """Сохраняет все решения в файл"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"solutions_main_{'_'.join(map(str, main_diag))}_anti_{'_'.join(map(str, anti_diag))}_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"ВСЕ РЕШЕНИЯ ДЛЯ ФИКСИРОВАННЫХ ДИАГОНАЛЕЙ\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Главная диагональ (фиксированный порядок): {main_diag}\n")
        f.write(f"Побочная диагональ (фиксированный порядок): {anti_diag}\n")
        f.write(f"Время поиска: {elapsed_time:.2f} сек\n")
        f.write(f"Всего найдено решений: {len(hex_solutions_list)}\n\n")
        
        f.write("РЕШЕНИЯ (16-ричные представления):\n")
        f.write("№     | 16-ричная строка\n")
        f.write("-" * 45 + "\n")
        
        for i, hex_sol in enumerate(hex_solutions_list, 1):
            f.write(f"{i:6d} | {hex_sol}\n")
    
    print(f"\nВсе решения сохранены в файл: {filename}")

def verify_uniqueness(hex_solutions_list):
    """Проверяет уникальность решений"""
    print(f"\nПроверка уникальности решений...")
    
    # Проверка через set
    unique_set = set(hex_solutions_list)
    
    if len(hex_solutions_list) == len(unique_set):
        print(f"✓ Все решения уникальны (уникальных: {len(unique_set)})")
        return True
    else:
        print(f"✗ Найдены дубликаты! Всего решений: {len(hex_solutions_list)}, уникальных: {len(unique_set)}")
        
        # Находим дубликаты
        seen = set()
        duplicates = set()
        for sol in hex_solutions_list:
            if sol in seen:
                duplicates.add(sol)
            else:
                seen.add(sol)
        
        print(f"  Найдено дубликатов: {len(duplicates)}")
        if duplicates:
            print(f"  Примеры дубликатов: {list(duplicates)[:5]}")
        
        return False

def main():
    """Главная функция"""
    # Пара #871 с фиксированной расстановкой диагоналей
    main_diag_fixed = [0, 1, 8, 15]  # Фиксированный порядок на главной диагонали
    anti_diag_fixed = [5, 9, 10, 13]  # Фиксированный порядок на побочной диагонали
    
    print("="*80)
    print(f"ПАРА #871: Главная диагональ: {main_diag_fixed}, Побочная диагональ: {anti_diag_fixed}")
    print("="*80)
    
    # Находим все решения
    hex_solutions, tuple_solutions = find_all_solutions_for_fixed_diagonals(main_diag_fixed, anti_diag_fixed)
    
    # Проверяем уникальность
    if hex_solutions:
        verify_uniqueness(hex_solutions)
        
        # Дополнительная статистика
        print(f"\nДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:")
        print(f"  Всего решений: {len(hex_solutions)}")
        
        # Анализируем структуру решений
        print(f"\nАНАЛИЗ СТРУКТУРЫ РЕШЕНИЙ:")
        
        # Считаем частоту появления каждого блока на каждой позиции
        position_stats = []
        for i in range(16):
            position_stats.append([0] * 16)
        
        # Преобразуем 16-ричные решения обратно в числовые
        for hex_sol in hex_solutions:
            # Преобразуем 16-ричную строку в список чисел
            num_solution = []
            for char in hex_sol:
                if '0' <= char <= '9':
                    num_solution.append(int(char))
                else:
                    num_solution.append(ord(char) - ord('A') + 10)
            
            # Собираем статистику
            for pos, block_id in enumerate(num_solution):
                position_stats[pos][block_id] += 1
        
        # Находим наиболее популярные блоки для каждой позиции
        print(f"  Наиболее популярные блоки для каждой позиции (топ-3):")
        for pos in range(16):
            # Сортируем блоки по частоте для этой позиции
            block_freq = [(block_id, freq) for block_id, freq in enumerate(position_stats[pos]) if freq > 0]
            block_freq.sort(key=lambda x: x[1], reverse=True)
            
            if block_freq:
                top_blocks = block_freq[:3]
                row = pos // 4
                col = pos % 4
                print(f"    Позиция ({row},{col}): ", end="")
                for block_id, freq in top_blocks:
                    percentage = freq / len(hex_solutions) * 100
                    print(f"{block_id}({percentage:.1f}%) ", end="")
                print()
    
    else:
        print("\nРешения не найдены!")

if __name__ == "__main__":
    main()