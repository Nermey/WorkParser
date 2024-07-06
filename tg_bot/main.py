import telebot
import requests
from config import BOT_TOKEN
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from schema import VacancyDTO

API_BASE_URL = 'http://vacancy_server:6201'

print(BOT_TOKEN)
bot = telebot.TeleBot(BOT_TOKEN)


user_filters = {}


def create_filter_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Название", callback_data="filter_name"))
    keyboard.add(InlineKeyboardButton("Зарплата от", callback_data="filter_salary_from"))
    keyboard.add(InlineKeyboardButton("Зарплата до", callback_data="filter_salary_to"))
    keyboard.add(InlineKeyboardButton("Тип занятости", callback_data="filter_employment_status"))
    keyboard.add(InlineKeyboardButton("Опыт работы", callback_data="filter_work_experience"))
    keyboard.add(InlineKeyboardButton("Работодатель", callback_data="filter_employer"))
    keyboard.add(InlineKeyboardButton("Город", callback_data="filter_city"))
    keyboard.add(InlineKeyboardButton("Поиск", callback_data="search_vacancies"))
    return keyboard


@bot.message_handler(commands=['start', 'filters'])
def send_filter_options(message):
    user_filters[message.chat.id] = {
        'name': None,
        'salary_from': None,
        'salary_to': None,
        'employment_status': None,
        'work_experience': None,
        'employer': None,
        'city': None,
    }
    bot.send_message(message.chat.id, "Параметры для фильтрации вакансий:", reply_markup=create_filter_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith('filter_'))
def filter_callback(call):
    param = call.data.split('_')[1]
    msg = f"Введите значение для параметра '{param}':"
    bot.send_message(call.message.chat.id, msg)
    bot.register_next_step_handler(call.message, set_filter_value, param)


def set_filter_value(message, param):
    user_filters[message.chat.id][param] = message.text
    bot.send_message(message.chat.id, f"Изменение применено", reply_markup=create_filter_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'search_vacancies')
def search_vacancies(call):
    params = user_filters.get(call.message.chat.id, {})

    params = {k: v for k, v in params.items() if v}
    try:
        vacancies = requests.get(f"{API_BASE_URL}/vacancy", params=params).json()
        for item in vacancies:
            vacancy = VacancyDTO(**item)
            msg = (f"{vacancy.name} \n"
                   f"{vacancy.employment}"
                   f"\n {vacancy.experience}")
            msg += (f"{"\n от " + str(vacancy.salary_from) if vacancy.salary_from else ""} "
                    f"{"до " + str(vacancy.salary_to) if vacancy.salary_to else ""} "
                    f"{vacancy.currency if vacancy.currency else ""}")
            if vacancy.city:
                msg += f"\n г. {vacancy.city}"
            msg += f"\n Работодатель: {vacancy.employer}"
            msg += f"\n {vacancy.address if vacancy.address else ''}"
            bot.send_message(call.message.chat.id, msg)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Ошибка {e}")


bot.polling(none_stop=True)
