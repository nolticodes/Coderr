from rest_framework.pagination import PageNumberPagination


class OffersPagination(PageNumberPagination):
    """Paginate offers with 6 items by default and a configurable maximum of 100."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
