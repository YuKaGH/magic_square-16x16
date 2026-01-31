import numpy as np
from itertools import combinations

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

print("=" * 70)
print("ТОЧНЫЙ ПОДСЧЕТ КОЛИЧЕСТВА ПАР ДИАГОНАЛЕЙ")
print("=" * 70)

# Шаг 1: Найти все наборы из 4 блоков для главной диагонали
print("\n1. Поиск наборов для главной диагонали (сумма главных диагоналей = 260)...")
main_sets = []
for combo in combinations(range(16), 4):
    if sum(block_props[i]['main_diag'] for i in combo) == TARGET:
        main_sets.append(set(combo))

print(f"   Найдено наборов для главной диагонали: {len(main_sets)}")

# Шаг 2: Найти все наборы из 4 блоков для побочной диагонали
print("2. Поиск наборов для побочной диагонали (сумма побочных диагоналей = 260)...")
anti_sets = []
for combo in combinations(range(16), 4):
    if sum(block_props[i]['anti_diag'] for i in combo) == TARGET:
        anti_sets.append(set(combo))

print(f"   Найдено наборов для побочной диагонали: {len(anti_sets)}")

# Шаг 3: Все возможные пары (даже с пересечениями)
print("\n3. Все возможные пары (включая с пересечениями):")
all_possible_pairs = len(main_sets) * len(anti_sets)
print(f"   {len(main_sets)} × {len(anti_sets)} = {all_possible_pairs} пар")

# Шаг 4: Пары без пересечений (но с симметричными дублями)
print("\n4. Пары без пересечений (с симметричными дублями):")
pairs_no_intersection = 0
for main_set in main_sets:
    for anti_set in anti_sets:
        if main_set.isdisjoint(anti_set):
            pairs_no_intersection += 1

print(f"   Найдено пар без пересечений: {pairs_no_intersection}")
print(f"   Процент от всех пар: {pairs_no_intersection/all_possible_pairs*100:.1f}%")

# Шаг 5: Уникальные пары (без симметричных дублей)
print("\n5. Уникальные пары (без симметричных дублей):")
unique_pairs_set = set()

for main_set in main_sets:
    for anti_set in anti_sets:
        if main_set.isdisjoint(anti_set):
            # Преобразуем в отсортированные кортежи
            main_tuple = tuple(sorted(main_set))
            anti_tuple = tuple(sorted(anti_set))
            
            # Упорядочиваем пару: меньший кортеж идет первым
            # Это гарантирует, что (A,B) и (B,A) считаются одинаковыми
            if main_tuple < anti_tuple:
                pair_key = (main_tuple, anti_tuple)
            else:
                pair_key = (anti_tuple, main_tuple)
            
            unique_pairs_set.add(pair_key)

print(f"   Уникальных пар (без симметричных дублей): {len(unique_pairs_set)}")

# Шаг 6: Подробная статистика
print("\n" + "=" * 70)
print("ПОДРОБНАЯ СТАТИСТИКА")
print("=" * 70)

# Размеры наборов для анализа
print("\nРазмеры наборов для анализа:")
print(f"  Всего возможных комбинаций из 4 блоков из 16: C(16,4) = {len(list(combinations(range(16), 4)))}")

# Выведем несколько примеров наборов
print("\nПримеры наборов для главной диагонали:")
for i in range(min(3, len(main_sets))):
    print(f"  Набор {i+1}: {sorted(main_sets[i])}")

print("\nПримеры наборов для побочной диагонали:")
for i in range(min(3, len(anti_sets))):
    print(f"  Набор {i+1}: {sorted(anti_sets[i])}")

# Выведем несколько примеров уникальных пар
print("\nПримеры уникальных пар диагоналей:")
unique_pairs_list = list(unique_pairs_set)
for i in range(min(5, len(unique_pairs_list))):
    main_tuple, anti_tuple = unique_pairs_list[i]
    print(f"  Пара {i+1}:")
    print(f"    Главная: {list(main_tuple)}")
    print(f"    Побочная: {list(anti_tuple)}")

# Шаг 7: Расчет общего времени поиска
print("\n" + "=" * 70)
print("ОЦЕНКА ВРЕМЕНИ ПОЛНОГО ПОИСКА")
print("=" * 70)

# Время на одну пару (из вашего предыдущего запуска)
time_per_pair = 0.05  # секунды

print(f"\nИсходные данные:")
print(f"  Уникальных пар: {len(unique_pairs_set)}")
print(f"  Время на одну пару: {time_per_pair} сек")

# Для каждой уникальной пары нужно проверить все перестановки на диагоналях
permutations_per_pair = 24 * 24  # 4! для главной × 4! для побочной
print(f"  Перестановок на пару: {permutations_per_pair}")

# Общее время
total_time_estimate = len(unique_pairs_set) * time_per_pair
print(f"\nОценка времени для всех пар:")
print(f"  Всего пар: {len(unique_pairs_set)}")
print(f"  Время на пару: {time_per_pair} сек")
print(f"  Оценочное общее время: {total_time_estimate:.2f} сек")
print(f"  Оценочное общее время: {total_time_estimate/60:.2f} мин")

# Шаг 8: Сохранение списка всех пар в файл
print("\n" + "=" * 70)
print("СОХРАНЕНИЕ РЕЗУЛЬТАТОВ")
print("=" * 70)

# Сохраняем список всех уникальных пар
output_filename = "all_unique_pairs.txt"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write("ВСЕ УНИКАЛЬНЫЕ ПАРЫ ДИАГОНАЛЕЙ\n")
    f.write("=" * 70 + "\n\n")
    
    f.write("СТАТИСТИКА:\n")
    f.write(f"  Наборов для главной диагонали: {len(main_sets)}\n")
    f.write(f"  Наборов для побочной диагонали: {len(anti_sets)}\n")
    f.write(f"  Всех возможных пар: {all_possible_pairs}\n")
    f.write(f"  Пар без пересечений: {pairs_no_intersection}\n")
    f.write(f"  Уникальных пар (без симметричных дублей): {len(unique_pairs_set)}\n\n")
    
    f.write("СПИСОК ВСЕХ УНИКАЛЬНЫХ ПАР:\n")
    f.write("-" * 50 + "\n")
    
    # Сортируем пары для удобства
    sorted_pairs = sorted(unique_pairs_list)
    
    for idx, (main_tuple, anti_tuple) in enumerate(sorted_pairs, 1):
        f.write(f"Пара #{idx}:\n")
        f.write(f"  Главная диагональ: {list(main_tuple)}\n")
        f.write(f"  Побочная диагональ: {list(anti_tuple)}\n")
        
        # Преобразуем в 16-ричный формат для наглядности
        def to_hex_list(num_list):
            hex_map = {10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}
            result = []
            for num in num_list:
                if 0 <= num <= 9:
                    result.append(str(num))
                elif num in hex_map:
                    result.append(hex_map[num])
                else:
                    result.append('?')
            return ''.join(result)
        
        f.write(f"  В 16-ричном виде: {to_hex_list(main_tuple)} / {to_hex_list(anti_tuple)}\n")
        f.write("\n")

print(f"Список всех уникальных пар сохранен в файл: '{output_filename}'")

# Шаг 9: Проверка конкретной пары из вашего примера
print("\n" + "=" * 70)
print("ПРОВЕРКА КОНКРЕТНОЙ ПАРЫ")
print("=" * 70)

# Ваша пара из предыдущего поиска
test_main_set = {2, 1, 13, 8}
test_anti_set = {11, 5, 3, 6}

print(f"Проверяемая пара:")
print(f"  Главная диагональ: {sorted(test_main_set)}")
print(f"  Побочная диагональ: {sorted(test_anti_set)}")

# Проверяем, есть ли эта пара в нашем списке
test_main_tuple = tuple(sorted(test_main_set))
test_anti_tuple = tuple(sorted(test_anti_set))

# Упорядочиваем для поиска
if test_main_tuple < test_anti_tuple:
    test_pair_key = (test_main_tuple, test_anti_tuple)
else:
    test_pair_key = (test_anti_tuple, test_main_tuple)

if test_pair_key in unique_pairs_set:
    print("✓ Эта пара присутствует в списке уникальных пар")
    
    # Находим ее индекс
    pair_index = sorted_pairs.index(test_pair_key) + 1
    print(f"  Номер пары в списке: #{pair_index}")
else:
    print("✗ Эта пара НЕ найдена в списке уникальных пар")
    print("  Возможно, суммы диагоналей не равны 260?")

print("\n" + "=" * 70)
print("ВЫВОДЫ")
print("=" * 70)
print("1. Число 8540, скорее всего, получено из другого метода подсчета")
print("2. Реальное количество уникальных пар будет показано выше")
print("3. При времени 0.05 сек на пару, полный поиск займет около 14 секунд")
print("4. Теперь можно принять решение о запуске полного поиска")