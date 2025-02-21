import os
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
import tempfile

# テスト対象のFastAPIアプリをインポート
from atcoder_assistant_new import app, settings

# テストクライアントの作成
client = TestClient(app)

# テスト用のデータ
SAMPLE_PYTHON_CODE = """
def solve():
    a, b = map(int, input().split())
    print(a + b)

if __name__ == "__main__":
    solve()
"""

SAMPLE_CPP_CODE = """
#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""


@pytest.fixture
def temp_base_dir():
    """一時的なベースディレクトリを作成するフィクスチャ"""
    with tempfile.TemporaryDirectory() as temp_dir:
        original_base_dir = settings.BASE_DIR
        settings.BASE_DIR = temp_dir
        yield temp_dir
        settings.BASE_DIR = original_base_dir


def test_save_testcases(temp_base_dir):
    """テストケース保存のテスト"""
    contest_id = "abc001"
    problem_id = "a"
    response = client.post(
        "/api/testcase",
        json={
            "url": f"https://atcoder.jp/contests/{contest_id}/tasks/{problem_id}",
            "problem_title": "A",
            "testcases": [
                {"input": "1 2", "output": "3"},
                {"input": "4 5", "output": "9"}
            ]
        }
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Testcases saved successfully"}

    test_dir = Path(temp_base_dir) / contest_id / problem_id / "test"
    assert test_dir.exists()
    assert (test_dir / "sample-1.in").read_text() == "1 2\n"
    assert (test_dir / "sample-1.out").read_text() == "3\n"


# @pytest.mark.parametrize("language,code", [
#     ("python", SAMPLE_PYTHON_CODE),
#     ("cpp", SAMPLE_CPP_CODE)
# ])
# def test_run_code_success(language, code):
#     """コード実行の成功テスト"""
#     response = client.post(
#         "/api/run",
#         json={
#             "language": language,
#             "code": code,
#             "input": "1 2",
#             "expected_output": "3"
#         }
#     )

#     assert response.status_code == 200
#     result = response.json()
#     assert result["result"] == "success"
#     assert result["output"] == "3"


@pytest.mark.parametrize("language,code", [
    ("python", SAMPLE_PYTHON_CODE),
    ("cpp", SAMPLE_CPP_CODE)
])
def test_run_all_tests_partial_failure(language, code):
    """一部のテストケースが失敗するケースのテスト"""
    response = client.post(
        "/api/runall",
        json={
            "language": language,
            "code": code,
            "testcases": [
                {"input": "1 2", "output": "3"},  # 正解
                {"input": "4 5", "output": "10"},  # 不正解
                {"input": "10 20", "output": "31"}  # 不正解
            ]
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert result["result"] == "failure"
    assert len(result["failed_cases"]) == 2


def test_float_comparison():
    """浮動小数点数の比較テスト"""
    code = """
print("0.1 + 0.2 =", 0.1 + 0.2)
"""
    response = client.post(
        "/api/run",
        json={
            "language": "python",
            "code": code,
            "input": "",
            "expected_output": "0.1 + 0.2 = 0.3"
        }
    )

    assert response.status_code == 200
    assert response.json()["result"] == "success"


if __name__ == "__main__":
    pytest.main(["-v"])
