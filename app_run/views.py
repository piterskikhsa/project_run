from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def company_details(request):
    company_info = {
        "company_name": "Бегуны",
        "slogan": "Беги за своими мечами",
        "contacts": "г. Сыктывкар ул. Пушкина 1",
    }
    return Response(company_info)