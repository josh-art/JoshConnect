from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Contacts, Gallary
from django.views import View
from .models import Post, Like, Comment, Favourites, Notification, Advert
from django.shortcuts import render, get_object_or_404
from .models import File
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.messages.views import SuccessMessageMixin
from .forms import NewCommentForm
from django.urls import reverse_lazy
from django.contrib import messages, auth
from .forms import UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as dj_login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .models import Message
from django.http.response import JsonResponse, HttpResponse


# Create your views here.
def signup(request):
    return render(request, "register.html")


# view for rendering login page
def login(request):
    return render(request, "login.html")


def handlesignup(request):
    if request.method == 'POST':
        # get the post parameters
        username = request.POST["uname"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        # check for errors in input
        if request.method == 'POST':
            try:
                user_exists = User.objects.get(username=request.POST['uname'])
                messages.error(
                    request, " Username already taken, Try another username!!!")
                return redirect("/signup")
            except User.DoesNotExist:
                if len(username) > 15:
                    messages.error(
                        request, " Username must be max 15 characters, Please try again")
                    return redirect("/signup")
                if not username.isalnum():
                    messages.error(
                        request, " Username should only contain letters and numbers, Please try again")
                    return redirect("/signup")
                if password1 != password2:
                    messages.error(
                        request, " Password do not match, Please try again")
                    return redirect("/signup")
        # create the user
        user = User.objects.create_user(username, email, password1)
        user.first_name = fname
        user.last_name = lname
        user.phone = phone
        user.save()
        messages.success(
            request, " Your account has been successfully created<br>Please login below")
        return redirect("login")
    else:
        return HttpResponse('404 - NOT FOUND ')


# view for rendering data from login page
def handlelogin(request):
    if request.method == 'POST':
        # get the post parameters
        name = request.POST["uname"]
        password = request.POST["password1"]
        user = authenticate(username=name, password=password)
        # cheching for valid login
        if user is not None:
            dj_login(request, user)
            messages.success(request, "You have Successfully logged in to your account")
            return redirect("home")
        else:
            messages.error(request, " Invalid Credentials, Please try again")
            return redirect("home")
    return HttpResponse('404 - NOT FOUND ')


# view for rendering logout
def handlelogout(request):
    logout(request)
    messages.success(request, " Successfully logged out")
    return redirect('/')


def index(request):
    context = {
        'all_files': File.objects.all(),

    }
    return render(request, 'post_form.html', context)


def upload(request):
    uploaded_file = request.FILES
    new_upload = File.objects.create(
        file_name=request.POST['file_name'],
        image=uploaded_file['image']
    )
    return redirect('/')


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'chat/post_delete.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author


class PostEditView(UpdateView):
    model = Post
    fields = ['body']
    template_name = 'chat/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post_detail', kwargs={'pk': pk})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'post_form.html'
    fields = ['body', 'caption']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['body', 'caption']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False




############################
# for post update

def post_update(request):
    return render(request, 'post_update.html')


class PostDeleteview(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'
    template_name = 'comment_delete.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class UserPostListView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-created_date')


def index1(request):
    gallary = Gallary.objects.all().filter(created_date__lte=timezone.now()).order_by('-created_date')
    posts = Post.objects.all().filter(created_date__lte=timezone.now()).order_by('-created_date')
    user = request.user
    context = {
        'gallary' : gallary,
        'posts': posts,
        'user': user,
    }
    return render(request, 'cityblogs/home.html', context)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Comment
    template_name = 'comment_update.html'
    fields = ['content']
    success_url = '/index'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False

    def get_success_message(self, cleaned_data):
        return 'Updated successfully'


###########################
# comment delete

def delete(request, id):
    comment = Comment.objects.get(id=id).delete()
    messages.info(request, 'comment deleted')
    return redirect('/index')


#########################
# User Favourite posts

def favourite(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_post = Post.objects.get(id=post_id)

        if user in post_post.favourite.all():
            post_post.favourite.remove(user)
        else:
            post_post.favourite.add(user)
        Fav, created = Favourites.objects.get_or_create(user=user, post_id=post_id)
        if not created:
            if Fav.value == 'Save':
                Fav.value = 'Saved'
            else:
                Fav.value = 'Save'
        Fav.save()
    return redirect('index')


def favourite_posts(request):
    user = request.user
    num_count = user.favourite.filter().count()
    favourite_posts = user.favourite.all()
    context = {
        'favourite_posts': favourite_posts,
        'num_count': num_count
    }

    return render(request, 'favourite_posts.html', context)


def home(request):
    gallary = Gallary.objects.all().filter(created_date__lte=timezone.now()).order_by('-created_date')
    posts = Post.objects.all().filter(created_date__lte=timezone.now()).order_by('-created_date')
    user = request.user
    context = {
        'gallary':gallary,
        'posts': posts,
        'user': user,

    }
    return render(request, 'index.html', context)


def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index1')
        else:
            messages.info(request, "invalid username or password")
            return redirect('login')
    else:
        return render(request, 'login.html')


def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: " + request.user.email + " User Type: " + request.user.user_type)
    else:
        return HttpResponse("Please Login First")


def testimonial(request):
    user = request.user
    posts = Post.objects.filter(author=request.user).order_by('-created_date')
    return render(request, 'department/testimonial.html', {'posts': posts, 'user': user})


def contactForm(request):
    if request.method == "GET":
        return render(request, 'cityblogs/contactpage.html')
    elif request.method == "POST":
        try:
            name = request.POST['name']
            email = request.POST['email']
            mobile = request.POST['mobile']
            message = request.POST['message']
            contact = Contacts(user_name=name, email=email, mobile_number=mobile, message=message)
            contact.save()
            print("name = " + name)
            return render(request, 'cityblogs/contactpage.html', {'success': True})
        except Exception as e:
            print("error in request")
            return render(request, 'cityblogs/contactpage.html', {'success': False})


def profile(request):
    return render(request, 'profile.html')


def profile_posts(request):
    user = request.user
    posts = Post.objects.filter(author=request.user).order_by('-created_date')
    return render(request, 'profile_posts.html', {'posts': posts, 'user': user})


@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'profile details updated successfully')
            return render(request, 'profile.html')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'profile_update.html', context)


def like_post(request):
    user = request.user
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        post_post = Post.objects.get(id=post_id)

        if user in post_post.liked.all():
            post_post.liked.remove(user)
        else:
            post_post.liked.add(user)
        like, created = Like.objects.get_or_create(user=user, post_id=post_id)
        if not created:
            if like.value == 'Like':
                like.value = 'Unlike'
            else:
                like.value = 'Like'
        like.save()
        if not Like:
            post_post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user,
                                                       to_user=post_post.author, post_post=post_post)
    return redirect('index')


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def view(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)

class GallaryDetailView(DetailView):
    model = Gallary
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def view(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)

def advert(request):
    return render(request, 'Advert.html')


def AdvertForm(request):
    if request.method == "GET":
        return render(request, 'requests.html')
    elif request.method == "POST":
        try:
            name = request.POST['name1']
            email = request.POST['email1']
            mobile = request.POST['mobile1']
            message = request.POST['message1']
            picture = request.POST['picture']
            advertisement = Advert(user_name=name, email=email, mobile_number=mobile, message=message, picture=picture)
            advertisement.save()
            print("name = " + name)
            return render(request, 'requests.html', {'success': True})
        except Exception as e:
            print("error in request")
            return render(request, 'requests.html', {'success': False})



class PostDeleteview(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/index'
    template_name = 'comment_delete.html'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def owino(request):
    return render(request, 'owino.html')

def owino1(request):
    return render(request, 'owino1.html')

# Create your views here.
