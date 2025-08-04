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

class SafeSystemMessageCleanerBot:
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
🛡️ **Безопасный бот для очистки системных сообщений**

Привет! Я удаляю ТОЛЬКО системные уведомления с атрибутами Telegram.

**Что я удаляю:**
• Сообщения с атрибутом new_chat_members
• Сообщения с атрибутом left_chat_member
• Сообщения с атрибутом new_chat_title
• Сообщения с атрибутом pinned_message
• Другие системные атрибуты Telegram

**Что я НЕ удаляю:**
• Любые сообщения от пользователей
• Текстовые сообщения
• Фото, видео, документы
• Стикеры, голосовые сообщения

**Команды:**
/start - показать это сообщение
/help - справка
/status - статус бота
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🛡️ **Справка по безопасному боту**

**Как работает бот:**
1. Проверяет ТОЛЬКО системные атрибуты Telegram
2. Удаляет сообщения с атрибутами new_chat_members, left_chat_member, etc.
3. НИКОГДА не удаляет сообщения от пользователей

**Удаляются ТОЛЬКО:**
• Сообщения с атрибутом new_chat_members
• Сообщения с атрибутом left_chat_member
• Сообщения с атрибутом new_chat_title
• Сообщения с атрибутом new_chat_photo
• Сообщения с атрибутом pinned_message
• И другие системные атрибуты

**НЕ удаляются:**
• Любые сообщения от пользователей
• Текстовые сообщения
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
📊 **Статус безопасного бота в чате**

**Чат:** {chat.title or chat.first_name}
**Тип чата:** {chat.type}
**ID чата:** {chat.id}

**Права бота:**
• Администратор: {'✅' if bot_member.status in ['administrator', 'creator'] else '❌'}
• Может удалять сообщения: {'✅' if bot_member.can_delete_messages else '❌'}
• Может просматривать сообщения: {'✅' if bot_member.can_read_messages else '❌'}

**Режим:** 🛡️ Безопасный (только системные атрибуты)
**Статус:** {'🟢 Активен' if bot_member.status in ['administrator', 'creator'] else '🔴 Неактивен'}
            """
        except Exception as e:
            status_text = f"❌ Ошибка при получении статуса: {e}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех сообщений для удаления системных"""
        message = update.message
        
        # Проверяем только системные атрибуты Telegram
        if self.has_system_attribute(message):
            try:
                # Удаляем системное сообщение
                await message.delete()
                message_type = self.get_system_attribute_type(message)
                logger.info(f"Удалено системное сообщение с атрибутом: {message_type} в чате {message.chat.id}")
                
                # Уведомляем только администраторов в личные сообщения
                await self.notify_admins_privately(message, context, message_type)
                    
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
    
    async def notify_admins_privately(self, message, context, message_type=None, error=False):
        """Уведомляет администраторов в личные сообщения"""
        try:
            admins = await message.chat.get_administrators()
            for admin in admins:
                if admin.user.id != context.bot.id:  # Не уведомляем самого бота
                    try:
                        if error:
                            notification_text = f"⚠️ Не удалось удалить системное сообщение в чате {message.chat.title}. Проверьте права бота."
                        else:
                            notification_text = f"🗑️ В чате {message.chat.title} удалено системное сообщение с атрибутом: {message_type}"
                        
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=notification_text
                        )
                    except:
                        pass  # Игнорируем ошибки отправки в личные сообщения
        except Exception as e:
            logger.error(f"Ошибка при уведомлении администраторов: {e}")
    
    def has_system_attribute(self, message) -> bool:
        """Проверяет наличие системных атрибутов Telegram"""
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                logger.info(f"Найден системный атрибут: {message_type}")
                return True
        return False
    
    def get_system_attribute_type(self, message) -> str:
        """Возвращает тип системного атрибута"""
        for message_type in SYSTEM_MESSAGE_TYPES:
            if hasattr(message, message_type) and getattr(message, message_type) is not None:
                return message_type
        return "unknown"
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск безопасного бота для очистки системных сообщений...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = SafeSystemMessageCleanerBot()
    bot.run() 