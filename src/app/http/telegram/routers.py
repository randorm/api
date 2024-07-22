import ujson
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

from src.app.http.telegram.info import TelegramInfo
from src.app.http.telegram.states import States
from src.utils.logger.logger import Logger

router = Router()

log = Logger("telegram-router")


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
    with log.activity("start-link-open"):
        assert msg.from_user is not None

        log.info(f"received message {msg.text} from user {msg.from_user.id}")

        if command.args is None:
            ...  # todo: send error message
            return

        payload = dict([pair.split("=") for pair in command.args.split()])
        log.info("deep link payload: {}", ujson.dumps(payload))
        allocation_id = payload.get("allocationId")

        if allocation_id is None:
            log.info("allocation id not found in deep link")
            ...  # todo: send error message
            return

        registered = (await state.get_data()).get("registered", False)

        if not registered:
            log.info("user is not registered, allocation id found")

            log.info("saving allocation id in user data")
            await state.update_data(allocation_id=allocation_id)

            log.info("sending greeting message to user")
            await msg.answer("Hi, here we will help you to find the perfect roommates")

            log.info("navigating to check username state")
            await msg.reply("Let's start answering the questions :)")
            await state.set_state(States.check_username)
            await check_username(msg, state, info)


@router.message(CommandStart())
async def start(msg: Message, state: FSMContext, info: TelegramInfo):
    with log.activity("start-command"):
        assert msg.from_user is not None

        log.info(f"received message {msg.text} from user {msg.from_user.id}")

        return


async def check_username(msg: Message, state: FSMContext, info: TelegramInfo):
    if (user := msg.from_user) is None or user.username is None:
        log.info("user has no username")

        await state.set_state(States.recheck_username)

        builder = InlineKeyboardBuilder()
        builder.button(text="Check again 🔄")

        send_message = await msg.reply(
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
        builder.button(text="Check again 🔄")

        user_data = await state.get_data()
        check_msg_id = user_data.get("check_username_message")
        if check_msg_id is not None and msg.bot is not None:
            await msg.bot.edit_message_text(
                "Sorry, still can not see it. Please go into the settings and fix it",
                check_msg_id,
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
    first_name_message = await msg.reply(
        "Enter your first name like <i>Ivan</i>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Cancel 🔙", callback_data="cancel")]
            ]
        ),
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
                            text="Edit 🖋️", callback_data="edit-first-name"
                        )
                    ]
                ]
            ),
        )


@router.callback_query(States.ask_first_name)
async def ask_first_name_callback(
    callback: CallbackQuery, state: FSMContext, info: TelegramInfo
):
    await callback.answer()
    if callback.data == "edit-first-name":
        await state.set_state(States.edit_first_name)
        await state.update_data(next_state=States.ask_last_name.state)

        assert callback.message is not None
        await ask_first_name(callback.message, state, info)  # type: ignore

    if callback.data == "cancel":
        ...
