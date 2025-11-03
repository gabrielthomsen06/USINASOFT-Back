from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date, timedelta
from .models import OrdemProducao, OrdemProducaoItem
from .serializers import OrdemProducaoSerializer, OrdemProducaoItemSerializer


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.all().order_by("-created_at")
    serializer_class = OrdemProducaoSerializer


class OrdemProducaoItemViewSet(viewsets.ModelViewSet):
    queryset = (
        OrdemProducaoItem.objects.select_related("ordem", "peca").all().order_by("-created_at")
    )
    serializer_class = OrdemProducaoItemSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def indicadores_summary(request):

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

        tz = timezone.get_current_timezone()
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        if timezone.is_naive(start_datetime):
            start_datetime = timezone.make_aware(start_datetime, timezone=tz)
        if timezone.is_naive(end_datetime):
            end_datetime = timezone.make_aware(end_datetime, timezone=tz)

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

    # Agregação por status (resulta apenas nos status encontrados)
    agregacao = qs.values("status").annotate(total=Count("id")).order_by("status")
    agregacao_dict = {item["status"]: item["total"] for item in agregacao}

    # Garantir a presença de todos os status possíveis, mesmo com zero ocorrências
    status_choices = dict(OrdemProducao.StatusChoices.choices)
    por_status = {status: agregacao_dict.get(status, 0) for status in status_choices.keys()}

    # Total geral
    total = sum(por_status.values())

    # Lista detalhada para facilitar a renderização no frontend
    detalhes_por_status = []
    for status, label in status_choices.items():
        quantidade = por_status[status]
        percentual = round((quantidade / total) * 100, 2) if total else 0.0
        detalhes_por_status.append(  # fornece dados tabulados para o frontend
            {
                "status": status,
                "rotulo": label,
                "quantidade": quantidade,
                "percentual": percentual,
            }
        )

    # Agrupamento simplificado para o frontend (mantido para compatibilidade)
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
            "detalhes_por_status": detalhes_por_status,
            "agrupado": agrupado,
        }
    )
