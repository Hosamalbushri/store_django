from rest_framework import generics
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny ,IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Address
from .serializers import AddressSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To bypass CSRF check for API requests

   
    


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    
    
    
class AddressViewSet(viewsets.ModelViewSet):  # ModelViewSet includes 'create' by default
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]  # Ensures user is authenticated
    
    def post(self, request):
          # Restrict addresses to those associated with the authenticated customer
        return self.queryset.filter(customer=self.request.user.customer)

    def get_queryset(self):
        pass
      