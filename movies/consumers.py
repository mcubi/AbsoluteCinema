import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Review


class ReviewConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.movie_id = int(self.scope['url_route']['kwargs']['movie_id'])
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
        parent_id = data.get('parent_id')
        
        if not rating or not content:
            await self.send(text_data=json.dumps({
                'error': 'La puntuación y el contenido son obligatorios'
            }))
            return
        
        # Guardar la reseña en la base de datos
        review = await self.save_review(user, self.movie_id, movie_title, rating, content, parent_id)
        
        # Obtener la URL del avatar correctamente
        avatar_url = await self.get_avatar_url(user)
        
        # Enviar la nueva reseña a todos en el grupo
        review_data = {
            'id': review.id,
            'user': user.username,
            'rating': review.rating,
            'content': review.content,
            'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
            'avatar': avatar_url
        }
        
        if parent_id:
            review_data['parent_id'] = parent_id
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'review_message',
                'review': review_data
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
    def get_avatar_url(self, user):
        try:
            if hasattr(user, 'perfil') and user.perfil.avatar:
                return user.perfil.avatar.url
        except Exception:
            pass
        return None
    
    @database_sync_to_async
    def save_review(self, user, movie_id, movie_title, rating, content, parent_id=None):
        parent_review = None
        if parent_id:
            try:
                parent_review = Review.objects.get(id=parent_id, movie_id=movie_id)
            except Review.DoesNotExist:
                pass
        
        review = Review.objects.create(
            user=user,
            movie_id=movie_id,
            movie_title=movie_title,
            rating=rating,
            content=content,
            parent=parent_review
        )
        return review
    
    @database_sync_to_async
    def load_reviews(self):
        # Get only top-level reviews (no parent)
        reviews = Review.objects.filter(movie_id=self.movie_id, parent=None).select_related('user')
        
        reviews_data = []
        for review in reviews:
            # get the url of the avatar
            avatar_url = None
            try:
                if hasattr(review.user, 'perfil') and review.user.perfil.avatar:
                    avatar_url = review.user.perfil.avatar.url
            except Exception:
                pass
            
            # Get replies for this review
            replies = Review.objects.filter(parent=review).select_related('user').order_by('created_at')
            replies_data = []
            for reply in replies:
                reply_avatar_url = None
                try:
                    if hasattr(reply.user, 'perfil') and reply.user.perfil.avatar:
                        reply_avatar_url = reply.user.perfil.avatar.url
                except Exception:
                    pass
                
                replies_data.append({
                    'id': reply.id,
                    'user': reply.user.username,
                    'rating': reply.rating,
                    'content': reply.content,
                    'created_at': reply.created_at.strftime('%d/%m/%Y %H:%M'),
                    'avatar': reply_avatar_url,
                    'parent_id': review.id
                })
            
            reviews_data.append({
                'id': review.id,
                'user': review.user.username,
                'rating': review.rating,
                'content': review.content,
                'created_at': review.created_at.strftime('%d/%m/%Y %H:%M'),
                'avatar': avatar_url,
                'replies': replies_data,
                'reply_count': len(replies_data)
            })
        
        return reviews_data