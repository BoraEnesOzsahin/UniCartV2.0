from django.urls import path

from . import views


urlpatterns = [
    path('', views.inbox, name='chat_inbox'),
    path('start/<int:listing_id>/', views.start_conversation, name='chat_start'),
    path('<int:conversation_id>/', views.conversation_detail, name='chat_detail'),
    path('<int:conversation_id>/hide/', views.hide_conversation, name='chat_hide'),
    path('<int:conversation_id>/block/', views.block_conversation, name='chat_block'),
    path('<int:conversation_id>/unblock/', views.unblock_conversation, name='chat_unblock'),
    path('<int:conversation_id>/report/', views.report_conversation, name='chat_report'),
    path('<int:conversation_id>/upload-image/', views.upload_image, name='chat_upload_image'),
]
