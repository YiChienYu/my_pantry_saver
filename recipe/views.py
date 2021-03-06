from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from ingredient.models import Ingredient
from .models import Recipe, RecipeIngredient
from django.forms.models import model_to_dict
from django.contrib.auth.mixins import LoginRequiredMixin

# A complete list of all recipes.
class RecipeList(ListView):
    model = Recipe
    context_object_name = 'recipes'

# Details of a recipe.
class RecipeDetail(DetailView):
    model = Recipe
    context_object_name = 'recipe'
    template_name = 'recipe/recipe_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_ingredients'] = RecipeIngredient.objects.all().filter(recipe=context['recipe'])
        return context

# Creating a recipe
class RecipeCreate(CreateView):
    model = Recipe
    fields = 'name', 'instructions', 'meal', 'time'
    success_url = reverse_lazy('recipelist')

# Updating a recipe
class RecipeUpdate(UpdateView):
    model = Recipe
    fields = 'name', 'instructions', 'meal', 'time'
    success_url = reverse_lazy('recipelist')

# Deleting a recipe
class RecipeDelete(DeleteView):
    model = Recipe
    context_object_name = 'recipe'
    success_url = reverse_lazy('recipelist')

# Attaching ingredients to a recipe.
class RecipeIngredientCreate(CreateView):
    model = RecipeIngredient
    fields = 'ingredient', 'quantity', 'unit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['parent_recipe'] = Recipe.objects.get(id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        form.instance.recipe = Recipe.objects.get(id=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('recipe', kwargs={'pk': self.kwargs['pk']})

# Update the list of ingredients in a recipe.
class RecipeIngredientUpdate(UpdateView):
    model = RecipeIngredient
    fields = 'quantity', 'unit'

    def get_object(self, *args, **kwargs):
        return RecipeIngredient.objects.get(id=self.kwargs['RecipeIngredient_pk'])

    def get_success_url(self):
        return reverse_lazy('recipe', kwargs={'pk': self.kwargs['pk']})

# Deleting an ingredient from a recipe.
class RecipeIngredientDelete(DeleteView):
    model = RecipeIngredient

    def get_object(self, *args, **kwargs):
        return RecipeIngredient.objects.get(id=self.kwargs['RecipeIngredient_pk'])

    def get_success_url(self):
        return reverse_lazy('recipe', kwargs={'pk': self.kwargs['pk']})
