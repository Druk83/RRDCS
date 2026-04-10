# check-encoding

Проверяет репозиторий на подозрительные строки, похожие на ошибки кодировки (mojibake).

## Быстрый старт

```powershell
# Кросс-платформенный запуск (рекомендуется)
python .tools/check-encoding/check_encoding.py --paths .

# PowerShell-вариант
powershell -ExecutionPolicy Bypass -File .tools/check-encoding/check-encoding.ps1 -Paths .
```

## Параметры

- `-Paths <string[]>` - список файлов/папок для проверки (по умолчанию `.`).

## Выход (Python runner)

- `0` - подозрительных строк не найдено.
- `1` - найдены подозрительные строки.

## Выход (PowerShell runner)

- `0` - подозрительных строк не найдено.
- `1` - найдены подозрительные строки.
- `2` - отсутствует `rg` (ripgrep).

## Примеры

```powershell
# Проверить весь репозиторий (кросс-платформенно)
python .tools/check-encoding/check_encoding.py --paths .

# Проверить весь репозиторий
powershell -ExecutionPolicy Bypass -File .tools/check-encoding/check-encoding.ps1 -Paths .

# Проверить только измененные области
powershell -ExecutionPolicy Bypass -File .tools/check-encoding/check-encoding.ps1 -Paths server client
```
