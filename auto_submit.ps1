param(
    [string]$file_path
)

$contest_id = $file_path.split('\')[-3]
$problem_id = $file_path.split('\')[-2]

# 先頭が大文字のときは、先頭2文字を飛ばす
if ($problem_id[0] -cmatch '[A-Z]') {
    $problem_id = $problem_id.Substring(2)
}

Write-Host "Contest ID: $contest_id"
Write-Host "Problem ID: $problem_id"

$filename = $file_path.split('\')[-1]

if ($filename -match '.*\.py$') {
    $cmd = "oj submit https://atcoder.jp/contests/$contest_id/tasks/$problem_id $file_path --guess-python-interpreter pypy -w 0.1 -y --open"
} else {
    $cmd = "oj submit https://atcoder.jp/contests/$contest_id/tasks/$problem_id $file_path -w 0.1 -y --open"
}

Write-Host $cmd
Invoke-Expression $cmd
