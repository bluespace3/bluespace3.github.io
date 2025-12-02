// 文章加密脚本

// 检查页面是否有需要加密的内容
document.addEventListener('DOMContentLoaded', function() {
  const encryptedContent = document.getElementById('encrypted-content');
  const articleContent = document.querySelector('.e-content.article-entry');
  
  if (encryptedContent && articleContent) {
    // 隐藏原始内容
    const originalContent = articleContent.innerHTML;
    
    // 创建密码输入界面
    const passwordForm = document.createElement('div');
    passwordForm.className = 'password-form';
    passwordForm.innerHTML = `
      <div class="password-container">
        <h3>🔒 这篇文章已加密</h3>
        <p>请输入密码查看内容</p>
        <div class="password-input-container">
          <input type="password" id="article-password" placeholder="请输入密码" />
          <button id="password-submit">确认</button>
        </div>
        <p id="password-error" style="color: red; display: none;">密码错误，请重试</p>
      </div>
    `;
    
    // 替换文章内容为密码输入框
    articleContent.innerHTML = '';
    articleContent.appendChild(passwordForm);
    
    // 添加密码验证逻辑
    const submitButton = document.getElementById('password-submit');
    const passwordInput = document.getElementById('article-password');
    const passwordError = document.getElementById('password-error');
    
    submitButton.addEventListener('click', function() {
      validatePassword();
    });
    
    passwordInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        validatePassword();
      }
    });
    
    function validatePassword() {
      const password = passwordInput.value;
      const correctPassword = encryptedContent.getAttribute('data-password');
      
      if (password === correctPassword) {
        // 密码正确，显示内容
        articleContent.innerHTML = originalContent;
        
        // 保存到 sessionStorage，避免刷新后再次输入密码
        const postUrl = window.location.pathname;
        sessionStorage.setItem('unlocked_' + postUrl, 'true');
      } else {
        // 密码错误，显示错误信息
        passwordError.style.display = 'block';
      }
    }
    
    // 检查 sessionStorage，如果已经解锁过，直接显示内容
    const postUrl = window.location.pathname;
    if (sessionStorage.getItem('unlocked_' + postUrl) === 'true') {
      articleContent.innerHTML = originalContent;
    }
  }
});

// 添加样式
const style = document.createElement('style');
style.textContent = `
  .password-container {
    text-align: center;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 500px;
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: #f9f9f9;
  }
  
  .password-input-container {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
  }
  
  #article-password {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px 0 0 4px;
    font-size: 16px;
    outline: none;
  }
  
  #password-submit {
    padding: 8px 16px;
    background-color: #ff6b6b;
    color: white;
    border: none;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    font-size: 16px;
  }
  
  #password-submit:hover {
    background-color: #ff5252;
  }
`;
document.head.appendChild(style);