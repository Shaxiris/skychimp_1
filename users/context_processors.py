from urllib.request import Request


def is_manager(request: Request) -> dict:
    """
    Контекстный процессор для передачи в контекст всех страниц результата проверки,
    принадлежит ли текущий пользователь к группе менеджеров
    """

    if request.user.is_authenticated:
        return {'is_manager': request.user.groups.filter(name='Managers').exists()}
    else:
        return {'is_manager': False}
