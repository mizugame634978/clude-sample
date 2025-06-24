"""Todoアプリケーションのフォーム定義。

このモジュールはTodoアプリケーションで使用するフォームクラスを含み、
Todo作成・編集のためのフォーム処理を定義します。
"""

from __future__ import annotations
from django import forms
from .models import Todo


class TodoForm(forms.ModelForm):
    """Todo作成・編集用のModelFormクラス。
    
    Todoモデルに基づいてフォームを生成し、タイトルと詳細の
    入力フィールドを提供します。Bootstrap用のCSSクラスと
    プレースホルダーが設定されています。
    
    Attributes:
        Meta: フォームの設定を定義するメタクラス。
    """
    
    class Meta:
        """TodoFormのメタ設定。
        
        Attributes:
            model: フォームのベースとなるTodoモデル。
            fields: フォームに含めるフィールドのリスト。
            widgets: 各フィールドのウィジェット設定。
        """
        model = Todo
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'タイトルを入力してください'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': '詳細を入力してください（任意）'
            }),
        }