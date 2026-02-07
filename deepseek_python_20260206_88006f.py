import json
import os
import time
from itertools import permutations
import numpy as np

# Блоки и функции из предыдущего кода (нужны для подсчета решений)
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

def backtrack_fill_count(grid_4x4, used_blocks, pos):
    """Оптимизированный backtracking, который только считает решения (не хранит их)"""
    if pos == 16:
        if check_rows_and_cols(grid_4x4):
            grid_8x8 = build_8x8(grid_4x4)
            if is_solution(grid_8x8):
                return 1
        return 0

    row, col = divmod(pos, 4)

    if grid_4x4[row][col] != -1:
        return backtrack_fill_count(grid_4x4, used_blocks, pos + 1)

    count = 0
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
                count += backtrack_fill_count(grid_4x4, used_blocks, pos + 1)

            used_blocks[block_id] = False
            grid_4x4[row][col] = -1

    return count

def count_solutions_for_pair_detailed(main_diag, anti_diag):
    """Подсчитывает количество решений для каждой перестановки диагоналей в паре"""
    main_perms = list(permutations(main_diag))
    anti_perms = list(permutations(anti_diag))
    
    permutations_stats = []
    total_solutions = 0
    
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

            # Запускаем backtracking для подсчета решений
            solutions_count = backtrack_fill_count(grid_4x4, used_blocks, 0)
            
            permutations_stats.append({
                'main_perm': main_perm,
                'anti_perm': anti_perm,
                'solutions_count': solutions_count
            })
            
            total_solutions += solutions_count
    
    return total_solutions, permutations_stats

def load_top10_pairs():
    """Загружает топ-10 пар из combined_statistics.json или из всех файлов прогресса"""
    # Пробуем загрузить из combined_statistics.json
    if os.path.exists("combined_statistics.json"):
        with open("combined_statistics.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        if 'top10_pairs' in data:
            return data['top10_pairs']
    
    # Иначе собираем из всех файлов прогресса
    all_top_pairs = []
    for part_num in range(1, 11):
        filename = f"progress_part_{part_num}.json"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'top10_pairs' in data:
                all_top_pairs.extend(data['top10_pairs'])
    
    # Сортируем по количеству решений и берем топ-10
    all_top_pairs.sort(key=lambda x: x['solutions_count'], reverse=True)
    return all_top_pairs[:10]

def main():
    print("="*80)
    print("АНАЛИЗ ТОП-10 ПАР С НАИБОЛЬШИМ КОЛИЧЕСТВОМ РЕШЕНИЙ")
    print("="*80)
    
    # Загружаем топ-10 пар
    top10_pairs = load_top10_pairs()
    
    if not top10_pairs:
        print("Не удалось загрузить топ-10 пар. Убедитесь, что файлы с результатами существуют.")
        return
    
    print(f"\nНайдено {len(top10_pairs)} пар для анализа.\n")
    
    # Для каждой пары в топ-10
    for idx, pair in enumerate(top10_pairs, 1):
        main_diag = pair['main_diag']
        anti_diag = pair['anti_diag']
        total_solutions = pair['solutions_count']
        
        print(f"\n{idx}. Анализ пары #{pair.get('pair_index', idx)}:")
        print(f"   Главная диагональ: {sorted(main_diag)}")
        print(f"   Побочная диагональ: {sorted(anti_diag)}")
        print(f"   Всего решений: {total_solutions:,}")
        
        # Проверяем, есть ли уже детальный файл для этой пары
        detailed_filename = f"detailed_pair_{idx}.json"
        
        if os.path.exists(detailed_filename):
            # Загружаем из файла
            print(f"   Загружаем детальные данные из файла {detailed_filename}...")
            with open(detailed_filename, 'r', encoding='utf-8') as f:
                detailed_data = json.load(f)
            permutations_stats = detailed_data['permutations_stats']
        else:
            # Запускаем детальный подсчет
            print(f"   Запуск детального подсчета для {576} перестановок...")
            start_time = time.time()
            calculated_total, permutations_stats = count_solutions_for_pair_detailed(main_diag, anti_diag)
            elapsed_time = time.time() - start_time
            
            # Проверяем, совпадает ли общее количество решений
            if calculated_total != total_solutions:
                print(f"   Внимание: рассчитанное количество решений ({calculated_total}) не совпадает с сохраненным ({total_solutions})")
            
            # Сохраняем детальные данные
            detailed_data = {
                'main_diag': main_diag,
                'anti_diag': anti_diag,
                'total_solutions': calculated_total,
                'permutations_stats': permutations_stats
            }
            
            with open(detailed_filename, 'w', encoding='utf-8') as f:
                json.dump(detailed_data, f, indent=2, ensure_ascii=False)
            
            print(f"   Детальные данные сохранены в {detailed_filename} (время: {elapsed_time:.1f} сек)")
        
        # Анализируем перестановки: сортируем по количеству решений
        sorted_permutations = sorted(permutations_stats, key=lambda x: x['solutions_count'], reverse=True)
        
        # Выводим топ-5 перестановок
        print(f"\n   Топ-5 перестановок с наибольшим количеством решений:")
        for i, perm_stat in enumerate(sorted_permutations[:5], 1):
            print(f"   {i}. Главная: {list(perm_stat['main_perm'])}, "
                  f"Побочная: {list(perm_stat['anti_perm'])} -> "
                  f"{perm_stat['solutions_count']:,} решений")
        
        # Также выводим перестановки с 0 решений (если есть)
        zero_solutions = [p for p in permutations_stats if p['solutions_count'] == 0]
        if zero_solutions:
            print(f"   Перестановок без решений: {len(zero_solutions)} из {len(permutations_stats)} "
                  f"({len(zero_solutions)/len(permutations_stats)*100:.1f}%)")
        
        # Выводим распределение по количеству решений
        print(f"\n   Распределение перестановок по количеству решений:")
        
        # Группируем по диапазонам
        ranges = [
            (0, 0, "0"),
            (1, 10, "1-10"),
            (11, 50, "11-50"),
            (51, 100, "51-100"),
            (101, 200, "101-200"),
            (201, 500, "201-500"),
            (501, 1000, "501-1,000"),
            (1001, 10000, "1,001-10,000"),
            (10001, 1000000, ">10,000")
        ]
        
        range_counts = {label: 0 for _, _, label in ranges}
        
        for perm in permutations_stats:
            count = perm['solutions_count']
            for min_val, max_val, label in ranges:
                if min_val <= count <= max_val:
                    range_counts[label] += 1
                    break
        
        for label in ranges:
            label_name = label[2]
            count = range_counts[label_name]
            if count > 0:
                percentage = count / len(permutations_stats) * 100
                print(f"     {label_name:15s}: {count:3d} перестановок ({percentage:5.1f}%)")

if __name__ == "__main__":
    main()