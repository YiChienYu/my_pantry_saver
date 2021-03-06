from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls.base import is_valid_path, reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from ingredient.models import Ingredient
from .models import UserRecipe, UserIngredient
from recipe.models import RecipeIngredient, Recipe
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, request

# Login page
class UserLoginView(LoginView):
    template_name = 'user/login.html'
    fields = '__all__ '
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('mypantry')

# Register page
class UserRegister(FormView):
    template_name = 'user/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('mypantry')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(UserRegister, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('mypantry')
        return super(UserRegister, self).get(*args, **kwargs)

# User's meal plan page.
class MyPantry(LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/mypantry.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipes'] = UserRecipe.objects.all().filter(user=self.request.user)
        context['ingredients'] = UserIngredient.objects.all().filter(user=self.request.user)
        context['days'] = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        context['meals'] = ["BREAKFAST", "LUNCH", "DINNER"]
        return context

# User adding an ingredient to their pantry.
class UserIngredientCreate(LoginRequiredMixin, CreateView):
    model = UserIngredient
    fields = ['ingredient', 'expiry_date', 'quantity', 'unit']
    template_name = 'user/user_ingredient_form.html'
    success_url = reverse_lazy('pantry')
    context_object_name = 'ingredient_list'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.in_pantry = True
        return super(UserIngredientCreate, self).form_valid(form)

# User updating an ingredient in their pantry.
class UserIngredientUpdate(LoginRequiredMixin, UpdateView):
    model = UserIngredient
    fields = ['ingredient', 'expiry_date', 'quantity', 'unit']
    template_name = 'user/user_ingredient_form.html'
    success_url = reverse_lazy('pantry')

# User deleting an ingredient from their pantry.
class UserIngredientDelete(LoginRequiredMixin, DeleteView):
    model = UserIngredient
    context_object_name = 'ingredient'
    template_name = 'user/user_ingredient_confirm_delete.html'
    success_url = reverse_lazy('pantry')

# User list of ingredients in their pantry.
class Pantry(LoginRequiredMixin, ListView):
    model = UserIngredient
    template_name = 'user/pantry.html'
    context_object_name = 'user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipes'] = UserRecipe.objects.all().filter(user=self.request.user)
        context['ingredients'] = UserIngredient.objects.all().filter(user=self.request.user, in_pantry=True)
        context['fridge'] = UserIngredient.objects.all().filter(user=self.request.user, ingredient__place_in='FRIDGE', in_pantry=True)
        context['pantry'] = UserIngredient.objects.all().filter(user=self.request.user, ingredient__place_in='PANTRY', in_pantry=True)
        context['freezer'] = UserIngredient.objects.all().filter(user=self.request.user, ingredient__place_in='FREEZER', in_pantry=True)
        return context

# User adding a recipe to their meal plan.
class UserRecipeCreate(LoginRequiredMixin, CreateView):
    model = UserRecipe
    fields = ['recipe', 'meal', 'day']
    template_name = 'user/user_recipe_form.html'
    success_url = reverse_lazy('mypantry')
    context_object_name = 'recipe_list'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        a = set(Recipe.objects.all())
        recipe_ingredients = RecipeIngredient.objects.all().filter()
        user_ingredients = UserIngredient.objects.all().filter(user=self.request.user, in_pantry=True)
        u_i = {}
        u_ids = []
        for l in user_ingredients:
            if l.ingredient.id not in u_ids:
                u_ids.append(l.ingredient.id)
                u_i[l.ingredient.id] = [l.quantity, l.unit]
            else:
                u_i[l.ingredient.id][0] += l.quantity
        all_result = []
        recipe_id = []
        added = False
        for item in recipe_ingredients.iterator():
            if item.recipe.id not in recipe_id:
                temp = {'recipe':item.recipe, 'all_ingredient':[], 'missing':[]}
                recipe_id.append(item.recipe.id)
                all_result.append(temp)
            all_result[recipe_id.index(item.recipe.id)]['all_ingredient'].append({"ingredient":item.ingredient, "quantity":item.quantity, "unit":item.unit})
            
        for ingre in all_result:
            for ing in ingre['all_ingredient']:
                for kk in u_i:
                    if kk == ing['ingredient'].id:
                        q = ing['quantity']- u_i[kk][0]
                        if q > 0:
                            ingre['missing'].append({"ingredient":ing['ingredient'], "quantity":abs(ing['quantity']-u_i[kk][0]), "unit":ing['unit']})
                        added = True
                            
                if not added:
                    ingre['missing'].append({"ingredient":ing['ingredient'], "quantity":abs(ing['quantity']), "unit":ing['unit']})
    

                added = False

        context['result'] = all_result
        context['meals'] = ["BREAKFAST", "LUNCH", "DINNER"]
        context['recipes'] = a
        context['recipe_ingredients'] = RecipeIngredient.objects.all().filter()
        return context
        
    def form_valid(self, form):
        form.instance.user = self.request.user
        user_recipe = form.save()
        return super(UserRecipeCreate, self).form_valid(form)

# User viewing a recipe in their meal plan.
class UserRecipeDetail(LoginRequiredMixin, DetailView):
    model = UserRecipe
    context_object_name = 'recipe'
    template_name = 'user/user_recipe_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipe_ingredients'] = RecipeIngredient.objects.all()
        a = set(Recipe.objects.all())
        recipe_ingredients = RecipeIngredient.objects.all().filter()
        user_ingredients = UserIngredient.objects.all().filter(user=self.request.user, in_pantry=True)
        u_i = {}
        u_ids = []

        for l in user_ingredients:
            if l.ingredient.id not in u_ids:
                u_ids.append(l.ingredient.id)
                u_i[l.ingredient.id] = [l.quantity, l.unit]
            else:
                u_i[l.ingredient.id][0] += l.quantity

        all_result = []
        recipe_id = []
        added = False

        for item in recipe_ingredients.iterator():
            if item.recipe.id not in recipe_id:
                temp = {'recipe':item.recipe, 'all_ingredient':[], 'missing':[]}
                recipe_id.append(item.recipe.id)
                all_result.append(temp)
            all_result[recipe_id.index(item.recipe.id)]['all_ingredient'].append({"ingredient":item.ingredient, "quantity":item.quantity, "unit":item.unit})

        for ingre in all_result:
            for ing in ingre['all_ingredient']:
                for kk in u_i:
                    if kk == ing['ingredient'].id:
                        q = ing['quantity']- u_i[kk][0]
                        if q > 0:
                            ingre['missing'].append({"ingredient":ing['ingredient'], "quantity":abs(ing['quantity']-u_i[kk][0]), "unit":ing['unit']})
                        added = True                         
                if not added:

                    ingre['missing'].append({"ingredient":ing['ingredient'], "quantity":abs(ing['quantity']), "unit":ing['unit']})

                added = False

        context['result'] = all_result
        context['meals'] = ["BREAKFAST", "LUNCH", "DINNER"]
        context['recipes'] = a
        context['recipe_ingredients'] = RecipeIngredient.objects.all().filter()
        return context

# User updaing the recipe in their meal plan. 
class UserRecipeUpdate(LoginRequiredMixin, UpdateView):
    model = UserRecipe
    fields = ['meal', 'day']
    template_name = 'user/user_recipe_form.html'
    success_url = reverse_lazy('mypantry')
    
# User deleting a recipe in their meal plan.
class UserRecipeDelete(LoginRequiredMixin, DeleteView):
    model = UserRecipe
    context_object_name = 'recipe'
    template_name = 'user/user_recipe_confirm_delete.html'
    success_url = reverse_lazy('mypantry')

# A list of ingredient the user must purchase to cook a meal.
class ShoppingList(LoginRequiredMixin, ListView):
    model = UserIngredient
    template_name = 'user/shopping_list.html'

    def get_context_data(self, **kwargs):
        global li
        context = super().get_context_data(**kwargs)
        user_i = UserIngredient.objects.all().filter(user=self.request.user, in_pantry=True)
        recipes = UserRecipe.objects.all().filter(user=self.request.user)
        result = []
        id_list = []

        for r in recipes.iterator():
            recipe_ingredient = RecipeIngredient.objects.all().filter(recipe_id=r.recipe.id)
            for i in recipe_ingredient.iterator():
                if len(result) != 0:
                    for ingredient_each in result:
                        if i.ingredient.id == ingredient_each["ingredient"].id:
                            ingredient_each["quantity"] += i.quantity
                        elif i.ingredient.id not in id_list:
                            temp = {'ingredient':i.ingredient, "quantity":i.quantity, 'unit':i.unit}
                            id_list.append(i.ingredient.id)
                            result.append(temp)
                            break               
                else:
                    temp = {'ingredient':recipe_ingredient[0].ingredient, "quantity":recipe_ingredient[0].quantity, 'unit':recipe_ingredient[0].unit}
                    id_list.append(recipe_ingredient[0].ingredient.id)
                    result.append(temp)
        for all in result[:]:
            for user_ingredient in user_i.iterator():
                if all['ingredient'].id == user_ingredient.ingredient.id:
                    temp = all['quantity'] - user_ingredient.quantity
                    if temp <= 0:
                        result.remove(all)
                        break
                    else:
                        result[result.index(all)]['quantity'] = temp

        context['result'] = result 
        return context

# A function to add ingredients from the shopping list to the pantry after purchase.
def shopping_list_item_to_pantry(request, pk):
    ingredient = UserIngredient.objects.get(id=pk)
    ingredient.in_pantry = True
    ingredient.save()

    return HttpResponseRedirect(reverse_lazy('shopping-list'))

# User adding details such as expiry date when they are adding a new ingredient from the shopping list.
class UserIngredientShoppingCreate(LoginRequiredMixin, CreateView):
    model = UserIngredient
    fields = ['expiry_date']
    template_name = 'user/shopping_list_pantry_form.html'
    success_url = reverse_lazy('shopping-list')
    context_object_name = 'ingredient_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredient'] = RecipeIngredient.objects.all().filter(ingredient_id=self.kwargs['ingredientName'])[0].ingredient
        context['quantity'] = self.kwargs['quantity']
        context['unit'] = self.kwargs['unit']
        
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        id = self.request.POST.get('ingredient')
        quantity = self.request.POST.get('quantity')
        unit = self.request.POST.get('unit')
        ingredient = RecipeIngredient.objects.all().filter(ingredient_id=id)[0].ingredient
        form.instance.ingredient = ingredient
        form.instance.quantity = quantity
        form.instance.unit = unit
        form.instance.in_pantry = True
        
        return super(UserIngredientShoppingCreate, self).form_valid(form)

# Function to remove ingredients once the user has finish cooking a meal.
def user_complete_recipe(request, pk):
    user_recipe = UserRecipe.objects.get(id=pk)
    recipe_ingredients = RecipeIngredient.objects.all().filter(recipe_id=user_recipe.recipe.id)
    all =[]
    ids = []
    user_ingredients = UserIngredient.objects.all().filter(user=request.user, in_pantry=True)
    print(user_ingredients)
    u_i = {}
    u_ids = []
    for item in user_ingredients:
        print(item)
        print(UserIngredient.objects.all().filter(ingredient_id=item.ingredient.id).count())
        if item.ingredient.id not in u_ids:
            u_ids.append(item.ingredient.id)
            u_i[item.ingredient.id] = item.quantity
            print('new')
        else:
            u_i[item.ingredient.id] += item.quantity
            print('adding')
                    
    for item in recipe_ingredients:
        temp = {'id':item.ingredient.id, 'quantity':item.quantity}
        if item.ingredient.id not in ids:
            all.append(temp)
            ids.append(item.ingredient.id)
        else:
            for i in all:
                if i['id'] == item.ingredient.id:
                    i['quantity'] += item.quantity
    
    temp1 = []
    temp2 = []
    print(all)
    print(ids)
    print(u_i)
    print(u_ids)

    for id in all:
         for ingredient in user_ingredients.iterator():
            if (ingredient.ingredient.id in temp1) and (ingredient.id not in temp2):
                ingredient.delete()
                continue
            if ingredient.ingredient.id == id['id']:
                q = u_i[ingredient.ingredient.id] - id['quantity']
                if q > 0:
                    temp = UserIngredient(
                user=request.user,
                user_recipe=None,
                ingredient=ingredient.ingredient,
                expiry_date=ingredient.expiry_date,
                quantity=q,
                unit=ingredient.unit,
                in_pantry=True,
            )   
                    if ingredient.ingredient.id not in temp1:
                        temp1.append(ingredient.ingredient.id)
                        temp.save()
                        ingredient.delete()
                        temp2.append(temp.id)
                else:
                    ingredient.delete()
                       
    user_recipe.delete()
    return HttpResponseRedirect(reverse_lazy('mypantry'))

