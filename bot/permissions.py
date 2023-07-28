from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Пользовательское разрешение (permission) для проверки прав доступа к объектам.

    Это разрешение позволяет пользователям с правами администратора выполнять любые действия (создание, обновление, удаление)
    над объектами, а все остальные пользователи имеют только право на чтение (GET-запросы).

    Methods:
        has_permission(request, view): Проверяет, имеет ли пользователь право доступа к списку объектов.
        has_object_permission(request, view, obj): Проверяет, имеет ли пользователь право доступа к конкретному объекту.
    """
    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь право доступа к списку объектов.

        Args:
            request (HttpRequest): Запрос, выполняемый клиентом.
            view (APIView): Представление (view) DRF, к которому применяется разрешение.

        Returns:
            bool: True, если пользователь имеет право доступа к списку объектов (разрешены все методы GET, HEAD, OPTIONS);
                  False в противном случае.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь право доступа к конкретному объекту.

        Args:
            request (HttpRequest): Запрос, выполняемый клиентом.
            view (APIView): Представление (view) DRF, к которому применяется разрешение.
            obj: Объект, к которому применяется разрешение (в данном случае, сообщение).

        Returns:
            bool: True, если пользователь является администратором (разрешены все методы доступа к объекту);
                  False в противном случае.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser
