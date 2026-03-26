from django.contrib import admin
from .models import Quiz, Question, Answer

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'author', 'created_at') 
    search_fields = ('topic', 'author__username')
    list_filter = ('created_at', 'author')

admin.site.register(Question)
admin.site.register(Answer)