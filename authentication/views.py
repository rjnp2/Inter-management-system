from rest_framework import viewsets
from .models import Profile
from .serializers import UserSerializer,UserCreate,ProfileSerializer,ProfileSerializerCreate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db import connection
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreate
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.is_superuser:
            return Response({'message':'Please fill form'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message':'Only admin and superuser have permission to add user'}, status=status.HTTP_401_UNAUTHORIZED) 

    def create(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.is_superuser:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['password'] = make_password((serializer.validated_data['password']))
            serializer.save()

            user_data = serializer.data
            headers = self.get_success_headers(user_data)            
            return Response(user_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'message':'Only admin and superuser have permission to add user'}, status=status.HTTP_401_UNAUTHORIZED)

class UserView(viewsets.ModelViewSet):    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'put', 'patch', 'delete', 'head', 'options', 'trace']	

    def list(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True).data
                # print('len',len(connection.queries))
                return self.get_paginated_response(serializer)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not allowed to view'},status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = self.request.user

        if user.is_admin or user.is_superuser:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if user == instance:
            return Response({'message': 'You are not allowed to deleted yourself'},status=status.HTTP_403_FORBIDDEN)
        elif user.is_admin and instance.is_admin and not user.is_superuser:
            return Response({'message': 'Admin is not allowed to deleted Admin'})
        elif user.is_superuser:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class ProfileView(viewsets.ModelViewSet):    
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )

    def list(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.is_superuser:
            queryset = self.filter_queryset(self.get_queryset())

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)        
        else:
            queryset = Profile.objects.filter(user=request.user)
            if queryset:
                serializer = ProfileSerializer(queryset.first())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'can\'t find your profile'},status=status.HTTP_204_NO_CONTENT)
    
    def create(self, request, *args, **kwargs):
        if request.user.is_admin or request.user.is_superuser:
            serializer = ProfileSerializerCreate(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user_data = serializer.data
            headers = self.get_success_headers(user_data)            
            return Response(user_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'message':'Only admin and superuser have permission to add user'}, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        user = self.request.user

        if user == instance.user or user.is_superuser or request.user.is_admin:
            serializer = ProfileSerializerCreate(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if user == instance.user :
            return Response({'message': 'You are not allowed to deleted yourself'},status=status.HTTP_403_FORBIDDEN)
        elif user.is_superuser or user.is_admin:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    http_method_names = ['get', 'post']

    def get(self, request):
        return Response(
            {'message': 'Enter credentials to login'},
            status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        final_data = {}
        final_data['jwt_token'] = data
        user = serializer.user
        final_data['permissions'] = user.get_all_permissions()
        final_data['user'] = UserSerializer(user).data

        response = Response(final_data, status=status.HTTP_200_OK)
        response.set_cookie('token', serializer.validated_data['access'])
        # print('len',len(connection.queries)
        return response

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(
            {'message': 'Enter refresh to logout'},
            status=status.HTTP_200_OK)

    def post(self, request):
        if request.data.get("refresh_token"):
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':'sucessfully logout'},status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response({'message':'please provide refresh_token'},status=status.HTTP_400_BAD_REQUEST)

