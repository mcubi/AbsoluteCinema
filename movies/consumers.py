import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Review


class ReviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.movie_id = self.scope['url_route']['kwargs']['movie_id']
        self.room_group_name = f'reviews_{self.movie_id}'
        
        # Unirse al grupo de la sala
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Salir del grupo de la sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'add_review':
            await self.add_review(text_data_json)
        elif action == 'get_reviews':
            await self.get_reviews()
    
    async def add_review(self, data):
        user = self.scope['user']
        
        if isinstance(user, AnonymousUser):
            await self.send(text_data=json.dumps({
                'error': 'Debes estar autenticado para enviar una reseña'
            }))
            return
        
        rating = data.get('rating')
        content = data.get('content')
        movie_title = data.get('movie_title', '')
        
        if not rating or not content:
            await self.send(text_data=json.dumps({
                'error': 'La puntuación y el contenido son obligatorios'
            }))
            return
        
        # Guardar la reseña en la base de datos
        review = await self.save_review(user, self.movie_id, movie_title, rating, content)
        
        # Enviar la nueva reseña a todos en el grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'review_message',
                'review': {
                    'id': review.id,
                    'user': user.username,
                    'rating': review.rating,
                    'content': review.content,
                    'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                    'avatar': user.users.avatar.url if hasattr(user, 'users') and user.users.avatar else '/static/img/default-avatar.png'
                }
            }
        )
    
    async def get_reviews(self):
        reviews = await self.load_reviews()
        
        await self.send(text_data=json.dumps({
            'action': 'reviews_list',
            'reviews': reviews
        }))
    
    async def review_message(self, event):
        review = event['review']
        
        # Enviar la reseña al WebSocket
        await self.send(text_data=json.dumps({
            'action': 'new_review',
            'review': review
        }))
    
    @database_sync_to_async
    def save_review(self, user, movie_id, movie_title, rating, content):
        review = Review.objects.create(
            user=user,
            movie_id=movie_id,
            movie_title=movie_title,
            rating=rating,
            content=content
        )
        return review
    
    @database_sync_to_async
    def load_reviews(self):
        reviews = Review.objects.filter(movie_id=self.movie_id).select_related('user')
        return [
            {
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': review.user.users.avatar.url if hasattr(review.user, 'users') and review.user.users.avatar else '/static/img/default-avatar.png'
            }
            for review in reviews
        ]