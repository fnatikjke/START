import logging, re, os, paramiko
from telegram import Update, ForceReply
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext
import psycopg2
from psycopg2 import Error

load_dotenv()
TOKEN = os.getenv("TOKEN")
host = os.getenv("RM_HOST")
port = os.getenv("RM_PORT")
username = os.getenv("RM_USER")
password = os.getenv("RM_PASSWORD")

# Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Функция приветствия
def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(f'Привет {user.full_name}! Я бот. Введите /help для получения списка команд')


# Функция демонстрации всех возможных команд
def helpCommand(update: Update, context):
     commands_list = [
        "/start - Начать",
        "/help - Получить список команд",
        "/find_email - поиск email адресов в тексте",
        "/find_phone_number - поиск номеров телефонов в тексте",
        "/verify_password - проверка сложности пароля",
        "/get_release - информация о релизе системы",
        "/get_uname - информация об архитектуре процессора и тд",
        "/get_uptime - информация о времени работы",
        "/get_df - информация о состоянии файловой системы",
        "/get_free - информация о состоянии оперативной памяти",
        "/get_mpstat - информация о производительности системы",
        "/get_w - информация о пользователях",
        "/get_auths - последние 10 логов в систему",
        "/get_critical - последние 5 критических событий",
        "/get_ps - информация о запущенных процессах",
        "/get_ss - информация об используемых портах",
        "/get_apt_list - информация об установленных пакетах",
        "/get_repl_logs - вывод логов о репликации БД",
        "/get_emails - вывод email адресов из таблицы",
        "/get_phone_numbers - вывод номеров телефонов из таблицы"
    ]
     update.message.reply_text("\n".join(commands_list))

#---------------------------------------------------------------------------------

#Функция поиска телефонных номеров
def find_phone_number_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска телефонных номеров: ')
    return 'find_phone_number'

def find_phone_number (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов

    phoneNumRegex = re.compile(r'(?:\+7|8)\d{10}|(?:\+7|8)-\d{3}-\d{3}-\d{2}-\d{2}|(?:\+7|8)\s\d{3}\s\d{3}\s\d{2}\s\d{2}|(?:\+7|8)\(\d{3}\)\d{7}|(?:\+7|8)\s\(\d{3}\)\s\d{3}\s\d{2}\s\d{2}') # Регулярное выражение

    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return ConversationHandler.END # Завершаем выполнение обработчика

    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер
        
    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text('Хотите сохранить найденные номера телефонов в базе данных? (ДА/НЕТ)')
    context.user_data['phoneNumberList'] = phoneNumberList
    return 'save_phone_number' # Завершаем работу обработчика диалога


def save_phone_number(update, context):
    user_response = update.message.text.upper() # Получаем ответ пользователя в верхнем регистре

    if user_response == 'ДА':
        # Сохраняем найденные телефоны в базе данных PostgreSQL
        phoneNumberList = context.user_data['phoneNumberList']
        connection = psycopg2.connect(user=os.getenv("DB_USER"), 
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()

        for phoneNumber in phoneNumberList:
            cursor.execute("INSERT INTO Телефон (\"Номер телефона\") VALUES (%s)", (phoneNumber,))

        connection.commit()
        cursor.close()
        connection.close()

        update.message.reply_text('Номера телефонов сохранены в базе данных.')
    elif user_response == 'НЕТ':
        update.message.reply_text('Номера телефонов не будут сохранены в базе данных.')
    else:
        update.message.reply_text('Некорректный ответ. Пожалуйста, введите "ДА" или "НЕТ".')

    return ConversationHandler.END # Завершаем выполнение обработчика диалога

#---------------------------------------------------------------------------------

#Функция поиска адресов электронных почту
def find_email_Command(update: Update, context):
    update.message.reply_text('Введите текст для поиска электронной почты: ')
    return 'find_email'


def find_email (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий(или нет) электронную почту

    emailRegex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+.[a-zA-Z]{2,4}') # регулярное выражение

    emailList = emailRegex.findall(user_input) # Ищем адреса email

    if not emailList: # Обрабатываем случай, когда отсутствуют email
        update.message.reply_text('Адреса электронных почт не найдены')
        return ConversationHandler.END # Завершаем выполнение обработчика

    emails = '' # Создаем строку, в которую будем записывать адреса email
    for i in range(len(emailList)):
        emails += f'{i+1}. {emailList[i]}\n' # Записываем очередной адрес

    update.message.reply_text(emails) # Отправляем сообщение пользователю
    update.message.reply_text('Хотите сохранить найденные адреса в базе данных? (ДА/НЕТ)')
    context.user_data['emailList'] = emailList
    return 'save_email' # Завершаем работу обработчика диалога

def save_email(update, context):
    user_response = update.message.text.upper() # Получаем ответ пользователя в верхнем регистре

    if user_response == 'ДА':
        # Сохраняем найденные адреса в базе данных PostgreSQL
        emailList = context.user_data['emailList']
        connection = psycopg2.connect(user=os.getenv("DB_USER"), 
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()

        for email in emailList:
            cursor.execute("INSERT INTO Email (\"Электронная почта\") VALUES (%s)", (email,))

        connection.commit()
        cursor.close()
        connection.close()

        update.message.reply_text('Адреса электронной почты сохранены в базе данных.')
    elif user_response == 'НЕТ':
        update.message.reply_text('Адреса электронной почты не будут сохранены в базе данных.')
    else:
        update.message.reply_text('Некорректный ответ. Пожалуйста, введите "ДА" или "НЕТ".')

    return ConversationHandler.END # Завершаем выполнение обработчика диалога

#---------------------------------------------------------------------------------

#Функция проверки пароля на сложность
def verify_password_Command(update: Update, context):
    update.message.reply_text("Введите пароль для проверки его сложности.")
    return 'verify_password'

def verify_password(update: Update, context):
    user_input = update.message.text
    if is_password_complex(user_input):
        update.message.reply_text("Пароль сложный.")
    else:
        update.message.reply_text("Пароль простой.")
    return ConversationHandler.END

def is_password_complex(password):
    passwordRegex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    return bool(re.match(passwordRegex, password))

#---------------------------------------------------------------------------------

#Функция подключения по SSH к удаленной ВМ
def ssh_connect(host, port, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    return ssh

#Функция вывода информации о релизе
def get_release(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('cat /etc/os-release')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о релизе:\n\n{data}')

#Функция вывода информации об архитектуре процессора, имени хоста системы и версии ядра. 
def get_uname(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('uname -a')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация об архитектуре процессора, имени хоста и версии ядра системы:\n\n{data}')

#Функция вывода информации о времени работы 
def get_uptime(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('uptime')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о времени работы системы:\n\n{data}')

#Функция вывода информации о состоянии файловой системы 
def get_df(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('df')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о состоянии файловой системы:\n\n{data}')

#Функция вывода информации о состоянии оперативной памяти
def get_free(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('free -h')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о состоянии оперативной памяти:\n\n{data}')

#Функция вывода информации о состоянии производительности системы
def get_mpstat(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('mpstat')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о состоянии производительности системы:\n\n{data}')

#Функция вывода информации о работающих в данной системе пользователях
def get_w(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('w')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о работающих в данной системе пользователях:\n\n{data}')

#Функция вывода информации о последних 10 входах в систему
def get_auths(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('last -n 10')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Последние 10 входов в систему:\n\n{data}')

#Функция вывода информации о последних 5 критических событий
def get_critical(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('journalctl -p 3 -n 5')
    data = stdout.read().decode('utf-8')
    update.message.reply_text(f'Последние 5 критических событий:\n\n{data}')


#Функция вывода информации о запущенных процессах
def get_ps(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('ps')
    data = stdout.read().decode('utf-8')
    ssh.close()
    send_long_message(update,context,data)

#Функция вывода информации об используемых портах
def get_ss(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('ss')
    data = stdout.read().decode('utf-8')
    ssh.close()
    send_long_message(update,context,data)
    
#Функция вывода информации о запущенных службах
def get_services(update: Update, context):
    ssh = ssh_connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('systemctl --type=service --state=running')
    data = stdout.read().decode('utf-8')
    ssh.close()
    update.message.reply_text(f'Информация о запущенных службах:\n\n{data}')

#Функция вывода информации о пакетах
def get_apt_list_Command(update: Update, context):
    update.message.reply_text('Если необходимо вывести все пакеты, то напишите ВСЕ ПАКЕТЫ. Если необходимо вывести информацию о конкретном пакете, то напишите его название с маленькой буквы (например, less): ')
    return 'get_apt_list'

def get_apt_list (update: Update, context):
    user_input = update.message.text # Получаем текст, содержащий пакеты, которые нужно вывести

    if (user_input == "ВСЕ ПАКЕТЫ"):
        ssh = ssh_connect(host, port, username, password)
        stdin, stdout, stderr = ssh.exec_command('dpkg -l')
        data = stdout.read().decode('utf-8')
        ssh.close()
        send_long_message(update,context,data)
        return ConversationHandler.END # Завершаем работу обработчика диалога
    else:
        ssh = ssh_connect(host, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(f'dpkg -l {user_input}')
        data = stdout.read().decode('utf-8')
        ssh.close()
        update.message.reply_text(f'Информация о пакете {user_input}:\n\n{data}')
        return ConversationHandler.END # Завершаем работу обработчика диалога

# Функция отправки длинных сообщений
def send_long_message(update: Update, context, text):
    max_length = 4096  # Максимальная длина сообщения в Telegram
    if len(text) <= max_length:
        update.message.reply_text(text)
    else:
        update.message.reply_text(text[:max_length])
        send_long_message(update, context, text[max_length:])

#Функция вывода логов репликации БД
def get_repl_logs(update: Update, context):
    ssh = ssh_connect(hostbd, port, username, password)
    stdin, stdout, stderr = ssh.exec_command('docker logs db_image 2>&1 | grep "replica"')
    data = stdout.read().decode('utf-8')
    ssh.close()
    send_long_message(update,context,data)

#Функция вывода email адресов из таблицы
def get_emails(update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"), 
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Email")
        data = cursor.fetchall()
        response = ""
        for row in data:
            response += str(row) + "\n"
        send_long_message(update,context,response)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        cursor.close()
        connection.close()

#Функция вывода номеров телефонов из таблицы
def get_phone_numbers(update: Update, context):
    try:
        connection = psycopg2.connect(user=os.getenv("DB_USER"), 
                                      password=os.getenv("DB_PASSWORD"),
                                      host=os.getenv("DB_HOST"),
                                      port=os.getenv("DB_PORT"),
                                      database=os.getenv("DB_DATABASE"))
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Телефон")
        data = cursor.fetchall()
        response = ""
        for row in data:
            response += str(row) + "\n"
        send_long_message(update,context,response)
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error("Ошибка при работе с PostgreSQL: %s", error)
    finally:
        cursor.close()
        connection.close()


#---------------------------------------------------------------------------------

def main():
    updater = Updater(TOKEN, use_context=True)
#    updater = Updater(TOKEN)
    # Получаем диспетчер для регистрации обработчиков
    dp = updater.dispatcher

    # Обработчик диалога (телефонные номера)
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', find_phone_number_Command)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'save_phone_number': [MessageHandler(Filters.text & ~Filters.command, save_phone_number)],
        },
        fallbacks=[]
    )
      # Обработчик диалога (электронные почты)
    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_email_Command)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'save_email': [MessageHandler(Filters.text & ~Filters.command, save_email)],
        },
        fallbacks=[]
    )

      # Обработчик диалога (сложность пароля)
    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_password_Command)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

      # Обработчик диалога (информация об установленных пакетах)
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_list_Command)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

	# Регистрируем обработчики команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(convHandlerfind_phone_number)
    dp.add_handler(convHandlerfind_email)
    dp.add_handler(convHandlerverify_password)
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(convHandlerget_apt_list)
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))
	# Запускаем бота
    updater.start_polling()

	# Останавливаем бота при нажатии Ctrl+C
    updater.idle()


if __name__ == '__main__':
    main()
