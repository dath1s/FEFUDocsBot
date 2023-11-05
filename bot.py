import telebot as tb
import psycopg2
import os
from datetime import datetime

users_documents_folder_path = r'Docs/'

bot = tb.TeleBot('5996073761:AAGAEna6L1c2Gh4nCXOCmo98inltGKhCa_Y')

action_keyboard = tb.types.ReplyKeyboardMarkup()
action_keyboard.row(tb.types.KeyboardButton('Подать заявку'), tb.types.KeyboardButton('Статус заявки'))
action_keyboard.row(tb.types.KeyboardButton('Техничская поддержка'))

skip_keyboard = tb.types.ReplyKeyboardMarkup()
skip_keyboard.row(tb.types.KeyboardButton('Пропустить'))

application_keyboard = tb.types.ReplyKeyboardMarkup()
application_keyboard.row(tb.types.KeyboardButton('По основной форме'), tb.types.KeyboardButton('По договору ГПХ'))
application_keyboard.row(tb.types.KeyboardButton('Назад'))

edit_gph_keyboard = tb.types.ReplyKeyboardMarkup()
edit_gph_keyboard.row(tb.types.KeyboardButton('Изменить паспорт(1стр)'),
                      tb.types.KeyboardButton('Изменить паспорт(прописка)'))
edit_gph_keyboard.row(tb.types.KeyboardButton('Изменить ИНН'), tb.types.KeyboardButton('Изменить СНИЛС'))
edit_gph_keyboard.row(tb.types.KeyboardButton('Изменить выписку из банка'),
                      tb.types.KeyboardButton('Изменить согласие'))
edit_gph_keyboard.row(tb.types.KeyboardButton('Сохранить'))

edit_main_keyboard = tb.types.ReplyKeyboardMarkup()
edit_main_keyboard.row(tb.types.KeyboardButton('Изменить паспорт(1стр)'),
                       tb.types.KeyboardButton('Изменить паспорт(прописка)'))
edit_main_keyboard.row(tb.types.KeyboardButton('Изменить ИНН'), tb.types.KeyboardButton('Изменить СНИЛС'))
edit_main_keyboard.row(tb.types.KeyboardButton('Изменить военный билет'),
                       tb.types.KeyboardButton('Изменить документ об образовании'))
edit_main_keyboard.row(tb.types.KeyboardButton('Изменить справку с места обучения'),
                       tb.types.KeyboardButton('Изменить форму СТД-Р'))
edit_main_keyboard.row(tb.types.KeyboardButton('Изменить Свидетельство о браке/перемене имени(фамилии)'),
                       tb.types.KeyboardButton('Изменить справку об отсутствии судимости'))
edit_main_keyboard.row(tb.types.KeyboardButton('Сохранить'))


@bot.message_handler(commands=['start', 'restart'])
def welcome(message):
    user_id = message.from_user.id

    with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin", port="5432") as conn:
        cur = conn.cursor()

        cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
        is_user_exist = True if list(cur.fetchall()) else False

        if is_user_exist:
            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_name = ' '.join(cur.fetchall()[0][2].split()[1:])

            bot.send_message(
                user_id,
                f"{user_name}, чем я могу вам помочь?",
                reply_markup=action_keyboard
            )
        else:
            bot.send_message(
                user_id,
                'Для регистрации введите ваше ФИО\n(Например: <b>Иванов Иван Иванович</b>)',
                parse_mode='html'
            )
            bot.register_next_step_handler(message, process_fullname_step)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.chat.type == 'private':
        user_id = message.from_user.id

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            is_user_exist = True if list(cur.fetchall()) else False

            if is_user_exist:
                if 'Техничская поддержка' == message.text:
                    bot.send_message(
                        user_id,
                        'Контакты технической поддержки:\nТелефон: +7(914)999-99-99\nemail: kovtunov.da@students.dvfu.ru'
                    )

                elif 'Подать заявку' == message.text:
                    bot.send_message(
                        user_id,
                        'Выберите форму, на основе который вы будете подавать документы на трудоустройство.',
                        reply_markup=application_keyboard
                    )

                elif 'Назад' == message.text:
                    cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
                    user_name = ' '.join(cur.fetchall()[0][2].split()[1:])

                    bot.send_message(
                        user_id,
                        f"{user_name}, чем я могу вам помочь?",
                        reply_markup=action_keyboard
                    )

                elif 'Статус заявки' == message.text:
                    with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                                          port="5432") as conn:
                        cur = conn.cursor()

                        cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
                        user_db_id = cur.fetchall()[0][0]

                        cur.execute(f'select status from "Applications" where user_id = {user_db_id}')
                        application_status = cur.fetchall()[0][0]

                        if application_status == 'Нет действительной заявки':
                            bot.send_message(
                                user_id,
                                'Вы не подавали заявок ранее'
                            )
                        else:
                            cur.execute(
                                f'select application_type, status, date, comment from "Applications" '
                                f'where user_id = {user_db_id}')
                            form, status, date, comment = cur.fetchall()[0]

                            bot.send_message(
                                user_id,
                                f'Форма заявки: {form}\nДата создания заявки: {date}\nСтатус заявки: {status}\n'
                                f'{f"Комментарий: {comment}" if comment else ""}'
                            )

                elif 'По основной форме' == message.text:
                    continue_back_keyboard = tb.types.InlineKeyboardMarkup(row_width=3)
                    continue_back_keyboard.add(
                        tb.types.InlineKeyboardButton('Продолжить', callback_data='continue_main'))
                    continue_back_keyboard.add(tb.types.InlineKeyboardButton('Нет', callback_data='back'))

                    bot.send_message(
                        user_id,
                        'Для подачи заявления на трудоустройство по основной форме нужно подать пакет документов:\n'
                        'Весь пакет условно можно разделить на две части:\n'
                        '1) Документы, которые можно подать в электронном виде(или подать лично сканы)\n'
                        '2) Документы, которые подаются лично.'
                    )
                    bot.send_message(
                        user_id,
                        'Документы, которые можно подать электронно:\n\t'
                        '✅ Паспорт;\n\t'
                        '✅ Страховое свидетельство обязательного пенсионного страхования (СНИЛС);\n\t'
                        '✅ ИНН;\n\t'
                        '✅ Военный билет (для военнообязанных, кроме совместителей);\n\t'
                        '✅ Документ об образовании, повышение квалификации, кандидата, доктора;\n\t'
                        '✅ Справка с места обучения (магистратура, аспирантура (при наличии));\n\t'
                        '✅ Форма СТД-Р (заказать через портал ГосУслуг, внешним совместителям: справка с места работы, заверенная копия трудовой книжки);\n\t'
                        '✅ Свидетельство о браке, свидетельство о перемене имени (фамилии), свидетельство о рождении детей (при наличии); - в эл. виде\n\t'
                        '✅ Справка об отсутствии судимости(оформить через портал Госуслуг, При подаче заявления нужно выбрать форму — электронную)\n'
                        '<b>Электронная справка об отсутствии судимости придёт в личный кабинет в виде pdf-документа'
                        ' с электронной подписью сотрудника МВД. Подлинность подписи можно проверить на портале.;</b>\n',
                        parse_mode='html'
                    )
                    bot.send_message(
                        user_id,
                        'Документы подающиеся лично:\n\t'
                        '✅ Заявление о ПРИЕМЕ внешний совместитель (5247897 v1)\n\t'
                        '✅ Бланк для Фонда соц. Страхования (вставить только подпись в прямоугольнике черной гелевой ручкой )(5247053 v1)\n\t'
                        '✅ Бланк Сведения о родстве (5247078 v1)\n\t'
                        '✅ Трудовая книжка; (заверенная трудовая книжка – для внешних совместителей)\n\t'
                        '✅ Заявление на перечисление ЗП МИР (5247145 v1)\n\t'
                        '✅ Лист ознакомления сотрудников с ВНД (5293676 v1)\n\t'
                        '✅ Согласие на Простую эл. подпись (5247104 v1)\n\t'
                        '✅ Согласие на размещение и обработку ПД в биометрической системе (5247107 v1)\n\t'
                        '✅ Согласие на размещение ПД на интернет-ресурсах (5247113 v1)\n\t'
                        '✅ Согласие сотрудника на обработку ПД (5247122 v1)\n\t'
                        '✅ Справка с места работы (для внешних совместителей)\n\t'
                        '✅ Фотография 3*4 (1шт.)\n'
                        '<b>Скачать бланки для заполнения можно из папки можно по ссылке: '
                        'https://drive.google.com/drive/folders/1o3HQZ4Gw1OprNRr8Ol_HbUUYmcmjQdDX?usp=sharing</b>',
                        parse_mode='html'
                    )
                    bot.send_message(
                        user_id,
                        'Документы нужно предоставить в кабинет D955.\n'
                        'После того, как документы будут переданы в отдел кадров, Вам нужно будет пройти мед. осмотр.\n'
                        'Продолжить?',
                        reply_markup=continue_back_keyboard
                    )

                elif 'По договору ГПХ' == message.text:
                    continue_back_keyboard = tb.types.InlineKeyboardMarkup(row_width=3)
                    continue_back_keyboard.add(
                        tb.types.InlineKeyboardButton('Продолжить', callback_data='continue_gph'))
                    continue_back_keyboard.add(tb.types.InlineKeyboardButton('Нет', callback_data='back'))

                    bot.send_message(
                        user_id,
                        'Для подачи заявления на основе договора ГПХ вам надо будет предоставить следующий '
                        'список документов:\n'
                        '✅ Паспорт(1-я страница и страница с пропиской)\n'
                        '✅ ИНН\n'
                        '✅ СНИЛС\n'
                        '✅ Выписка из банка с указанием номера лицевого счета\n'
                        '✅ Согласие на обработку персональных данных(форма для заполнения будет прикреплена далее)\n'
                        'Продолжить?',
                        reply_markup=continue_back_keyboard
                    )
            else:
                bot.send_message(
                    user_id,
                    'Для начала работы, пожалуйста, пройдите регистрацию'
                )
                bot.send_message(
                    user_id,
                    'Для регистрации введите ваше ФИО\n(Например: <b>Иванов Иван Иванович</b>)',
                    parse_mode='html'
                )
                bot.register_next_step_handler(message, process_fullname_step)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin", port="5432") as conn:
        cur = conn.cursor()

        cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
        is_user_exist = True if list(cur.fetchall()) else False

        if 'no_fullname' in call.data:
            if not is_user_exist:
                bot.send_message(
                    user_id,
                    'Для регистрации введите ваше ФИО\n(Например: <b>Иванов Иван Иванович</b>)',
                    parse_mode='html'
                )
                bot.register_next_step_handler(call.message, process_fullname_step)

        elif 'yes_fullname' in call.data:
            if not is_user_exist:
                fullname: str = call.message.text[9:].strip()

                folder_path = fullname + f'({user_id})'

                cur.execute(f'''
                    insert into "Users" (user_telegram_id, fullname, folder_name) 
                    values ({user_id}, '{fullname}', '{folder_path}')
                ''')
                conn.commit()

                cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
                user_db_id = cur.fetchall()[0][0]

                cur.execute(f'''insert into "Applications" (user_id) values ({user_db_id})''')
                conn.commit()

                cur.execute(f'''insert into "Documents" (user_id) values ({user_db_id})''')
                conn.commit()

                os.mkdir(users_documents_folder_path + folder_path)

                bot.send_message(
                    user_id,
                    "Регистрация прошла успешно🥳\nЯ готов к работе!"
                )
                bot.send_message(
                    user_id,
                    f"{' '.join(fullname.split()[1:])}, чем я могу вам помочь?",
                    reply_markup=action_keyboard
                )

        elif 'continue_gph' in call.data:
            if is_user_exist:
                cur_data = datetime.now()
                date = f'{cur_data.day}-{cur_data.month}-{cur_data.year}'

                cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
                user_db_id = cur.fetchall()[0][0]

                cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
                user_folder_name = cur.fetchall()[0][0]
                for f in os.listdir(f'Docs/{user_folder_name}'):
                    os.remove(f'Docs/{user_folder_name}/{f}')

                cur.execute(f'''
                    update "Applications" 
                    set application_type = 'ГПХ', status = 'В процессе заполнения', date = '{date}'
                    where user_id = {user_db_id}
                ''')
                conn.commit()

                cur.execute(f"""
                    update "Documents"
                    set passport='-', inn = '-', snils='-',bank_statement='-',pd='-',military_ticket='-',
                    education_document='-',study_certificate='-',stdr_form='-',marriage_certificate='-',
                    change_name_certificate='-',kids_born_certificate='-',no_criminal_certificate='-',
                    passport2='-'
                    where user_id={user_db_id}
                """)
                conn.commit()

                bot.send_message(
                    user_id,
                    'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)'
                )
                bot.register_next_step_handler(call.message, save_passport1_get_passport2)

        elif 'back' in call.data:
            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_name = ' '.join(cur.fetchall()[0][2].split()[1:])

            bot.send_message(
                user_id,
                f"{user_name}, чем я могу вам помочь?",
                reply_markup=action_keyboard
            )

        elif 'continue_main' in call.data:
            if is_user_exist:
                cur_data = datetime.now()
                date = f'{cur_data.day}-{cur_data.month}-{cur_data.year}'

                cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
                user_db_id = cur.fetchall()[0][0]

                cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
                user_folder_name = cur.fetchall()[0][0]
                for f in os.listdir(f'Docs/{user_folder_name}'):
                    os.remove(f'Docs/{user_folder_name}/{f}')

                cur.execute(f'''
                    update "Applications" 
                    set application_type = 'Основная форма', status = 'В процессе заполнения', date = '{date}'
                    where user_id = {user_db_id}
                ''')
                conn.commit()

                cur.execute(f"""
                    update "Documents"
                    set passport='-', inn = '-', snils='-',bank_statement='-',pd='-',military_ticket='-',
                    education_document='-',study_certificate='-',stdr_form='-',marriage_certificate='-',
                    change_name_certificate='-',kids_born_certificate='-',no_criminal_certificate='-',
                    passport2='-'
                    where user_id={user_db_id}
                """)
                conn.commit()

                bot.send_message(
                    user_id,
                    'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)',
                    reply_markup=tb.types.ReplyKeyboardRemove()
                )
                bot.register_next_step_handler(call.message, save_passport1_get_passport2_main)


################################################Форма ГПХ###############################################################
def save_passport1_get_passport2(photo_passpor1):
    user_id = photo_passpor1.chat.id

    try:
        assert photo_passpor1.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_passpor1.document.file_id if photo_passpor1.content_type == 'document' else photo_passpor1.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(1 стр. паспорта)" + photo_passpor1.document.file_name if photo_passpor1.content_type == "document" else "Паспорт(1 стр.).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                update "Documents" set passport = '{file_path}' where user_id = {user_db_id}
            ''')

            bot.send_message(
                user_id,
                'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
            )
            bot.register_next_step_handler(photo_passpor1, save_passport2_get_inn)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor1, save_passport1_get_passport2)


def save_passport2_get_inn(photo_passpor2):
    user_id = photo_passpor2.chat.id

    try:
        assert photo_passpor2.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_passpor2.document.file_id if photo_passpor2.content_type == 'document' else photo_passpor2.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(прописка паспорта)" + photo_passpor2.document.file_name if photo_passpor2.content_type == "document" else "Паспорт(прописка).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                        update "Documents" set passport2 = '{file_path}' where user_id = {user_db_id}
                    ''')

        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor2, save_inn_get_snils)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor2, save_passport2_get_inn)


def save_inn_get_snils(photo_inn):
    user_id = photo_inn.chat.id

    try:
        assert photo_inn.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_inn.document.file_id if photo_inn.content_type == 'document' else photo_inn.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(ИНН)" + photo_inn.document.file_name if photo_inn.content_type == "document" else "ИНН.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set inn = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_inn, save_snils_get_bank)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_inn, save_inn_get_snils)


def save_snils_get_bank(photo_snils):
    user_id = photo_snils.chat.id

    try:
        assert photo_snils.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_snils.document.file_id if photo_snils.content_type == 'document' else photo_snils.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(СНИЛС)" + photo_snils.document.file_name if photo_snils.content_type == "document" else "СНИЛС.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set snils = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите выписку из банка(скан или фотография в хорошем качестве)\n'
            '<b>Данную выписку можно получить онлайн на сайте или в отделении вашего банка.</b>',
            parse_mode='html'
        )
        bot.register_next_step_handler(photo_snils, save_bank_get_pd)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_snils, save_snils_get_bank)


def save_bank_get_pd(photo_bank):
    user_id = photo_bank.chat.id

    try:
        assert photo_bank.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_bank.document.file_id if photo_bank.content_type == 'document' else photo_bank.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Выписка из банка)" + photo_bank.document.file_name if photo_bank.content_type == "document" else "Выписка из банка.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set bank_statement = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Скачайте, заполните и отправьте бланк согласия на обработку персональных данных\n'
            '<b>Форма для заполнения прикреплена ниже</b>',
            parse_mode='html'
        )
        bot.send_document(user_id,
                          open(r'documents_samples/СогласиеНаОбработкуПерсональныхДанных.docx',
                               mode='rb'))

        bot.register_next_step_handler(photo_bank, save_pd_check_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите выписку из банка(скан или фотография в хорошем качестве)\n'
            '<b>Данную выписку можно получить онлайн на сайте или в отделении вашего банка.</b>',
            parse_mode='html'
        )
        bot.register_next_step_handler(photo_bank, save_bank_get_pd)


def save_pd_check_gph(photo_pd):
    user_id = photo_pd.chat.id

    try:
        assert photo_pd.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_pd.document.file_id if photo_pd.content_type == 'document' else photo_pd.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Согласие на обработку ПД)" + photo_pd.document.file_name if photo_pd.content_type == "document" else "Согласие на обработку ПД.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set pd = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_gph_keyboard
        )

        bot.register_next_step_handler(photo_pd, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Скачайте, заполните и отправьте бланк согласия на обработку персональных данных\n'
            '<b>Форма для заполнения прикреплена ниже</b>',
            parse_mode='html'
        )
        bot.send_document(user_id,
                          open(r'documents_samples/СогласиеНаОбработкуПерсональныхДанных.docx',
                               mode='rb'))

        bot.register_next_step_handler(photo_pd, save_pd_check_gph)


def edit_continue_gph(message):
    user_id = message.chat.id

    if message.text == 'Сохранить':
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()
            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                update "Applications"
                set status = 'Ожидает рассмотрения' 
                where user_id = {user_db_id}
            ''')
            conn.commit()

        bot.send_message(
            user_id,
            'Ваша заявка успешна отправлена. В ближайшее время ваша заявка будет рассмотрена.\n'
            'Чтобы узнать статус вашей заявки вы можете воспользоваться кнопкой "Статус заявки"',
            reply_markup=action_keyboard
        )

    elif 'Изменить паспорт(1стр)' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Паспорт(1 стр.).png' or i[:17] == "(1 стр. паспорта)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_passport1)

    elif 'Изменить паспорт(прописка)' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Паспорт(прописка).png' or i[:19] == "(прописка паспорта)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_passport2)

    elif 'Изменить ИНН' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if i == 'ИНН.png' or i[:5] == "(ИНН)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите ваш ИНН(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_inn)

    elif 'Изменить СНИЛС' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if i == 'СНИЛС.png' or i[:7] == "(СНИЛС)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_snils)

    elif 'Изменить выписку из банка' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Выписка из банка.png' or i[:18] == "(Выписка из банка)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите выписку из банка(скан или фотография в хорошем качестве)\n'
                '<b>Данную выписку можно получить онлайн на сайте или в отделении вашего банка.</b>',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_bank)

    elif 'Изменить согласие' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Согласие на обработку ПД.png' or i[:26] == "(Согласие на обработку ПД)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Скачайте, заполните и отправьте бланк согласия на обработку персональных данных\n'
                '<b>Форма для заполнения прикреплена ниже</b>',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.send_document(user_id,
                              open(r'documents_samples/СогласиеНаОбработкуПерсональныхДанных.docx',
                                   mode='rb'))
            bot.register_next_step_handler(message, edit_pd)

    else:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста выберите один из предложенных вариантов.',
            reply_markup=edit_gph_keyboard
        )

        bot.register_next_step_handler(message, edit_continue_gph)


def edit_passport1(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(1 стр. паспорта)" + photo.document.file_name if photo.content_type == "document" else "Паспорт(1 стр.).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                    update "Documents" set passport = '{file_path}' where user_id = {user_db_id}
                ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo, edit_passport1)


def edit_passport2(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(прописка паспорта)" + photo.document.file_name if photo.content_type == "document" else "Паспорт(прописка).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                        update "Documents" set passport2 = '{file_path}' where user_id = {user_db_id}
                    ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo, edit_passport2)


def edit_inn(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(ИНН)" + photo.document.file_name if photo.content_type == "document" else "ИНН.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set inn = '{file_path}' where user_id = {user_db_id}
                        ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_inn)


def edit_snils(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(СНИЛС)" + photo.document.file_name if photo.content_type == "document" else "СНИЛС.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set snils = '{file_path}' where user_id = {user_db_id}
                            ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_snils)


def edit_bank(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Выписка из банка)" + photo.document.file_name if photo.content_type == "document" else "Выписка из банка.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                    update "Documents" set bank_statement = '{file_path}' where user_id = {user_db_id}
                                ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите выписку из банка(скан или фотография в хорошем качестве)\n'
            '<b>Данную выписку можно получить онлайн на сайте или в отделении вашего банка.</b>',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_bank)


def edit_pd(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Согласие на обработку ПД)" + photo.document.file_name if photo.content_type == "document" else "Согласие на обработку ПД.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                        update "Documents" set pd = '{file_path}' where user_id = {user_db_id}
                                    ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_gph_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_gph)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Скачайте, заполните и отправьте бланк согласия на обработку персональных данных\n'
            '<b>Форма для заполнения прикреплена ниже</b>',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.send_document(user_id,
                          open(r'documents_samples/СогласиеНаОбработкуПерсональныхДанных.docx',
                               mode='rb'))
        bot.register_next_step_handler(photo, edit_pd)


###############################################Основная формф###########################################################
def save_passport1_get_passport2_main(photo_passpor1):
    user_id = photo_passpor1.chat.id

    try:
        assert photo_passpor1.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_passpor1.document.file_id if photo_passpor1.content_type == 'document' else photo_passpor1.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(1 стр. паспорта)" + photo_passpor1.document.file_name if photo_passpor1.content_type == "document" else "Паспорт(1 стр.).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                update "Documents" set passport = '{file_path}' where user_id = {user_db_id}
            ''')

            bot.send_message(
                user_id,
                'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
            )
            bot.register_next_step_handler(photo_passpor1, save_passport2_get_inn_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor1, save_passport1_get_passport2_main)


def save_passport2_get_inn_main(photo_passpor2):
    user_id = photo_passpor2.chat.id

    try:
        assert photo_passpor2.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_passpor2.document.file_id if photo_passpor2.content_type == 'document' else photo_passpor2.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(прописка паспорта)" + photo_passpor2.document.file_name if photo_passpor2.content_type == "document" else "Паспорт(прописка).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                        update "Documents" set passport2 = '{file_path}' where user_id = {user_db_id}
                    ''')

        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor2, save_inn_get_snils_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_passpor2, save_passport2_get_inn_main)


def save_inn_get_snils_main(photo_inn):
    user_id = photo_inn.chat.id

    try:
        assert photo_inn.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_inn.document.file_id if photo_inn.content_type == 'document' else photo_inn.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(ИНН)" + photo_inn.document.file_name if photo_inn.content_type == "document" else "ИНН.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set inn = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_inn, save_snils_get_military)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_inn, save_inn_get_snils_main)


def save_snils_get_military(photo_snils):
    user_id = photo_snils.chat.id

    try:
        assert photo_snils.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_snils.document.file_id if photo_snils.content_type == 'document' else
                photo_snils.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(СНИЛС)" + photo_snils.document.file_name if photo_snils.content_type == "document" else "СНИЛС.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set snils = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите скан или фотографию вашего военного билета(при наличии).\n'
            '<b>Если вы не военнообязанный или вы совместитель нажмите кнопку "Пропустить"</b>',
            parse_mode='html',
            reply_markup=skip_keyboard
        )
        bot.register_next_step_handler(photo_snils, save_military_get_education)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo_snils, save_snils_get_military)


def save_military_get_education(photo_milittary):
    user_id = photo_milittary.chat.id

    try:
        assert photo_milittary.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_milittary.document.file_id if photo_milittary.content_type == 'document' else
                photo_milittary.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Военный билет)" + photo_milittary.document.file_name if photo_milittary.content_type == "document" else "Военный билет.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set military_ticket = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Документ об образовании, повышение квалификации, кандидата, доктора',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo_milittary, save_education_get_study)

    except AssertionError:
        if photo_milittary.text == 'Пропустить':
            bot.send_message(
                user_id,
                'Документ об образовании, повышение квалификации, кандидата, доктора',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(photo_milittary, save_education_get_study)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фотографию вашего военного билета(при наличии).\n'
                '<b>Если вы не военнообязанный или вы совместитель нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo_milittary, save_snils_get_military)


def save_education_get_study(photo_education):
    user_id = photo_education.chat.id

    try:
        assert photo_education.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_education.document.file_id if photo_education.content_type == 'document' else
                photo_education.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Документ об образовании)" + photo_education.document.file_name if photo_education.content_type == "document" else "Документ об образовании.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set education_document = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите скан или фотографию справки с места обучения (магистратура, аспирантура (при наличии)).\n'
            '<b>Если у вас отсутствует справка нажмите кнопку "Пропустить"</b>',
            parse_mode='html',
            reply_markup=skip_keyboard
        )
        bot.register_next_step_handler(photo_education, save_study_get_stdr)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Документ об образовании, повышение квалификации, кандидата, доктора',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo_education, save_education_get_study)


def save_study_get_stdr(photo_study):
    user_id = photo_study.chat.id

    try:
        assert photo_study.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_study.document.file_id if photo_study.content_type == 'document' else
                photo_study.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Справка с места обучения)" + photo_study.document.file_name if photo_study.content_type == "document" else "Справка с места обучения.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set study_certificate = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите форму СТД-Р (её можно заказать через портал ГосУслуг)\n'
            '<b>Внешним совместителям нужно предоставить справку с места работы, заверенная копия трудовой книжки</b>',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo_study, save_stdr_get_marry)

    except AssertionError:
        if photo_study.text == 'Пропустить':
            bot.send_message(
                user_id,
                'Вышлите форму СТД-Р (её можно заказать через портал ГосУслуг)\n'
                '<b>Внешним совместителям нужно предоставить справку с места работы, заверенная копия трудовой книжки</b>',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(photo_study, save_stdr_get_marry)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фотографию справки с места обучения (магистратура, аспирантура (при наличии)).\n'
                '<b>Если у вас отсутствует справка нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo_study, save_study_get_stdr)


def save_stdr_get_marry(stdr):
    user_id = stdr.chat.id

    try:
        assert stdr.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                stdr.document.file_id if stdr.content_type == 'document' else
                stdr.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Форма СТД-Р)" + stdr.document.file_name if stdr.content_type == "document" else "Форма СТД-Р.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set stdr_form = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите скан или фото свидетельства о браке, свидетельства о перемене имени (фамилии), свидетельства о рождении детей (при наличии)\n'
            'При отсутствии нажмите кнопку "Пропустить"',
            parse_mode='html',
            reply_markup=skip_keyboard
        )
        bot.register_next_step_handler(stdr, save_marry_get_no_criminal)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите форму СТД-Р (её можно заказать через портал ГосУслуг)\n'
            '<b>Внешним совместителям нужно предоставить справку с места работы, заверенная копия трудовой книжки</b>',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(stdr, save_stdr_get_marry)


def save_marry_get_no_criminal(photo_marry):
    user_id = photo_marry.chat.id

    try:
        assert photo_marry.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_marry.document.file_id if photo_marry.content_type == 'document' else
                photo_marry.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Свидетельство о браке,смене фамилии или имени)" + photo_marry.document.file_name if photo_marry.content_type == "document" else "Свидетельство о браке,смене фамилии или имени.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set marriage_certificate = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Вышлите справку об отсутствии судимости',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo_marry, save_no_criminal_check)

    except AssertionError:
        if photo_marry.text == 'Пропустить':
            bot.send_message(
                user_id,
                'Вышлите справку об отсутствии судимости',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(photo_marry, save_no_criminal_check)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фото свидетельства о браке, свидетельства о перемене имени (фамилии), свидетельства о рождении детей (при наличии)\n'
                'При отсутствии нажмите кнопку "Пропустить"',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo_marry, save_marry_get_no_criminal)


def save_no_criminal_check(photo_no_crim):
    user_id = photo_no_crim.chat.id

    try:
        assert photo_no_crim.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo_no_crim.document.file_id if photo_no_crim.content_type == 'document' else photo_no_crim.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Справка об отсутствии судимости)" + photo_no_crim.document.file_name if photo_no_crim.content_type == "document" else "Справка об отсутствии судимости.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set no_criminal_certificate = '{file_path}' where user_id = {user_db_id}
                            ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo_no_crim, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите справку об отсутствии судимости',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )

        bot.register_next_step_handler(photo_no_crim, save_no_criminal_check)


def edit_continue_main(message):
    user_id = message.chat.id

    if message.text == 'Сохранить':
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()
            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                update "Applications"
                set status = 'Ожидает рассмотрения' 
                where user_id = {user_db_id}
            ''')
            conn.commit()

        bot.send_message(
            user_id,
            'Ваша заявка успешна отправлена. В ближайшее время ваша заявка будет рассмотрена.\n'
            'Чтобы узнать статус вашей заявки вы можете воспользоваться кнопкой "Статус заявки"',
            reply_markup=action_keyboard
        )

    elif 'Изменить паспорт(1стр)' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Паспорт(1 стр.).png' or i[:17] == "(1 стр. паспорта)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_passport1_main)

    elif 'Изменить паспорт(прописка)' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == 'Паспорт(прописка).png' or i[:19] == "(прописка паспорта)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_passport2_main)

    elif 'Изменить ИНН' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if i == 'ИНН.png' or i[:5] == "(ИНН)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите ваш ИНН(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_inn_main)

    elif 'Изменить СНИЛС' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if i == 'СНИЛС.png' or i[:7] == "(СНИЛС)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_snils_main)

    elif 'Изменить военный билет' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Военный билет.png" or i[:15] == "(Военный билет)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите скан или фотографию вашего военного билета(при наличии).\n'
                '<b>Если вы не военнообязанный или вы совместитель нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(message, edit_military)

    elif 'Изменить документ об образовании' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Документ об образовании.png" or i[:25] == "(Документ об образовании)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Документ об образовании, повышение квалификации, кандидата, доктора',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_education)

    elif 'Изменить справку с места обучения' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Справка с места обучения.png" or i[:26] == "(Справка с места обучения)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите скан или фотографию справки с места обучения (магистратура, аспирантура (при наличии)).\n'
                '<b>Если у вас отсутствует справка нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(message, edit_study)

    elif 'Изменить форму СТД-Р' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Форма СТД-Р.png" or i[:13] == "(Форма СТД-Р)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите форму СТД-Р (её можно заказать через портал ГосУслуг)\n'
                '<b>Внешним совместителям нужно предоставить справку с места работы, заверенная копия трудовой книжки</b>',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_stdr)

    elif 'Изменить Свидетельство о браке/перемене имени(фамилии)' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Свидетельство о браке,смене фамилии или имени.png" or i[
                                                                                  :47] == "(Свидетельство о браке,смене фамилии или имени)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите скан или фото свидетельства о браке, свидетельства о перемене имени (фамилии), свидетельства о рождении детей (при наличии)\n'
                'При отсутствии нажмите кнопку "Пропустить"',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(message, edit_born_certificate)

    elif 'Изменить справку об отсутствии судимости' == message.text:
        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            for f in [i for i in os.listdir(f'Docs/{user_folder_name}') if
                      i == "Справка об отсутствии судимости.png" or i[:33] == "(Справка об отсутствии судимости)"]:
                os.remove(f'Docs/{user_folder_name}/{f}')

            bot.send_message(
                user_id,
                'Вышлите справку об отсутствии судимости',
                parse_mode='html',
                reply_markup=tb.types.ReplyKeyboardRemove()
            )
            bot.register_next_step_handler(message, edit_no_criminal)

    else:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста выберите один из предложенных вариантов.',
            reply_markup=edit_gph_keyboard
        )

        bot.register_next_step_handler(message, edit_continue_gph)


def edit_passport1_main(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(1 стр. паспорта)" + photo.document.file_name if photo.content_type == "document" else "Паспорт(1 стр.).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                       update "Documents" set passport = '{file_path}' where user_id = {user_db_id}
                   ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите первую страницу вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo, edit_passport1_main)


def edit_passport2_main(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(прописка паспорта)" + photo.document.file_name if photo.content_type == "document" else "Паспорт(прописка).png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set passport2 = '{file_path}' where user_id = {user_db_id}
                        ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите страницу c пропиской из вашего паспорта(скан или фотография в хорошем качестве)'
        )
        bot.register_next_step_handler(photo, edit_passport2_main)


def edit_snils_main(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(СНИЛС)" + photo.document.file_name if photo.content_type == "document" else "СНИЛС.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                    update "Documents" set snils = '{file_path}' where user_id = {user_db_id}
                                ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш СНИЛС(скан или фотография в хорошем качестве)',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_snils_main)


def edit_inn_main(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(ИНН)" + photo.document.file_name if photo.content_type == "document" else "ИНН.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                update "Documents" set inn = '{file_path}' where user_id = {user_db_id}
                            ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите ваш ИНН(скан или фотография в хорошем качестве)',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_inn_main)


def edit_military(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else
                photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Военный билет)" + photo.document.file_name if photo.content_type == "document" else "Военный билет.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                    update "Documents" set military_ticket = '{file_path}' where user_id = {user_db_id}
                                ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except AssertionError:
        if photo.text == 'Пропустить':
            cur.execute(f'''
                                                update "Documents" set military_ticket = '-' where user_id = {user_db_id}
                                            ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фотографию вашего военного билета(при наличии).\n'
                '<b>Если вы не военнообязанный или вы совместитель нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo, edit_military)


def edit_education(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else
                photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Документ об образовании)" + photo.document.file_name if photo.content_type == "document" else "Документ об образовании.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set education_document = '{file_path}' where user_id = {user_db_id}
                        ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Документ об образовании, повышение квалификации, кандидата, доктора',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_education)


def edit_study(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else
                photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Справка с места обучения)" + photo.document.file_name if photo.content_type == "document" else "Справка с места обучения.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set study_certificate = '{file_path}' where user_id = {user_db_id}
                        ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except AssertionError:
        if photo.text == 'Пропустить':
            cur.execute(f'''
                            update "Documents" set study_certificate = '-' where user_id = {user_db_id}
                        ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фотографию справки с места обучения (магистратура, аспирантура (при наличии)).\n'
                '<b>Если у вас отсутствует справка нажмите кнопку "Пропустить"</b>',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo, edit_study)


def edit_stdr(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else
                photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Форма СТД-Р)" + photo.document.file_name if photo.content_type == "document" else "Форма СТД-Р.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set stdr_form = '{file_path}' where user_id = {user_db_id}
                        ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите форму СТД-Р (её можно заказать через портал ГосУслуг)\n'
            '<b>Внешним совместителям нужно предоставить справку с места работы, заверенная копия трудовой книжки</b>',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(photo, edit_stdr)


def edit_born_certificate(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else
                photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Свидетельство о браке,смене фамилии или имени)" + photo.document.file_name if photo.content_type == "document" else "Свидетельство о браке,смене фамилии или имени.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                            update "Documents" set marriage_certificate = '{file_path}' where user_id = {user_db_id}
                        ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except AssertionError:
        if photo.text == 'Пропустить':
            cur.execute(f'''
                            update "Documents" set marriage_certificate = '-' where user_id = {user_db_id}
                         ''')

            bot.send_message(
                user_id,
                'Пожалуйста, перепроверьте введённые вами данные. '
                'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
                'Если введённые вами данные верны, нажмите "Сохранить".',
                reply_markup=edit_main_keyboard
            )

            bot.register_next_step_handler(photo, edit_continue_main)
        else:
            bot.send_message(
                user_id,
                'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
            )
            bot.send_message(
                user_id,
                'Вышлите скан или фото свидетельства о браке, свидетельства о перемене имени (фамилии), свидетельства о рождении детей (при наличии)\n'
                'При отсутствии нажмите кнопку "Пропустить"',
                parse_mode='html',
                reply_markup=skip_keyboard
            )
            bot.register_next_step_handler(photo, edit_born_certificate)


def edit_no_criminal(photo):
    user_id = photo.chat.id

    try:
        assert photo.content_type in ['document', 'photo']

        with psycopg2.connect(dbname="postgres", host="localhost", user="postgres", password="admin",
                              port="5432") as conn:
            cur = conn.cursor()

            cur.execute(f'select folder_name from "Users" where user_telegram_id = {user_id}')
            user_folder_name = cur.fetchall()[0][0]

            file_info = bot.get_file(
                photo.document.file_id if photo.content_type == 'document' else photo.photo[
                    -1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            file_path = users_documents_folder_path + f'{user_folder_name}/' \
                                                      f'{"(Справка об отсутствии судимости)" + photo.document.file_name if photo.content_type == "document" else "Справка об отсутствии судимости.png"}'

            with open(file_path, 'wb+') as new_file:
                new_file.write(downloaded_file)

            cur.execute(f'select * from "Users" where user_telegram_id = {user_id}')
            user_db_id = cur.fetchall()[0][0]

            cur.execute(f'''
                                    update "Documents" set no_criminal_certificate = '{file_path}' where user_id = {user_db_id}
                                ''')

        bot.send_message(
            user_id,
            'Пожалуйста, перепроверьте введённые вами данные. '
            'В случае ошибки воспользуйтесь одной из кнопок на клавиатуре.\n'
            'Если введённые вами данные верны, нажмите "Сохранить".',
            reply_markup=edit_main_keyboard
        )

        bot.register_next_step_handler(photo, edit_continue_main)

    except Exception:
        bot.send_message(
            user_id,
            'Возможно вы ошиблись при вводе. Пожалуйста повторите попытку.'
        )
        bot.send_message(
            user_id,
            'Вышлите справку об отсутствии судимости',
            parse_mode='html',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )

        bot.register_next_step_handler(photo, edit_no_criminal)


########################################Допполнительные функции#########################################################
def process_fullname_step(fullname_text):
    telegram_id = fullname_text.chat.id

    yes_no_fullname_keyboard = tb.types.InlineKeyboardMarkup(row_width=3)
    yes_no_fullname_keyboard.add(tb.types.InlineKeyboardButton('Да', callback_data='yes_fullname'))
    yes_no_fullname_keyboard.add(tb.types.InlineKeyboardButton('Нет', callback_data='no_fullname'))

    fullname = ' '.join([i.capitalize() for i in fullname_text.text.split()])

    try:
        bot.send_message(
            telegram_id,
            f'Ваше ФИО: <b>{fullname}</b>',
            reply_markup=yes_no_fullname_keyboard,
            parse_mode='html'
        )
    except Exception:
        bot.send_message(
            telegram_id,
            'Произошла какая-то ошибка. Попробуйте снова.'
        )


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
    bot.polling(skip_pending=True)
