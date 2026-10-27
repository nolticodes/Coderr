from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from .serializers import (
    RegistrationPostSerializer,
)


class RegistrationPostView(APIView):
    permission_classes = AllowAny

    def post(self, request):
        serializer = RegistrationPostSerializer(data=request.data)

        data = {}

        if serializer.is_valid():
            new_user = serializer.save()
            token = Token.objects.get(user=new_user)

            data = {
                "token": token.key,
                "username": new_user.username,
                "email": new_user.email,
                "user_id": new_user.id
            }
            return Response(data, status = status.HTTP_201_CREATED)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )