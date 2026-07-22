"""Clases de paginacion reutilizables."""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    """Paginacion estandar con tamano configurable por query param."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(
            {
                "exito": True,
                "mensaje": "Listado obtenido correctamente.",
                "data": {
                    "total": self.page.paginator.count,
                    "pagina_actual": self.page.number,
                    "total_paginas": self.page.paginator.num_pages,
                    "siguiente": self.get_next_link(),
                    "anterior": self.get_previous_link(),
                    "resultados": data,
                },
            }
        )


class LargePagination(DefaultPagination):
    """Paginacion para listados extensos (por ejemplo, lecturas biometricas)."""

    page_size = 50
    max_page_size = 500
