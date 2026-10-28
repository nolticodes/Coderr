from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.contrib.auth import authenticate

from .serializers import (
    RegistrationPostSerializer,
    LoginSerializer
)


class RegistrationPostView(APIView):

    permission_classes = [AllowAny]
    serializer_class = RegistrationPostSerializer

    def post(request, self):
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

            return Response(
                data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginPostView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                token, created = Token.objects.get_or_create(user=user)

                return Response(
                    {
                        "token": token.key,
                        "username": user.username,
                        "email": user.email,
                        "user_id": user.id,
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {
                    "detail": "Ungültige Anmeldedaten."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
