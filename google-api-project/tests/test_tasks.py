from django.test import TestCase
from api.tasks import add

class CeleryTaskTest(TestCase):
    def test_add_task(self):
        # タスクを遅延実行
        result = add.delay(2, 3)
        # タスク完了を待機
        output = result.get(timeout=10)
        self.assertEqual(output, 5)