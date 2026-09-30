import os
import shutil
import tempfile
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from rest_framework.test import APITestCase

from apps.task.models import Profile, Task, TaskTemplate
from apps.terminal.models import Workspace
from apps.utils.funksion import TerminalEngine
from apps.utils.tasks import async_check_task

# Testlar haqiqiy workspaces/ papkasini ifloslantirmasligi uchun vaqtinchalik papka
TMP_BASE = tempfile.mkdtemp(prefix="termina_tests_")


def tearDownModule():
    shutil.rmtree(TMP_BASE, ignore_errors=True)


def make_user(username):
    """Foydalanuvchi + profil. Workspace signal orqali avtomatik yaratiladi."""
    user = User.objects.create_user(username=username, password="Str0ng-Pass-123")
    Profile.objects.get_or_create(user=user)
    return user


def make_task(user, structure=None, status="pending", xp=10):
    template = TaskTemplate.objects.create(
        title="Test",
        description="Test topshiriq",
        target_structure=structure or {"hello.txt": "Salom"},
        level=1,
        type="file",
        xp=xp,
    )
    return Task.objects.create(
        user=user,
        template=template,
        level=1,
        title=template.title,
        description=template.description,
        target_structure=template.target_structure,
        xp=xp,
        status=status,
    )


@override_settings(BASE_DIR=TMP_BASE)
class TaskStatusEndpointTests(APITestCase):
    """CeleryTaskStatusView: begona foydalanuvchi ma'lumotini ko'ra olmasligi kerak."""

    def setUp(self):
        self.alice = make_user("alice")
        self.bob = make_user("bob")
        self.task = make_task(self.alice, status="in_progress")
        self.task.check_job_id = "job-alice-1"
        self.task.save()

    def test_anonymous_gets_401(self):
        response = self.client.get("/api/task-status/job-alice-1/")
        self.assertEqual(response.status_code, 401)

    def test_other_user_gets_404(self):
        self.client.force_authenticate(self.bob)
        response = self.client.get("/api/task-status/job-alice-1/")
        self.assertEqual(response.status_code, 404)

    @mock.patch("api.views.signals_view.AsyncResult")
    def test_owner_sees_own_status(self, async_result):
        async_result.return_value.status = "SUCCESS"
        async_result.return_value.ready.return_value = True
        self.client.force_authenticate(self.alice)

        response = self.client.get("/api/task-status/job-alice-1/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "SUCCESS")
        self.assertIn("xp", response.data)


@override_settings(BASE_DIR=TMP_BASE)
class PathSafetyTests(TestCase):
    """Foydalanuvchi o'z workspace papkasidan chiqib keta olmasligi kerak."""

    def setUp(self):
        self.user = make_user("carol")
        self.other = make_user("carol2")
        self.engine = TerminalEngine(Workspace.objects.get(user=self.user))

    def test_dotdot_is_blocked(self):
        result = self.engine.execute_command("cat ../../../etc/passwd")
        self.assertEqual(result["type"], "error")

    def test_cd_above_root_is_blocked(self):
        result = self.engine.execute_command("cd ..")
        self.assertEqual(result["type"], "error")

    def test_cannot_enter_other_users_workspace(self):
        other_dir = Workspace.objects.get(user=self.other).root_dir
        result = self.engine.execute_command(f"cd {other_dir}")
        self.assertEqual(result["type"], "error")

    def test_cannot_delete_root(self):
        result = self.engine.execute_command("rm .")
        self.assertEqual(result["type"], "error")
        self.assertTrue(os.path.isdir(self.engine.workspace.root_dir))

    def test_unknown_command_is_rejected(self):
        result = self.engine.execute_command("curl http://example.com")
        self.assertEqual(result["type"], "error")

    def test_too_large_file_is_rejected(self):
        big = "a" * (TerminalEngine.MAX_FILE_BYTES + 1)
        result = self.engine.execute_command("nano big.txt", content_to_write=big)
        self.assertEqual(result["type"], "error")


@override_settings(BASE_DIR=TMP_BASE)
class CheckCommandTests(TestCase):
    """`check` buyrug'i to'g'ri topshiriqni tekshirishi va ID ni saqlashi kerak."""

    def setUp(self):
        self.user = make_user("dave")
        self.engine = TerminalEngine(Workspace.objects.get(user=self.user))

    def test_check_requires_being_in_task_folder(self):
        make_task(self.user, status="in_progress")
        result = self.engine.execute_command("check")
        self.assertEqual(result["type"], "error")

    @mock.patch("apps.utils.funksion.async_check_task")
    def test_check_uses_started_task_and_queues_once(self, celery_task):
        celery_task.delay.return_value.id = "job-123"
        task_a = make_task(self.user)
        task_b = make_task(self.user)  # keyin yaratilgan, lekin boshlanmagan

        self.engine.execute_command(f"start {task_a.id}")
        result = self.engine.execute_command("check")

        self.assertEqual(result["type"], "check_queued")
        self.assertEqual(result["celery_task_id"], "job-123")
        self.assertEqual(celery_task.delay.call_count, 1)  # ikki marta emas

        args = celery_task.delay.call_args.args
        self.assertEqual(args[1], task_a.id)  # B emas, aynan A tekshirildi

        task_a.refresh_from_db()
        task_b.refresh_from_db()
        self.assertEqual(task_a.check_job_id, "job-123")  # status endpoint topa oladi
        self.assertEqual(task_b.status, "pending")


@override_settings(BASE_DIR=TMP_BASE)
class XpAwardTests(TestCase):
    """Bir topshiriq uchun XP faqat bir marta berilishi kerak."""

    def setUp(self):
        self.user = make_user("erin")
        workspace = Workspace.objects.get(user=self.user)
        self.task = make_task(self.user, {"hello.txt": "Salom"}, status="in_progress", xp=10)

        self.task_dir = os.path.join(workspace.root_dir, f"task_{self.task.id}_papkasi")
        os.makedirs(self.task_dir, exist_ok=True)
        self._write("Salom")

    def _write(self, text):
        with open(os.path.join(self.task_dir, "hello.txt"), "w", encoding="utf-8") as f:
            f.write(text)

    def test_xp_is_awarded_once_even_if_checked_twice(self):
        async_check_task(self.user.id, self.task.id, self.task_dir)
        async_check_task(self.user.id, self.task.id, self.task_dir)  # takroriy vazifa

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 10)
        self.assertEqual(profile.total_completed_tasks, 1)

        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "completed")

    def test_wrong_answer_marks_failed_and_resets_streak(self):
        self._write("Xato matn")

        async_check_task(self.user.id, self.task.id, self.task_dir)

        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.xp, 0)
        self.assertEqual(profile.failed_attempts, 1)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, "failed")
