from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.app.http.telegram import utils
from src.app.http.telegram.info import TelegramInfo
from src.app.http.telegram.states import States
from src.utils.logger.logger import Logger

router = Router()

log = Logger("telegram_router")


@router.message(CommandStart(deep_link=True))
async def start_link_open(
    msg: Message, command: CommandObject, state: FSMContext, info: TelegramInfo
):
    # scenario 1: user is not yet registeted, opens bot, allocation is running
    # case 1: allocation is started => user is need to be registered first
    # and then asked to fill the form.
    # in this case, allocation id is embedded in the /start message
    # so we can extract it and update the context, saving it for the future and navigate
    # user to the registration state.
    # "https://t.me/randorm_bot?start=allocationId%3D669c4f80916f6f81cd61f75e" # 12345678
    with log.activity("start_link_open"):
        assert msg.from_user is not None

        log.info(f"received message {msg.text} from user {msg.from_user.id}")

        if (args := command.args) is None or (
            allocation_id := utils.command_args_to_dict(args).get("allocationId")
        ) is None:
            log.info(
                "allocation id not found in deep link, interpreting as a regular start"
            )
            await start(msg, state, info)
            return

        await state.update_data(allocation_id=allocation_id)
        registered = (await state.get_data()).get("registered", False)

        if not registered:
            log.info("user is not registered, allocation id found")
            await start_registration(msg, state, info)


@router.message(CommandStart())
async def start(msg: Message, state: FSMContext, info: TelegramInfo):
    with log.activity("start_command"):
        assert msg.from_user is not None
        log.info(f"received message {msg.text} from user {msg.from_user.id}")

        registered = (await state.get_data()).get("registered", False)
        if not registered:
            log.info("user is not registered, allocation id found")
            await start_registration(msg, state, info)


async def start_registration(msg: Message, state: FSMContext, info: TelegramInfo):
    log.info("saving allocation id in user data")

    log.info("sending greeting message to user")
    await msg.answer("Hi, here we will help you to find the perfect roommates")

    log.info("navigating to check username state")
    await msg.answer("Let's start answering the questions :)")
    await state.set_state(States.check_username)
    await check_username(msg, state, info)


async def check_username(msg: Message, state: FSMContext, info: TelegramInfo):
    if (user := msg.from_user) is None or user.username is None:
        log.info("user has no username")

        await state.set_state(States.recheck_username)

        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Check again")

        send_message = await msg.answer(
            "Oops, wait. We can't detect your @username. Please go into the settings and fix it",
            reply_markup=builder.as_markup(),
        )
        await state.update_data(check_username_message=send_message.message_id)
    else:
        await successful_username(msg, state, info)


@router.message(States.recheck_username)
@router.callback_query(States.recheck_username)
async def recheck_username(
    msg: Message,
    state: FSMContext,
    info: TelegramInfo,
    callback: CallbackQuery | None = None,
):
    if callback is not None:
        await callback.answer()

    if (user := msg.from_user) is None or user.username is None:
        log.info("user still has no username")

        builder = InlineKeyboardBuilder()
        builder.button(text="🔄 Check again")

        user_data = await state.get_data()
        check_msg_id = user_data.get("check_username_message")
        if check_msg_id is not None and msg.bot is not None:
            await msg.bot.edit_message_text(
                "Sorry, still can not see it. Please go into the settings and fix it",
                chat_id=msg.chat.id,
                message_id=check_msg_id,
                reply_markup=builder.as_markup(),
            )
    else:
        await successful_username(msg, state, info)


async def successful_username(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None

    user_data = await state.get_data()
    check_username_msg_id = user_data.get("check_username_message")
    if check_username_msg_id is not None and msg.bot is not None:
        await msg.bot.delete_message(msg.chat.id, check_username_msg_id)
        await state.set_data(user_data.pop("check_username_message", None))

    await state.update_data(username=msg.from_user.username)
    await state.set_state(States.ask_first_name)
    await ask_first_name(msg, state, info)


async def ask_first_name(msg: Message, state: FSMContext, info: TelegramInfo):
    first_name_message = await msg.answer(
        "Enter your first name like <i>Ivan</i>", reply_markup=None
    )

    await state.update_data(first_name_message=first_name_message.message_id)


@router.message(States.ask_first_name)
async def first_name_response(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(first_name=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("first_name_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your first name like <i>Ivan</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_first_name"
                        )
                    ]
                ]
            ),
        )

    await state.set_state(States.ask_last_name)
    await ask_last_name(msg, state, info)


@router.message(States.edit_first_name)
async def edit_first_name(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(first_name=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("first_name_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your first name like <i>Ivan</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_first_name"
                        )
                    ]
                ]
            ),
        )

    next_state = (await state.get_data()).get("next_state", States.ask_last_name.state)
    await state.set_state(next_state)
    await state.update_data(next_state=None)

    if next_state == States.ask_first_name.state:
        await ask_first_name(msg, state, info)
    if next_state == States.ask_last_name.state:
        await ask_last_name(msg, state, info)
    if next_state == States.ask_birthdate.state:
        await ask_birthdate(msg, state, info)
    if next_state == States.ask_lanuage_code.state:
        await ask_lanuage_code(msg, state, info)
    if next_state == States.ask_gender.state:
        await ask_gender(msg, state, info)
    if next_state == States.confirm_registration.state:
        await confirm_registration(msg, state, info)


async def ask_last_name(msg: Message, state: FSMContext, info: TelegramInfo):
    last_name_message = await msg.answer(
        "Enter your last name like <i>Ivanov</i>", reply_markup=None
    )

    await state.update_data(last_name_message=last_name_message.message_id)


@router.message(States.ask_last_name)
async def last_name_response(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(last_name=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("last_name_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your last name like <i>Ivanov</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_last_name"
                        )
                    ]
                ]
            ),
        )

    await state.set_state(States.ask_birthdate)
    await ask_birthdate(msg, state, info)


@router.message(States.edit_last_name)
async def edit_last_name(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(last_name=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("last_name_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your last name like <i>Ivanov</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_last_name"
                        )
                    ]
                ]
            ),
        )

    next_state = (await state.get_data()).get("next_state", States.ask_last_name.state)
    await state.set_state(next_state)

    if next_state == States.ask_first_name:
        await ask_first_name(msg, state, info)
    if next_state == States.ask_last_name:
        await ask_last_name(msg, state, info)
    if next_state == States.ask_birthdate:
        await ask_birthdate(msg, state, info)
    if next_state == States.ask_lanuage_code:
        await ask_lanuage_code(msg, state, info)
    if next_state == States.ask_gender:
        await ask_gender(msg, state, info)
    if next_state == States.confirm_registration:
        await confirm_registration(msg, state, info)


async def ask_birthdate(msg: Message, state: FSMContext, info: TelegramInfo):
    birthdate_message = await msg.answer(
        "Enter your birthdate like <i>2023-08-26</i>", reply_markup=None
    )

    await state.update_data(birthdate_message=birthdate_message.message_id)


@router.message(States.ask_birthdate)
async def birthdate_response(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(birthdate=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("birthdate_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your birthdate like <i>2023-08-26</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_birthdate"
                        )
                    ]
                ]
            ),
        )

    await state.set_state(States.ask_lanuage_code)
    await ask_lanuage_code(msg, state, info)


@router.message(States.edit_birthdate)
async def edit_birthdate(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None
    await state.update_data(birthdate=msg.text)

    user_data = await state.get_data()

    name_msg_id = user_data.get("birthdate_message")
    if name_msg_id is not None and msg.bot is not None:
        await msg.bot.edit_message_text(
            f"Enter your birthdate like <i>2023-08-26</i>\n\nAnswer:<blockquote>{msg.text}</blockquote>\n",
            chat_id=msg.chat.id,
            message_id=name_msg_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🖋️ Edit", callback_data="edit_birthdate"
                        )
                    ]
                ]
            ),
        )

    next_state = (await state.get_data()).get(
        "next_state", States.ask_lanuage_code.state
    )
    await state.set_state(next_state)

    next_state = (await state.get_data()).get("next_state", States.ask_last_name.state)
    await state.set_state(next_state)

    if next_state == States.ask_first_name:
        await ask_first_name(msg, state, info)
    if next_state == States.ask_last_name:
        await ask_last_name(msg, state, info)
    if next_state == States.ask_birthdate:
        await ask_birthdate(msg, state, info)
    if next_state == States.ask_lanuage_code:
        await ask_lanuage_code(msg, state, info)
    if next_state == States.ask_gender:
        await ask_gender(msg, state, info)
    if next_state == States.confirm_registration:
        await confirm_registration(msg, state, info)


async def ask_lanuage_code(msg: Message, state: FSMContext, info: TelegramInfo):
    language_code_message = await msg.answer(
        "Choose your language",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🇺🇸 English", callback_data="english"),
                    InlineKeyboardButton(text="🇷🇺 Русский", callback_data="russian"),
                ]
            ]
        ),
    )

    await state.update_data(language_code_message=language_code_message.message_id)


@router.callback_query(States.ask_lanuage_code)
async def ask_lanuage_code_callback(
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    assert callback.message is not None

    await callback.answer()
    if callback.data == "cancel_language_code":
        await state.set_state(States.ask_lanuage_code)
        await state.update_data(next_state=States.ask_gender.state)

        assert callback.message is not None
        await ask_lanuage_code(callback.message, state, info)  # type: ignore

    elif callback.data == "english":
        await state.update_data(language_code="en")

        language_code_msg_id = (await state.get_data()).get("language_code_message")
        if language_code_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your language\n\nAnswer:<blockquote>English</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=language_code_msg_id,
                reply_markup=None,
            )

        await state.set_state(States.ask_gender)
        await ask_gender(callback.message, state, info)  # type: ignore

    elif callback.data == "russian":
        await state.update_data(language_code="ru")

        language_code_msg_id = (await state.get_data()).get("language_code_message")
        if language_code_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your language\n\nAnswer:<blockquote>Русский</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=language_code_msg_id,
                reply_markup=None,
            )

        await state.set_state(States.ask_gender)
        await ask_gender(callback.message, state, info)  # type: ignore

    else:
        await global_callback_query(callback, state, info)


@router.callback_query(States.edit_language_code)
async def edit_language_code_callback(  # noqa: C901
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    assert callback.message is not None

    await callback.answer()

    if callback.data == "edit_language_code":
        await state.set_state(States.edit_language_code)
        await state.update_data(next_state=States.ask_lanuage_code.state)

        assert callback.message is not None
        await ask_lanuage_code(callback.message, state, info)  # type: ignore

    elif callback.data == "english":
        await state.update_data(language_code="en")

        language_code_msg_id = (await state.get_data()).get("language_code_message")
        if language_code_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your language\n\nAnswer:<blockquote>English</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=language_code_msg_id,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🖋️ Edit", callback_data="edit_language_code"
                            ),
                        ]
                    ]
                ),
            )

    elif callback.data == "russian":
        await state.update_data(language_code="ru")

        language_code_msg_id = (await state.get_data()).get("language_code_message")
        if language_code_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your language\n\nAnswer:<blockquote>Русский</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=language_code_msg_id,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🖋️ Edit", callback_data="edit_language_code"
                            ),
                        ]
                    ]
                ),
            )
    else:
        await global_callback_query(callback, state, info)

    next_state = (await state.get_data()).get("next_state", States.ask_gender.state)
    await state.set_state(next_state)

    if next_state == States.ask_first_name:
        await ask_first_name(callback.message, state, info)  # type: ignore
    if next_state == States.ask_last_name:
        await ask_last_name(callback.message, state, info)  # type: ignore
    if next_state == States.ask_birthdate:
        await ask_birthdate(callback.message, state, info)  # type: ignore
    if next_state == States.ask_lanuage_code:
        await ask_lanuage_code(callback.message, state, info)  # type: ignore
    if next_state == States.ask_gender:
        await ask_gender(callback.message, state, info)  # type: ignore
    if next_state == States.confirm_registration:
        await confirm_registration(callback.message, state, info)  # type: ignore


async def ask_gender(msg: Message, state: FSMContext, info: TelegramInfo):
    gender_message = await msg.answer(
        "Choose your gender",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Male 👨", callback_data="male"),
                    InlineKeyboardButton(text="Female 👩", callback_data="female"),
                ]
            ]
        ),
    )

    await state.update_data(gender_message=gender_message.message_id)


@router.callback_query(States.ask_gender)
async def ask_gender_callback(
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    assert callback.message is not None

    await callback.answer()
    if callback.data == "cancel_gender":
        await state.set_state(States.ask_gender)
        await state.update_data(next_state=States.confirm_registration.state)

        assert callback.message is not None
        await ask_gender(callback.message, state, info)  # type: ignore

    elif callback.data == "male":
        await state.update_data(gender="male")

        gender_msg_id = (await state.get_data()).get("gender_message")
        if gender_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your gender\n\nAnswer:<blockquote>Male</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=gender_msg_id,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🖋️ Edit", callback_data="edit_gender"
                            ),
                        ]
                    ]
                ),
            )

        await state.set_state(States.confirm_registration)
        await confirm_registration(callback.message, state, info)  # type: ignore

    elif callback.data == "female":
        await state.update_data(gender="female")

        gender_msg_id = (await state.get_data()).get("gender_message")
        if gender_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your gender\n\nAnswer:<blockquote>Female</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=gender_msg_id,
                reply_markup=None,
            )

        await state.set_state(States.confirm_registration)
        await confirm_registration(callback.message, state, info)  # type: ignore

    else:
        await global_callback_query(callback, state, info)


@router.callback_query(States.edit_gender)
async def edit_gender_callback(  # noqa: C901
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    assert callback.message is not None

    await callback.answer()
    if callback.data == "edit_gender":
        await state.set_state(States.ask_gender)
        await state.update_data(next_state=States.confirm_registration.state)

        assert callback.message is not None
        await ask_gender(callback.message, state, info)  # type: ignore

    elif callback.data == "male":
        await state.update_data(gender="male")

        gender_msg_id = (await state.get_data()).get("gender_message")
        if gender_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your gender\n\nAnswer:<blockquote>Male</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=gender_msg_id,
                reply_markup=None,
            )

    elif callback.data == "female":
        await state.update_data(gender="female")

        gender_msg_id = (await state.get_data()).get("gender_message")
        if gender_msg_id is not None and callback.message.bot is not None:
            await callback.message.bot.edit_message_text(
                "Choose your gender\n\nAnswer:<blockquote>Female</blockquote>\n",
                chat_id=callback.message.chat.id,
                message_id=gender_msg_id,
                reply_markup=None,
            )

    else:
        await global_callback_query(callback, state, info)

    next_state = (await state.get_data()).get(
        "next_state", States.confirm_registration.state
    )

    if next_state == States.ask_first_name:
        await ask_first_name(callback.message, state, info)
    if next_state == States.ask_last_name:
        await ask_last_name(callback.message, state, info)
    if next_state == States.ask_birthdate:
        await ask_birthdate(callback.message, state, info)
    if next_state == States.ask_lanuage_code:
        await ask_lanuage_code(callback.message, state, info)
    if next_state == States.ask_gender:
        await ask_gender(callback.message, state, info)
    if next_state == States.confirm_registration:
        await confirm_registration(callback.message, state, info)


async def confirm_registration(msg: Message, state: FSMContext, info: TelegramInfo):
    assert msg.from_user is not None

    await state.set_state(States.confirm_registration)

    user_data = await state.get_data()

    await msg.answer(
        text=f"""
First Name: {user_data.get("first_name", "")}
Last Name: {user_data.get("last_name", "")}
Birthdate: {user_data.get("birthdate", "")}
Language: {user_data.get("language_code", "")}
Gender: {user_data.get("gender", "")}

If anything is wrong, please edut the information.
""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="👍 All correct", callback_data="done"),
                ],
                [
                    InlineKeyboardButton(
                        text="🖋️ Edit first name", callback_data="edit_first_name"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🖋️Edit last name", callback_data="edit_last_name"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🖋️Edit birthdate", callback_data="edit_birthdate"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🖋️Edit language", callback_data="edit_language_code"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🖋️ Edit gender", callback_data="edit_gender"
                    ),
                ],
            ]
        ),
    )


@router.callback_query(States.confirm_registration)
async def confirm_registration_callback(
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    assert callback.bot is not None
    assert callback.message is not None

    if callback.data == "done":
        await state.update_data(registered=True)
        await state.set_state(States.default)

        await callback.bot.send_message(
            callback.message.chat.id, "🎉 Registration done!"
        )
    else:
        global_callback_query(callback, state, info)


@router.callback_query()
async def global_callback_query(
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    log.info(f"received callback query {callback.data}")

    await callback.answer()
    if callback.data == "edit_first_name":
        await state.update_data(next_state=(await state.get_state()))
        await state.set_state(States.edit_first_name)

        assert callback.message is not None
        await ask_first_name(callback.message, state, info)  # type: ignore

    if callback.data == "edit_last_name":
        await state.update_data(next_state=(await state.get_state()))
        await state.set_state(States.edit_last_name)

        assert callback.message is not None
        await ask_last_name(callback.message, state, info)  # type: ignore

    if callback.data == "edit_birthdate":
        await state.update_data(next_state=(await state.get_state()))
        await state.set_state(States.edit_birthdate)

        assert callback.message is not None
        await ask_birthdate(callback.message, state, info)  # type: ignore

    if callback.data == "edit_language_code":
        await state.update_data(next_state=(await state.get_state()))
        await state.set_state(States.edit_language_code)

        assert callback.message is not None
        await ask_lanuage_code(callback.message, state, info)  # type: ignore

    if callback.data == "edit_gender":
        await state.update_data(next_state=(await state.get_state()))
        await state.set_state(States.edit_gender)

        assert callback.message is not None
        await ask_gender(callback.message, state, info)  # type: ignore

    if callback.data == "cancel":
        ...
