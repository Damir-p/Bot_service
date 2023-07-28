from rest_framework import generics
from .models import Message
from .serializers import MessageSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .permissions import IsAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    """
    API-представление для просмотра списка сообщений и создания новых сообщений.

    Attributes:
        queryset (QuerySet): Набор объектов модели Message, полученных из базы данных.
        serializer_class (Serializer): Класс сериализатора для преобразования объектов Message в JSON и обратно.
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется пользовательское разрешение IsAdminOrReadOnly,
                                   которое позволяет администраторам выполнять любые действия, а остальным
                                   пользователям разрешены только запросы на чтение (GET, HEAD, OPTIONS).
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminOrReadOnly]


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API-представление для просмотра, обновления и удаления отдельного сообщения.

    Attributes:
        queryset (QuerySet): Набор объектов модели Message, полученных из базы данных.
        serializer_class (Serializer): Класс сериализатора для преобразования объектов Message в JSON и обратно.
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется пользовательское разрешение IsAdminOrReadOnly,
                                   которое позволяет администраторам выполнять любые действия, а остальным
                                   пользователям разрешены только запросы на чтение (GET, HEAD, OPTIONS).
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAdminOrReadOnly]


class TokenObtainPairView(APIView):
    """
    API-представление для получения пары токенов аутентификации (JWT) на основе учетных данных пользователя.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение AllowAny, которое позволяет всем
                                   пользователям (аутентифицированным и неаутентифицированным) выполнять запросы к представлению.
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """
        Обработчик POST-запроса для получения пары токенов аутентификации на основе учетных данных пользователя.

        Args:
            request (Request): Объект запроса, содержащий учетные данные пользователя (username и password).

        Returns:
            Response: JSON-ответ с парой токенов аутентификации в случае успешной аутентификации,
                      или сообщение об ошибке в случае неверных учетных данных.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})

        return Response({'error': 'Invalid credentials'}, status=400)
    

class MessageHistoryView(APIView):
    """
    API-представление для просмотра истории всех сообщений.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение IsAuthenticated, которое позволяет
                                   выполнять запросы к представлению только аутентифицированным пользователям.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Обработчик GET-запроса для получения истории всех сообщений.

        Args:
            request (Request): Объект запроса.

        Returns:
            Response: JSON-ответ со списком всех сообщений из базы данных, сериализованных с помощью MessageSerializer.
        """
        messages = Message.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageUpdateView(APIView):
    """
    API-представление для обновления отдельного сообщения.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение IsAuthenticated, которое позволяет
                                   выполнять запросы к представлению только аутентифицированным пользователям.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        """
        Обработчик PUT-запроса для обновления отдельного сообщения.

        Args:
            request (Request): Объект запроса.
            pk (int): Первичный ключ (id) сообщения, которое нужно обновить.

        Returns:
            Response: JSON-ответ с обновленными данными сообщения из базы данных, сериализованными с помощью MessageSerializer.
        """
        message = Message.objects.get(pk=pk)

        message.text = request.data.get('text', message.text)
        message.command = request.data.get('command', message.command)
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data)


class DashboardView(APIView):
    """
    API-представление для отображения данных на дашборде.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение IsAuthenticated, которое позволяет
                                   выполнять запросы к представлению только аутентифицированным пользователям.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Обработчик GET-запроса для получения данных на дашборде.

        Args:
            request (Request): Объект запроса.

        Returns:
            Response: JSON-ответ с данными для отображения на дашборде, такими как количество активных диалогов,
                      статистика по количеству запросов и наиболее популярные команды.
        """
        active_dialogs = Message.objects.filter(is_active=True).count()
        request_counts = Message.objects.values('timestamp').annotate(count=Count('id'))
        popular_commands = Message.objects.values('command').annotate(count=Count('id')).order_by('-count')[:5]

        dashboard_data = {
            'active_dialogs': active_dialogs,
            'request_counts': request_counts,
            'popular_commands': popular_commands,
        }

        return Response(dashboard_data)


class UserRegistrationView(APIView):
    """
    API-представление для регистрации нового пользователя.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение AllowAny, которое позволяет
                                   выполнять запросы к представлению без аутентификации.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Обработчик POST-запроса для регистрации нового пользователя.

        Args:
            request (Request): Объект запроса.

        Returns:
            Response: JSON-ответ с данными нового пользователя и токенами доступа.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=400)


class UserLoginView(APIView):
    """
    API-представление для аутентификации пользователя.

    Attributes:
        permission_classes (list): Список классов разрешений для определения прав доступа к представлению.
                                   В данном случае используется разрешение AllowAny, которое позволяет
                                   выполнять запросы к представлению без аутентификации.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Обработчик POST-запроса для аутентификации пользователя.

        Args:
            request (Request): Объект запроса.

        Returns:
            Response: JSON-ответ с токенами доступа, если аутентификация прошла успешно, и сообщение об ошибке
                      при неправильных учетных данных.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=200)

        return Response({'detail': 'Invalid credentials'}, status=401)
