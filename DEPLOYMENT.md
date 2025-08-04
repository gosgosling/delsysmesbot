# 🚀 Деплой бота для работы 24/7

## 🎯 Рекомендуемый вариант: Railway (Бесплатно)

### Шаг 1: Подготовка проекта

1. **Создайте GitHub репозиторий** и загрузите туда все файлы бота
2. **Убедитесь, что у вас есть файлы:**
   - `bot.py` или `advanced_bot.py`
   - `config.py` (с токеном)
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`

### Шаг 2: Настройка Railway

1. **Перейдите на [Railway.app](https://railway.app)**
2. **Войдите через GitHub**
3. **Нажмите "New Project"**
4. **Выберите "Deploy from GitHub repo"**
5. **Выберите ваш репозиторий с ботом**

### Шаг 3: Настройка переменных окружения

1. **В Railway перейдите в "Variables"**
2. **Добавьте переменную:**
   ```
   BOT_TOKEN = ваш_токен_бота
   ```
3. **Сохраните изменения**

### Шаг 4: Запуск

1. **Railway автоматически запустит бота**
2. **Проверьте логи в разделе "Deployments"**
3. **Бот будет работать 24/7!**

---

## 🌐 Альтернативные варианты

### Render (Бесплатно)

1. **Перейдите на [Render.com](https://render.com)**
2. **Создайте "Web Service"**
3. **Подключите GitHub репозиторий**
4. **Настройте:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
5. **Добавьте переменную окружения `BOT_TOKEN`**

### PythonAnywhere (Бесплатно)

1. **Зарегистрируйтесь на [PythonAnywhere.com](https://www.pythonanywhere.com)**
2. **Создайте новый Bash консоль**
3. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ваш_username/ваш_репозиторий.git
   cd ваш_репозиторий
   ```
4. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Настройте токен в config.py**
6. **Запустите бота:**
   ```bash
   python bot.py
   ```

### Heroku (Бесплатно ограниченно)

1. **Установите Heroku CLI**
2. **Создайте приложение:**
   ```bash
   heroku create ваш-бот-имя
   ```
3. **Добавьте переменную окружения:**
   ```bash
   heroku config:set BOT_TOKEN=ваш_токен
   ```
4. **Задеплойте:**
   ```bash
   git push heroku main
   ```

---

## 💰 Платные варианты

### VPS сервер (от $3-5/месяц)

1. **Арендуйте VPS** (DigitalOcean, Vultr, Linode)
2. **Подключитесь по SSH**
3. **Установите Python и зависимости**
4. **Клонируйте репозиторий**
5. **Настройте systemd сервис для автозапуска**

### Облачные платформы

- **Google Cloud Platform** - $300 кредитов бесплатно
- **AWS** - 12 месяцев бесплатно
- **Microsoft Azure** - $200 кредитов бесплатно

---

## 🔧 Настройка автоперезапуска

### Для VPS серверов создайте systemd сервис:

```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

Содержимое файла:
```ini
[Unit]
Description=Telegram System Message Cleaner Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

---

## 📊 Мониторинг

### Проверка работы бота:

1. **Отправьте команду `/status` боту**
2. **Проверьте логи в панели управления**
3. **Настройте уведомления о сбоях**

### Для Railway/Render:
- Логи доступны в веб-интерфейсе
- Автоматические перезапуски при сбоях
- Мониторинг доступности

---

## 🚨 Важные замечания

1. **Никогда не публикуйте токен** в публичных репозиториях
2. **Используйте переменные окружения** для токена
3. **Настройте мониторинг** для отслеживания работы
4. **Регулярно проверяйте логи** на наличие ошибок

---

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи в панели управления
2. Убедитесь, что токен настроен правильно
3. Проверьте, что все зависимости установлены
4. Обратитесь в поддержку платформы 