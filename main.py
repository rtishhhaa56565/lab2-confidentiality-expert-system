"""Консольный интерфейс экспертной системы."""

from pathlib import Path

from analyzer import extract_facts
from logger import LOG_FILE, write_log
from rules import evaluate


def analyze_text(text: str, save_log: bool = True):
    if not text or not text.strip():
        raise ValueError("Текст для анализа не может быть пустым.")
    facts = extract_facts(text)
    decisions = evaluate(facts)
    if save_log:
        write_log(text, decisions)
    return facts, decisions


def print_result(facts, decisions) -> None:
    print("\n" + "=" * 72)
    print("РЕЗУЛЬТАТ ЭКСПЕРТНОГО АНАЛИЗА")
    print("=" * 72)
    print("Субъекты:", ", ".join(sorted(facts.subjects)) or "не определены")
    print("Получатели:", ", ".join(sorted(facts.recipients)) or "не определены")
    print("Объекты:", ", ".join(sorted(facts.objects)) or "не определены")
    print("Действия:", ", ".join(sorted(facts.actions)) or "не определены")
    print("Контекст:", ", ".join(sorted(facts.context)) or "не определён")

    for number, decision in enumerate(decisions, 1):
        print(f"\nВывод {number} — {decision.status} [{decision.rule_id}]")
        print("Норма:", decision.law)
        print("Почему:", decision.reason)
        print("Рекомендация:", decision.action)
        if decision.questions:
            print("Уточняющие вопросы:")
            for question in decision.questions:
                print("  -", question)
    print("\nИнцидент записан в", LOG_FILE)


def read_file() -> str:
    path = Path(input("Введите путь к TXT-файлу: ").strip())
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise ValueError("Выбранный файл пуст.")
    return text


def show_menu() -> None:
    print("\nЭКСПЕРТНАЯ СИСТЕМА АНАЛИЗА КОНФИДЕНЦИАЛЬНОСТИ")
    print("1 — Ввести текст вручную")
    print("2 — Загрузить текст из файла")
    print("3 — Просмотреть журнал")
    print("0 — Выход")


def main() -> None:
    while True:
        show_menu()
        choice = input("Выберите действие: ").strip()
        try:
            if choice == "0":
                print("Работа программы завершена.")
                break
            if choice == "1":
                text = input("Введите описание ситуации: ")
            elif choice == "2":
                text = read_file()
            elif choice == "3":
                print(LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "Журнал пока пуст.")
                continue
            else:
                print("Неизвестная команда. Выберите 0, 1, 2 или 3.")
                continue
            facts, decisions = analyze_text(text)
            print_result(facts, decisions)
        except (ValueError, FileNotFoundError, UnicodeDecodeError) as error:
            print("Ошибка:", error)


if __name__ == "__main__":
    main()

