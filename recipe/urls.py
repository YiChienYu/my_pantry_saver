from django.urls import path
from .views import RecipeList, RecipeDetail, RecipeCreate, RecipeUpdate, RecipeDelete

urlpatterns = [
    path('recepes/', RecipeList.as_view(), name='recipelist'), 
    path('recipe/<int:pk>', RecipeDetail.as_view(), name='recipe'), 
    path('recepe/new', RecipeCreate.as_view(), name='new-recipe'), 
    path('recepe/edit/<int:pk>', RecipeUpdate.as_view(), name='edit-recipe'), 
    path('recepe/delete/<int:pk>', RecipeDelete.as_view(), name='delete-recipe'), 
]