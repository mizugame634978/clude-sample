"""Todoアプリケーションのテストケース。

このモジュールはTodoアプリケーションの機能をテストするテストケースを含み、
ユーザー認証とTodoのCRUD操作のテストを実行します。
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
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
