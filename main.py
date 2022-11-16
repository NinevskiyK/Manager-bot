import telebot
from telebot import types
from datetime import date, datetime, time, timedelta

"""
!!!!Надо обязательно сделать /start в группе!!!!
"""
TOKEN = ''
bot = telebot.TeleBot(TOKEN)
chat_id = -1
banned = {}


def something_wrong(id=chat_id):
    try:
        bot.send_message(id, 'Что то пошло не так....')
    except:
        print('Не братишка вот тут ты не прав конкретно')


@bot.message_handler(content_types=['new_chat_members'])
def handler_new_member(message):
    try:
        username = message.new_chat_members[0].username
        bot.send_message(message.chat.id, "@{}, сколько. ты. зарабатываешь?".format(username))
        bot.send_photo(message.chat.id, "https://s4.cdn.eg.ru/wp-content/uploads/2020/01/22015723.jpg")
    except:
        something_wrong(message.chat.id)


def get_ban_markup(asked, to_ban, to_ban_username):
    try:
        ban_markup = types.InlineKeyboardMarkup()
        to_end = str(asked) + '|' + str(to_ban) + '|' + str(to_ban_username)
        seconds = types.InlineKeyboardButton(text='60 Секунд', callback_data='seconds|60|' + to_end)
        minutes = types.InlineKeyboardButton(text='15 Минут', callback_data='minutes|15|' + to_end)
        hours = types.InlineKeyboardButton(text='1 час', callback_data='hours|1|' + to_end)
        days = types.InlineKeyboardButton(text='1 день', callback_data='days|1|' + to_end)
        months = types.InlineKeyboardButton(text='1 месяц', callback_data='months|1|' + to_end)
        forever = types.InlineKeyboardButton(text='Навсегда!', callback_data='days|367|' + to_end)
        ban_markup.row(seconds, minutes, hours)
        ban_markup.row(days, months)
        ban_markup.row(forever)
        return ban_markup
    except:
        something_wrong()


def ban(id_, username, col, what):
    try:
        d = {str(what): int(col)}
        tm = datetime.now() + timedelta(**d)
        banned[username] = id_
        return bot.ban_chat_member(chat_id, id_, int(tm.timestamp()))
    except:
        something_wrong()


def unban(id_):
    try:
        if chat_id != -1:
            bot.unban_chat_member(chat_id, id_, True)
    except:
        something_wrong()


@bot.callback_query_handler(func=lambda c: True)
def proccess_banning(message):
    try:
        splitted = message.data.split('|')
        person_asked = splitted[2]
        if person_asked != str(message.from_user.id):
            bot.answer_callback_query(callback_query_id=message.id, text='Не ты же просил, не надо жать!')
        else:
            bot.edit_message_reply_markup(message.message.chat.id, message.message.message_id, reply_markup=None)
            if ban(splitted[3], splitted[4], splitted[1], splitted[0]):
                bot.send_message(message.message.chat.id,
                                 '@{} ушел в бан на {} {}'.format(splitted[4], splitted[1], splitted[0]))
            else:
                bot.send_message(message.message.chat.id, 'Что то пошло не так')
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['leave_pls'])
def goodbye(message):
    try:
        if check_if_person_admin(message.from_user.id):
            global chat_id
            bot.send_message(message.chat.id, 'Эх ну и оставайтесь в гордом одиночестве!')
            chat_id = -1
            bot.leave_chat(message.chat.id)
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['statistics'])
def statistics(message):
    try:
        members = bot.get_chat_member_count(message.chat.id)
        admins = len(bot.get_chat_administrators(message.chat.id))
        bot.send_message(message.chat.id, "Всего тут {} участников и {} админов".format(members, admins))
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['start'])
def hello(message):
    try:
        global chat_id
        if chat_id != -1:
            bot.send_message(chat_id, 'Меня позвали в другом чатике, я пошел!')
        chat_id = message.chat.id
        bot.send_message(message.chat.id, 'Привет! Теперь я работаю в этом чатике.'
                                          ' Чтобы я работал в другом, вызови там /start\n'
                         'Я помогу тебе администрировать группы. Только дай мне админские права!\n'
                         'Чтобы забанить, сделать админом или антиадмином человека, вызови /ban, /to_admin,'
                         '/to_member на реплай.\n'
                         'Если захочешь разбанить, напиши в поиске @botname чтобы я показал тебе инлайновые опции.\n'
                         'Также /statistics и /leave_pls дают статистику или просят бота уйти.\n'
                         'А еще он приветствует всех зашедших людей(по своему)!')
    except:
        something_wrong(message.chat.id)


def check_if_person_admin(id_, send_something=True):
    try:
        if chat_id == -1:
            return False
        user = bot.get_chat_member(chat_id, id_)
        if user.status == 'creator':
            if send_something:
                bot.send_message(chat_id, 'Прячтесь люди! Создатель чата пришел!')
            return True
        if user.status in ['administrator', 'creator']:
            if send_something:
                bot.send_message(chat_id, 'Ща сделаем')
            return True
        elif user.status == 'member':
            if send_something:
                bot.send_message(chat_id, 'Ну и куда ты? Мемберам нельзя!')
            return False
        else:
            if send_something:
                bot.send_message(chat_id, 'Не понял, кто ты. Не могу выполнить функцию!')
            return False
    except:
        something_wrong()


@bot.message_handler(commands=['to_admin'])
def query_text(message):
    try:
        if check_if_person_admin(message.from_user.id):
            if message.reply_to_message is None:
                bot.send_message(message.chat.id, 'Вызови реплай на того человека, которого ты хочешь сделать админом')
                return
            user_to_admin_id = message.reply_to_message.from_user.id
            user_to_admin = bot.get_chat_member(message.chat.id, user_to_admin_id)
            if user_to_admin.status in ['administrator', 'creator']:
                bot.send_message(message.chat.id, 'Он уже админ!')
            elif user_to_admin.status in ['member', 'restricted']:
                bot.promote_chat_member(message.chat.id, user_to_admin_id, *[True] * 8, False, *[True] * 3)
                bot.send_message(message.chat.id, 'Привет админ!')
            else:
                bot.send_message(message.chat.id, 'Либо он забанен, либо вышел, либо ты просишь что то незаконное!')
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['to_member'])
def query_text(message):
    try:
        if check_if_person_admin(message.from_user.id):
            if message.reply_to_message is None:
                bot.send_message(message.chat.id,
                                 'Вызови реплай на того человека, которого ты хочешь сделать антиадмином')
                return
            user_from_admin_id = message.reply_to_message.from_user.id
            user_from_admin = bot.get_chat_member(message.chat.id, user_from_admin_id)
            if user_from_admin.status not in ['administrator', 'creator']:
                bot.send_message(message.chat.id, 'Он и так не админ!')
            else:
                bot.promote_chat_member(message.chat.id, user_from_admin_id, *[False] * 12)
                bot.send_message(message.chat.id, 'Пока админ(')
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['ban'])
def query_text(message):
    try:
        if check_if_person_admin(message.from_user.id):
            if message.reply_to_message is None:
                bot.send_message(message.chat.id, 'Вызови реплай на того человека, которого ты хочешь забанить')
                return
            user_ban_id = message.reply_to_message.from_user.id
            user_ban_admin = bot.get_chat_member(message.chat.id, user_ban_id)
            if user_ban_admin.status in ['administrator', 'creator']:
                bot.send_message(message.chat.id, 'Сначала сделай мембером, потом бань!')
            else:
                ban_markup = get_ban_markup(message.from_user.id, user_ban_id,
                                            message.reply_to_message.from_user.username)
                bot.send_message(message.chat.id, 'На сколько хочешь забанит?',
                                 reply_markup=ban_markup)
    except:
        something_wrong(message.chat.id)


@bot.message_handler(commands=['unban'])
def query_text(message):
    try:
        if check_if_person_admin(message.from_user.id):
            if len(message.text.split(' ')) == 1:
                bot.send_message(message.chat.id, 'Ты должен указать юзернейм того, кого надо разбанить')
                return
            user_unban_username = message.text.split(' ')[1]
            if user_unban_username not in banned:
                bot.send_message(message.chat.id, 'Он не забанен...')
            else:
                unban(banned[user_unban_username])
                banned.pop(user_unban_username)
                bot.send_message(message.chat.id, 'Разбанил!')
    except:
        something_wrong(message.chat.id)


@bot.inline_handler(func=lambda query: True)
def query_text(query):
    try:
        ans = []
        if check_if_person_admin(query.from_user.id, False):
            for num, i in enumerate(banned):
                ans.append(types.InlineQueryResultArticle(
                    id=str(num + 2), title="@{}".format(i),
                    description='Разбанить!',
                    input_message_content=types.InputTextMessageContent(
                        message_text='/unban {}'.format(i))))
            if len(ans) == 0:
                ans.append(types.InlineQueryResultArticle(
                    id='1', title="Нет забаненных!",
                    description='((',
                    input_message_content=types.InputTextMessageContent(
                        message_text='камиль крутой')))
        else:
            ans.append(types.InlineQueryResultArticle(
                id='0', title="Ты не админ!",
                description="Только админы могут разбанить!",
                input_message_content=types.InputTextMessageContent(
                    message_text='камиль крутой')))
        bot.answer_inline_query(query.id, ans, cache_time=0)
    except:
        something_wrong()


bot.polling(none_stop=True)
