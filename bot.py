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

class SystemMessageCleanerBot:
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
🤖 **Бот для очистки системных сообщений**

Привет! Я автоматически удаляю системные сообщения из чатов.

**Что я удаляю:**
• Сообщения о входе/выходе участников
• Изменения названия чата
• Изменения фото чата
• Сообщения о создании чата
• Закрепленные сообщения
• И другие системные уведомления

**Команды:**
/start - показать это сообщение
/help - справка
/status - статус бота

Для работы добавьте меня в чат и дайте права администратора для удаления сообщений.
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 **Справка по использованию бота**

**Как использовать:**
1. Добавьте бота в чат
2. Сделайте бота администратором
3. Дайте права на удаление сообщений
4. Бот автоматически начнет удалять системные сообщения

**Требования:**
• Бот должен быть администратором чата
• Права на удаление сообщений
• Права на просмотр сообщений

**Поддерживаемые типы системных сообщений:**
• new_chat_members - новые участники
• left_chat_member - вышедшие участники
• new_chat_title - изменение названия
• new_chat_photo - изменение фото
• pinned_message - закрепленные сообщения
• И многие другие...

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
📊 **Статус бота в чате**

**Чат:** {chat.title or chat.first_name}
**Тип чата:** {chat.type}
**ID чата:** {chat.id}

**Права бота:**
• Администратор: {'✅' if bot_member.status in ['administrator', 'creator'] else '❌'}
• Может удалять сообщения: {'✅' if bot_member.can_delete_messages else '❌'}
• Может просматривать сообщения: {'✅' if bot_member.can_read_messages else '❌'}

**Статус:** {'🟢 Активен' if bot_member.status in ['administrator', 'creator'] else '🔴 Неактивен'}
            """
        except Exception as e:
            status_text = f"❌ Ошибка при получении статуса: {e}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех сообщений для удаления системных"""
        message = update.message
        
        # Проверяем, является ли сообщение системным
        if self.is_system_message(message):
            try:
                # Удаляем системное сообщение
                await message.delete()
                logger.info(f"Удалено системное сообщение типа {self.get_message_type(message)} в чате {message.chat.id}")
                
                # Уведомляем только администраторов в личные сообщения
                await self.notify_admins_privately(message, context)
                    
            except Exception as e:
                logger.error(f"Ошибка при удалении сообщения: {e}")
                # Если не удалось удалить, отправляем уведомление только администраторам
                try:
                    await self.notify_admins_privately(message, context, error=True)
                except:
                    pass
    
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
                            notification_text = f"🗑️ В чате {message.chat.title} удалено системное сообщение типа: {self.get_message_type(message)}"
                        
                        await context.bot.send_message(
                            chat_id=admin.user.id,
                            text=notification_text
                        )
                    except:
                        pass  # Игнорируем ошибки отправки в личные сообщения
        except Exception as e:
            logger.error(f"Ошибка при уведомлении администраторов: {e}")
    
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
        
        return "unknown"
    
    def run(self):
        """Запуск бота"""
        logger.info("Запуск бота для очистки системных сообщений...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = SystemMessageCleanerBot()
    bot.run() 