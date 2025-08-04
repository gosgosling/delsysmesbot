import logging
import json
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, SYSTEM_MESSAGE_TYPES

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AdvancedSystemMessageCleanerBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.stats = {
            'messages_deleted': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        self.settings = {
            'auto_delete': True,
            'log_deletions': False,  # По умолчанию отключено
            'notify_admins': True    # По умолчанию включено
        }
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Обработчик inline кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработчик всех сообщений
        self.application.add_handler(MessageHandler(filters.ALL, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("📊 Статистика", callback_data='stats')],
            [InlineKeyboardButton("⚙️ Настройки", callback_data='settings')],
            [InlineKeyboardButton("📖 Справка", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 **Продвинутый бот для очистки системных сообщений**

Привет! Я автоматически удаляю системные сообщения из чатов.

**Основные возможности:**
• Автоматическое удаление системных сообщений
• Статистика работы
• Настраиваемые параметры
• Уведомления администраторов
• Подробное логирование

**Быстрые действия:**
        """
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 **Подробная справка**

**Команды:**
/start - главное меню
/help - эта справка
/status - статус бота в чате
/stats - статистика работы
/settings - настройки бота

**Настройки:**
• auto_delete - автоматическое удаление
• log_deletions - логирование удалений в чат
• notify_admins - уведомления админов в личные сообщения

**Требования для работы:**
• Права администратора
• Права на удаление сообщений
• Права на просмотр сообщений

**Поддерживаемые системные сообщения:**
• Уведомления о входе/выходе участников
• Изменения настроек чата
• Закрепленные сообщения
• Создание/удаление чатов
• И многие другие...
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        chat = update.effective_chat
        
        try:
            bot_member = await chat.get_member(context.bot.id)
            
            status_text = f"""
📊 **Статус бота в чате**

**Информация о чате:**
• Название: {chat.title or chat.first_name}
• Тип: {chat.type}
• ID: {chat.id}
• Участников: {await chat.get_member_count() if chat.type in ['group', 'supergroup'] else 'N/A'}

**Права бота:**
• Статус: {bot_member.status}
• Администратор: {'✅' if bot_member.status in ['administrator', 'creator'] else '❌'}
• Удаление сообщений: {'✅' if bot_member.can_delete_messages else '❌'}
• Просмотр сообщений: {'✅' if bot_member.can_read_messages else '❌'}

**Статус работы:** {'🟢 Активен' if bot_member.status in ['administrator', 'creator'] else '🔴 Неактивен'}
            """
        except Exception as e:
            status_text = f"❌ Ошибка при получении статуса: {e}"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        uptime = datetime.now() - self.stats['start_time']
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        stats_text = f"""
📈 **Статистика работы бота**

**Время работы:** {uptime.days}д {hours}ч {minutes}м {seconds}с
**Удалено сообщений:** {self.stats['messages_deleted']}
**Ошибок:** {self.stats['errors']}
**Эффективность:** {self.stats['messages_deleted'] / max(1, self.stats['messages_deleted'] + self.stats['errors']) * 100:.1f}%

**Настройки:**
• Автоудаление: {'✅' if self.settings['auto_delete'] else '❌'}
• Логирование в чат: {'✅' if self.settings['log_deletions'] else '❌'}
• Уведомления админов: {'✅' if self.settings['notify_admins'] else '❌'}
        """
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settings"""
        keyboard = [
            [
                InlineKeyboardButton(
                    f"{'✅' if self.settings['auto_delete'] else '❌'} Автоудаление", 
                    callback_data='toggle_auto_delete'
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if self.settings['log_deletions'] else '❌'} Логирование в чат", 
                    callback_data='toggle_log_deletions'
                )
            ],
            [
                InlineKeyboardButton(
                    f"{'✅' if self.settings['notify_admins'] else '❌'} Уведомления админов", 
                    callback_data='toggle_notify_admins'
                )
            ],
            [InlineKeyboardButton("🔄 Сбросить статистику", callback_data='reset_stats')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        settings_text = """
⚙️ **Настройки бота**

Выберите параметр для изменения:
        """
        await update.message.reply_text(settings_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на inline кнопки"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'stats':
            await self.stats_command(update, context)
        elif query.data == 'settings':
            await self.settings_command(update, context)
        elif query.data == 'help':
            await self.help_command(update, context)
        elif query.data == 'toggle_auto_delete':
            self.settings['auto_delete'] = not self.settings['auto_delete']
            await query.edit_message_text("✅ Настройка 'Автоудаление' изменена!")
        elif query.data == 'toggle_log_deletions':
            self.settings['log_deletions'] = not self.settings['log_deletions']
            await query.edit_message_text("✅ Настройка 'Логирование в чат' изменена!")
        elif query.data == 'toggle_notify_admins':
            self.settings['notify_admins'] = not self.settings['notify_admins']
            await query.edit_message_text("✅ Настройка 'Уведомления админов' изменена!")
        elif query.data == 'reset_stats':
            self.stats['messages_deleted'] = 0
            self.stats['errors'] = 0
            await query.edit_message_text("✅ Статистика сброшена!")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик всех сообщений для удаления системных"""
        if not self.settings['auto_delete']:
            return
            
        message = update.message
        
        # Проверяем, является ли сообщение системным
        if self.is_system_message(message):
            try:
                # Удаляем системное сообщение
                await message.delete()
                self.stats['messages_deleted'] += 1
                
                logger.info(f"Удалено системное сообщение типа {self.get_message_type(message)} в чате {message.chat.id}")
                
                # Логирование в чат (если включено)
                if self.settings['log_deletions'] and message.chat.type in ['group', 'supergroup']:
                    log_message = f"🗑️ Удалено системное сообщение: {self.get_message_type(message)}"
                    await context.bot.send_message(
                        chat_id=message.chat.id,
                        text=log_message,
                        reply_to_message_id=None
                    )
                
                # Уведомление администраторов в личные сообщения
                if self.settings['notify_admins']:
                    await self.notify_admins_privately(message, context)
                    
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Ошибка при удалении сообщения: {e}")
                
                # Уведомление об ошибке только администраторам
                if self.settings['notify_admins']:
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
        logger.info("Запуск продвинутого бота для очистки системных сообщений...")
        logger.info(f"Настройки: {self.settings}")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = AdvancedSystemMessageCleanerBot()
    bot.run() 