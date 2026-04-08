def get_limit_and_offset_by_page(
    total: int, current_page: int = 1, page_size: int = 10
) -> tuple[int, int]:
    """
    Расчет limit и offset для пагинации.

    :param total: Общее количество элементов.
    :param current_page: Номер текущей страница.
    :param page_size: Кол-во элементов на странице.
    :return: Кортеж (limit, offset).
    """
    if current_page <= 0:
        current_page = 1

    total_pages = max((total + page_size - 1) // page_size, 1)
    current_page = max(1, min(current_page, total_pages))

    limit = page_size
    offset = (current_page - 1) * page_size
    return limit, offset


def get_total_pages(total: int, page_size: int = 10) -> int:
    """
    Расчет общего количества страниц.

    :param total: Общее количество элементов.
    :param page_size: Кол-во элементов на странице.
    :return: Количество страниц.
    """
    return max((total + page_size - 1) // page_size, 1)
