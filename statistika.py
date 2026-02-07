import json
import os
from collections import defaultdict

def combine_progress_files(total_parts=10):
    """Объединяет результаты из всех файлов прогресса"""
    print("="*80)
    print("ОБЪЕДИНЕНИЕ СТАТИСТИКИ ИЗ СОХРАНЕННЫХ ФАЙЛОВ ПРОГРЕССА")
    print("="*80)
    
    all_results = []  # Все результаты по парам из всех файлов
    combined_distribution = defaultdict(int)  # Распределение пар по количеству решений
    combined_top10 = []  # Топ-10 пар из всех файлов
    total_pairs_processed = 0
    total_solutions_all = 0
    total_time_all = 0
    all_range_distribution = defaultdict(int)  # Распределение по диапазонам
    
    # Диапазоны для группировки
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
    
    # Читаем все файлы прогресса
    for part_num in range(1, total_parts + 1):
        filename = f"progress_part_{part_num}.json"
        
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"\nЗагружен файл: {filename}")
                print(f"  Обработано пар: {data.get('processed_pairs', 0)}")
                print(f"  Всего решений: {data.get('total_solutions_found', 0):,}")
                print(f"  Время обработки: {data.get('timestamp', 'не указано')}")
                
                # Добавляем результаты из этого файла
                if 'all_results' in data:
                    all_results.extend(data['all_results'])
                    total_pairs_processed += len(data['all_results'])
                
                # Суммируем общее количество решений
                total_solutions_all += data.get('total_solutions_found', 0)
                
                # Объединяем распределение
                if 'distribution' in data:
                    for count, freq in data['distribution'].items():
                        combined_distribution[int(count)] += freq
                
                # Добавляем пары в топ-10
                if 'top10_pairs' in data:
                    for pair in data['top10_pairs']:
                        # Добавляем информацию о части, если её нет
                        if 'part_number' not in pair:
                            pair['part_number'] = part_num
                        combined_top10.append(pair)
                
            except Exception as e:
                print(f"  Ошибка при загрузке файла {filename}: {e}")
        else:
            print(f"\nФайл {filename} не найден")
    
    # Если нет файлов с результатами
    if total_pairs_processed == 0:
        print("\n❌ Не найдено ни одного файла с результатами!")
        print("   Убедитесь, что файлы progress_part_1.json ... progress_part_10.json находятся в текущей папке.")
        return
    
    # Сортируем топ-10 по количеству решений
    combined_top10.sort(key=lambda x: x['solutions_count'], reverse=True)
    final_top10 = combined_top10[:10]
    
    # Группируем распределение по диапазонам
    for count, freq in combined_distribution.items():
        for min_val, max_val, label in ranges:
            if min_val <= count <= max_val:
                all_range_distribution[label] += freq
                break
    
    print(f"\n{'='*80}")
    print("ОБЩАЯ СТАТИСТИКА")
    print(f"{'='*80}")
    
    print(f"\nВсего обработано пар: {total_pairs_processed}")
    print(f"Общее количество решений: {total_solutions_all:,}")
    
    # Распределение пар по количеству решений
    print(f"\nРАСПРЕДЕЛЕНИЕ ПАР ПО КОЛИЧЕСТВУ РЕШЕНИЙ:")
    print("Количество решений | Количество пар")
    print("-" * 45)
    
    # Сортируем по количеству решений
    sorted_distribution = sorted(combined_distribution.items())
    
    # Сначала выводим пары с 0 решений
    if 0 in combined_distribution:
        count = combined_distribution[0]
        percentage = count / total_pairs_processed * 100
        print(f"{'0':17s} | {count:14d} ({percentage:5.1f}%)")
    
    # Выводим остальные в порядке возрастания
    for count, freq in sorted_distribution:
        if count != 0:
            percentage = freq / total_pairs_processed * 100
            print(f"{count:17,d} | {freq:14d} ({percentage:5.1f}%)")
    
    # Распределение по диапазонам
    print(f"\nРАСПРЕДЕЛЕНИЕ ПО ДИАПАЗОНАМ:")
    print("Диапазон решений     | Количество пар")
    print("-" * 40)
    
    label_order = [
        "0", "1-1,000", "1,001-5,000", "5,001-10,000", 
        "10,001-20,000", "20,001-50,000", "50,001-100,000", 
        "100,001-150,000", ">150,000"
    ]
    
    for label in label_order:
        if label in all_range_distribution:
            pairs_count = all_range_distribution[label]
            percentage = pairs_count / total_pairs_processed * 100
            print(f"{label:20s} | {pairs_count:14d} ({percentage:5.1f}%)")
    
    # Топ-10 пар
    print(f"\nТОП-10 ПАР С МАКСИМАЛЬНЫМ КОЛИЧЕСТВОМ РЕШЕНИЙ:")
    print("№  | Решений      | Главная диагональ       | Побочная диагональ")
    print("-" * 80)
    
    for i, pair in enumerate(final_top10, 1):
        main_str = str(sorted(pair['main_diag'])).replace('[', '').replace(']', '')
        anti_str = str(sorted(pair['anti_diag'])).replace('[', '').replace(']', '')
        print(f"{i:2d} | {pair['solutions_count']:11,} | {main_str:23s} | {anti_str}")
    
    # Дополнительная статистика
    print(f"\n{'='*80}")
    print("ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА")
    print(f"{'='*80}")
    
    # Пар без решений
    pairs_with_zero = combined_distribution.get(0, 0)
    pairs_with_solutions = total_pairs_processed - pairs_with_zero
    
    print(f"Пар без решений: {pairs_with_zero} ({pairs_with_zero/total_pairs_processed*100:.1f}%)")
    print(f"Пар с решениями: {pairs_with_solutions} ({pairs_with_solutions/total_pairs_processed*100:.1f}%)")
    
    if pairs_with_solutions > 0:
        avg_solutions = total_solutions_all / pairs_with_solutions
        print(f"Среднее количество решений на пару (с решениями): {avg_solutions:,.0f}")
    
    # Максимальное количество решений
    if final_top10:
        max_solutions = final_top10[0]['solutions_count']
        print(f"Максимальное количество решений в одной паре: {max_solutions:,}")
    
        # Минимальное количество решений среди пар с решениями
        min_solutions = min([p['solutions_count'] for p in all_results if p['solutions_count'] > 0])
        print(f"Минимальное количество решений (среди пар с решениями): {min_solutions:,}")
    
    # Медианное количество решений
    if all_results:
        solutions_counts = [r['solutions_count'] for r in all_results if r['solutions_count'] > 0]
        if solutions_counts:
            solutions_counts.sort()
            median_index = len(solutions_counts) // 2
            median_solutions = solutions_counts[median_index]
            print(f"Медианное количество решений: {median_solutions:,}")
    
    # Сохраняем объединенную статистику
    final_stats = {
        'total_pairs_processed': total_pairs_processed,
        'total_solutions': total_solutions_all,
        'pairs_with_zero_solutions': pairs_with_zero,
        'pairs_with_solutions': pairs_with_solutions,
        'percentage_with_solutions': pairs_with_solutions / total_pairs_processed * 100 if total_pairs_processed > 0 else 0,
        'average_solutions_per_pair_with_solutions': total_solutions_all / pairs_with_solutions if pairs_with_solutions > 0 else 0,
        'distribution': dict(sorted_distribution),
        'range_distribution': dict(all_range_distribution),
        'top10_pairs': final_top10,
        'all_pairs_sample': all_results[:100] if len(all_results) > 100 else all_results  # Сохраняем только выборку
    }
    
    with open("combined_statistics.json", "w", encoding='utf-8') as f:
        json.dump(final_stats, f, indent=2, ensure_ascii=False)
    
    print(f"\nОбъединенная статистика сохранена в файл: combined_statistics.json")
    
    # Экспорт в CSV для Excel/Google Sheets
    export_to_csv(all_results, "results_export.csv")
    
    print(f"Данные для анализа экспортированы в файл: results_export.csv")

def export_to_csv(all_results, filename):
    """Экспортирует результаты в CSV файл"""
    try:
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['pair_index', 'main_diag', 'anti_diag', 'solutions_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in all_results:
                # Преобразуем списки в строки для CSV
                row = {
                    'pair_index': result.get('pair_index', ''),
                    'main_diag': str(result.get('main_diag', [])),
                    'anti_diag': str(result.get('anti_diag', [])),
                    'solutions_count': result.get('solutions_count', 0)
                }
                writer.writerow(row)
        
        print(f"  ✓ Экспортировано {len(all_results)} записей в {filename}")
        
    except Exception as e:
        print(f"  ✗ Ошибка при экспорте в CSV: {e}")

def analyze_specific_part(part_num):
    """Анализирует конкретную часть"""
    filename = f"progress_part_{part_num}.json"
    
    if not os.path.exists(filename):
        print(f"Файл {filename} не найден")
        return
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"АНАЛИЗ ПАРТИИ {part_num}")
    print(f"{'='*80}")
    
    print(f"Обработано пар: {data.get('processed_pairs', 0)}")
    print(f"Всего решений: {data.get('total_solutions_found', 0):,}")
    print(f"Время последнего сохранения: {data.get('timestamp', 'не указано')}")
    
    if 'top10_pairs' in data:
        print(f"\nТоп-10 пар этой части:")
        for i, pair in enumerate(data['top10_pairs'][:5], 1):
            print(f"{i}. Решений: {pair['solutions_count']:,} - "
                  f"Главная: {sorted(pair['main_diag'])}, "
                  f"Побочная: {sorted(pair['anti_diag'])}")
    
    if 'distribution' in data:
        print(f"\nРаспределение в этой части:")
        
        # Группируем по диапазонам
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
        
        range_dist = {}
        for count_str, freq in data['distribution'].items():
            count = int(count_str)
            for min_val, max_val, label in ranges:
                if min_val <= count <= max_val:
                    if label not in range_dist:
                        range_dist[label] = 0
                    range_dist[label] += freq
                    break
        
        total_pairs = sum(data['distribution'].values())
        
        label_order = ["0", "1-1,000", "1,001-5,000", "5,001-10,000", 
                      "10,001-20,000", "20,001-50,000", "50,001-100,000", 
                      "100,001-150,000", ">150,000"]
        
        for label in label_order:
            if label in range_dist:
                pairs_count = range_dist[label]
                percentage = pairs_count / total_pairs * 100
                print(f"  {label:17s}: {pairs_count:4d} пар ({percentage:5.1f}%)")

def check_completion_status():
    """Проверяет статус завершения всех частей"""
    print("\n" + "="*80)
    print("СТАТУС ЗАВЕРШЕНИЯ ЧАСТЕЙ")
    print("="*80)
    
    for part_num in range(1, 11):
        filename = f"progress_part_{part_num}.json"
        
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            processed = data.get('processed_pairs', 0)
            expected = 427  # Примерное ожидаемое количество пар в части
            
            if 'all_results' in data:
                actual_pairs = len(data['all_results'])
                status = "✓ ЗАВЕРШЕНА" if actual_pairs >= expected else f"В ПРОЦЕССЕ ({actual_pairs}/{expected})"
            else:
                status = "✓ ЗАВЕРШЕНА" if processed >= expected else f"В ПРОЦЕССЕ ({processed}/{expected})"
            
            print(f"Часть {part_num}: {status} - {data.get('total_solutions_found', 0):,} решений")
        else:
            print(f"Часть {part_num}: ❌ ФАЙЛ ОТСУТСТВУЕТ")

def main():
    """Главная функция"""
    print("АНАЛИЗАТОР РЕЗУЛЬТАТОВ ПОИСКА МАГИЧЕСКИХ КВАДРАТОВ 8×8")
    print("Этот инструмент объединяет статистику из сохраненных файлов прогресса")
    print("="*80)
    
    while True:
        print("\nДоступные действия:")
        print("1. Объединить статистику из всех 10 частей")
        print("2. Проверить статус завершения всех частей")
        print("3. Проанализировать конкретную часть")
        print("4. Выйти")
        
        choice = input("\nВыберите действие (1-4): ").strip()
        
        if choice == "1":
            combine_progress_files()
        elif choice == "2":
            check_completion_status()
        elif choice == "3":
            try:
                part_num = int(input("Введите номер части (1-10): "))
                if 1 <= part_num <= 10:
                    analyze_specific_part(part_num)
                else:
                    print("Номер части должен быть от 1 до 10")
            except ValueError:
                print("Пожалуйста, введите число от 1 до 10")
        elif choice == "4":
            print("Выход из программы")
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите 1, 2, 3 или 4")
        
        input("\nНажмите Enter для продолжения...")

if __name__ == "__main__":
    main()