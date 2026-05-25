from contextlib import suppress

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot_service.common.telegram.keyboards.vacancies import (
    matches_list_pagination_keyboard,
)
from shared.domain.exceptions.match_results import MatchResultNotFoundError
from shared.infrastructure.telegram_bot.callbacks import (
    MatchCallback,
    MatchesCallback,
)
from shared.infrastructure.telegram_bot.keyboards import match_found_keyboard
from shared.infrastructure.telegram_bot.messages import match_result_details_message
from shared.services.match_results import (
    get_match_result_by_id_service,
    get_match_results_by_vacancy_id_service,
)

router = Router(name="matches_handlers_router")

MATCHES_DEFAULT_PAGE_SIZE = 5


@router.callback_query(MatchesCallback.filter())
async def callback_get_matches_page_handler(
    callback: CallbackQuery,
    callback_data: MatchesCallback,
    postgres_session: AsyncSession,
) -> None:
    matches, total_matches = await get_match_results_by_vacancy_id_service(
        postgres_session=postgres_session,
        vacancy_id=callback_data.vacancy_id,
        limit=MATCHES_DEFAULT_PAGE_SIZE,
        offset=(callback_data.page - 1) * MATCHES_DEFAULT_PAGE_SIZE,
    )

    if not matches:
        await callback.answer(
            "У этой вакансии пока нет подходящих кандидатов", show_alert=True
        )
        return

    if callback.message is not None:
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                text="🤝 <b>Список подходящих кандидатов</b>\n\nНиже представлены резюме с наилучшим соответствием.",
                reply_markup=matches_list_pagination_keyboard(
                    matches=matches,
                    vacancy_id=callback_data.vacancy_id,
                    total_matches=total_matches,
                    current_page=callback_data.page,
                    page_size=MATCHES_DEFAULT_PAGE_SIZE,
                ),
                parse_mode=ParseMode.HTML,
            )
    await callback.answer()


@router.callback_query(MatchCallback.filter())
async def callback_get_match_handler(
    callback: CallbackQuery,
    callback_data: MatchCallback,
    postgres_session: AsyncSession,
) -> None:
    try:
        match_result = await get_match_result_by_id_service(
            postgres_session=postgres_session,
            match_result_id=callback_data.id,
        )
    except MatchResultNotFoundError:
        await callback.answer("Результат не найден", show_alert=True)
        return

    if callback.message is not None:
        await callback.message.edit_text(
            text=match_result_details_message(match_result=match_result),
            reply_markup=match_found_keyboard(vacancy_id=match_result.vacancy_id),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    await callback.answer()
