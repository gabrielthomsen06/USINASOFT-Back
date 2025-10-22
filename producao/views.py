from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import OrdemProducao, OrdemProducaoItem
from .serializers import OrdemProducaoSerializer, OrdemProducaoItemSerializer


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all().order_by("-created_at")
    serializer_class = OrdemProducaoSerializer
    permission_classes = [AllowAny]


class OrdemProducaoItemViewSet(viewsets.ModelViewSet):
    queryset = (
        OrdemProducaoItem.objects.select_related("ordem", "peca").all().order_by("-created_at")
    )
    serializer_class = OrdemProducaoItemSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([AllowAny])
def indicadores_summary(request):
    """
    Endpoint para agregação de indicadores de Ordens de Produção.

    Query params:
    - start: data inicial (YYYY-MM-DD), default: 30 dias atrás
    - end: data final (YYYY-MM-DD), default: hoje
    - date_field: campo a usar para filtro ('data_fim_prevista' ou 'created_at'), default: 'data_fim_prevista'

    Retorna:
    {
        "periodo": {"start": "2025-01-01", "end": "2025-01-31"},
        "total": 150,
        "por_status": {
            "aberta": 10,
            "em_andamento": 45,
            "pausada": 5,
            "concluida": 85,
            "cancelada": 5
        },
        "agrupado": {
            "emFila": 10,      // aberta
            "emAndamento": 50, // em_andamento + pausada
            "concluidas": 85   // concluida
        }
    }
    """
    # Parse de datas com defaults
    end_date = request.GET.get("end")
    start_date = request.GET.get("start")
    date_field = request.GET.get("date_field", "data_fim_prevista")

    # Validar date_field
    if date_field not in ["data_fim_prevista", "created_at", "data_inicio_prevista"]:
        return Response(
            {
                "error": f"date_field inválido. Use: data_fim_prevista, data_inicio_prevista ou created_at"
            },
            status=400,
        )

    try:
        if end_date:
            end_date = date.fromisoformat(end_date)
        else:
            end_date = date.today()

        if start_date:
            start_date = date.fromisoformat(start_date)
        else:
            start_date = end_date - timedelta(days=30)

        if start_date > end_date:
            return Response({"error": "start deve ser anterior ou igual a end"}, status=400)
    except ValueError as e:
        return Response(
            {"error": f"Formato de data inválido. Use YYYY-MM-DD. Detalhes: {str(e)}"}, status=400
        )

    # Construir filtro dinâmico
    # Se usar created_at (DateTimeField), comparar com datas no início/fim do dia
    if date_field == "created_at":
        from datetime import datetime, time

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        filter_kwargs = {
            f"{date_field}__gte": start_datetime,
            f"{date_field}__lte": end_datetime,
        }
    else:
        # DateField: usar comparação direta
        filter_kwargs = {
            f"{date_field}__gte": start_date,
            f"{date_field}__lte": end_date,
        }

    # Queryset base
    qs = OrdemProducao.objects.filter(**filter_kwargs)

    # Agregação por status
    agregacao = qs.values("status").annotate(total=Count("id")).order_by("status")

    # Montar dicionário por_status
    por_status = {item["status"]: item["total"] for item in agregacao}

    # Total geral
    total = sum(por_status.values())

    # Agrupamento simplificado para o frontend
    agrupado = {
        "emFila": por_status.get("aberta", 0),
        "emAndamento": por_status.get("em_andamento", 0) + por_status.get("pausada", 0),
        "concluidas": por_status.get("concluida", 0),
    }

    return Response(
        {
            "periodo": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "date_field": date_field,
            },
            "total": total,
            "por_status": por_status,
            "agrupado": agrupado,
        }
    )
