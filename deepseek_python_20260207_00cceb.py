import numpy as np
from itertools import permutations, combinations
import time
import json
import os
import sys

# Увеличиваем лимит рекурсии для backtracking
sys.setrecursionlimit(10000)

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

def count_solutions_for_pair(main_diag, anti_diag):
    """Подсчитывает количество решений для одной пары диагоналей (без хранения решений)"""
    main_perms = list(permutations(main_diag))
    anti_perms = list(permutations(anti_diag))
    
    total_solutions = 0
    
    for main_perm in main_perms:
        for anti_perm in anti_perms:
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
            total_solutions += backtrack_fill_count(grid_4x4, used_blocks, 0)
    
    return total_solutions

def generate_all_unique_pairs():
    """Генерирует все уникальные пары диагоналей (симметричные убираем)"""
    print("Генерация всех уникальных пар диагоналей...")
    
    # Находим все наборы для главной диагонали
    main_sets = []
    for combo in combinations(range(16), 4):
        if sum(block_props[i]['main_diag'] for i in combo) == TARGET:
            main_sets.append(set(combo))
    
    # Находим все наборы для побочной диагонали
    anti_sets = []
    for combo in combinations(range(16), 4):
        if sum(block_props[i]['anti_diag'] for i in combo) == TARGET:
            anti_sets.append(set(combo))
    
    # Собираем уникальные пары (убираем симметричные (d1,d2) и (d2,d1))
    unique_pairs_set = set()
    for main_set in main_sets:
        for anti_set in anti_sets:
            if main_set.isdisjoint(anti_set):
                # Создаем упорядоченный ключ, чтобы (d1,d2) и (d2,d1) считались одинаковыми
                main_tuple = tuple(sorted(main_set))
                anti_tuple = tuple(sorted(anti_set))
                
                # Упорядочиваем пару, чтобы главная была меньше побочной
                if main_tuple < anti_tuple:
                    pair_key = (main_tuple, anti_tuple)
                else:
                    pair_key = (anti_tuple, main_tuple)
                
                unique_pairs_set.add(pair_key)
    
    # Преобразуем обратно в списки
    unique_pairs = [(list(main), list(anti)) for main, anti in unique_pairs_set]
    
    print(f"Сгенерировано уникальных пар: {len(unique_pairs)}")
    return unique_pairs

def update_top10(top10, new_pair, solutions_count, pair_index):
    """Обновляет топ-10 пар с максимальным количеством решений"""
    # Добавляем новую пару
    top10.append({
        'pair_index': pair_index,
        'main_diag': new_pair[0],
        'anti_diag': new_pair[1],
        'solutions_count': solutions_count
    })
    
    # Сортируем по убыванию количества решений
    top10.sort(key=lambda x: x['solutions_count'], reverse=True)
    
    # Оставляем только топ-10
    if len(top10) > 10:
        top10 = top10[:10]
    
    return top10

def save_progress(part_num, processed_pairs, top10, distribution, total_solutions, all_results):
    """Сохраняет прогресс в JSON файл"""
    progress_data = {
        'part_number': part_num,
        'processed_pairs': processed_pairs,
        'total_solutions_found': total_solutions,
        'top10_pairs': top10,
        'distribution': distribution,
        'all_results': all_results,  # Только количество решений для каждой пары
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    filename = f"progress_part_{part_num}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(progress_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nПрогресс сохранен в файл: {filename}")
    return filename

def load_progress(part_num):
    """Загружает прогресс из JSON файла"""
    filename = f"progress_part_{part_num}.json"
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки файла {filename}: {e}")
            return None
    return None

def process_pairs_batch(pairs_batch, part_num):
    """Обрабатывает партию пар и возвращает статистику"""
    print(f"\n{'='*80}")
    print(f"ОБРАБОТКА ПАРТИИ {part_num} (пары {len(pairs_batch)} шт.)")
    print(f"{'='*80}")
    
    # Пробуем загрузить предыдущий прогресс
    progress = load_progress(part_num)
    if progress:
        print(f"Найден сохраненный прогресс. Продолжаем...")
        start_from = progress['processed_pairs']
        top10 = progress['top10_pairs']
        distribution = progress['distribution']
        total_solutions = progress['total_solutions_found']
        all_results = progress['all_results']
    else:
        start_from = 0
        top10 = []
        distribution = {}
        total_solutions = 0
        all_results = []
    
    start_time = time.time()
    batch_start_idx = (part_num - 1) * 427  # Предполагаем 427 пар в каждой части
    
    # Обрабатываем пары
    for i, (main_diag, anti_diag) in enumerate(pairs_batch[start_from:], start=start_from):
        pair_start = time.time()
        pair_index = batch_start_idx + i
        
        print(f"\nПара {i+1}/{len(pairs_batch)} в партии {part_num} (общая #{pair_index}):")
        print(f"  Главная: {sorted(main_diag)}")
        print(f"  Побочная: {sorted(anti_diag)}")
        
        # Подсчитываем количество решений
        solutions_count = count_solutions_for_pair(main_diag, anti_diag)
        
        # Обновляем статистику
        total_solutions += solutions_count
        
        # Обновляем распределение
        if solutions_count not in distribution:
            distribution[solutions_count] = 0
        distribution[solutions_count] += 1
        
        # Сохраняем результат для этой пары (только количество)
        all_results.append({
            'pair_index': pair_index,
            'main_diag': main_diag,
            'anti_diag': anti_diag,
            'solutions_count': solutions_count
        })
        
        # Обновляем топ-10
        top10 = update_top10(top10, (main_diag, anti_diag), solutions_count, pair_index)
        
        # Выводим результат
        print(f"  Найдено решений: {solutions_count}")
        print(f"  Время на пару: {time.time() - pair_start:.1f} сек")
        
        # Сохраняем прогресс каждые 10 пар
        if (i + 1) % 10 == 0:
            elapsed_total = time.time() - start_time
            avg_time_per_pair = elapsed_total / (i + 1 - start_from)
            remaining_pairs = len(pairs_batch) - (i + 1)
            estimated_remaining = avg_time_per_pair * remaining_pairs
            
            print(f"\n  Прогресс партии {part_num}: {i+1}/{len(pairs_batch)} пар")
            print(f"  Общее время: {elapsed_total:.1f} сек")
            print(f"  Среднее время на пару: {avg_time_per_pair:.1f} сек")
            print(f"  Оценочное время до завершения: {estimated_remaining:.1f} сек")
            
            # Сохраняем промежуточный прогресс
            save_progress(part_num, i + 1, top10, distribution, total_solutions, all_results)
    
    # Сохраняем финальный прогресс
    final_filename = save_progress(part_num, len(pairs_batch), top10, distribution, total_solutions, all_results)
    
    total_time = time.time() - start_time
    
    return {
        'part_number': part_num,
        'pairs_processed': len(pairs_batch),
        'total_solutions': total_solutions,
        'top10_pairs': top10,
        'distribution': distribution,
        'total_time': total_time,
        'results_file': final_filename
    }

def print_statistics_header():
    """Печатает заголовок статистики"""
    print("\n" + "="*100)
    print("СТАТИСТИКА ПОИСКА РЕШЕНИЙ МАГИЧЕСКИХ КВАДРАТОВ 8×8")
    print("="*100)

def main():
    """Основная функция"""
    print_statistics_header()
    
    # Генерируем все уникальные пары
    print("\nГенерация всех уникальных пар диагоналей...")
    all_pairs = generate_all_unique_pairs()
    
    print(f"\nВсего уникальных пар: {len(all_pairs)}")
    print("Разбиваем на 10 частей...")
    
    # Разбиваем на 10 частей (примерно по 427 пар в каждой)
    total_parts = 10
    pairs_per_part = len(all_pairs) // total_parts
    
    all_results_summary = []
    
    for part_num in range(1, total_parts + 1):
        # Определяем диапазон для текущей части
        start_idx = (part_num - 1) * pairs_per_part
        if part_num == total_parts:
            end_idx = len(all_pairs)  # Для последней части берем все оставшиеся
        else:
            end_idx = part_num * pairs_per_part
        
        pairs_batch = all_pairs[start_idx:end_idx]
        
        print(f"\nПартия {part_num}: пары {start_idx}-{end_idx} ({len(pairs_batch)} пар)")
        
        # Обрабатываем партию
        result = process_pairs_batch(pairs_batch, part_num)
        all_results_summary.append(result)
        
        # Выводим статистику по партии
        print(f"\n{'='*80}")
        print(f"РЕЗУЛЬТАТЫ ПАРТИИ {part_num}")
        print(f"{'='*80}")
        print(f"Обработано пар: {result['pairs_processed']}")
        print(f"Общее количество решений: {result['total_solutions']}")
        print(f"Общее время: {result['total_time']:.1f} сек ({result['total_time']/60:.1f} мин)")
        
        # Выводим топ-10 для этой партии
        print(f"\nТоп-10 пар (партия {part_num}):")
        for i, pair in enumerate(result['top10_pairs'], 1):
            print(f"{i:2d}. #{pair['pair_index']:4d} - "
                  f"Главная: {sorted(pair['main_diag'])}, "
                  f"Побочная: {sorted(pair['anti_diag'])}, "
                  f"Решений: {pair['solutions_count']}")
    
    # Объединяем результаты всех партий
    print(f"\n{'='*100}")
    print("ОБЪЕДИНЕНИЕ РЕЗУЛЬТАТОВ ВСЕХ ПАРТИЙ")
    print(f"{'='*100}")
    
    # Собираем общую статистику
    total_pairs_processed = sum(r['pairs_processed'] for r in all_results_summary)
    total_solutions_all = sum(r['total_solutions'] for r in all_results_summary)
    total_time_all = sum(r['total_time'] for r in all_results_summary)
    
    # Объединяем распределения
    combined_distribution = {}
    for result in all_results_summary:
        for count, freq in result['distribution'].items():
            if count not in combined_distribution:
                combined_distribution[count] = 0
            combined_distribution[count] += freq
    
    # Объединяем топ-10 из всех партий
    combined_top10 = []
    for result in all_results_summary:
        for pair in result['top10_pairs']:
            combined_top10.append(pair)
    
    # Сортируем и берем топ-10
    combined_top10.sort(key=lambda x: x['solutions_count'], reverse=True)
    final_top10 = combined_top10[:10]
    
    print(f"\nОБЩАЯ СТАТИСТИКА:")
    print(f"Всего обработано пар: {total_pairs_processed}")
    print(f"Общее количество решений: {total_solutions_all}")
    print(f"Общее время выполнения: {total_time_all:.1f} сек ({total_time_all/3600:.2f} часов)")
    
    # Анализ распределения
    print(f"\nРАСПРЕДЕЛЕНИЕ ПАР ПО КОЛИЧЕСТВУ РЕШЕНИЙ:")
    print("Количество решений | Количество пар")
    print("-" * 45)
    
    # Группируем по диапазонам для лучшей читаемости
    ranges = [
        (0, 0, "0"),
        (1, 1000, "1-1,000"),
        (1001, 5000, "1,001-5,000"),
        (5001, 10000, "5,001-10,000"),
        (10001, 20000, "10,001-20,000"),
        (20001, 50000, "20,001-50,000"),
        (50001, 100000, "50,001-100,000"),
        (100001, 150000, "100,001-150,000"),
        (150001, 1000000, ">150,000")
    ]
    
    range_distribution = {}
    for count, freq in combined_distribution.items():
        for min_val, max_val, label in ranges:
            if min_val <= count <= max_val:
                if label not in range_distribution:
                    range_distribution[label] = 0
                range_distribution[label] += freq
                break
    
    # Исправление: используем фиксированный порядок меток вместо сортировки
    label_order = [
        "0", "1-1,000", "1,001-5,000", "5,001-10,000", 
        "10,001-20,000", "20,001-50,000", "50,001-100,000", 
        "100,001-150,000", ">150,000"
    ]
    
    for label in label_order:
        if label in range_distribution:
            pairs_count = range_distribution[label]
            percentage = pairs_count / total_pairs_processed * 100
            print(f"{label:17s} | {pairs_count:14d} ({percentage:5.1f}%)")
    
    # Выводим итоговый топ-10
    print(f"\nИТОГОВЫЙ ТОП-10 ПАР С МАКСИМАЛЬНЫМ КОЛИЧЕСТВОМ РЕШЕНИЙ:")
    for i, pair in enumerate(final_top10, 1):
        print(f"{i:2d}. #{pair['pair_index']:4d} - "
              f"Главная: {sorted(pair['main_diag'])}, "
              f"Побочная: {sorted(pair['anti_diag'])}, "
              f"Решений: {pair['solutions_count']:,}")
    
    # Сохраняем финальные результаты
    final_results = {
        'total_unique_pairs': len(all_pairs),
        'total_pairs_processed': total_pairs_processed,
        'total_solutions_found': total_solutions_all,
        'total_time_seconds': total_time_all,
        'combined_distribution': combined_distribution,
        'range_distribution': range_distribution,
        'final_top10': final_top10,
        'all_parts_results': [
            {
                'part_number': r['part_number'],
                'pairs_processed': r['pairs_processed'],
                'total_solutions': r['total_solutions'],
                'total_time': r['total_time'],
                'results_file': r['results_file']
            }
            for r in all_results_summary
        ]
    }
    
    with open("final_results.json", "w", encoding='utf-8') as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False)
    
    print(f"\nФинальные результаты сохранены в файл: final_results.json")
    
    # Дополнительный анализ
    print(f"\n{'='*100}")
    print("ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ")
    print(f"{'='*100}")
    
    # Подсчитываем пары без решений
    pairs_with_zero = combined_distribution.get(0, 0)
    pairs_with_solutions = total_pairs_processed - pairs_with_zero
    
    print(f"Пар без решений: {pairs_with_zero} ({pairs_with_zero/total_pairs_processed*100:.1f}%)")
    print(f"Пар с решениями: {pairs_with_solutions} ({pairs_with_solutions/total_pairs_processed*100:.1f}%)")
    
    if pairs_with_solutions > 0:
        avg_solutions_per_pair_with_solutions = total_solutions_all / pairs_with_solutions
        print(f"Среднее количество решений на пару (с решениями): {avg_solutions_per_pair_with_solutions:,.0f}")
    
    # Максимальное количество решений в одной паре
    if final_top10:
        max_solutions = final_top10[0]['solutions_count']
        print(f"Максимальное количество решений в одной паре: {max_solutions:,}")
    
    # Среднее время на пару
    avg_time_per_pair = total_time_all / total_pairs_processed
    print(f"Среднее время обработки одной пары: {avg_time_per_pair:.1f} сек")
    
    # Оценка для полного перебора
    print(f"\nОЦЕНКА ДЛЯ ПОЛНОГО ПЕРЕБОРА ВСЕХ {len(all_pairs)} ПАР:")
    estimated_total_time = avg_time_per_pair * len(all_pairs)
    print(f"Оценочное общее время: {estimated_total_time:.1f} сек ({estimated_total_time/3600:.1f} часов)")

if __name__ == "__main__":
    main()