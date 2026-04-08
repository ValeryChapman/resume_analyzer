from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot_service.common.telegram.callbacks import (
    Callbacks,
    VacanciesCallback,
    VacancyCallback,
)
from bot_service.common.telegram.keyboards.vacancies import (
    add_vacancy_keyboard,
    vacancies_list_pagination_keyboard,
    vacancy_details_keyboard,
)
from bot_service.common.telegram.states import AddVacancyState
from bot_service.common.telegram.texts.messages.vacancies import (
    add_vacancy_non_text_message,
    add_vacancy_prompt_message,
    add_vacancy_validation_message,
    vacancies_list_message,
    vacancies_not_found_message,
    vacancy_created_message,
    vacancy_details_message,
    vacancy_not_found_message,
)
from bot_service.common.tools.pagination import get_limit_and_offset_by_page
from shared.application.services.vacancies import (
    create_vacancy_service,
    get_vacancies_by_user_id_service,
    get_vacancies_count_by_user_id_service,
    get_vacancy_by_id_service,
)
from shared.domain.exceptions.vacancies import (
    VacancyNotFoundError,
    VacancyValidationError,
)
from shared.infrastructure.postgres.models.user import User

router = Router(name="vacancies_handlers_router")

VACANCIES_DEFAULT_PAGE_SIZE = 5


@router.callback_query(F.data == Callbacks.ADD_VACANCY)
async def callback_add_vacancy_handler(
    callback: CallbackQuery, state: FSMContext
) -> None:
    await state.set_state(AddVacancyState.waiting_for_text)
    if callback.message is not None:
        await callback.message.edit_text(
            text=add_vacancy_prompt_message(),
            reply_markup=add_vacancy_keyboard(),
        )
    await callback.answer()


@router.callback_query(VacanciesCallback.filter())
async def callback_get_vacancies_page_handler(
    callback: CallbackQuery,
    callback_data: VacanciesCallback,
    db_user: User,
    postgres_session: AsyncSession,
) -> None:
    total_user_vacancies: int = await get_vacancies_count_by_user_id_service(
        postgres_session=postgres_session, user_id=db_user.id
    )
    if total_user_vacancies == 0:
        await callback.answer(vacancies_not_found_message(), show_alert=True)
        return

    limit, offset = get_limit_and_offset_by_page(
        total=total_user_vacancies,
        current_page=callback_data.page,
        page_size=VACANCIES_DEFAULT_PAGE_SIZE,
    )
    vacancies = await get_vacancies_by_user_id_service(
        postgres_session=postgres_session,
        user_id=db_user.id,
        limit=limit,
        offset=offset,
    )
    if callback.message is not None:
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                text=vacancies_list_message(),
                reply_markup=vacancies_list_pagination_keyboard(
                    vacancies=vacancies,
                    total_vacancies=total_user_vacancies,
                    current_page=callback_data.page,
                    page_size=VACANCIES_DEFAULT_PAGE_SIZE,
                ),
            )
    await callback.answer()


@router.callback_query(VacancyCallback.filter())
async def callback_get_vacancy_handler(
    callback: CallbackQuery,
    callback_data: VacancyCallback,
    db_user: User,
    postgres_session: AsyncSession,
) -> None:
    try:
        vacancy = await get_vacancy_by_id_service(
            postgres_session=postgres_session,
            vacancy_id=callback_data.id,
            user_id=db_user.id,
        )
    except VacancyNotFoundError:
        await callback.answer(vacancy_not_found_message(), show_alert=True)
        return

    if callback.message is not None:
        await callback.message.edit_text(
            text=vacancy_details_message(vacancy=vacancy),
            reply_markup=vacancy_details_keyboard(),
        )
    await callback.answer()


@router.message(AddVacancyState.waiting_for_text, F.text)
async def message_add_vacancy_handler(
    message: Message,
    state: FSMContext,
    db_user: User,
    postgres_session: AsyncSession,
) -> None:
    try:
        await create_vacancy_service(
            postgres_session=postgres_session,
            user_id=db_user.id,
            raw_text=message.text or "",
        )
    except VacancyValidationError as exc:
        await message.answer(
            text=add_vacancy_validation_message(str(exc)),
            reply_markup=add_vacancy_keyboard(),
        )
        return

    await state.clear()
    await message.answer(
        text=vacancy_created_message(),
        reply_markup=add_vacancy_keyboard(),
    )


@router.message(AddVacancyState.waiting_for_text)
async def message_add_vacancy_non_text_handler(message: Message) -> None:
    await message.answer(
        text=add_vacancy_non_text_message(),
        reply_markup=add_vacancy_keyboard(),
    )
