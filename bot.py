import os
import logging
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
    CallbackContext,
)

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для состояний разговора
(
    START,
    CLEANING_TYPE,
    APARTMENT_ROOMS,
    APARTMENT_BATHROOMS,
    ADDITIONAL_SERVICES,
    WARDROBE_AREA,
    WINDOWS_QUESTION,
    WINDOWS_COUNT,
    WINDOWS_INSTRUCTION,
    CHEMICAL_QUESTION,
    CHEMICAL_TYPE,
    SOFA_PLACES,
    MATTRESS_SIZE,
    CARPET_AREA,
    CHAIRS_COUNT,
    AFTER_REPAIR_AREA,
    COMMERCIAL_DETAILS,
    PROMO_CODE,
    PHONE,
    ADDRESS,
    DATE,
    NAME,
    CONFIRMATION,
    SPECIAL_REQUESTS,
     WARDROBE_AREA_INPUT,
) = range(25)

# Цены
PRICES = {
    "room": 1305,
    "bathroom": 1760,
    "kitchen": 1900,
    "additional": {
        "oven": 960,
        "hood": 896,
        "microwave": 512,
        "dishes": 640,
        "fridge": 960,
        "cabinets": 1660,
        "ironing": 1530,
        "balcony": 960,
        "litter_box": 256,
        "wardrobe": 450,
    },
    "chemical": {
        "sofa": {
            "2": 4005,
            "3": 4905,
            "4": 6255,
            "5-6": 7155,
            "7": 8325,
        },
        "mattress": {
            "1_1": 2000,
            "1_2": 4000,
            "2_1": 5500,
            "2_2": 11000,
        },
        "chair": 450,
        "headboard": 1600,
        "carpet": 320,
    },
    "windows": 1450,
    "after_repair": 210,
    "commercial": 70,
}


async def start(update: Update, context: CallbackContext) -> int:
    """Перезапускает бота, очищая предыдущие данные."""
    # Очищаем все данные пользователя
    context.user_data.clear()
    
    # Приветственное сообщение с клавиатурой
    reply_keyboard = [
        ["🧺 Уборка квартиры", "🏡 Уборка дома"],
        ["🔧 После ремонта", "🪟 Мытье окон"],
        ["🛋️ Химчистка", "👔 Коммерческое помещение"]
    ]
    
    await update.message.reply_text(
        "Привет! 👋 Я бот «Клиноголик» — помогу рассчитать стоимость уборки за 1 минуту!\n\n"
        "👉 *Выберите тип уборки:*",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True, 
            resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    return CLEANING_TYPE


async def cleaning_type(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор типа уборки."""
    user = update.message.from_user
    text = update.message.text
    context.user_data["cleaning_type"] = text

    logger.info("Пользователь %s выбрал: %s", user.first_name, text)

    if text in ["🧺 Уборка квартиры", "🏡 Уборка дома"]:
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "Будем мыть кухню?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return APARTMENT_ROOMS
    elif text == "🔧 После ремонта":
        await update.message.reply_text(
            "В сообщении напишите площадь помещения (например, 42)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return AFTER_REPAIR_AREA
    elif text == "🪟 Мытье окон":
        reply_keyboard = [["Как считать окна?"]]
        await update.message.reply_text(
            "Чтобы окна сияли, нам нужно знать их количество 😊",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return WINDOWS_INSTRUCTION
    elif text == "🛋️ Химчистка":
        reply_keyboard = [
            ["Диван🛋️", "Матрас"],
            ["Ковер", "Стулья/кресла 🪑"],
            ["Изголовье кровати", "❌Нет, не нужно"],
            ["Готово"],
        ]
        await update.message.reply_text(
            "👉*Выберите тип химчистки*\nМожете выбрать несколько",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=False, resize_keyboard=True
            ),
            parse_mode="Markdown",
        )
        context.user_data["chemical_services"] = []
        return CHEMICAL_TYPE
    elif text == "👔 Коммерческое помещение":
        await update.message.reply_text(
            "Спасибо за ваш запрос! 💙\n\n"
            "Стоимость уборки коммерческого помещения рассчитывается индивидуально — учитываем площадь, тип уборки и особенности объекта.\n\n"
            "Примерные цены: от 70 руб/м² (за базовую уборку) — если хотите ориентир😊\n\n"
            "📋 Чтобы мы могли подготовить для вас точное коммерческое предложение, пожалуйста, укажите:**\n\n"
            "1. **Тип помещения** (офис, магазин, салон, склад и т.д.)\n"
            "2. **Площадь** (м²)\n"
            "3. **Какие виды уборки нужны** (ежедневная, генеральная, после ремонта, химчистка и пр.)\n"
            "4. **Особые задачи** (например, мытьё витрин, чистка ковров, уборка санузлов)\n\n"
            "❗️отправьте информацию ОДНИМ сообщением\n\n"
            "💼 *Пример:*\n"
            "«Офис 150 м², нужна ежедневная уборка (пылесос, протирка поверхностей, санузлы) + мытьё окон 1 раз в месяц»",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
        return COMMERCIAL_DETAILS


async def apartment_rooms(update: Update, context: CallbackContext) -> int:
    """Обрабатывает вопрос о мытье кухни и запрашивает количество комнат."""
    text = update.message.text
    if text == "Да":
        context.user_data["kitchen"] = True
    else:
        context.user_data["kitchen"] = False

    await update.message.reply_text(
        "*Укажите количество комнат (только комнаты. Без кухни и санузлов.)*",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown",
    )
    return APARTMENT_BATHROOMS


async def apartment_bathrooms(update: Update, context: CallbackContext) -> int:
    """Обрабатывает количество комнат и запрашивает количество санузлов."""
    try:
        rooms = int(update.message.text)
        context.user_data["rooms"] = rooms
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return APARTMENT_BATHROOMS

    reply_keyboard = [["1", "2", "3"], ["4", "5", "6"]]
    await update.message.reply_text(
        "*Укажите количество санузлов (1 ванная + 1 туалет = 1 санузел)*",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode="Markdown",
    )
    return ADDITIONAL_SERVICES


async def additional_services(update: Update, context: CallbackContext) -> int:
    """Обрабатывает количество санузлов и предлагает дополнительные услуги."""
    try:
        bathrooms = int(update.message.text)
        context.user_data["bathrooms"] = bathrooms
    except ValueError:
        await update.message.reply_text("Пожалуйста, выберите вариант из предложенных.")
        return APARTMENT_BATHROOMS

    reply_keyboard = [
        ["🧽Помыть духовку (+960₽)", "🫧Помыть вытяжку (+896₽)"],
        ["✨Микроволновка (+512₽)", "🍽️Помыть посуду (+640₽)"],
        ["❄️Холодильник(+960₽)", "🗄️Внутри кух.шкафов (+1660₽)"],
        ["👚Погладить одежду (+1530₽/час)", "🪣Убраться на балконе (+960₽)"],
        ["🐾Лоток животных (+256₽)", "🧥Гардеробная (+450₽/м2)"],
        ["❌ Нет, только основная уборка", "Готово"],
    ]
    await update.message.reply_text(
        "*Нужны ли дополнительные услуги?*\nНажмите на все нужные варианты 😊",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=False, resize_keyboard=True
        ),
        parse_mode="Markdown",
    )
    context.user_data["additional_services"] = []
    return WARDROBE_AREA


async def wardrobe_area(update: Update, context: CallbackContext) -> int:
    """Обрабатывает дополнительные услуги и запрашивает площадь гардеробной с проверкой ввода."""
    text = update.message.text
    additional_services = context.user_data.get("additional_services", [])

    if text == "Готово":
        if "🧥Гардеробная (+450₽/м2)" in additional_services:
            await update.message.reply_text(
                "Сколько м² ваша гардеробная? Введите число (например: 3.5):",
                reply_markup=ReplyKeyboardRemove(),
            )
            return WARDROBE_AREA_INPUT  # Новое состояние для ввода площади
            
        return await ask_windows_cleaning(update)  # Переход к вопросу об окнах

    elif text == "❌ Нет, только основная уборка":
        context.user_data["additional_services"] = []
        return await ask_windows_cleaning(update)  # Переход к вопросу об окнах

    else:
        if text not in additional_services:
            additional_services.append(text)
        context.user_data["additional_services"] = additional_services
        return WARDROBE_AREA


async def wardrobe_area_input(update: Update, context: CallbackContext) -> int:
    """Обрабатывает ввод площади гардеробной с проверкой."""
    try:
        area = float(update.message.text)
        if area <= 0:
            raise ValueError("Площадь должна быть больше 0")
            
        context.user_data["wardrobe_area"] = area
        return await ask_windows_cleaning(update)  # Переход к вопросу об окнах
        
    except ValueError:
        await update.message.reply_text(
            "❌ Пожалуйста, введите корректное число (например: 2 или 3.5):",
            reply_markup=ReplyKeyboardRemove()
        )
        return WARDROBE_AREA_INPUT


async def ask_windows_cleaning(update: Update) -> int:
    """Задает вопрос о мытье окон (вынесено в отдельную функцию для повторного использования)."""
    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "*Помыть вам окна?* 🪟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode="Markdown"
    )
    return WINDOWS_QUESTION


async def windows_question(update: Update, context: CallbackContext) -> int:
    """Обрабатывает вопрос о мытье окон и предлагает химчистку после подсчёта."""
    text = update.message.text

    async def send_window_instructions():
        """Отправляет инструкцию по подсчёту окон с примерами."""
        await update.message.reply_text(
            "🪟 Мы считаем окна створками. Они могут различаться по размеру, *главное — их количество*",
            parse_mode="Markdown",
        )
        
        # Отправка примеров окон
        images = [
            "https://disk.yandex.ru/i/2YOHFSazb0NfLg",
            "https://disk.yandex.ru/i/CRTYcZ0ZyBTmow",
            "https://disk.yandex.ru/i/bD0nvSTxnrW7Jg",
            "https://disk.yandex.ru/i/JuuMOEG0QTj3xw",
            "https://disk.yandex.ru/i/Cg--s85r7ivGGw",
            "https://disk.yandex.ru/i/3JbC8AXn6gTHKw",
        ]
        for img in images:
            try:
                await update.message.reply_photo(img)
                await asyncio.sleep(0.3)  # Пауза между изображениями
            except Exception as e:
                logger.error(f"Ошибка отправки изображения: {e}")
        
        await update.message.reply_text(
            "*Сколько у вас окон?* 😊\n(можно дробное число, например 2.5 -> через точку)",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )

    # Обработка кнопки "Как считать окна?" или согласия на мытьё окон ("Да")
    if text == "Как считать окна?" or text == "Да":
        await send_window_instructions()
        return WINDOWS_COUNT
    
    # Обработка отказа от мытья окон ("Нет")
    elif text == "Нет":
        if context.user_data.get("cleaning_type") in ["🧺 Уборка квартиры", "🏡 Уборка дома", "🔧 После ремонта"]:
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "*Хотите заказать химчистку мебели и ковров одновременно с уборкой?* 🛋️",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                ),
                parse_mode="Markdown",
            )
            return CHEMICAL_QUESTION
        return await show_summary(update, context)
    
    # Обработка неожиданных сообщений
    else:
        reply_keyboard = [["Как считать окна?"]]
            
        await update.message.reply_text(
            "Пожалуйста, используйте кнопки для ответа:",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
        )
        return WINDOWS_QUESTION


async def windows_instruction(update: Update, context: CallbackContext) -> int:
    """Показывает инструкцию по подсчёту окон"""
    text = update.message.text
    
    if text == "Как считать окна?":
        # 1. Отправляем текстовое пояснение
        await update.message.reply_text(
            "🪟 Мы считаем окна створками. Они могут различаться по размеру, *главное — их количество*",
            parse_mode="Markdown"
        )
        
        # 2. Отправляем все примеры изображений
        images = [
            "https://disk.yandex.ru/i/2YOHFSazb0NfLg",
            "https://disk.yandex.ru/i/CRTYcZ0ZyBTmow",
            "https://disk.yandex.ru/i/bD0nvSTxnrW7Jg",
            "https://disk.yandex.ru/i/JuuMOEG0QTj3xw",
            "https://disk.yandex.ru/i/Cg--s85r7ivGGw",
            "https://disk.yandex.ru/i/3JbC8AXn6gTHKw"
        ]
        
        for img_url in images:
            try:
                await update.message.reply_photo(img_url)
                await asyncio.sleep(0.3)  # Небольшая пауза между изображениями
            except Exception as e:
                logger.error(f"Ошибка отправки изображения: {e}")
        
        # 3. Запрашиваем количество окон
        await update.message.reply_text(
            "Теперь укажите *сколько у вас окон* (можно дробное число, например 2.5 -> через точку):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        
        # Переходим в состояние ожидания ввода числа
        return WINDOWS_COUNT
    
    # Если получен неожиданный ввод
    await update.message.reply_text("Пожалуйста, нажмите кнопку 'Как считать окна?'")
    return WINDOWS_INSTRUCTION
    
    
async def windows_count(update: Update, context: CallbackContext) -> int:
    """Обрабатывает количество окон и предлагает химчистку."""
    try:
        windows = float(update.message.text)
        if windows <= 0:
            raise ValueError("Число должно быть положительным")
            
        context.user_data["windows"] = windows
        
        # Предлагаем химчистку после ввода количества окон
        if context.user_data.get("cleaning_type") in ["🧺 Уборка квартиры", "🏡 Уборка дома", "🔧 После ремонта"]:
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "*Отлично! Хотите добавить химчистку мебели/ковров?* 🛋️",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                ),
                parse_mode="Markdown",
            )
            return CHEMICAL_QUESTION
        
        # Для других типов уборки переходим к итогам
        return await show_summary(update, context)
        
    except ValueError:
        await update.message.reply_text(
            "Пожалуйста, введите корректное число (например: 3 или 2.5)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return WINDOWS_COUNT


async def chemical_question(update: Update, context: CallbackContext) -> int:
    """Обрабатывает вопрос о химчистке."""
    text = update.message.text
    if text == "Да":
        reply_keyboard = [
            ["Диван🛋️", "Матрас"],
            ["Ковер", "Стулья/кресла 🪑"],
            ["Изголовье кровати", "❌Нет, не нужно"],
            ["Готово"],
        ]
        await update.message.reply_text(
            "Выберите какая химчистка вам нужна?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=False, resize_keyboard=True
            ),
        )
        context.user_data["chemical_services"] = []
        return CHEMICAL_TYPE
    elif text == "Нет":
        return await show_summary(update, context)


async def chemical_type(update: Update, context: CallbackContext) -> int:
    """Обрабатывает выбор типа химчистки."""
    text = update.message.text
    chemical_services = context.user_data.get("chemical_services", [])

    if text == "Готово":
        if not chemical_services or "❌Нет, не нужно" in chemical_services:
            return await show_summary(update, context)
        else:
            # Начинаем уточнять параметры для выбранных услуг
            if "Диван🛋️" in chemical_services:
                reply_keyboard = [
                    ["2х местный"],
                    ["3х местный"],
                    ["4х местный"],
                    ["5-6 местный"],
                    ["7 местный"],
                ]
                await update.message.reply_text(
                    "*Укажите количество мест на диване:*",
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                    ),
                    parse_mode="Markdown",
                )
                return SOFA_PLACES
            elif "Матрас" in chemical_services:
                reply_keyboard = [
                    ["1 местный/ помыть с одной стороны"],
                    ["1 местный/ помыть с 2 сторон"],
                    ["2 местный/ помыть с 1 стороны"],
                    ["2 местный/ помыть с 2 сторон"],
                ]
                await update.message.reply_text(
                    "*Укажите размер матраса🛏️:*",
                    reply_markup=ReplyKeyboardMarkup(
                        reply_keyboard, one_time_keyboard=True, resize_keyboard=True
                    ),
                    parse_mode="Markdown",
                )
                return MATTRESS_SIZE
            elif "Ковер" in chemical_services:
                await update.message.reply_text(
                    "Сколько м2 ваш ковёр?\n(напишите цифру в сообщении)",
                    reply_markup=ReplyKeyboardRemove(),
                )
                return CARPET_AREA
            elif "Стулья/кресла 🪑" in chemical_services:
                await update.message.reply_text(
                    "*В сообщении напишите общее количество кресел/ стульев*",
                    reply_markup=ReplyKeyboardRemove(),
                    parse_mode="Markdown",
                )
                return CHAIRS_COUNT
            elif "Изголовье кровати" in chemical_services:
                context.user_data["headboard"] = True
                # Переходим к следующему выбранному пункту
                remaining_services = [
                    s
                    for s in chemical_services
                    if s
                    not in [
                        "Изголовье кровати",
                        "Диван🛋️",
                        "Матрас",
                        "Ковер",
                        "Стулья/кресла 🪑",
                    ]
                ]
                if remaining_services:
                    # Есть еще услуги для уточнения
                    if "Диван🛋️" in remaining_services:
                        reply_keyboard = [
                            ["2х местный"],
                            ["3х местный"],
                            ["4х местный"],
                            ["5-6 местный"],
                            ["7 местный"],
                        ]
                        await update.message.reply_text(
                            "*Укажите количество мест на диване:*",
                            reply_markup=ReplyKeyboardMarkup(
                                reply_keyboard,
                                one_time_keyboard=True,
                                resize_keyboard=True,
                            ),
                            parse_mode="Markdown",
                        )
                        return SOFA_PLACES
                    # ... аналогично для других услуг
                else:
                    return await show_summary(update, context)
            else:
                return await show_summary(update, context)
    elif text == "❌Нет, не нужно":
        context.user_data["chemical_services"] = []
        return await show_summary(update, context)
    else:
        if text not in chemical_services:
            chemical_services.append(text)
        context.user_data["chemical_services"] = chemical_services
        return CHEMICAL_TYPE


async def sofa_places(update: Update, context: CallbackContext) -> int:
    """Обрабатывает количество мест на диване."""
    text = update.message.text
    context.user_data["sofa_places"] = text

    chemical_services = context.user_data.get("chemical_services", [])
    # Проверяем, есть ли еще услуги для уточнения
    if "Матрас" in chemical_services and "mattress_size" not in context.user_data:
        reply_keyboard = [
            ["1 местный/ помыть с одной стороны"],
            ["1 местный/ помыть с 2 сторон"],
            ["2 местный/ помыть с 1 стороны"],
            ["2 местный/ помыть с 2 сторон"],
        ]
        await update.message.reply_text(
            "*Укажите размер матраса🛏️:*",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, resize_keyboard=True
            ),
            parse_mode="Markdown",
        )
        return MATTRESS_SIZE
    elif "Ковер" in chemical_services and "carpet_area" not in context.user_data:
        await update.message.reply_text(
            "Сколько м2 ваш ковёр?\n(напишите цифру в сообщении)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return CARPET_AREA
    elif (
        "Стулья/кресла 🪑" in chemical_services
        and "chairs_count" not in context.user_data
    ):
        await update.message.reply_text(
            "*В сообщении напишите общее количество кресел/ стульев*",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
        return CHAIRS_COUNT
    else:
        return await show_summary(update, context)


async def mattress_size(update: Update, context: CallbackContext) -> int:
    """Обрабатывает размер матраса."""
    text = update.message.text
    context.user_data["mattress_size"] = text

    chemical_services = context.user_data.get("chemical_services", [])
    # Проверяем, есть ли еще услуги для уточнения
    if "Ковер" in chemical_services and "carpet_area" not in context.user_data:
        await update.message.reply_text(
            "Сколько м2 ваш ковёр?\n(напишите цифру в сообщении)",
            reply_markup=ReplyKeyboardRemove(),
        )
        return CARPET_AREA
    elif (
        "Стулья/кресла 🪑" in chemical_services
        and "chairs_count" not in context.user_data
    ):
        await update.message.reply_text(
            "*В сообщении напишите общее количество кресел/ стульев*",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
        return CHAIRS_COUNT
    else:
        return await show_summary(update, context)


async def carpet_area(update: Update, context: CallbackContext) -> int:
    """Обрабатывает площадь ковра."""
    try:
        area = int(update.message.text)
        context.user_data["carpet_area"] = area
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return CARPET_AREA

    chemical_services = context.user_data.get("chemical_services", [])
    if (
        "Стулья/кресла 🪑" in chemical_services
        and "chairs_count" not in context.user_data
    ):
        await update.message.reply_text(
            "*В сообщении напишите общее количество кресел/ стульев*",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown",
        )
        return CHAIRS_COUNT
    else:
        return await show_summary(update, context)


async def chairs_count(update: Update, context: CallbackContext) -> int:
    """Обрабатывает количество стульев."""
    try:
        count = int(update.message.text)
        context.user_data["chairs_count"] = count
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return CHAIRS_COUNT

    return await show_summary(update, context)


async def after_repair_area(update: Update, context: CallbackContext) -> int:
    """Обрабатывает площадь помещения после ремонта."""
    try:
        area = int(update.message.text)
        context.user_data["after_repair_area"] = area
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return AFTER_REPAIR_AREA

    reply_keyboard = [["Да", "Нет"]]
    await update.message.reply_text(
        "*Помыть вам окна?*🪟",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode="Markdown",
    )
    return WINDOWS_QUESTION


async def commercial_details(update: Update, context: CallbackContext) -> int:
    """Обрабатывает детали коммерческого помещения."""
    context.user_data["commercial_details"] = update.message.text

    reply_keyboard = [["🎉Начать оформление", "❌Отменить заказ"]]
    await update.message.reply_text(
        "Спасибо за информацию!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return PROMO_CODE


async def show_summary(update: Update, context: CallbackContext) -> int:
    """Показывает сводку заказа с ценами для всех услуг."""
    total = 0
    details = []
    cleaning_type = context.user_data.get("cleaning_type")

    # Расчет стоимости для разных типов уборки
    if cleaning_type in ["🧺 Уборка квартиры", "🏡 Уборка дома"]:
        rooms = context.user_data.get("rooms", 0)
        if rooms > 0:
            room_cost = rooms * PRICES["room"]
            total += room_cost
            details.append(f"Уборка {rooms} комнат: {room_cost}₽")

        bathrooms = context.user_data.get("bathrooms", 0)
        if bathrooms > 0:
            bathroom_cost = bathrooms * PRICES["bathroom"]
            total += bathroom_cost
            details.append(f"Уборка {bathrooms} санузлов: {bathroom_cost}₽")

        if context.user_data.get("kitchen", False):
            total += PRICES["kitchen"]
            details.append(f"Уборка кухни: {PRICES['kitchen']}₽")

        # Обработка дополнительных услуг
        additional_prices = {
            "духовку": ("oven", "Мытье духовки: {}₽"),
            "вытяжку": ("hood", "Мытье вытяжки: {}₽"),
            "Микроволновка": ("microwave", "Мытье микроволновки: {}₽"),
            "посуду": ("dishes", "Мытье посуды: {}₽"),
            "Холодильник": ("fridge", "Мытье холодильника: {}₽"),
            "кух.шкафов": ("cabinets", "Мытье кухонных шкафов: {}₽"),
            "Погладить": ("ironing", "Глажка одежды: {}₽"),
            "балконе": ("balcony", "Уборка балкона: {}₽"),
            "лоток": ("litter_box", "Уборка лотка животных: {}₽"),
            "Гардеробная": ("wardrobe", "Уборка гардеробной ({}м²): {}₽")
        }

        for service in context.user_data.get("additional_services", []):
            for key, (price_key, description) in additional_prices.items():
                if key in service:
                    if key == "Гардеробная":
                        area = context.user_data.get("wardrobe_area", 0)
                        cost = area * PRICES["additional"][price_key]
                        details.append(description.format(area, cost))
                    else:
                        cost = PRICES["additional"][price_key]
                        details.append(description.format(cost))
                    total += cost
                    break

    elif cleaning_type == "🔧 После ремонта":
        area = context.user_data.get("after_repair_area", 0)
        if area > 0:
            cost = area * PRICES["after_repair"]
            total += cost
            details.append(f"Уборка после ремонта ({area}м²): {cost}₽")

    elif cleaning_type == "🪟 Мытье окон":
        windows = context.user_data.get("windows", 0)
        if windows > 0:
            cost = windows * PRICES["windows"]
            total += cost
            details.append(f"Мытье {windows} окон: {cost:.2f}₽")

    elif cleaning_type == "👔 Коммерческое помещение":
        details.append("Коммерческое помещение: расчет индивидуальный")
        details.append(f"Детали: {context.user_data.get('commercial_details', '')}")

    # Полностью переработанный блок химчистки
    chemical_services_config = {
        "Диван🛋️": {
            "price_key": "sofa",
            "data_key": "sofa_places",
            "template": "Химчистка {}-местного дивана: {}₽",
            "value_mapping": {
                "2х местный": "2",
                "3х местный": "3",
                "4х местный": "4",
                "5-6 местный": "5-6",
                "7 местный": "7"
            }
        },
        "Матрас": {
            "price_key": "mattress",
            "data_key": "mattress_size",
            "template": "Химчистка матраса ({}): {}₽",
            "value_mapping": {
                "1 местный/ помыть с одной стороны": "1_1",
                "1 местный/ помыть с 2 сторон": "1_2",
                "2 местный/ помыть с 1 стороны": "2_1",
                "2 местный/ помыть с 2 сторон": "2_2"
            }
        },
        "Ковер": {
            "price_key": "carpet",
            "data_key": "carpet_area",
            "template": "Химчистка ковра ({}м²): {}₽"
        },
        "Стулья/кресла 🪑": {
            "price_key": "chair",
            "data_key": "chairs_count",
            "template": "Химчистка {} {}: {}₽",
            "pluralize": lambda x: ("стульев" if x >= 5 else "стула" if x >= 2 else "стул")
        },
        "Изголовье кровати": {
            "price_key": "headboard",
            "template": "Химчистка изголовья кровати: {}₽"
        }
    }

    for service_name in context.user_data.get("chemical_services", []):
        if service_name in chemical_services_config:
            config = chemical_services_config[service_name]
            
            if "data_key" in config:
                raw_value = context.user_data.get(config["data_key"])
                if not raw_value:
                    continue
                    
                if "value_mapping" in config:
                    value_key = config["value_mapping"].get(raw_value)
                    if not value_key:
                        continue
                    cost = PRICES["chemical"][config["price_key"]].get(value_key, 0)
                    display_value = raw_value.split("/")[0].strip()
                else:
                    try:
                        value = float(raw_value)
                        cost = value * PRICES["chemical"][config["price_key"]]
                        display_value = str(value)
                    except (ValueError, TypeError):
                        continue
                
                if "pluralize" in config:
                    details.append(config["template"].format(
                        int(value), 
                        config["pluralize"](value), 
                        cost
                    ))
                else:
                    details.append(config["template"].format(display_value, cost))
                
                total += cost
            else:
                cost = PRICES["chemical"][config["price_key"]]
                details.append(config["template"].format(cost))
                total += cost

    # Мытье окон для других типов уборки
    if cleaning_type != "🪟 Мытье окон" and "windows" in context.user_data:
        windows = context.user_data["windows"]
        if windows > 0:
            cost = windows * PRICES["windows"]
            total += cost
            details.append(f"Мытье {windows} окон: {cost}₽")

    # Сохранение результатов
    context.user_data["total"] = total
    context.user_data["order_details"] = details

    # Формирование сообщения
    message = "*Отлично! 💡 Предварительная стоимость:*\n\n"
    message += "\n".join(details) if details else "Базовый тариф"
    message += f"\n\n*Итого: {total:.2f}₽*"

    # Для мытья окон сразу переходим к вводу телефона
    if cleaning_type == "🪟 Мытье окон":
        await update.message.reply_text(
            message + "\n\nЧтобы подтвердить заказ, оставьте\n📱 *Ваш телефон*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHONE

    # Для других услуг предлагаем начать оформление
    reply_keyboard = [["🎉Начать оформление", "❌Отменить заказ"]]
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
        parse_mode="Markdown",
    )
    return PROMO_CODE


async def promo_code(update: Update, context: CallbackContext) -> int:
    """Обрабатывает промокод или пропускает его для услуги мытья окон."""
    text = update.message.text
    cleaning_type = context.user_data.get("cleaning_type", "")
    
    # Флаг, что мы ожидаем ответ на вопрос о промокоде
    expecting_promo_answer = context.user_data.get("expecting_promo_answer", False)

    # Обработка отмены заказа (всегда доступна)
    if text == "❌Отменить заказ":
        await update.message.reply_text(
            "Жаль, что вы отменили заказ.😔😢\n\n"
            "Но мы будем рады помочь вам в другой раз!\n\n"
            "Если передумаете—просто нажмите[/start].🧹💛",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    # Если выбрано мытьё окон - пропускаем промокод
    if cleaning_type == "🪟 Мытье окон":
        await update.message.reply_text(
            "Чтобы уточнить детали и подтвердить заказ, оставьте\n📱 *Ваш телефон*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return PHONE

    # Если это первый вход в состояние (из show_summary)
    if not expecting_promo_answer and text == "🎉Начать оформление":
        reply_keyboard = [["Да", "Нет"]]
        await update.message.reply_text(
            "У вас есть промокод на скидку? 🫰",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, 
                one_time_keyboard=True, 
                resize_keyboard=True,
                input_field_placeholder="Выберите вариант ниже ⬇️"
            ),
        )
        context.user_data["expecting_promo_answer"] = True  # Устанавливаем флаг ожидания ответа
        return PROMO_CODE

    # Если ожидаем ответ на вопрос о промокоде
    if expecting_promo_answer:
        if text == "Да":
            await update.message.reply_text(
                "Напишите промокод в сообщении 💫",
                reply_markup=ReplyKeyboardRemove(),
            )
            context.user_data["expecting_promo_answer"] = False  # Сбрасываем флаг
            return PROMO_CODE  # Ожидаем ввод промокода
        
        elif text == "Нет":
            await update.message.reply_text(
                "Чтобы уточнить детали и подтвердить заказ, оставьте\n📱 *Ваш телефон*",
                parse_mode="Markdown",
                reply_markup=ReplyKeyboardRemove(),
            )
            context.user_data["expecting_promo_answer"] = False  # Сбрасываем флаг
            return PHONE
        
        else:
            # Если получен неожиданный ввод, повторяем вопрос
            reply_keyboard = [["Да", "Нет"]]
            await update.message.reply_text(
                "Пожалуйста, используйте кнопки для ответа:",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, 
                    one_time_keyboard=True, 
                    resize_keyboard=True,
                    input_field_placeholder="Выберите вариант ниже ⬇️"
                ),
            )
            return PROMO_CODE

    # Обработка введённого промокода (если флаг сброшен)
    promo = text.upper()
    if promo == "MARIA":
        total = context.user_data.get("total", 0)
        discount = int(total * 0.15)
        new_total = total - discount
        context.user_data["total"] = new_total
        context.user_data["discount"] = discount
        
        await update.message.reply_text(
            f"Ура!🎉 Вот вам скидка 15% лично от Марии\nТеперь стоимость уборки: *{new_total}₽*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif promo == "FIRST":
        total = context.user_data.get("total", 0)
        discount = int(total * 0.15)
        new_total = total - discount
        context.user_data["total"] = new_total
        context.user_data["discount"] = discount
        
        await update.message.reply_text(
            f"Нам очень приятно с вами познакомиться! 😊\nВ честь первой встречи дарим вам скидку 15%\nТеперь стоимость уборки: *{new_total}₽*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
    elif promo == "MECHTA":
        total = context.user_data.get("total", 0)
        discount = int(total * 0.10)
        new_total = total - discount
        context.user_data["total"] = new_total
        context.user_data["discount"] = discount
        
        await update.message.reply_text(
            f"Мечты сбываются! ✨\nВаша скидка по промокоду 10%\nТеперь стоимость уборки: *{new_total}₽*",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "Такого промокода нет, но вы все равно молодец! 😊",
            reply_markup=ReplyKeyboardRemove(),
        )

    # Переход к вводу телефона
    await update.message.reply_text(
        "Чтобы уточнить детали и подтвердить заказ, оставьте\n📱 *Ваш телефон*",
        parse_mode="Markdown",
    )
    return PHONE


async def phone(update: Update, context: CallbackContext) -> int:
    """Обрабатывает номер телефона."""
    if update.message.text in ["Да", "Нет"]:
        # Это ответ на вопрос о промокоде
        if update.message.text == "Да":
            await update.message.reply_text(
                "Напишите промокод в сообщении💫", reply_markup=ReplyKeyboardRemove()
            )
            return PROMO_CODE
        else:
            await update.message.reply_text(
                "Чтобы уточнить детали и подтвердить заказ, оставьте\n📱 *Ваш телефон*",
                parse_mode="Markdown",
            )
            return PHONE
    else:
        context.user_data["phone"] = update.message.text
        await update.message.reply_text(
            "🏢 *Адрес уборки* (город/улица/дом)\n❗️в ОДНОМ сообщении",
            parse_mode="Markdown",
        )
        return ADDRESS


async def address(update: Update, context: CallbackContext) -> int:
    """Обрабатывает адрес."""
    context.user_data["address"] = update.message.text
    await update.message.reply_text(
        "🗓 *Желаемая дата и время уборки*\n❗️в ОДНОМ сообщении",
        parse_mode="Markdown",
    )
    return DATE


async def date(update: Update, context: CallbackContext) -> int:
    """Обрабатывает дату."""
    context.user_data["date"] = update.message.text
    await update.message.reply_text("👥Напишите своё имя")
    return NAME


async def name(update: Update, context: CallbackContext) -> int:
    """Обрабатывает имя и показывает подтверждение."""
    context.user_data["name"] = update.message.text

    # Формируем сообщение для подтверждения
    message = "Проверьте правильно ли введены данные?😊\n\n"
    message += f"☎️Номер: {context.user_data.get('phone', '')}\n"
    message += f"📍Адрес: {context.user_data.get('address', '')}\n"
    message += f"🗓️Дата: {context.user_data.get('date', '')}\n"
    message += f"👥Имя: {context.user_data.get('name', '')}"

    reply_keyboard = [["Да", "Нет, хочу изменить"]]
    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return CONFIRMATION


async def confirmation(update: Update, context: CallbackContext) -> int:
    """Обрабатывает подтверждение или изменение данных."""
    text = update.message.text
    if text == "Нет, хочу изменить":
        await update.message.reply_text(
            "Давайте начнем заново.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            "Чтобы уточнить детали и подтвердить заказ, оставьте\n📱 *Ваш телефон*",
            parse_mode="Markdown",
        )
        return PHONE
    else:
        await update.message.reply_text(
            "🙏Напишите есть ли моменты или места, которые требуют отдельного внимания?\n❗️в ОДНОМ сообщении",
            reply_markup=ReplyKeyboardRemove(),
        )
        return SPECIAL_REQUESTS


async def special_requests(update: Update, context: CallbackContext) -> int:
    """Обрабатывает особые пожелания и завершает заказ."""
    context.user_data["special_requests"] = update.message.text
    user = update.message.from_user  # Получаем информацию о пользователе

    # Формируем информацию о клиенте
    client_info = (
        f"👤 *Информация о клиенте:*\n"
        f"ID: {user.id}\n"
        f"Username: @{user.username if user.username else 'нет'}\n"
        f"Имя: {user.first_name or ''} {user.last_name or ''}\n"
        f"Язык: {user.language_code if user.language_code else 'не указан'}"
    )

    # Отправляем информацию менеджеру
    manager_chat_id = os.getenv("MANAGER_CHAT_ID")
    if manager_chat_id:
        try:
            # Основное сообщение с заказом
            order_message = "📌 *Новый заказ!*\n\n"
            order_message += f"Тип уборки: {context.user_data.get('cleaning_type', '')}\n"
            order_message += "\n".join(context.user_data.get("order_details", []))
            order_message += f"\n\n*Итого: {context.user_data.get('total', 0):.2f}₽*\n"
            if "discount" in context.user_data:
                order_message += f"(С учетом скидки {context.user_data['discount']}₽)\n"
            order_message += f"\nКлиент: {context.user_data.get('name', '')}\n"
            order_message += f"Телефон: {context.user_data.get('phone', '')}\n"
            order_message += f"Адрес: {context.user_data.get('address', '')}\n"
            order_message += f"Дата: {context.user_data.get('date', '')}\n"
            order_message += f"Особые пожелания: {context.user_data.get('special_requests', '')}"

            # Сначала отправляем информацию о заказе
            await context.bot.send_message(
                chat_id=manager_chat_id,
                text=order_message,
                parse_mode="Markdown"
            )
            
            # Затем отправляем информацию о клиенте
            await context.bot.send_message(
                chat_id=manager_chat_id,
                text=client_info,
                parse_mode="Markdown"
            )
            
            # Если есть username, добавляем кнопку "Написать клиенту"
            if user.username:
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        "✉️ Написать клиенту", 
                        url=f"https://t.me/{user.username}"
                    )]
                ])
                await context.bot.send_message(
                    chat_id=manager_chat_id,
                    text="Можно написать клиенту напрямую:",
                    reply_markup=reply_markup
                )

        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения менеджеру: {e}")
            # Можно добавить уведомление админу об ошибке

    # Отправляем подтверждение клиенту
    await update.message.reply_text(
        "*Спасибо! 🎉 Наш менеджер свяжется с вами в течение 15 минут для подтверждения.*\n\n"
        "📍МО, Дмитровский муниципальный округ, п.«Пески»\n"
        "☎️ +7(991)600-32-23",
        parse_mode="Markdown",
    )

    # Очищаем данные пользователя после завершения заказа
    context.user_data.clear()

    # Предлагаем начать заново
    reply_keyboard = [["/start"]]
    await update.message.reply_text(
        "Хотите сделать еще один заказ?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    """Отменяет диалог и предлагает начать заново."""
    reply_markup = ReplyKeyboardMarkup(
        [["/start"]], 
        resize_keyboard=True
    )
    await update.message.reply_text(
        "Заказ отменён. 😢\n"
        "Хотите начать новый заказ?",
        reply_markup=reply_markup
    )
    context.user_data.clear()
    return ConversationHandler.END


async def price(update: Update, context: CallbackContext) -> None:
    """Показывает стандартные тарифы."""
    message = (
        "💰 *Стандартные тарифы:*\n\n"
        "🧹 *Уборка квартиры/дома:*\n"
        "- Комната: 1305₽\n"
        "- Санузел: 1760₽\n"
        "- Кухня: 1900₽\n\n"
        "🔧 *После ремонта:* 210₽/м²\n\n"
        "🪟 *Мытье окон:* 1450₽ за створку\n\n"
        "🛋️ *Химчистка:*\n"
        "- Диван 2-местный: 4005₽\n"
        "- Диван 3-местный: 4905₽\n"
        "- Диван 4-местный: 6255₽\n"
        "- Диван 5-6 местный: 7155₽\n"
        "- Диван 7-местный: 8325₽\n"
        "- Матрас 1-местный (1 сторона): 2000₽\n"
        "- Матрас 1-местный (2 стороны): 4000₽\n"
        "- Матрас 2-местный (1 сторона): 5500₽\n"
        "- Матрас 2-местный (2 стороны): 11000₽\n"
        "- Ковер: 320₽/м²\n"
        "- Стул/кресло: 450₽\n"
        "- Изголовье кровати: 1600₽\n\n"
        "👔 *Коммерческие помещения:* от 70₽/м²"
    )
    await update.message.reply_text(message, parse_mode="Markdown")


async def contacts(update: Update, context: CallbackContext) -> None:
    """Показывает контакты компании."""
    message = (
        "📍 *Адрес:* МО, Дмитровский муниципальный округ, п.«Пески»\n"
        "☎️ *Телефон:* +7(991)600-32-23"
    )
    await update.message.reply_text(message, parse_mode="Markdown")
    
async def fallback_handler(update: Update, context: CallbackContext) -> int:
    """Предлагает начать заново при неожиданном вводе."""
    await update.message.reply_text(
        "Не понимаю команду. 😕\n\n"
        "Введите /start для нового заказа или /cancel для отмены.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() -> None:
    """Запускает бота."""
    # Создаем Application и передаем ему токен бота
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Добавляем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CLEANING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, cleaning_type)],
            APARTMENT_ROOMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, apartment_rooms)],
            APARTMENT_BATHROOMS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, apartment_bathrooms)
            ],
            ADDITIONAL_SERVICES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, additional_services)
            ],
            WARDROBE_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, wardrobe_area)],
            WINDOWS_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, windows_question)
            ],
            WARDROBE_AREA_INPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, wardrobe_area_input)
            ],
            WINDOWS_INSTRUCTION: [MessageHandler(filters.TEXT, windows_instruction)],
            WINDOWS_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, windows_count)],
            CHEMICAL_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chemical_question)
            ],
            CHEMICAL_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, chemical_type)],
            SOFA_PLACES: [MessageHandler(filters.TEXT & ~filters.COMMAND, sofa_places)],
            MATTRESS_SIZE: [MessageHandler(filters.TEXT & ~filters.COMMAND, mattress_size)],
            CARPET_AREA: [MessageHandler(filters.TEXT & ~filters.COMMAND, carpet_area)],
            CHAIRS_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, chairs_count)],
            AFTER_REPAIR_AREA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, after_repair_area)
            ],
            COMMERCIAL_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, commercial_details)
            ],
            PROMO_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, promo_code)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, date)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmation)],
            SPECIAL_REQUESTS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, special_requests)
            ],
        },
        fallbacks=[
        CommandHandler("cancel", cancel),
        CommandHandler("start", start),  # Добавлено для перезапуска
        MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_handler)
    ],
    allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("price", price))
    application.add_handler(CommandHandler("contacts", contacts))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()