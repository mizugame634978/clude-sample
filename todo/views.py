"""Todoアプリケーションのビュー関数。

このモジュールはTodoアプリケーションのビュー関数を含み、
ユーザー認証とTodoのCRUD操作を処理します。
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Todo
from .forms import TodoForm


def login_view(request):
    """ユーザーログイン処理を行うビュー。
    
    GETリクエストの場合はログインフォームを表示し、
    POSTリクエストの場合は認証を行います。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        
    Returns:
        HttpResponse: ログインフォームのレンダリング結果、
                     または成功時はTodo一覧ページへのリダイレクト。
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('todo_list')
        else:
            messages.error(request, 'ユーザー名またはパスワードが正しくありません。')
    return render(request, 'registration/login.html')


def register_view(request):
    """新規ユーザー登録処理を行うビュー。
    
    GETリクエストの場合は登録フォームを表示し、
    POSTリクエストの場合は新しいユーザーを作成します。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        
    Returns:
        HttpResponse: 登録フォームのレンダリング結果、
                     または成功時はログインページへのリダイレクト。
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}さんのアカウントが作成されました。')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """ユーザーログアウト処理を行うビュー。
    
    現在のユーザーをログアウトし、ログインページにリダイレクトします。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        
    Returns:
        HttpResponseRedirect: ログインページへのリダイレクト。
    """
    logout(request)
    return redirect('login')


@login_required
def todo_list(request):
    """ログイン中のユーザーのTodo一覧を表示するビュー。
    
    現在のユーザーに属するすべてのTodoを取得し、
    一覧ページとして表示します。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        
    Returns:
        HttpResponse: Todo一覧ページのレンダリング結果。
    """
    todos = Todo.objects.filter(user=request.user)
    return render(request, 'todo/todo_list.html', {'todos': todos})


@login_required
def todo_create(request):
    """新しいTodoを作成するビュー。
    
    GETリクエストの場合は作成フォームを表示し、
    POSTリクエストの場合は新しいTodoを作成します。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        
    Returns:
        HttpResponse: Todo作成フォームのレンダリング結果、
                     または成功時はTodo一覧ページへのリダイレクト。
    """
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            messages.success(request, 'Todoが作成されました。')
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todo/todo_form.html', {'form': form, 'title': 'Todo作成'})


@login_required
def todo_update(request, pk):
    """既存のTodoを更新するビュー。
    
    指定されたIDのTodoを取得し、編集フォームを表示します。
    現在のユーザーが所有するTodoのみ編集可能です。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        pk (int): 更新するTodoの主キー。
        
    Returns:
        HttpResponse: Todo編集フォームのレンダリング結果、
                     または成功時はTodo一覧ページへのリダイレクト。
                     
    Raises:
        Http404: 指定されたTodoが存在しない、または現在のユーザーが所有していない場合。
    """
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Todoが更新されました。')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todo/todo_form.html', {'form': form, 'title': 'Todo編集'})


@login_required
def todo_delete(request, pk):
    """既存のTodoを削除するビュー。
    
    指定されたIDのTodoを取得し、削除確認ページを表示します。
    現在のユーザーが所有するTodoのみ削除可能です。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        pk (int): 削除するTodoの主キー。
        
    Returns:
        HttpResponse: 削除確認ページのレンダリング結果、
                     または成功時はTodo一覧ページへのリダイレクト。
                     
    Raises:
        Http404: 指定されたTodoが存在しない、または現在のユーザーが所有していない場合。
    """
    todo = get_object_or_404(Todo, pk=pk, user=request.user)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'Todoが削除されました。')
        return redirect('todo_list')
    return render(request, 'todo/todo_confirm_delete.html', {'todo': todo})


@login_required
def todo_toggle(request, pk):
    """Todoの完了状態を切り替えるビュー。
    
    指定されたIDのTodoの完了状態を反転し、
    JSONレスポンスで新しい状態を返します。
    
    Args:
        request (HttpRequest): HTTPリクエストオブジェクト。
        pk (int): 状態を切り替えるTodoの主キー。
        
    Returns:
        JsonResponse: 新しい完了状態を含むJSONレスポンス。
                     例: {'completed': True}
                     
    Raises:
        Http404: 指定されたTodoが存在しない、または現在のユーザーが所有していない場合。
    """
    if request.method == 'POST':
        todo = get_object_or_404(Todo, pk=pk, user=request.user)
        todo.completed = not todo.completed
        todo.save()
        return JsonResponse({'completed': todo.completed})
