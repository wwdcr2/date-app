/**
 * UI 유틸리티 함수들
 */

class UIUtils {
    constructor() {
        this.init();
    }
    
    init() {
        this.setupFormValidation();
        this.setupLoadingStates();
        this.setupTooltips();
        this.setupConfirmDialogs();
        this.setupImagePreviews();
        this.setupAutoSave();
    }
    
    // 폼 검증 설정
    setupFormValidation() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM' && form.hasAttribute('data-validate')) {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            }
        });
        
        // 실시간 검증
        document.addEventListener('input', (e) => {
            if (e.target.hasAttribute('data-validate')) {
                this.validateField(e.target);
            }
        });
        
        document.addEventListener('blur', (e) => {
            if (e.target.hasAttribute('data-validate')) {
                this.validateField(e.target);
            }
        });
    }
    
    // 폼 검증
    validateForm(form) {
        let isValid = true;
        const fields = form.querySelectorAll('[data-validate]');
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // 필드 검증
    validateField(field) {
        const rules = field.dataset.validate.split('|');
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        for (const rule of rules) {
            const [ruleName, ruleValue] = rule.split(':');
            
            switch (ruleName) {
                case 'required':
                    if (!value) {
                        isValid = false;
                        errorMessage = '이 필드는 필수입니다.';
                    }
                    break;
                    
                case 'email':
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    if (value && !emailRegex.test(value)) {
                        isValid = false;
                        errorMessage = '올바른 이메일 주소를 입력해주세요.';
                    }
                    break;
                    
                case 'min':
                    if (value && value.length < parseInt(ruleValue)) {
                        isValid = false;
                        errorMessage = `최소 ${ruleValue}자 이상 입력해주세요.`;
                    }
                    break;
                    
                case 'max':
                    if (value && value.length > parseInt(ruleValue)) {
                        isValid = false;
                        errorMessage = `최대 ${ruleValue}자까지 입력 가능합니다.`;
                    }
                    break;
                    
                case 'match':
                    const matchField = document.querySelector(`[name="${ruleValue}"]`);
                    if (matchField && value !== matchField.value) {
                        isValid = false;
                        errorMessage = '비밀번호가 일치하지 않습니다.';
                    }
                    break;
                    
                case 'date':
                    if (value) {
                        const date = new Date(value);
                        if (isNaN(date.getTime())) {
                            isValid = false;
                            errorMessage = '올바른 날짜를 입력해주세요.';
                        }
                    }
                    break;
                    
                case 'future':
                    if (value) {
                        const date = new Date(value);
                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        if (date <= today) {
                            isValid = false;
                            errorMessage = '미래 날짜를 선택해주세요.';
                        }
                    }
                    break;
                    
                case 'past':
                    if (value) {
                        const date = new Date(value);
                        const today = new Date();
                        today.setHours(23, 59, 59, 999);
                        if (date > today) {
                            isValid = false;
                            errorMessage = '과거 또는 오늘 날짜를 선택해주세요.';
                        }
                    }
                    break;
            }
            
            if (!isValid) break;
        }
        
        this.showFieldValidation(field, isValid, errorMessage);
        return isValid;
    }
    
    // 필드 검증 결과 표시
    showFieldValidation(field, isValid, errorMessage) {
        const formGroup = field.closest('.form-group');
        if (!formGroup) return;
        
        // 기존 에러 메시지 제거
        const existingError = formGroup.querySelector('.form-error');
        if (existingError) {
            existingError.remove();
        }
        
        // 필드 스타일 업데이트
        field.classList.remove('error', 'success');
        
        if (!isValid && errorMessage) {
            field.classList.add('error');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'form-error';
            errorDiv.textContent = errorMessage;
            formGroup.appendChild(errorDiv);
        } else if (field.value.trim()) {
            field.classList.add('success');
        }
    }
    
    // 로딩 상태 설정
    setupLoadingStates() {
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.tagName === 'FORM') {
                const submitBtn = form.querySelector('button[type="submit"], input[type="submit"]');
                if (submitBtn) {
                    this.setLoadingState(submitBtn, true);
                }
            }
        });
        
        // AJAX 요청 시 로딩 상태
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-loading')) {
                this.setLoadingState(e.target, true);
            }
        });
    }
    
    // 로딩 상태 설정/해제
    setLoadingState(element, loading) {
        if (loading) {
            element.disabled = true;
            element.dataset.originalText = element.textContent;
            element.innerHTML = '<span class="loading-spinner"></span> 처리 중...';
            element.classList.add('loading');
        } else {
            element.disabled = false;
            element.textContent = element.dataset.originalText || element.textContent;
            element.classList.remove('loading');
        }
    }
    
    // 툴팁 설정
    setupTooltips() {
        document.addEventListener('mouseenter', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            }
        });
        
        document.addEventListener('mouseleave', (e) => {
            if (e.target.hasAttribute('data-tooltip')) {
                this.hideTooltip();
            }
        });
    }
    
    // 툴팁 표시
    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }
    
    // 툴팁 숨기기
    hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }
    
    // 확인 대화상자 설정
    setupConfirmDialogs() {
        document.addEventListener('click', (e) => {
            if (e.target.hasAttribute('data-confirm')) {
                const message = e.target.dataset.confirm;
                if (!confirm(message)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }
    
    // 이미지 미리보기 설정
    setupImagePreviews() {
        document.addEventListener('change', (e) => {
            if (e.target.type === 'file' && e.target.accept && e.target.accept.includes('image')) {
                this.handleImagePreview(e.target);
            }
        });
    }
    
    // 이미지 미리보기 처리
    handleImagePreview(input) {
        const file = input.files[0];
        if (!file) return;
        
        // 파일 크기 체크 (5MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('파일 크기는 5MB 이하여야 합니다.');
            input.value = '';
            return;
        }
        
        // 이미지 타입 체크
        if (!file.type.startsWith('image/')) {
            alert('이미지 파일만 업로드 가능합니다.');
            input.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            let preview = input.parentNode.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview';
                input.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <img src="${e.target.result}" alt="미리보기" style="max-width: 200px; max-height: 200px; border-radius: 8px; margin-top: 10px;">
                <button type="button" class="btn-remove-image" onclick="this.parentNode.remove(); this.parentNode.parentNode.querySelector('input[type=file]').value = '';">제거</button>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    // 자동 저장 설정
    setupAutoSave() {
        const autoSaveFields = document.querySelectorAll('[data-autosave]');
        autoSaveFields.forEach(field => {
            let timeout;
            field.addEventListener('input', () => {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    this.autoSave(field);
                }, 2000); // 2초 후 자동 저장
            });
        });
    }
    
    // 자동 저장 실행
    autoSave(field) {
        const key = field.dataset.autosave;
        const value = field.value;
        
        try {
            localStorage.setItem(`autosave_${key}`, value);
            this.showAutoSaveIndicator(field);
        } catch (e) {
            console.warn('자동 저장 실패:', e);
        }
    }
    
    // 자동 저장 표시
    showAutoSaveIndicator(field) {
        let indicator = field.parentNode.querySelector('.autosave-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.className = 'autosave-indicator';
            field.parentNode.appendChild(indicator);
        }
        
        indicator.textContent = '자동 저장됨';
        indicator.style.opacity = '1';
        
        setTimeout(() => {
            indicator.style.opacity = '0';
        }, 2000);
    }
    
    // 자동 저장된 데이터 복원
    restoreAutoSave() {
        const autoSaveFields = document.querySelectorAll('[data-autosave]');
        autoSaveFields.forEach(field => {
            const key = field.dataset.autosave;
            const saved = localStorage.getItem(`autosave_${key}`);
            if (saved && !field.value) {
                field.value = saved;
            }
        });
    }
    
    // 모달 관련 유틸리티
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }
    
    // 알림 표시
    showAlert(message, type = 'info', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `flash-message flash-${type}`;
        alert.innerHTML = `
            <span class="flash-text">${message}</span>
            <button class="flash-close" onclick="this.parentElement.remove()">&times;</button>
        `;
        
        let container = document.querySelector('.flash-messages');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-messages';
            document.body.appendChild(container);
        }
        
        container.appendChild(alert);
        
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
    }
    
    // 페이지 로딩 표시
    showPageLoading() {
        const loader = document.createElement('div');
        loader.id = 'page-loader';
        loader.className = 'page-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="loading-spinner"></div>
                <p>로딩 중...</p>
            </div>
        `;
        document.body.appendChild(loader);
    }
    
    hidePageLoading() {
        const loader = document.getElementById('page-loader');
        if (loader) {
            loader.remove();
        }
    }
    
    // 스크롤 위치 복원
    saveScrollPosition() {
        sessionStorage.setItem('scrollPosition', window.scrollY);
    }
    
    restoreScrollPosition() {
        const scrollPosition = sessionStorage.getItem('scrollPosition');
        if (scrollPosition) {
            window.scrollTo(0, parseInt(scrollPosition));
            sessionStorage.removeItem('scrollPosition');
        }
    }
    
    // 클립보드 복사
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showAlert('클립보드에 복사되었습니다.', 'success', 2000);
            return true;
        } catch (err) {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                this.showAlert('클립보드에 복사되었습니다.', 'success', 2000);
                return true;
            } catch (err) {
                this.showAlert('복사에 실패했습니다.', 'error');
                return false;
            } finally {
                document.body.removeChild(textArea);
            }
        }
    }
    
    // 디바운스 함수
    debounce(func, wait) {
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
    
    // 스로틀 함수
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// 전역 인스턴스 생성
window.uiUtils = new UIUtils();

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 자동 저장된 데이터 복원
    window.uiUtils.restoreAutoSave();
    
    // 스크롤 위치 복원
    window.uiUtils.restoreScrollPosition();
    
    // 페이지 언로드 시 스크롤 위치 저장
    window.addEventListener('beforeunload', () => {
        window.uiUtils.saveScrollPosition();
    });
    
    // 모달 외부 클릭 시 닫기
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
            document.body.style.overflow = '';
        }
    });
    
    // ESC 키로 모달 닫기
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal[style*="flex"]');
            if (openModal) {
                openModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        }
    });
});