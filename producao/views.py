from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import date, timedelta
from .models import OrdemProducao
from .serializers import OrdemProducaoSerializer


class OrdemProducaoViewSet(viewsets.ModelViewSet):
    queryset = OrdemProducao.objects.select_related("cliente").all().order_by("-created_at")
    serializer_class = OrdemProducaoSerializer


@api_view(["GET"])
def indicadores_summary(request):
    """
    Retorna indicadores agregados de produção baseados em OPs e peças.
    """
    end_date = request.GET.get("end")
    start_date = request.GET.get("start")
    date_field = request.GET.get("date_field", "created_at")

    # Validar date_field
    if date_field not in ["created_at", "updated_at"]:
        return Response(
            {"error": f"date_field inválido. Use: created_at ou updated_at"},
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

    # Construir filtro para DateTimeField
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

    # Queryset base
    qs = OrdemProducao.objects.filter(**filter_kwargs)

    # Agregação por status de OP
    agregacao = qs.values("status").annotate(total=Count("id")).order_by("status")
    agregacao_dict = {item["status"]: item["total"] for item in agregacao}

    # Garantir todos os status
    status_choices = dict(OrdemProducao.StatusChoices.choices)
    por_status = {status: agregacao_dict.get(status, 0) for status in status_choices.keys()}

    # Total de OPs
    total_ops = sum(por_status.values())

    # Detalhes por status
    detalhes_por_status = []
    for status, label in status_choices.items():
        quantidade = por_status[status]
        percentual = round((quantidade / total_ops) * 100, 2) if total_ops else 0.0
        detalhes_por_status.append(
            {
                "status": status,
                "rotulo": label,
                "quantidade": quantidade,
                "percentual": percentual,
            }
        )

    # Calcular tempo médio de produção (entre criação e conclusão)
    ops_concluidas = qs.filter(status="concluida")
    if ops_concluidas.exists():
        tempo_medio_segundos = ops_concluidas.annotate(
            duracao=F("updated_at") - F("created_at")
        ).aggregate(media=Avg("duracao"))["media"]

        if tempo_medio_segundos:
            tempo_medio_dias = tempo_medio_segundos.total_seconds() / (60 * 60 * 24)
        else:
            tempo_medio_dias = 0
    else:
        tempo_medio_dias = 0

    # Estatísticas de peças
    from pecas.models import Peca

    pecas_qs = Peca.objects.filter(ordem_producao__in=qs)
    total_pecas = pecas_qs.count()

    pecas_por_status = pecas_qs.values("status").annotate(total=Count("id"))
    pecas_status_dict = {item["status"]: item["total"] for item in pecas_por_status}

    return Response(
        {
            "periodo": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "date_field": date_field,
            },
            "ordens_producao": {
                "total": total_ops,
                "por_status": por_status,
                "detalhes_por_status": detalhes_por_status,
                "tempo_medio_producao_dias": round(tempo_medio_dias, 2),
            },
            "pecas": {
                "total": total_pecas,
                "por_status": pecas_status_dict,
            },
        }
    )
