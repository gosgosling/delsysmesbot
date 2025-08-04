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

class StrictSystemMessageCleanerBot:
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
🤖 **Строгий бот для очистки системных сообщений**

Привет! Я удаляю ТОЛЬКО системные уведомления о входе/выходе участников.

**Что я удаляю:**
• Сообщения типа "Владислав добавил(а) DelSysmess"
• Сообщения типа "Анна покинула группу"
• Другие системные уведомления о участниках

**Что я НЕ удаляю:**
• Обычные сообщения пользователей
• Фото, видео, документы
• Любые другие сообщения

**Команды:**
/start - показать это сообщение
/help - справка
/status - статус бота
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 **Справка по использованию строгого бота**

**Как работает бот:**
1. Анализирует каждое сообщение
2. Удаляет ТОЛЬКО системные уведомления
3. Оставляет все обычные сообщения нетронутыми

**Удаляются ТОЛЬКО:**
• Уведомления о добавлении участников
• Уведомления о выходе участников
• Изменения названия/фото чата
• Закрепленные сообщения

**НЕ удаляются:**
• Любые текстовые сообщения пользователей
• Фото, видео, аудио, документы
• Стикеры, голосовые сообщения
• Команды и ответы бота

**Команды:**
/start - главное меню
/help - эта справка
/status - статус работы
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        chat = update.effective_chat
        
        try:
            # Проверяем права бота
            bot_member = await chat.get_member(context.bot.id)
            
            status_text = f"""
📊 **Статус строгого бота в чате**

**Чат:** {chat.title or chat.first_name}
**Тип чата:** {chat.type}
**ID чата:** {chat.id}

**Права бота:**
• Администратор: {'✅' if bot_member.status in ['administrator', 'creator'] else '❌'}
• Может удалять сообщения: {'✅' if bot_member.can_delete_messages else '❌'}
• Может просматривать сообщения: {'✅' if bot_member.can_read_messages else '❌'}

**Режим:** 🔒 Строгий (удаляет только системные уведомления)
**Статус:** {'🟢 Активен' if bot_member.status in ['administrator', 'creator'] else '🔴 Неактивен'}
            """
        except Exception as e:
            status_text = f"❌ Ошибка при получении статуса: {e}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех сообщений для удаления системных"""
        message = update.message
        
        # Строгая проверка системных сообщений
        if self.is_strict_system_message(message):
            try:
                # Удаляем системное сообщение
                await message.delete()
                logger.info(f"Удалено системное сообщение: {message.text[:50] if message.text else 'No text'} в чате {message.chat.id}")
                
                # Уведомляем только администраторов в личные сообщения
                await self.notify_admins_privately(message, context)
                    
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")
                # Если не удалось удалить, отправляем уведомление только администраторам
                try:
                    await self.notify_admins_privately(message, context, error=True)
                except:
                    pass
        else:
            # Логируем обычные сообщения для отладки
            logger.info(f"Обычное сообщение оставлено: {message.text[:30] if message.text else 'No text'} от {message.from_user.first_name if message.from_user else 'Unknown'}")
    
    async def notify_admins_privately(self, message, context, error=False):
        """Уведомляет администраторов в личные сообщения"""
        try:
            admins = await message.chat.get_administrators()
            for admin in admins:
                if admin.user.id != context.bot.id:  # Не уведомляем самого бота
                    try:
                        if error:
                            notification_text = f"⚠️ Не удалось удалить системное сообщение в чате {message.chat.title}. Проверьте права бота."
                        else:
                            notification_text = f"🗑️ В чате {message.chat.title} удалено системное сообщение: {message.text[:50] if message.text else 'No text'}"
                        
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=notification_text
                        )
                    except:
                        pass  # Игнорируем ошибки отправки в личные сообщения
        except Exception as e:
            logger.error(f"Ошибка при уведомлении администраторов: {e}")
    
    def is_strict_system_message(self, message) -> bool:
        """Строгая проверка системных сообщений"""
        
        # 1. Проверяем системные атрибуты Telegram
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                logger.info(f"Системное сообщение по атрибуту: {message_type}")
                return True
        
        # 2. Проверяем текст на системные уведомления
        if message.text:
            # Уведомления о добавлении участников
            add_keywords = ['добавил(а)', 'добавил', 'добавила', 'added']
            if any(keyword in message.text for keyword in add_keywords):
                logger.info(f"Системное сообщение по ключевому слову добавления: {message.text}")
                return True
            
            # Уведомления о выходе участников
            leave_keywords = ['покинул(а)', 'покинул', 'покинула', 'left', 'ушел', 'ушла']
            if any(keyword in message.text for keyword in leave_keywords):
                logger.info(f"Системное сообщение по ключевому слову выхода: {message.text}")
                return True
            
            # Уведомления об изменениях чата
            change_keywords = ['изменил(а) название', 'изменил название', 'изменила название', 'изменил(а) фото', 'изменил фото', 'изменила фото', 'закрепил(а)', 'закрепил', 'закрепила']
            if any(keyword in message.text for keyword in change_keywords):
                logger.info(f"Системное сообщение по ключевому слову изменения: {message.text}")
                return True
        
        # 3. Проверяем отсутствие контента (чистые системные сообщения)
        if message.text is None and not any([
            message.photo, message.video, message.audio, message.document, 
            message.voice, message.video_note, message.sticker, message.animation
        ]):
            logger.info("Системное сообщение без контента")
            return True
        
        # 4. Если сообщение от пользователя и содержит контент - НЕ системное
        if message.from_user and message.from_user.id != context.bot.id:
            if message.text or message.photo or message.video or message.audio or message.document or message.voice or message.video_note or message.sticker or message.animation:
                return False
        
        return False
    
    def get_message_type(self, message) -> str:
        """Определяет тип системного сообщения"""
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                return message_type
        
        # Определяем тип по содержимому
        if message.text:
            if any(keyword in message.text for keyword in ['добавил(а)', 'добавил', 'добавила', 'added']):
                return 'new_chat_members'
            elif any(keyword in message.text for keyword in ['покинул(а)', 'покинул', 'покинула', 'left', 'ушел', 'ушла']):
                return 'left_chat_member'
            elif any(keyword in message.text for keyword in ['название']):
                return 'new_chat_title'
            elif any(keyword in message.text for keyword in ['фото']):
                return 'new_chat_photo'
            elif any(keyword in message.text for keyword in ['закрепил(а)', 'закрепил', 'закрепила']):
                return 'pinned_message'
        
        return "user_message"
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск строгого бота для очистки системных сообщений...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = StrictSystemMessageCleanerBot()
    bot.run() 