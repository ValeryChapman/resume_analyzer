from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot_service.common.telegram.keyboards.start import start_menu_keyboard
from bot_service.common.telegram.texts.messages.start import start_message
from bot_service.settings import settings
from shared.infrastructure.telegram_bot.callbacks import Callbacks

router = Router(name="start_handlers_router")


@router.message(CommandStart())
async def command_start_menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text=start_message(bot_name=settings.branding.bot_name),
        reply_markup=start_menu_keyboard(),
    )


@router.callback_query(F.data == Callbacks.START)
async def callback_start_menu_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await state.clear()
    await callback.message.edit_text(
        text=start_message(bot_name=settings.branding.bot_name),
        reply_markup=start_menu_keyboard(),
    )
