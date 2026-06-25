from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Notification, Target
from .serializers import NotificationSerializer, NotificationCreateSerializer
from .authentication import get_target_from_headers, get_empresa_from_headers


class NotificacoesNaoLidasCountView(APIView):
    """
    GET /api/notificacoes/nao-lidas/
    Retorna a quantidade de notificacoes nao lidas do usuario.
    """

    def get(self, request):
        target = get_target_from_headers(request)
        count = Notification.objects.filter(target=target, is_read=False).count()
        return Response({'count': count})


class NotificacoesListView(APIView):
    """
    GET /api/notificacoes/
    Retorna as notificacoes do usuario.

    Query params opcionais:
        ?is_read=true   → somente lidas
        ?is_read=false  → somente nao lidas
        (sem parametro) → todas
    """

    def get(self, request):
        target = get_target_from_headers(request)
        notificacoes = Notification.objects.filter(target=target)

        # Filtro opcional por is_read
        is_read_param = request.query_params.get('is_read')
        if is_read_param is not None:
            is_read = is_read_param.lower() in ['true', '1', 'sim']
            notificacoes = notificacoes.filter(is_read=is_read)

        serializer = NotificationSerializer(notificacoes, many=True)
        return Response(serializer.data)


class NotificacaoMarcarLidaView(APIView):
    """
    PATCH /api/notificacoes/<id>/lida/
    Marca uma notificacao como lida.
    """

    def patch(self, request, pk):
        target = get_target_from_headers(request)

        try:
            notificacao = Notification.objects.get(pk=pk, target=target)
        except Notification.DoesNotExist:
            return Response({'erro': 'Notificacao nao encontrada.'}, status=404)

        notificacao.is_read = True
        notificacao.save()

        serializer = NotificationSerializer(notificacao)
        return Response(serializer.data)


class NotificacaoCreateView(APIView):
    """
    POST /api/notificacoes/criar/
    Cria uma notificacao para um usuario.

    Esse endpoint e usado por OUTROS SISTEMAS (ou pelo admin/testes)
    para enviar notificacoes. O portfolio NAO usa esse endpoint —
    ele apenas LE as notificacoes.

    Headers: X-Api-Key (identifica a empresa)
    Body: { "user_id": 1, "mensagem": "Texto da notificacao" }
    """

    def post(self, request):
        empresa = get_empresa_from_headers(request)

        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Busca ou cria o target
        target, created = Target.objects.get_or_create(
            empresa=empresa,
            user_id=serializer.validated_data['user_id'],
        )

        # Cria a notificacao
        notificacao = Notification.objects.create(
            target=target,
            mensagem=serializer.validated_data['mensagem'],
        )

        return Response(
            NotificationSerializer(notificacao).data,
            status=status.HTTP_201_CREATED,
        )
        
class NotificacaoMarcarTodasLidasView(APIView):
    """
    PATCH /api/notificacoes/marcar-todas-lidas/
    Marca todas as notificacoes de um usuario como lidas de uma vez só.
    """
    def patch(self, request):
        target = get_target_from_headers(request)
        
        # O .update() altera todos os registros filtrados de uma vez no banco
        atualizadas = Notification.objects.filter(target=target, is_read=False).update(is_read=True)
        
        return Response({'mensagem': f'{atualizadas} notificacoes marcadas como lidas.'})
# Create your views here.
