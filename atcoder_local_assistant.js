// ==UserScript==
// @name         Atcoder Local Assistant
// @version      2.7
// @author       sanai
// @match        https://atcoder.jp/contests/*/tasks/*
// @exclude      https://atcoder.jp/contests/*/tasks/*/*
// @grant        none
// @description  Atcoderのテストケースを自動保存したり、テストケースをダウンロードしたりするツールです。
// ==/UserScript==

(function () {
  "use strict";

  // テストケースを取得する
  function getTestCases() {
    const testCases = [];

    const sampleElements = document.querySelectorAll("span.lang-ja pre[id^='pre-sample']");

    for (let i = 0; i < sampleElements.length; i += 2) {
      // 偶数番目が input、奇数番目が output
      const inputText = sampleElements[i].innerText.trim();
      const outputText = sampleElements[i + 1]?.innerText.trim() || "";

      testCases.push({ input: inputText, output: outputText });
    }

    return testCases;
  }

  // テストケースをダウンロードする
  function downloadTestCases(url, problemTitle, testCases) {
    fetch("http://localhost:8000/api/testcase", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: url,
        problem_title: problemTitle,
        testcases: testCases,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.result === "success") {
          console.log("テストケースが正常にダウンロードされました！");
        } else {
          console.error("テストケースのダウンロード中にエラーが発生しました。", data);
        }
      })
      .catch((error) => {
        console.error("APIへのリクエスト中にエラーが発生しました。", error);
      });
  }

  const langmode_to_lang = {
    "ace/mode/c_cpp": "cpp",
    "ace/mode/python": "python",
  };

  // 現在選択されている言語を取得する
  function getSelectedLanguage() {
    const editor = ace.edit("editor");
    const modeId = editor.session.$modeId;
    return langmode_to_lang[modeId];
  }

  // コードを書き込む
  function writeCode(code) {
    const editor = ace.edit("editor");
    editor.setValue(code);
  }

  // サーバーから保存されているコードを取得する
  async function getLocalCode() {
    const language = getSelectedLanguage();
    const url = window.location.href;
    const problemTitle = document.title;

    const response = await fetch("http://localhost:8000/api/code", {
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: url,
        problem_title: problemTitle,
        language: language,
      }),
    });

    if (!response.ok) {
      throw new Error("HTTP error! status: " + response.status);
    }

    const data = await response.json();
    return data.code;
  }

  const langmode_to_lang = {
    "ace/mode/c_cpp": "cpp",
    "ace/mode/python": "python",
  };

  // 現在選択されている言語を取得する
  function getSelectedLanguage() {
    const editor = ace.edit("editor");
    const modeId = editor.session.$modeId;
    return langmode_to_lang[modeId];
  }

  // コードを書き込む
  function writeCode(code) {
    const editor = ace.edit("editor");
    editor.setValue(code);
  }

  // サーバーから保存されているコードを取得する
  async function getLocalCode() {
    const language = getSelectedLanguage();
    const url = window.location.href;
    const problemTitle = document.title;

    const response = await fetch("http://localhost:8000/api/code", {
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        url: url,
        problem_title: problemTitle,
        language: language,
      }),
    });

    if (!response.ok) {
      throw new Error("HTTP error! status: " + response.status);
    }

    const data = await response.json();
    return data.code;
  }

  (function () {
    // URLからコンテストIDと問題IDを取得
    const url = window.location.href;
    const match = url.match(/contests\/([^/]+)\/tasks\/([^/]+)/);
    if (!match) {
      console.log("コンテストIDと問題IDを取得できませんでした。");
      return;
    }

    // タイトルを取得
    const problemTitle = document.title;

    // テストケースを取得
    const testCases = getTestCases();
    if (testCases.length === 0) {
      console.log("テストケースが見つかりませんでした。");
      return;
    }

    // APIに送信
    downloadTestCases(url, problemTitle, testCases);

    // 押すと、ローカルのコードを取得して、エディタに書き込む
    const button = document.createElement("button");
    button.textContent = "ローカルのコードを取得";
    button.className = "btn btn-default btn-sm";
    button.style.float = "right";
    button.onclick = async function (event) {
      event.preventDefault();
      const code = await getLocalCode();
      writeCode(code);
    };
    const formGroup = document.querySelector("div.form-group:nth-child(2)");
    formGroup.appendChild(button);
  })();
})();
