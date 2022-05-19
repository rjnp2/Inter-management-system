from rest_framework import viewsets
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceSerializerCreate
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from datetime import datetime,date

# Create your views here.
class AttendanceView(viewsets.ModelViewSet):    
    queryset = Attendance.objects.select_related('user').all()
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post','put', 'patch', 'head', 'options', 'trace']

    def get_serializer_class(self, *args, **kwargs):
        if self.request.method == 'POST':
            return AttendanceSerializerCreate
        return AttendanceSerializer

    def list(self, request, *args, **kwargs):

        if request.query_params.get('histroy'):
            if request.user.is_admin or request.user.is_superuser:
                queryset = self.filter_queryset(self.get_queryset())

                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                queryset = Attendance.objects.select_related('user').filter(user=request.user)
                if queryset:
                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'can\'t find your Attendance profile'},status=status.HTTP_204_NO_CONTENT)
        else:
            if request.user.is_admin or request.user.is_superuser:
                queryset = Attendance.objects.select_related('user').filter(date_time=date.today())

                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                queryset = Attendance.objects.select_related('user').filter(user=request.user,date_time=date.today())
                if queryset:
                    serializer = self.get_serializer(queryset, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'can\'t find your Attendance profile'},status=status.HTTP_204_NO_CONTENT)


    def create(self, request, *args, **kwargs):
        
        if request.user.profile.role == 1:
            request.data['user'] = request.user.id

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            user_data = serializer.data
            headers = self.get_success_headers(user_data)            
            return Response(user_data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response({'message': 'only interns can take attendance'},status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if user == instance.user:
            if request.data.get('action') == 'leave':
                if instance.status == "present" and not instance.leave_time:
                    instance.leave_time =  datetime.now()
                    instance.save()
                else:
                    return Response({'message': 'You have already set leave time'},status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'message': 'No action is given'},status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(instance)
            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'You are not allowed to update'},status=status.HTTP_403_FORBIDDEN)

