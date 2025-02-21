import platform
import time
import re
import os
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
try:
    import resource  # Linux/MacOS
except ImportError:
    resource = None  # Windows

# 設定クラスの定義


class Settings:
    def __init__(self):
        self.BASE_DIR = "C:/atcoder"


# アプリケーションとグローバル設定の作成
app = FastAPI(title="Code Runner API")
settings = Settings()
# CORSミドルウェアの追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TestCase(BaseModel):
    input: str
    output: str


class TestCaseRequest(BaseModel):
    url: str
    problem_title: str
    testcases: List[TestCase]


class CodeRunRequest(BaseModel):
    language: str
    code: str
    input: Optional[str] = ""


class CodeRunAllRequest(BaseModel):
    language: str
    code: str
    testcases: List[TestCase]


def compare_output(expected_output: str, actual_output: str, tolerance: float = 1e-10) -> bool:
    # スペースや改行を基準に文字列を分割してリストに変換
    expected_tokens = re.split(r'\s+', expected_output.strip())
    actual_tokens = re.split(r'\s+', actual_output.strip())

    # トークン数が異なる場合は不一致とみなす
    if len(expected_tokens) != len(actual_tokens):
        return False

    # 各トークンを比較
    for expected, actual in zip(expected_tokens, actual_tokens):
        try:
            # 実際のトークンに小数点が含まれる場合はfloatとして比較
            if '.' in actual:
                expected_num = float(expected)
                actual_num = float(actual)
                # 誤差を許容して比較
                if abs(expected_num - actual_num) > tolerance:
                    return False
            else:
                # 小数点が含まれない場合は整数として比較
                if int(expected) != int(actual):
                    return False
        except ValueError:
            # 数値でない場合は文字列として比較
            if expected != actual:
                return False

    return True


@app.post("/api/testcase", response_class=JSONResponse)
async def save_testcases(request: TestCaseRequest):
    url = request.url
    # なぜか、末尾に#がつくことがあるので、それを取り除く
    url = url.rstrip('#')
    comp = re.compile(r"https://atcoder.jp/contests/([a-zA-Z0-9_]+)/tasks/([a-zA-Z0-9_]+)")
    match = comp.match(url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    contest_id, problem_id = match.groups()
    contest_id = contest_id.lower()
    problem_id = problem_id.lower()
    problem_title = request.problem_title
    print(contest_id, problem_id, problem_title)

    # ADTコンテストの場合、problem_idの先頭にproblem_titleの先頭文字を追加
    if contest_id[:3] == 'adt':
        problem_id = problem_title[0].upper() + '_' + problem_id

    problem_dir = os.path.join(settings.BASE_DIR, contest_id, problem_id)

    # アーカイブされているかを確認する
    top_dir = contest_id[:3].upper() if contest_id[:3] in ['abc', 'arc', 'agc', 'adt'] else 'Others'
    archive_dir = os.path.join(settings.BASE_DIR, top_dir, contest_id)
    if os.path.exists(archive_dir):
        problem_dir = os.path.join(archive_dir, problem_id)
        print('すでに存在するディレクトリに保存します')
    print(problem_dir)

    # 保存先ディレクトリと、コードファイルの作成
    os.makedirs(problem_dir, exist_ok=True)
    code_file = os.path.join(problem_dir, 'main.py')
    if not os.path.exists(code_file):
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(f'# submit to {url}\n')

    # テストディレクトリ(テストケースの保存先)の作成
    test_dir = os.path.join(problem_dir, 'test')
    if os.path.exists(test_dir):
        raise HTTPException(status_code=400, detail="Test directory already exists")

    os.makedirs(test_dir, exist_ok=True)

    # テストケースの保存
    for idx, case in enumerate(request.testcases, start=1):
        input_file = os.path.join(test_dir, f'sample-{idx}.in')
        output_file = os.path.join(test_dir, f'sample-{idx}.out')
        with open(input_file, 'w', encoding='utf-8') as infile:
            infile.write(case.input + '\n')
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(case.output + '\n')

    return {"message": "Testcases saved successfully"}


@app.post("/api/run", response_class=JSONResponse)
async def run_code(request: CodeRunRequest):
    start_time = time.perf_counter()

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            compile_command = None
            command = None

            if request.language == 'python':
                code_file = os.path.join(temp_dir, 'main.py')
                command = ['pypy', code_file]
            elif request.language == 'cpp':
                code_file = os.path.join(temp_dir, 'main.cpp')
                executable = os.path.join(temp_dir, 'a.exe')
                compile_command = ['g++', code_file, '-o', executable, '-std=c++23', '-O0']
                command = [executable]
            else:
                return {"result": "error", "message": "Unsupported language"}

            with open(code_file, 'w', encoding='utf-8') as f:
                f.write(request.code)

            if compile_command:
                subprocess.run(compile_command, check=True, capture_output=True, text=True, timeout=10)

            # コードの実行
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                stdout, stderr = process.communicate(input=request.input, timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                raise HTTPException(status_code=400, detail="Time limit exceeded") from None

            end_time = time.perf_counter()
            exec_time = int((end_time - start_time) * 1000)  # 実際には提出すると2倍ほどかかる

            # メモリ使用量の取得
            if resource:
                usage = resource.getrusage(resource.RUSAGE_CHILDREN)
                memory_usage = usage.ru_maxrss
            else:
                memory_usage = -1

            if process.returncode == 0:
                return {
                    "result": "success",
                    "output": stdout,
                    "error": stderr,
                    "exit_code": 0,
                    "exec_time": exec_time,
                    "memory": memory_usage
                }
            else:
                return {
                    "result": "failure",
                    "output": stdout,
                    "error": stderr,
                    "exit_code": process.returncode,
                    "exec_time": exec_time,
                    "memory": memory_usage
                }

        except Exception as e:
            return {"result": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
