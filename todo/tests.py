"""Todoアプリケーションのテストケース。

このモジュールはTodoアプリケーションの機能をテストするテストケースを含み、
ユーザー認証とTodoのCRUD操作のテストを実行します。
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
from django.test import override_settings
from django.middleware.csrf import get_token
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
from datetime import datetime, timedelta
from .models import Todo


class AuthenticationTestCase(TestCase):
    """ユーザー認証機能のテストケース。
    
    ログイン、ログアウト、新規登録機能のテストを行います。
    また、認証が必要なビューへのアクセス制御もテストします。
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ログイン')

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('todo_list'))

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ユーザー名またはパスワードが正しくありません')

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新規登録')

    def test_register_view_post_valid_data(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_view_post_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'different123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    def test_authentication_required_for_todo_views(self):
        response = self.client.get(reverse('todo_list'))
        self.assertRedirects(response, '/login/?next=/')

        response = self.client.get(reverse('todo_create'))
        self.assertRedirects(response, '/login/?next=/create/')


class TodoCRUDTestCase(TestCase):
    """TodoのCRUD操作機能のテストケース。
    
    Todo作成、読み取り、更新、削除機能のテストを行います。
    また、ユーザー権限に基づくアクセス制御もテストします。
    """
    
    def setUp(self):
        """テスト用の初期データを設定。
        
        複数のユーザーとTodoアイテムを作成し、
        権限制御のテストに使用します。
        """
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        self.todo1 = Todo.objects.create(
            title='Todo 1',
            description='Description 1',
            user=self.user1
        )
        self.todo2 = Todo.objects.create(
            title='Todo 2',
            description='Description 2',
            user=self.user2
        )

    def test_todo_list_view_authenticated(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo 1')
        self.assertNotContains(response, 'Todo 2')

    def test_todo_create_view_get(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo作成')

    def test_todo_create_view_post(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('todo_create'), {
            'title': 'New Todo',
            'description': 'New Description'
        })
        self.assertRedirects(response, reverse('todo_list'))
        self.assertTrue(Todo.objects.filter(title='New Todo', user=self.user1).exists())

    def test_todo_update_view_get(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todo_update', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Todo編集')
        self.assertContains(response, 'Todo 1')

    def test_todo_update_view_post(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('todo_update', args=[self.todo1.pk]), {
            'title': 'Updated Todo',
            'description': 'Updated Description'
        })
        self.assertRedirects(response, reverse('todo_list'))
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.title, 'Updated Todo')

    def test_todo_update_view_unauthorized_user(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('todo_update', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_todo_delete_view_get(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('todo_delete', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '削除確認')

    def test_todo_delete_view_post(self):
        self.client.login(username='user1', password='testpass123')
        response = self.client.post(reverse('todo_delete', args=[self.todo1.pk]))
        self.assertRedirects(response, reverse('todo_list'))
        self.assertFalse(Todo.objects.filter(pk=self.todo1.pk).exists())

    def test_todo_delete_view_unauthorized_user(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(reverse('todo_delete', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_todo_toggle_view(self):
        self.client.login(username='user1', password='testpass123')
        self.assertFalse(self.todo1.completed)
        
        response = self.client.post(reverse('todo_toggle', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 200)
        
        self.todo1.refresh_from_db()
        self.assertTrue(self.todo1.completed)

    def test_todo_toggle_view_unauthorized_user(self):
        self.client.login(username='user2', password='testpass123')
        response = self.client.post(reverse('todo_toggle', args=[self.todo1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_todo_model_str_method(self):
        self.assertEqual(str(self.todo1), 'Todo 1')

    def test_todo_model_ordering(self):
        newer_todo = Todo.objects.create(
            title='Newer Todo',
            user=self.user1
        )
        todos = Todo.objects.filter(user=self.user1)
        self.assertEqual(todos.first(), newer_todo)


class TodoToggleCSRFTestCase(TestCase):
    """Todo切り替え機能のCSRF保護テストケース。
    
    CSRF トークンありの正常系とCSRF トークンなしの異常系をテストし、
    セキュリティ機能が適切に動作することを確認します。
    """
    
    def setUp(self) -> None:
        """テスト用の初期データを設定。
        
        ユーザーとTodoアイテムを作成し、CSRF テストに使用します。
        """
        self.client = Client(enforce_csrf_checks=True)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            user=self.user,
            completed=False
        )
        self.client.login(username='testuser', password='testpass123')

    def test_todo_toggle_with_valid_csrf_token(self) -> None:
        """CSRFトークンありでTodo切り替えが正常に動作することをテスト。
        
        正しいCSRFトークンを含むPOSTリクエストで、
        Todoの完了状態が正常に切り替わることを確認します。
        """
        # CSRFトークンを取得
        response = self.client.get(reverse('todo_list'))
        csrf_token = get_token(response.wsgi_request)
        
        # 初期状態の確認
        self.assertFalse(self.todo.completed)
        
        # CSRFトークン付きでPOSTリクエスト
        response = self.client.post(
            reverse('todo_toggle', args=[self.todo.pk]),
            data={'csrfmiddlewaretoken': csrf_token},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # レスポンスの確認
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['completed'])
        
        # データベースの状態確認
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.completed)

    def test_todo_toggle_without_csrf_token(self) -> None:
        """CSRFトークンなしでTodo切り替えが403エラーになることをテスト。
        
        CSRFトークンを含まないPOSTリクエストで、
        403 Forbiddenエラーが発生することを確認します。
        """
        # 初期状態の確認
        self.assertFalse(self.todo.completed)
        
        # CSRFトークンなしでPOSTリクエスト
        response = self.client.post(
            reverse('todo_toggle', args=[self.todo.pk]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # 403エラーの確認
        self.assertEqual(response.status_code, 403)
        
        # データベースの状態が変更されていないことを確認
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.completed)

    def test_todo_toggle_with_invalid_csrf_token(self) -> None:
        """無効なCSRFトークンでTodo切り替えが403エラーになることをテスト。
        
        間違ったCSRFトークンを含むPOSTリクエストで、
        403 Forbiddenエラーが発生することを確認します。
        """
        # 初期状態の確認
        self.assertFalse(self.todo.completed)
        
        # 無効なCSRFトークンでPOSTリクエスト
        response = self.client.post(
            reverse('todo_toggle', args=[self.todo.pk]),
            data={'csrfmiddlewaretoken': 'invalid_token'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # 403エラーの確認
        self.assertEqual(response.status_code, 403)
        
        # データベースの状態が変更されていないことを確認
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.completed)


class TodoDueDateTestCase(TestCase):
    """Todo期限日機能のテストケース。
    
    期限日フィールドの追加、バリデーション、期限ステータス判定機能のテストを行います。
    """
    
    def setUp(self):
        """テスト用の初期データを設定。"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_todo_with_due_date_creation(self):
        """期限日付きTodoの作成をテスト。"""
        due_date = timezone.now() + timedelta(days=7)
        todo = Todo.objects.create(
            title='期限日付きTodo',
            description='テスト用説明',
            user=self.user,
            due_date=due_date
        )
        
        self.assertEqual(todo.title, '期限日付きTodo')
        self.assertEqual(todo.due_date, due_date)
        self.assertIsNotNone(todo.due_date)
    
    def test_todo_without_due_date_creation(self):
        """期限日なしTodoの作成をテスト。"""
        todo = Todo.objects.create(
            title='期限日なしTodo',
            description='テスト用説明',
            user=self.user
        )
        
        self.assertEqual(todo.title, '期限日なしTodo')
        self.assertIsNone(todo.due_date)
    
    def test_due_date_validation_past_date(self):
        """過去の期限日でバリデーションエラーが発生することをテスト。"""
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo(
            title='過去期限日Todo',
            description='テスト用説明',
            user=self.user,
            due_date=past_date
        )
        
        with self.assertRaises(ValidationError):
            todo.full_clean()
    
    def test_due_date_validation_future_date(self):
        """未来の期限日でバリデーションが通ることをテスト。"""
        future_date = timezone.now() + timedelta(days=1)
        todo = Todo(
            title='未来期限日Todo',
            description='テスト用説明',
            user=self.user,
            due_date=future_date
        )
        
        # バリデーションエラーが発生しないことを確認
        try:
            todo.full_clean()
        except ValidationError:
            self.fail("未来の期限日でバリデーションエラーが発生しました")
    
    def test_due_date_validation_current_date(self):
        """現在日時の期限日でバリデーションが通ることをテスト。"""
        current_date = timezone.now()
        todo = Todo(
            title='当日期限日Todo',
            description='テスト用説明',
            user=self.user,
            due_date=current_date
        )
        
        # バリデーションエラーが発生しないことを確認
        try:
            todo.full_clean()
        except ValidationError:
            self.fail("当日の期限日でバリデーションエラーが発生しました")


class TodoDueStatusTestCase(TestCase):
    """Todo期限ステータス判定機能のテストケース。
    
    期限切れ、期限間近、期限まで余裕あり等のステータス判定機能をテストします。
    """
    
    def setUp(self):
        """テスト用の初期データを設定。"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_is_overdue_with_past_date(self):
        """期限切れTodoの判定をテスト。"""
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title='期限切れTodo',
            user=self.user,
            due_date=past_date
        )
        
        self.assertTrue(todo.is_overdue())
    
    def test_is_overdue_with_future_date(self):
        """期限前Todoの判定をテスト。"""
        future_date = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title='期限前Todo',
            user=self.user,
            due_date=future_date
        )
        
        self.assertFalse(todo.is_overdue())
    
    def test_is_overdue_without_due_date(self):
        """期限日なしTodoの判定をテスト。"""
        todo = Todo.objects.create(
            title='期限日なしTodo',
            user=self.user
        )
        
        self.assertFalse(todo.is_overdue())
    
    def test_is_due_soon_within_3_days(self):
        """3日以内期限のTodoの判定をテスト。"""
        soon_date = timezone.now() + timedelta(days=2)
        todo = Todo.objects.create(
            title='期限間近Todo',
            user=self.user,
            due_date=soon_date
        )
        
        self.assertTrue(todo.is_due_soon())
    
    def test_is_due_soon_beyond_3_days(self):
        """3日超期限のTodoの判定をテスト。"""
        far_date = timezone.now() + timedelta(days=5)
        todo = Todo.objects.create(
            title='期限余裕Todo',
            user=self.user,
            due_date=far_date
        )
        
        self.assertFalse(todo.is_due_soon())
    
    def test_is_due_soon_without_due_date(self):
        """期限日なしTodoの期限間近判定をテスト。"""
        todo = Todo.objects.create(
            title='期限日なしTodo',
            user=self.user
        )
        
        self.assertFalse(todo.is_due_soon())
    
    def test_is_due_today(self):
        """今日期限のTodoの判定をテスト。"""
        today = timezone.now().replace(hour=23, minute=59, second=59)
        todo = Todo.objects.create(
            title='今日期限Todo',
            user=self.user,
            due_date=today
        )
        
        self.assertTrue(todo.is_due_today())
    
    def test_is_due_today_tomorrow(self):
        """明日期限のTodoの判定をテスト。"""
        tomorrow = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title='明日期限Todo',
            user=self.user,
            due_date=tomorrow
        )
        
        self.assertFalse(todo.is_due_today())
    
    def test_get_due_status_overdue(self):
        """期限切れステータスの取得をテスト。"""
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title='期限切れTodo',
            user=self.user,
            due_date=past_date
        )
        
        self.assertEqual(todo.get_due_status(), 'overdue')
    
    def test_get_due_status_due_today(self):
        """今日期限ステータスの取得をテスト。"""
        today = timezone.now().replace(hour=23, minute=59, second=59)
        todo = Todo.objects.create(
            title='今日期限Todo',
            user=self.user,
            due_date=today
        )
        
        self.assertEqual(todo.get_due_status(), 'due_today')
    
    def test_get_due_status_due_soon(self):
        """期限間近ステータスの取得をテスト。"""
        soon_date = timezone.now() + timedelta(days=2)
        todo = Todo.objects.create(
            title='期限間近Todo',
            user=self.user,
            due_date=soon_date
        )
        
        self.assertEqual(todo.get_due_status(), 'due_soon')
    
    def test_get_due_status_normal(self):
        """通常ステータスの取得をテスト。"""
        far_date = timezone.now() + timedelta(days=7)
        todo = Todo.objects.create(
            title='通常Todo',
            user=self.user,
            due_date=far_date
        )
        
        self.assertEqual(todo.get_due_status(), 'normal')
    
    def test_get_due_status_no_due_date(self):
        """期限日なしステータスの取得をテスト。"""
        todo = Todo.objects.create(
            title='期限日なしTodo',
            user=self.user
        )
        
        self.assertEqual(todo.get_due_status(), 'no_due_date')


class TodoFormTestCase(TestCase):
    """Todoフォーム機能のテストケース。
    
    期限日フィールドを含むフォームのバリデーションとUI機能をテストします。
    """
    
    def setUp(self):
        """テスト用の初期データを設定。"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_todo_form_with_due_date(self):
        """期限日付きTodoフォームの投稿をテスト。"""
        future_date = timezone.now() + timedelta(days=7)
        response = self.client.post(reverse('todo_create'), {
            'title': 'フォームテスト用Todo',
            'description': 'テスト用説明',
            'due_date': future_date.strftime('%Y-%m-%d %H:%M')
        })
        
        self.assertRedirects(response, reverse('todo_list'))
        todo = Todo.objects.get(title='フォームテスト用Todo')
        self.assertIsNotNone(todo.due_date)
        # 期限日が設定されていることを確認（タイムゾーン差は許容）
        self.assertIsNotNone(todo.due_date)
        # 日付部分が一致することを確認
        self.assertEqual(todo.due_date.date(), future_date.date())
    
    def test_todo_form_without_due_date(self):
        """期限日なしTodoフォームの投稿をテスト。"""
        response = self.client.post(reverse('todo_create'), {
            'title': '期限日なしTodo',
            'description': 'テスト用説明'
        })
        
        self.assertRedirects(response, reverse('todo_list'))
        todo = Todo.objects.get(title='期限日なしTodo')
        self.assertIsNone(todo.due_date)
    
    def test_todo_form_invalid_past_date(self):
        """過去の期限日でフォームエラーになることをテスト。"""
        past_date = timezone.now() - timedelta(days=1)
        response = self.client.post(reverse('todo_create'), {
            'title': '過去期限日Todo',
            'description': 'テスト用説明',
            'due_date': past_date.strftime('%Y-%m-%d %H:%M')
        })
        
        # フォームエラーで同じページに戻る
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '期限日は過去の日付にできません')
        self.assertFalse(Todo.objects.filter(title='過去期限日Todo').exists())
    
    def test_todo_update_form_with_due_date(self):
        """期限日付きTodoの更新フォームをテスト。"""
        todo = Todo.objects.create(
            title='更新テスト用Todo',
            description='テスト用説明',
            user=self.user
        )
        
        future_date = timezone.now() + timedelta(days=5)
        response = self.client.post(reverse('todo_update', args=[todo.pk]), {
            'title': '更新後タイトル',
            'description': '更新後説明',
            'due_date': future_date.strftime('%Y-%m-%d %H:%M')
        })
        
        self.assertRedirects(response, reverse('todo_list'))
        todo.refresh_from_db()
        self.assertEqual(todo.title, '更新後タイトル')
        self.assertIsNotNone(todo.due_date)


class TodoUITestCase(TestCase):
    """TodoのUI表示機能のテストケース。
    
    期限日表示と期限ステータスの視覚的表示をテストします。
    """
    
    def setUp(self):
        """テスト用の初期データを設定。"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_todo_list_displays_due_date(self):
        """Todo一覧に期限日が表示されることをテスト。"""
        due_date = timezone.now() + timedelta(days=3)
        todo = Todo.objects.create(
            title='期限日表示テスト',
            description='テスト用説明',
            user=self.user,
            due_date=due_date
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '期限:')
        self.assertContains(response, due_date.strftime('%Y/%m/%d'))
    
    def test_overdue_todo_visual_status(self):
        """期限切れTodoの視覚的ステータス表示をテスト。"""
        past_date = timezone.now() - timedelta(days=1)
        todo = Todo.objects.create(
            title='期限切れTodo',
            user=self.user,
            due_date=past_date
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'badge bg-danger')
        self.assertContains(response, '期限切れ')
        self.assertContains(response, 'border-danger')
    
    def test_due_today_todo_visual_status(self):
        """今日期限Todoの視覚的ステータス表示をテスト。"""
        today = timezone.now().replace(hour=23, minute=59, second=59)
        todo = Todo.objects.create(
            title='今日期限Todo',
            user=self.user,
            due_date=today
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'badge bg-warning')
        self.assertContains(response, '今日期限')
        self.assertContains(response, 'border-warning')
    
    def test_due_soon_todo_visual_status(self):
        """期限間近Todoの視覚的ステータス表示をテスト。"""
        soon_date = timezone.now() + timedelta(days=2)
        todo = Todo.objects.create(
            title='期限間近Todo',
            user=self.user,
            due_date=soon_date
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'badge bg-info')
        self.assertContains(response, '期限間近')
        self.assertContains(response, 'border-info')
    
    def test_normal_due_date_todo_visual_status(self):
        """通常期限Todoの視覚的ステータス表示をテスト。"""
        future_date = timezone.now() + timedelta(days=7)
        todo = Todo.objects.create(
            title='通常期限Todo',
            user=self.user,
            due_date=future_date
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'badge bg-light')
        self.assertContains(response, '期限あり')
    
    def test_no_due_date_todo_display(self):
        """期限日なしTodoの表示をテスト。"""
        todo = Todo.objects.create(
            title='期限日なしTodo',
            user=self.user
        )
        
        response = self.client.get(reverse('todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '期限:')
        self.assertNotContains(response, 'badge bg-danger')
        self.assertNotContains(response, 'badge bg-warning')
        self.assertNotContains(response, 'badge bg-info')
    
    def test_todo_form_contains_due_date_field(self):
        """Todoフォームに期限日フィールドが含まれることをテスト。"""
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'flatpickr-datetime')
        self.assertContains(response, '期限日時を選択してください')
        self.assertContains(response, 'bi-calendar-event')
    
    def test_todo_form_contains_flatpickr_script(self):
        """TodoフォームにFlatpickr初期化スクリプトが含まれることをテスト。"""
        response = self.client.get(reverse('todo_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'flatpickr(')
        self.assertContains(response, 'enableTime: true')
        self.assertContains(response, 'locale: "ja"')
