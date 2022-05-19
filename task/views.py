from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import TaskSerializer, TaskSerializerlist
from .models import Task
from rest_framework.permissions import IsAuthenticated
from datetime import datetime,date

# Create your views here.
class TaskView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def list(self, request, *args, **kwargs):
        if request.user.profile.role == 2:
            queryset = Task.objects.select_related('created_by').filter(created_by=request.user.profile.id)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = TaskSerializerlist(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)    

        if request.user.profile.role == 1:
            queryset = Task.objects.select_related('created_by').filter(assign_to__in=[request.user.profile.id])
            if queryset:
                serializer = TaskSerializerlist(queryset.first())
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'can\'t find your task'},status=status.HTTP_204_NO_CONTENT)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user
        serializer = TaskSerializerlist(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def create(self, request, *args, **kwargs):
        if request.user.profile.role == 2:
            # request.data._mutable = True
            request.data['created_by'] = request.user.profile.id
            # request.data._mutable = False
            serializer = TaskSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user_data = serializer.data
            headers = self.get_success_headers(user_data)            
            return Response(user_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'message':'Only supervisior have permission to add task'}, status=status.HTTP_401_UNAUTHORIZED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        if request.data.get('action') == 'edit':
            if request.user.profile.role == 2:
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                if getattr(instance, '_prefetched_objects_cache', None):
                    instance._prefetched_objects_cache = {}

                return Response(serializer.data)
            else:
                return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)

        elif request.data.get('action') == 'submit':
            if request.user.profile.role == 1 and request.user.profile in instance.assign_to.get_queryset():
                instance.status.append([request.user.fullname(), str(datetime.now())])
                instance.save()
                serializer = TaskSerializerlist(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)

        elif request.data.get('action') == 'add':
            if request.user.profile.role == 2:
                instance.assign_to.add(*request.data.get('intern_list').split(','))
                instance.save()
                serializer = TaskSerializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'message': 'action is not given'},status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if user == instance.user :
            return Response({'message': 'You are not allowed to deleted yourself'},status=status.HTTP_403_FORBIDDEN)
        elif user.is_superuser or user.is_admin:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

