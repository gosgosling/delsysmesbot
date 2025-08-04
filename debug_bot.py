import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from config import BOT_TOKEN, SYSTEM_MESSAGE_TYPES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DebugSystemMessageCleanerBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Обработчик команды /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Обработчик команды /help
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчик команды /status
        self.application.add_handler(CommandHandler("status", self.status_command))
        
        # Обработчик всех сообщений для проверки системных сообщений
        self.application.add_handler(MessageHandler(filters.ALL, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = """
🔍 **Отладочный бот для очистки системных сообщений**

Это тестовая версия бота для проверки логики определения системных сообщений.

**Команды:**
/start - показать это сообщение
/help - справка
/status - статус бота

Бот будет показывать информацию о каждом сообщении, но НЕ будет их удалять.
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🔍 **Справка по отладочному боту**

Этот бот показывает информацию о каждом сообщении в чате:

**Что показывает бот:**
• Текст сообщения
• Тип сообщения (системное/обычное)
• Причины определения типа
• Рекомендации по удалению

**Используйте для:**
• Проверки логики определения системных сообщений
• Отладки проблем с удалением
• Настройки фильтров

**Команды:**
/start - главное меню
/help - эта справка
/status - статус бота
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        chat = update.effective_chat
        
        try:
            # Проверяем права бота
            bot_member = await chat.get_member(context.bot.id)
            
            status_text = f"""
📊 **Статус отладочного бота в чате**

**Чат:** {chat.title or chat.first_name}
**Тип чата:** {chat.type}
**ID чата:** {chat.id}

**Права бота:**
• Администратор: {'✅' if bot_member.status in ['administrator', 'creator'] else '❌'}
• Может удалять сообщения: {'✅' if bot_member.can_delete_messages else '❌'}
• Может просматривать сообщения: {'✅' if bot_member.can_read_messages else '❌'}

**Режим:** 🔍 Отладка (сообщения не удаляются)
**Статус:** {'🟢 Активен' if bot_member.status in ['administrator', 'creator'] else '🔴 Неактивен'}
            """
        except Exception as e:
            status_text = f"❌ Ошибка при получении статуса: {e}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех сообщений для отладки"""
        message = update.message
        
        # Анализируем сообщение
        is_system = self.is_system_message(message)
        message_type = self.get_message_type(message)
        
        # Создаем отладочную информацию
        debug_info = f"""
🔍 **Анализ сообщения:**

**Отправитель:** {message.from_user.first_name if message.from_user else 'Unknown'}
**Текст:** {message.text[:100] + '...' if message.text and len(message.text) > 100 else message.text or 'Нет текста'}
**Тип:** {message_type}
**Системное:** {'✅ Да' if is_system else '❌ Нет'}

**Атрибуты сообщения:**
"""
        
        # Проверяем системные атрибуты
        for attr in SYSTEM_MESSAGE_TYPES:
            value = getattr(message, attr, None)
            if value is not None:
                debug_info += f"• {attr}: ✅ {value}\n"
        
        # Проверяем наличие контента
        debug_info += f"""
**Контент:**
• Текст: {'✅' if message.text else '❌'}
• Фото: {'✅' if message.photo else '❌'}
• Видео: {'✅' if message.video else '❌'}
• Аудио: {'✅' if message.audio else '❌'}
• Документ: {'✅' if message.document else '❌'}
• Голос: {'✅' if message.voice else '❌'}
• Стикер: {'✅' if message.sticker else '❌'}

**Рекомендация:** {'🗑️ УДАЛИТЬ' if is_system else '✅ ОСТАВИТЬ'}
        """
        
        # Отправляем отладочную информацию только администраторам
        try:
            admins = await message.chat.get_administrators()
            for admin in admins:
                if admin.user.id != context.bot.id:
                    try:
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=debug_info,
                            parse_mode='Markdown'
                        )
                    except:
                        pass
        except Exception as e:
            logger.error(f"Ошибка при отправке отладочной информации: {e}")
    
    def is_system_message(self, message) -> bool:
        """Проверяет, является ли сообщение системным"""
        # Проверяем, есть ли у сообщения системные атрибуты
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                return True
        
        # Проверяем текст сообщения на системные уведомления
        if message.text:
            # Уведомления о добавлении участников
            if any(keyword in message.text for keyword in [
                'добавил(а)', 'добавил', 'добавила', 'присоединился', 'присоединилась',
                'added', 'joined', 'присоединился к группе', 'присоединилась к группе'
            ]):
                return True
            
            # Уведомления о выходе участников
            if any(keyword in message.text for keyword in [
                'покинул(а)', 'покинул', 'покинула', 'left', 'ушел', 'ушла',
                'покинул группу', 'покинула группу', 'ушел из группы', 'ушла из группы'
            ]):
                return True
            
            # Уведомления об изменениях чата
            if any(keyword in message.text for keyword in [
                'изменил(а) название', 'изменил название', 'изменила название',
                'изменил(а) фото', 'изменил фото', 'изменила фото',
                'удалил(а) фото', 'удалил фото', 'удалила фото',
                'закрепил(а)', 'закрепил', 'закрепила', 'pinned'
            ]):
                return True
        
        # Проверяем специальные случаи системных сообщений
        # Системные сообщения обычно не имеют текста или имеют специальный формат
        if message.text is None and not any([
            message.photo, message.video, message.audio, message.document, 
            message.voice, message.video_note, message.sticker, message.animation
        ]):
            # Если нет текста и нет медиа - это скорее всего системное сообщение
            return True
        
        return False
    
    def get_message_type(self, message) -> str:
        """Определяет тип системного сообщения"""
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                return message_type
        
        # Определяем тип по содержимому
        if message.text:
            if any(keyword in message.text for keyword in ['добавил(а)', 'добавил', 'добавила', 'присоединился', 'присоединилась', 'added', 'joined']):
                return 'new_chat_members'
            elif any(keyword in message.text for keyword in ['покинул(а)', 'покинул', 'покинула', 'left', 'ушел', 'ушла']):
                return 'left_chat_member'
            elif any(keyword in message.text for keyword in ['название', 'title']):
                return 'new_chat_title'
            elif any(keyword in message.text for keyword in ['фото', 'photo']):
                return 'new_chat_photo'
            elif any(keyword in message.text for keyword in ['закрепил(а)', 'закрепил', 'закрепила', 'pinned']):
                return 'pinned_message'
        
        return "user_message"
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск отладочного бота для очистки системных сообщений...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = DebugSystemMessageCleanerBot()
    bot.run() 