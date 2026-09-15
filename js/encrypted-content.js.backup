/**
 * Hugo 加密内容组件
 * 提供加密内容的解密功能
 */

class EncryptedContent {
    constructor() {
        this.init();
    }
    
    init() {
        this.bindEvents();
    }
    
    /**
     * 绑定所有加密内容的事件
     */
    bindEvents() {
        const encryptedContents = document.querySelectorAll('.encrypted-content');
        
        encryptedContents.forEach(encryptedDiv => {
            const passwordInput = encryptedDiv.querySelector('.password-input');
            const decryptBtn = encryptedDiv.querySelector('.decrypt-btn');
            
            if (passwordInput && decryptBtn) {
                // 绑定按钮点击事件
                decryptBtn.addEventListener('click', () => {
                    this.decryptContent(encryptedDiv.id);
                });
                
                // 绑定回车键事件
                passwordInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        e.preventDefault();
                        this.decryptContent(encryptedDiv.id);
                    }
                });
                
                // 输入框获得焦点时清除错误信息
                passwordInput.addEventListener('focus', () => {
                    this.hideError(encryptedDiv.id);
                });
            }
        });
    }
    
    /**
     * 解密内容
     * @param {string} elementId - 加密容器的ID
     */
    decryptContent(elementId) {
        const encryptedDiv = document.getElementById(elementId);
        if (!encryptedDiv) {
            console.error('加密容器不存在:', elementId);
            return;
        }
        
        const passwordInput = encryptedDiv.querySelector('.password-input');
        const errorMsg = encryptedDiv.querySelector('.error-message');
        const lockDiv = encryptedDiv.querySelector('.encrypted-lock');
        const contentDiv = document.getElementById(elementId + '-content');
        
        if (!passwordInput || !errorMsg || !lockDiv || !contentDiv) {
            console.error('加密容器缺少必要的子元素');
            return;
        }
        
        const enteredPassword = passwordInput.value.trim();
        const correctPassword = encryptedDiv.getAttribute('data-password');
        
        // 简单的密码验证（可以后续升级为更复杂的加密）
        if (enteredPassword === correctPassword) {
            this.showContent(lockDiv, contentDiv);
            this.clearPassword(passwordInput);
            this.hideError(elementId);
            
            // 触发自定义事件，允许其他脚本响应解密完成
            this.triggerDecryptedEvent(elementId);
        } else {
            this.showError(elementId, passwordInput);
        }
    }
    
    /**
     * 显示解密后的内容
     * @param {HTMLElement} lockDiv - 锁定界面
     * @param {HTMLElement} contentDiv - 内容容器
     */
    showContent(lockDiv, contentDiv) {
        lockDiv.style.display = 'none';
        contentDiv.style.display = 'block';
        
        // 触发页面重排，确保内容正确显示
        window.dispatchEvent(new Event('resize'));
        
        // 如果内容中有代码高亮，可能需要重新初始化
        this.reinitializeHighlighting(contentDiv);
    }
    
    /**
     * 重新初始化代码高亮（如果有）
     * @param {HTMLElement} contentDiv - 内容容器
     */
    reinitializeHighlighting(contentDiv) {
        // 检查是否有代码块需要重新高亮
        const codeBlocks = contentDiv.querySelectorAll('pre code');
        if (codeBlocks.length > 0 && typeof hljs !== 'undefined') {
            codeBlocks.forEach(block => {
                hljs.highlightElement(block);
            });
        }
    }
    
    /**
     * 清空密码输入框
     * @param {HTMLInputElement} passwordInput - 密码输入框
     */
    clearPassword(passwordInput) {
        passwordInput.value = '';
    }
    
    /**
     * 显示错误信息
     * @param {string} elementId - 加密容器的ID
     * @param {HTMLInputElement} passwordInput - 密码输入框
     */
    showError(elementId, passwordInput) {
        const errorMsg = document.getElementById(elementId + '-error');
        if (errorMsg) {
            errorMsg.style.display = 'block';
        }
        
        passwordInput.value = '';
        passwordInput.focus();
        
        // 添加震动效果
        passwordInput.style.animation = 'shake 0.5s';
        setTimeout(() => {
            passwordInput.style.animation = '';
        }, 500);
        
        // 3秒后自动隐藏错误信息
        setTimeout(() => {
            this.hideError(elementId);
        }, 3000);
    }
    
    /**
     * 隐藏错误信息
     * @param {string} elementId - 加密容器的ID
     */
    hideError(elementId) {
        const errorMsg = document.getElementById(elementId + '-error');
        if (errorMsg) {
            errorMsg.style.display = 'none';
        }
    }
    
    /**
     * 触发解密完成事件
     * @param {string} elementId - 加密容器的ID
     */
    triggerDecryptedEvent(elementId) {
        const event = new CustomEvent('contentDecrypted', {
            detail: { elementId: elementId },
            bubbles: true
        });
        
        const encryptedDiv = document.getElementById(elementId);
        if (encryptedDiv) {
            encryptedDiv.dispatchEvent(event);
        }
    }
    
    /**
     * 添加新的加密内容监听（适用于动态加载的内容）
     */
    addNewContentListener() {
        // 可以在这里添加 MutationObserver 来监听动态内容
        // 这个方法留作后续扩展使用
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
    20%, 40%, 60%, 80% { transform: translateX(5px); }
}
`;
document.head.appendChild(style);

// 页面加载完成后初始化加密内容组件
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new EncryptedContent();
    });
} else {
    // DOM 已经加载完成
    new EncryptedContent();
}

// 提供全局访问方法
window.EncryptedContent = EncryptedContent;
window.decryptContent = function(elementId) {
    const instance = new EncryptedContent();
    instance.decryptContent(elementId);
};