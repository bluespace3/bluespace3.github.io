// 文章加密脚本 - 修复版本
// 修复了sessionStorage存储和密码验证的问题

(function() {
  'use strict';

  // 调试函数（生产环境可以移除）
  function debugLog(message) {
    // console.log('[Encrypt Debug] ' + message);
  }

  // 检查页面是否有需要加密的内容
  function initEncryption() {
    const encryptedContent = document.getElementById('encrypted-content');
    const articleContent = document.querySelector('.e-content.article-entry');

    if (!encryptedContent || !articleContent) {
      debugLog('No encrypted content found');
      return; // 没有加密内容，直接返回
    }

    const correctPassword = encryptedContent.getAttribute('data-password');
    if (!correctPassword) {
      debugLog('No password found in data attribute');
      return;
    }

    // 隐藏原始内容
    const originalContent = articleContent.innerHTML;
    debugLog('Original content captured, length: ' + originalContent.length);

    // 检查 sessionStorage，如果已经解锁过，直接显示内容
    const postUrl = window.location.pathname;
    const sessionStorageKey = 'unlocked_' + postUrl;

    debugLog('Checking sessionStorage for key: ' + sessionStorageKey);
    debugLog('SessionStorage value: ' + sessionStorage.getItem(sessionStorageKey));

    if (sessionStorage.getItem(sessionStorageKey) === 'true') {
      debugLog('Content already unlocked, showing original content');
      articleContent.innerHTML = originalContent;
      return;
    }

    // 创建密码输入界面
    const passwordForm = document.createElement('div');
    passwordForm.className = 'encrypted-lock-container';
    passwordForm.innerHTML = `
      <div class="encrypted-lock" style="text-align: center; padding: 2rem; margin: 2rem auto; max-width: 500px; border: 1px solid #eee; border-radius: 8px; background-color: #f9f9f9;">
        <h3 style="margin: 0 0 1rem 0; color: #333;">🔒 这篇文章已加密</h3>
        <p style="margin: 0 0 1.5rem 0; color: #666;">请输入密码查看内容</p>
        <div style="display: flex; justify-content: center; margin: 1rem 0;">
          <input type="password" id="article-password" placeholder="请输入密码" style="padding: 8px 12px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 16px; outline: none;" />
          <button id="password-submit" style="padding: 8px 16px; background-color: #007bff; color: white; border: none; border-radius: 0 4px 4px 0; cursor: pointer; font-size: 16px;">确认</button>
        </div>
        <p id="password-error" style="color: red; display: none; margin-top: 1rem;">密码错误，请重试</p>
      </div>
    `;

    // 替换文章内容为密码输入框
    articleContent.innerHTML = '';
    articleContent.appendChild(passwordForm);

    // 添加密码验证逻辑
    const submitButton = document.getElementById('password-submit');
    const passwordInput = document.getElementById('article-password');
    const passwordError = document.getElementById('password-error');

    function validatePassword() {
      const password = passwordInput.value.trim();
      debugLog('Validating password: ' + password + ' (length: ' + password.length + ')');
      debugLog('Correct password: ' + correctPassword + ' (length: ' + correctPassword.length + ')');

      if (password === correctPassword) {
        debugLog('Password correct! Showing content');
        // 密码正确，显示内容
        articleContent.innerHTML = originalContent;

        // 保存到 sessionStorage，避免刷新后再次输入密码
        sessionStorage.setItem(sessionStorageKey, 'true');
        debugLog('Saved to sessionStorage with key: ' + sessionStorageKey);
      } else {
        debugLog('Password incorrect');
        // 密码错误，显示错误信息
        passwordError.style.display = 'block';
        passwordInput.value = '';
        passwordInput.focus();

        // 3秒后自动隐藏错误信息
        setTimeout(() => {
          passwordError.style.display = 'none';
        }, 3000);
      }
    }

    submitButton.addEventListener('click', validatePassword);

    passwordInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        validatePassword();
      }
    });

    debugLog('Encryption initialized successfully');
  }

  // 等待DOM加载完成后再初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initEncryption);
  } else {
    initEncryption();
  }
})();