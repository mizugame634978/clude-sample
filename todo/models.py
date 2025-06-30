"""Todoアプリケーションのモデル定義。

このモジュールはTodoアプリケーションのデータモデルを含み、
タスク管理のためのメインTodoモデルを定義します。
"""

from __future__ import annotations
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta


class Todo(models.Model):
    """ユーザーのタスクを表すTodoアイテムモデル。
    
    このモデルはユーザーに属する単一のtodoアイテムを表します。
    各todoはタイトル、オプションの説明、完了状態、
    作成・更新のタイムスタンプを持ちます。
    
    Attributes:
        title: todoアイテムのタイトル（最大200文字）。
        description: todoの詳細説明（オプション）。
        completed: todoが完了しているかどうか（デフォルト: False）。
        due_date: todoの期限日時（オプション）。
        created_at: todoが作成された日時。
        updated_at: todoが最後に更新された日時。
        user: このtodoを所有するユーザーへの参照。
    """
    
    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(blank=True, verbose_name='詳細')
    completed = models.BooleanField(default=False, verbose_name='完了')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='期限日時')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ユーザー')

    class Meta:
        """Todoモデルのメタ設定。"""
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'
        ordering = ['-created_at']

    def __str__(self) -> str:
        """Todoの文字列表現を返す。
        
        Returns:
            todoアイテムのタイトル。
        """
        return self.title
    
    def clean(self) -> None:
        """モデルのバリデーションを実行。
        
        期限日が過去の日付でないことを確認します。
        
        Raises:
            ValidationError: 期限日が過去の日付の場合。
        """
        super().clean()
        if self.due_date is not None:
            now = timezone.now()
            # 秒単位での比較ではなく、現在時刻より前の場合のみエラー
            if self.due_date < now.replace(second=0, microsecond=0):
                raise ValidationError({'due_date': '期限日は過去の日付にできません。'})
    
    def is_overdue(self) -> bool:
        """期限切れかどうかを判定。
        
        Returns:
            期限切れの場合True、そうでなければFalse。
        """
        if self.due_date is None:
            return False
        return timezone.now() > self.due_date
    
    def is_due_soon(self) -> bool:
        """期限間近かどうかを判定（3日以内）。
        
        Returns:
            期限まで3日以内の場合True、そうでなければFalse。
        """
        if self.due_date is None:
            return False
        return timezone.now() <= self.due_date <= timezone.now() + timedelta(days=3)
    
    def is_due_today(self) -> bool:
        """今日期限かどうかを判定。
        
        Returns:
            今日期限の場合True、そうでなければFalse。
        """
        if self.due_date is None:
            return False
        today = timezone.now().date()
        return self.due_date.date() == today
    
    def get_due_status(self) -> str:
        """期限ステータスを取得。
        
        Returns:
            期限ステータス文字列：
            - 'overdue': 期限切れ
            - 'due_today': 今日期限
            - 'due_soon': 期限間近（3日以内）
            - 'normal': 通常
            - 'no_due_date': 期限日なし
        """
        if self.due_date is None:
            return 'no_due_date'
        
        if self.is_overdue():
            return 'overdue'
        elif self.is_due_today():
            return 'due_today'
        elif self.is_due_soon():
            return 'due_soon'
        else:
            return 'normal'
