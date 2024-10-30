# urls.py
from django.urls import path
from .views import OrderCreateView, OrderItemDeleteView, OrderItemUpdateView, OrderListRetrieveDeleteView, OrderListRetrieveView, OrderUpdateView

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order-create'),
    path('edit/<int:pk>/', OrderUpdateView.as_view(), name='order-edit'),
    path('edit/<int:order_id>/items/<int:item_id>/', OrderItemUpdateView.as_view(), name='order-item-update'),  # Edit an order item
    path('', OrderListRetrieveView.as_view(), name='order-list'),         # To get all orders
    path('<int:order_id>/', OrderListRetrieveView.as_view(), name='order-detail'),  # To get a specific order
    path('delete/<int:order_id>/', OrderListRetrieveDeleteView.as_view(), name='order-detail'),  # To get a specific order
    path('delete/<int:order_id>/items/<int:item_id>/', OrderItemDeleteView.as_view(), name='order-item-delete'),  # To delete an order item
]
