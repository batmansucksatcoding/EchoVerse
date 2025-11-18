from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Journal Entries
    path('entries/', views.entry_list_view, name='entry_list'),
    path('entries/new/', views.entry_create_view, name='entry_create'),
    path('entries/<int:pk>/', views.entry_detail_view, name='entry_detail'),
    path('entries/<int:pk>/edit/', views.entry_update_view, name='entry_update'),
    path('entries/<int:pk>/delete/', views.entry_delete_view, name='entry_delete'),
    
    # Visualizations
    path('visualizations/', views.visualizations_view, name='visualizations'),
    path('visualizations/generate/', views.generate_visualization_view, name='generate_visualization'),
    
    # AI Insights
    path('insights/', views.insights_view, name='insights'),
    path('insights/generate/', views.generate_insight_view, name='generate_insight'),
    path('insights/<int:pk>/', views.insight_detail_view, name='insight_detail'),
    
    # Profile
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('blob-evolution/', views.blob_evolution_view, name='blob_evolution'),
    path('visuals/emotion-cards/', views.emotion_cards_view, name='emotion_cards'),
    path('visualizations/delete/<int:viz_id>/', views.delete_visualization_view, name='delete_visualization'),
    path('blob-evolution/', views.blob_evolution_view, name='blob_evolution'),



    

]
