from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import (Model, TextField, DateTimeField, ForeignKey,
                              CASCADE)
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


from PIL import Image


class Profile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(default=0)
    phone = models.CharField(max_length=14)
    cover_photos = models.ImageField(default='cover3.jpeg', upload_to='cover_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(username=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class Notification(models.Model):
    # 1 = Like, 2 = Comment, 3 = Follow
    notification_type = models.IntegerField(null=True, blank=True)
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user_has_seen = models.BooleanField(default=False)


class Advert(models.Model):
    user_name = models.CharField(max_length=200, blank=False)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(max_length=300)
    picture = models.FileField(upload_to='adverts')
    submitted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('submitted_date',)

    def __str__(self):
        return self.user_name

    pass


class Contacts(models.Model):
    user_name = models.CharField(max_length=200, blank=False)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField(max_length=300)
    submitted_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('submitted_date',)

    def __str__(self):
        return self.user_name

    pass


class File(models.Model):
    file_name = models.CharField(max_length=20)
    image = models.ImageField(upload_to='media/')


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='author')
    liked = models.ManyToManyField(User, default=None, blank=True, related_name='liked')
    image = models.ImageField(blank=True, null=False, upload_to='post_pics')
    body = models.TextField()
    caption = models.CharField(max_length=500)
    created_date = models.DateTimeField(default=timezone.now)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)
    video = models.FileField(upload_to='video_posts', null=True, blank=True)

    def __str__(self):
        return self.caption

    @property
    def num_favourites(self):
        return self.favourite.all().count()

    @property
    def num_likes(self):
        return self.liked.all().count()

    @property
    def number_of_comments(self):
        return Comment.objects.filter(post_connected=self).count()

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})
#############################################
LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')

)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, default='Like', max_length=10)

    def __str__(self):
        return str(self.post)


class Comment(models.Model):
    content = models.TextField(max_length=150)
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_connected = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_updated = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})


FAV_CHOICES = (
    ('Save', 'Save'),
    ('Saved', 'Saved')
)


class Favourites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=FAV_CHOICES, default='Save', max_length=10)

    def __str__(self):
        return str(self.post)


class Gallary(models.Model):
    image = models.ImageField(blank=True, null=False, upload_to='gallary')
    title = models.CharField(max_length=500)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class MessageModel(Model):
        """
        This class represents a chat message. It has a owner (user), timestamp and
        the message body.

        """
        user = ForeignKey(User, on_delete=CASCADE, verbose_name='user',
                          related_name='from_user', db_index=True)
        recipient = ForeignKey(User, on_delete=CASCADE, verbose_name='recipient',
                               related_name='to_user', db_index=True)
        timestamp = DateTimeField('timestamp', auto_now_add=True, editable=False,
                                  db_index=True)
        body = TextField('body')

        def __str__(self):
            return str(self.id)

        def characters(self):
            """
            Toy function to count body characters.
            :return: body's char number
            """
            return len(self.body)

        def notify_ws_clients(self):
            """
            Inform client there is a new message.
            """
            notification = {
                'type': 'recieve_group_message',
                'message': '{}'.format(self.id)
            }

            channel_layer = get_channel_layer()
            print("user.id {}".format(self.user.id))
            print("user.id {}".format(self.recipient.id))

            async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
            async_to_sync(channel_layer.group_send)("{}".format(self.recipient.id), notification)

        def save(self, *args, **kwargs):
            """
            Trims white spaces, saves the message and notifies the recipient via WS
            if the message is new.
            """
            new = self.id
            self.body = self.body.strip()  # Trimming whitespaces from the body
            super(MessageModel, self).save(*args, **kwargs)
            if new is None:
                self.notify_ws_clients()

        # Meta
        class Meta:
            app_label = 'Joshu'
            verbose_name = 'message'
            verbose_name_plural = 'messages'
            ordering = ('-timestamp',)

        class Meta:
         ordering = ('timestamp',)
