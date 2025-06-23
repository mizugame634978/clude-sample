"""Todoアプリケーションのモデル定義。

このモジュールはTodoアプリケーションのデータモデルを含み、
タスク管理のためのメインTodoモデルを定義します。
"""

from django.db import models
from django.contrib.auth.models import User


class Todo(models.Model):
    """ユーザーのタスクを表すTodoアイテムモデル。
    
    このモデルはユーザーに属する単一のtodoアイテムを表します。
    各todoはタイトル、オプションの説明、完了状態、
    作成・更新のタイムスタンプを持ちます。
    
    Attributes:
        title (CharField): todoアイテムのタイトル（最大200文字）。
        description (TextField): todoの詳細説明（オプション）。
        completed (BooleanField): todoが完了しているかどうか（デフォルト: False）。
        created_at (DateTimeField): todoが作成された日時。
        updated_at (DateTimeField): todoが最後に更新された日時。
        user (ForeignKey): このtodoを所有するユーザーへの参照。
    """
    
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='詳細')
    completed = models.BooleanField(default=False, verbose_name='完了')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')

    class Meta:
        """Todoモデルのメタ設定。"""
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'
        ordering = ['-created_at']

    def __str__(self):
        """Todoの文字列表現を返す。
        
        Returns:
            str: todoアイテムのタイトル。
        """
        return self.title
