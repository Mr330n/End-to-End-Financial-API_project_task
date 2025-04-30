from rest_framework import generics, filters
from .models import Transaction
from .serializers import TransactionSerializer, UserSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
# Create your views here.

# Endpoint 1: List and create transactions
class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user']
    search_fields = ['description']

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(transaction_date__range=[start_date, end_date])
        return queryset

# Endpoint 2: Retrieve, update, delete transactions
class TransactionRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

# Endpoint 3: List users
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Endpoint 4: List transactions by user
class UserTransactions(generics.ListAPIView):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Transaction.objects.filter(user=user_id)

# Endpoint 5: Generate reports
class ReportView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        period = request.query_params.get('period', 'monthly')
        
        transactions = Transaction.objects.filter(user=user_id)
        if period == 'yearly':
            data = transactions.values('transaction_date__year').annotate(total=Sum('amount'))
        else:
            data = transactions.values('transaction_date__year', 'transaction_date__month').annotate(total=Sum('amount'))
        return Response(data)
