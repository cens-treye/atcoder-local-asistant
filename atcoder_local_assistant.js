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

  // // エディタの内容を取得する
  // function getEditorContent() {
  //   var editor = ace.edit("editor");
  //   return editor.getValue();
  // }

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

  (function () {
    // URLからコンテストIDと問題IDを取得
    var url = window.location.href;
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
  })();
})();
