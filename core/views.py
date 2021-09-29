from django.contrib import messages 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin                   
from django.shortcuts import render, get_object_or_404, redirect                      
from django.views.generic import ListView, DetailView, View                      
from django.utils import timezone    
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from .models import (                           
    Item,
    Order,
    OrderItem,
    CheckoutAddress
)
from . import forms
# Create your views here.
def sign_up(request):
    form=forms.SignUpForm()
    if request.method =='POST':
        form=forms.SignUpForm(request.POST)
        if form.is_valid():
            email=form.cleaned_data.get('email').lower()
            user=form.save(commit=False)
            user.username=email
            user.save()

                    
            login(request,user,backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
    return render(request,'sign_up.html',{
        'form':form
    })
def home(request) :
    return render(request, 'home.html')
class HomeView(ListView):
    model = Item
    template_name = "home.html"
class ProductView(DetailView):
    model = Item
    template_name = "product.html"
@login_required
def add_to_cart(request, pk) :
    item = get_object_or_404(Item, pk = pk )
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    if order_qs.exists() :
        order = order_qs[0]
        
        if order.items.filter(item__pk = item.pk).exists() :
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Added quantity Item")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "Item added to your cart")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item added to your cart")
        return redirect("core:order-summary")
@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.info(request, "Item \""+order_item.item.item_name+"\" remove from your cart")
            return redirect("core:product")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("core:product", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("core:order-summary", pk = pk)
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object' : order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")
@login_required
def reduce_quantity_item(request, pk):
    item = get_object_or_404(Item, pk=pk )
    order_qs = Order.objects.filter(
        user = request.user, 
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists() :
            order_item = OrderItem.objects.filter(
                item = item,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            messages.info(request, "Item quantity was updated")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("core:order-summary")
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("core:order-summary")
def profile_page(request):
    user_form=forms.BasicUserForm(instance=request.user)
    password_form=PasswordChangeForm(request.user)
    if request.method=="POST":
        if request.POST.get('action') =='update_profile':
            user_form=forms.BasicUserForm(request.POST,instance=request.user)
            if user_form.is_valid() :
                user_form.save()
                messages.success(request,'Your profile has been updated')
                return redirect(reverse('core:profile'))
        elif request.POST.get('action') =='update_password':
            password_form=PasswordChangeForm(request.user,request.POST)
            if password_form.is_valid():
                user=password_form.save()
                update_session_auth_hash(request,user)
                messages.success(request,'Your password has been updated')
                return redirect(reverse('core:profile'))

    return render(request,'profile.html',{
        "user_form":user_form,
        "password_form":password_form,
    })
class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = forms.CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = forms.CheckoutForm(self.request.POST or None)
        
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print('hello')
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                checkout_address = CheckoutAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                print('hi')
                checkout_address.save()
                order.ordered=True
                order.checkout_address = checkout_address
                order.save()
                return redirect('/')
            messages.warning(self.request, "Failed Chekout")
            return redirect('/')

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an order")
            return redirect("/")
def OrderSummaryVieww(request):
    order = Order.objects.filter(user=request.user, ordered=True)
    print(order)
    return render(request, 'order_summary_post.html', {"order":order})
def t_home(request) :
    return render(request, 't_base.html')
