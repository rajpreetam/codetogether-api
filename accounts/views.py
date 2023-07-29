from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer


class GetAuthenticatedUser(APIView):
    def get(self, request):
        user = self.request.user
        print(user)
        serializer = UserSerializer(user, many=False)
        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'data': serializer.data,
            'message': 'User retrieved successfully'
        }, status=status.HTTP_200_OK)
