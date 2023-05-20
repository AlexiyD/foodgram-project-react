from rest_framework.pagination import PageNumberPagination


class LimitPagination(PageNumberPagination):
    page_query_param = 'limit'
