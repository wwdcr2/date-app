/**
 * 메인 JavaScript 파일
 */

document.addEventListener('DOMContentLoaded', function() {
    // 네비게이션 토글 기능
    initNavToggle();
    
    // 플래시 메시지 자동 제거
    initFlashMessages();
    
    // 모달 외부 클릭 시 닫기
    initModalHandlers();
    
    // 테마 토글 기능
    initThemeToggle();
});

/**
 * 네비게이션 토글 초기화
 */
function initNavToggle() {
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
}

/**
 * 플래시 메시지 자동 제거
 */
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(function(message) {
        // 5초 후 자동 제거
        setTimeout(function() {
            if (message.parentElement) {
                message.style.animation = 'slideOut 0.3s ease';
                setTimeout(function() {
                    message.remove();
                }, 300);
            }
        }, 5000);
    });
}

/**
 * 모달 핸들러 초기화
 */
function initModalHandlers() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(function(modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            const visibleModal = document.querySelector('.modal[style*="flex"]');
            if (visibleModal) {
                visibleModal.style.display = 'none';
            }
        }
    });
}

/**
 * API 요청 헬퍼 함수
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * 로딩 상태 표시/숨김
 */
function showLoading(element, text = '로딩 중...') {
    if (element) {
        element.innerHTML = `<div class="loading">${text}</div>`;
    }
}

function hideLoading(element, content = '') {
    if (element) {
        element.innerHTML = content;
    }
}

/**
 * 토스트 메시지 표시
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `flash-message flash-${type}`;
    toast.innerHTML = `
        <span class="flash-text">${message}</span>
        <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    container.appendChild(toast);
    
    // 자동 제거
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

/**
 * 폼 검증 헬퍼
 */
function validateEmail(email) {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

/**
 * 날짜 포맷팅 헬퍼
 */
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    const defaultOptions = {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    };
    
    return date.toLocaleDateString('ko-KR', { ...defaultOptions, ...options });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * 디바운스 함수
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 로컬 스토리지 헬퍼
 */
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Failed to save to localStorage:', error);
        }
    },
    
    get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Failed to read from localStorage:', error);
            return defaultValue;
        }
    },
    
    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Failed to remove from localStorage:', error);
        }
    }
};

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .nav-menu.active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--white);
        box-shadow: var(--shadow-md);
        padding: var(--spacing-lg);
        gap: var(--spacing-md);
    }
    
    .nav-toggle.active span:nth-child(1) {
        transform: rotate(-45deg) translate(-5px, 6px);
    }
    
    .nav-toggle.active span:nth-child(2) {
        opacity: 0;
    }
    
    .nav-toggle.active span:nth-child(3) {
        transform: rotate(45deg) translate(-5px, -6px);
    }
`;
document.head.appendChild(style);/**
 * 
테마 토글 초기화
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    
    if (!themeToggle) return;
    
    // 저장된 테마 불러오기 (기본값: light)
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // 토글 버튼 클릭 이벤트
    themeToggle.addEventListener('click', function() {
        const currentTheme = html.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
    });
    
    /**
     * 테마 설정
     * @param {string} theme - 'light' 또는 'dark'
     */
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // 버튼 상태 업데이트
        updateThemeButton(theme);
        
        // 테마 변경 애니메이션
        document.body.style.transition = 'background-color 0.3s ease, color 0.3s ease';
        
        // 메타 테마 컬러 업데이트 (모바일 브라우저용)
        updateMetaThemeColor(theme);
    }
    
    /**
     * 테마 버튼 상태 업데이트
     * @param {string} theme - 현재 테마
     */
    function updateThemeButton(theme) {
        const sunIcon = themeToggle.querySelector('.sun-icon');
        const moonIcon = themeToggle.querySelector('.moon-icon');
        
        if (theme === 'dark') {
            themeToggle.setAttribute('title', '라이트 모드로 변경');
            themeToggle.setAttribute('aria-label', '라이트 모드로 변경');
        } else {
            themeToggle.setAttribute('title', '다크 모드로 변경');
            themeToggle.setAttribute('aria-label', '다크 모드로 변경');
        }
    }
    
    /**
     * 메타 테마 컬러 업데이트
     * @param {string} theme - 현재 테마
     */
    function updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        // 테마에 따른 색상 설정
        const themeColors = {
            light: '#FFFFFF',
            dark: '#1A1A1A'
        };
        
        metaThemeColor.content = themeColors[theme];
    }
    
    // 시스템 테마 변경 감지 (선택사항)
    if (window.matchMedia) {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        // 저장된 테마가 없을 때만 시스템 테마 따라가기
        if (!localStorage.getItem('theme')) {
            setTheme(mediaQuery.matches ? 'dark' : 'light');
        }
        
        // 시스템 테마 변경 감지
        mediaQuery.addEventListener('change', function(e) {
            // 사용자가 수동으로 설정한 테마가 없을 때만 자동 변경
            if (!localStorage.getItem('theme-manual')) {
                setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
    
    // 수동 테마 변경 시 플래그 설정
    themeToggle.addEventListener('click', function() {
        localStorage.setItem('theme-manual', 'true');
    });
}

/**
 * 테마 관련 유틸리티 함수들
 */
window.ThemeUtils = {
    /**
     * 현재 테마 가져오기
     * @returns {string} 현재 테마 ('light' 또는 'dark')
     */
    getCurrentTheme: function() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    },
    
    /**
     * 다크모드 여부 확인
     * @returns {boolean} 다크모드 여부
     */
    isDarkMode: function() {
        return this.getCurrentTheme() === 'dark';
    },
    
    /**
     * 테마 변경 이벤트 리스너 추가
     * @param {function} callback - 테마 변경 시 실행할 콜백 함수
     */
    onThemeChange: function(callback) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'data-theme') {
                    const newTheme = document.documentElement.getAttribute('data-theme');
                    callback(newTheme);
                }
            });
        });
        
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    }
};