/**
 * 실시간 알림 시스템 JavaScript
 */

class NotificationManager {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.notificationContainer = null;
        this.notificationBadge = null;
        this.notificationList = null;
        this.partnerStatus = null;
        
        this.init();
    }
    
    init() {
        // SocketIO 연결
        this.socket = io();
        
        // DOM 요소 찾기
        this.notificationContainer = document.getElementById('notification-container');
        this.notificationBadge = document.getElementById('notification-badge');
        this.notificationList = document.getElementById('notification-list');
        this.partnerStatus = document.getElementById('partner-status');
        
        // 이벤트 리스너 등록
        this.setupSocketEvents();
        this.setupUIEvents();
        
        // 알림 UI 생성
        this.createNotificationUI();
    }
    
    setupSocketEvents() {
        // 연결 성공
        this.socket.on('connect', () => {
            console.log('SocketIO 연결됨');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            
            // 커플 룸 참여
            this.socket.emit('join_couple_room');
            
            // 알림 목록 요청
            this.socket.emit('get_notifications');
        });
        
        // 연결 해제
        this.socket.on('disconnect', () => {
            console.log('SocketIO 연결 해제됨');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });
        
        // 새 알림 수신
        this.socket.on('new_notification', (data) => {
            this.handleNewNotification(data);
        });
        
        // 알림 개수 업데이트
        this.socket.on('notification_count', (data) => {
            this.updateNotificationBadge(data.count);
        });
        
        // 알림 목록 수신
        this.socket.on('notifications_list', (data) => {
            this.updateNotificationList(data.notifications);
        });
        
        // 파트너 상태 업데이트
        this.socket.on('partner_status', (data) => {
            this.updatePartnerStatus(data);
        });
        
        // 알림 읽음 처리 완료
        this.socket.on('notification_marked_read', (data) => {
            if (data.success) {
                this.markNotificationAsRead(data.notification_id);
            }
        });
    }
    
    setupUIEvents() {
        // 알림 버튼 클릭
        document.addEventListener('click', (e) => {
            if (e.target.matches('#notification-btn') || e.target.closest('#notification-btn')) {
                e.preventDefault();
                this.toggleNotificationPanel();
            }
            
            // 알림 항목 클릭
            if (e.target.matches('.notification-item') || e.target.closest('.notification-item')) {
                const notificationItem = e.target.closest('.notification-item');
                const notificationId = notificationItem.dataset.notificationId;
                if (notificationId && !notificationItem.classList.contains('read')) {
                    this.markNotificationRead(notificationId);
                }
            }
            
            // 알림 패널 외부 클릭 시 닫기
            if (!e.target.closest('#notification-container')) {
                this.closeNotificationPanel();
            }
        });
        
        // 페이지 로드 시 알림 권한 요청
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    createNotificationUI() {
        // 알림 버튼이 없으면 생성
        if (!document.getElementById('notification-btn')) {
            const navbar = document.querySelector('.nav-menu');
            if (navbar) {
                const notificationBtn = document.createElement('div');
                notificationBtn.id = 'notification-btn';
                notificationBtn.className = 'notification-btn';
                notificationBtn.innerHTML = `
                    <span class="notification-icon">🔔</span>
                    <span id="notification-badge" class="notification-badge" style="display: none;">0</span>
                `;
                
                // 로그아웃 링크 앞에 삽입
                const logoutLink = navbar.querySelector('a[href*="logout"]');
                if (logoutLink) {
                    navbar.insertBefore(notificationBtn, logoutLink);
                } else {
                    navbar.appendChild(notificationBtn);
                }
                
                this.notificationBadge = document.getElementById('notification-badge');
            }
        }
        
        // 알림 패널이 없으면 생성
        if (!document.getElementById('notification-container')) {
            const notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.className = 'notification-container';
            notificationContainer.style.display = 'none';
            notificationContainer.innerHTML = `
                <div class="notification-header">
                    <h3>알림</h3>
                    <div id="connection-status" class="connection-status">
                        <span class="status-dot offline"></span>
                        <span class="status-text">연결 중...</span>
                    </div>
                </div>
                <div id="partner-status" class="partner-status" style="display: none;">
                    <span class="partner-name"></span>
                    <span class="partner-status-dot"></span>
                </div>
                <div id="notification-list" class="notification-list">
                    <div class="loading">알림을 불러오는 중...</div>
                </div>
            `;
            
            document.body.appendChild(notificationContainer);
            this.notificationContainer = notificationContainer;
            this.notificationList = document.getElementById('notification-list');
            this.partnerStatus = document.getElementById('partner-status');
        }
    }
    
    handleNewNotification(data) {
        console.log('새 알림 수신:', data);
        
        // 브라우저 알림 표시
        this.showBrowserNotification(data);
        
        // 토스트 알림 표시
        this.showToastNotification(data);
        
        // 알림 목록 새로고침
        this.socket.emit('get_notifications');
    }
    
    showBrowserNotification(data) {
        if ('Notification' in window && Notification.permission === 'granted') {
            const notification = new Notification(data.title, {
                body: data.content,
                icon: '/static/images/favicon.svg',
                tag: `notification-${data.id}`
            });
            
            // 3초 후 자동 닫기
            setTimeout(() => {
                notification.close();
            }, 3000);
        }
    }
    
    showToastNotification(data) {
        // 토스트 알림 생성
        const toast = document.createElement('div');
        toast.className = 'toast-notification';
        toast.innerHTML = `
            <div class="toast-icon">${data.icon}</div>
            <div class="toast-content">
                <div class="toast-title">${data.title}</div>
                <div class="toast-message">${data.content}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        // 토스트 컨테이너가 없으면 생성
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toast);
        
        // 애니메이션
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        // 닫기 버튼 이벤트
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.removeToast(toast);
        });
        
        // 5초 후 자동 제거
        setTimeout(() => {
            this.removeToast(toast);
        }, 5000);
    }
    
    removeToast(toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    updateNotificationBadge(count) {
        if (this.notificationBadge) {
            if (count > 0) {
                this.notificationBadge.textContent = count > 99 ? '99+' : count;
                this.notificationBadge.style.display = 'block';
            } else {
                this.notificationBadge.style.display = 'none';
            }
        }
    }
    
    updateNotificationList(notifications) {
        if (!this.notificationList) return;
        
        if (notifications.length === 0) {
            this.notificationList.innerHTML = '<div class="no-notifications">알림이 없습니다.</div>';
            return;
        }
        
        const notificationHTML = notifications.map(notification => `
            <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" 
                 data-notification-id="${notification.id}">
                <div class="notification-icon" style="color: ${notification.color}">
                    ${notification.icon}
                </div>
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.content}</div>
                    <div class="notification-time">${notification.formatted_time}</div>
                </div>
                ${!notification.is_read ? '<div class="unread-dot"></div>' : ''}
            </div>
        `).join('');
        
        this.notificationList.innerHTML = notificationHTML;
    }
    
    updatePartnerStatus(data) {
        if (!this.partnerStatus) return;
        
        const partnerName = this.partnerStatus.querySelector('.partner-name');
        const statusDot = this.partnerStatus.querySelector('.partner-status-dot');
        
        if (partnerName && statusDot) {
            partnerName.textContent = data.partner_name;
            statusDot.className = `partner-status-dot ${data.status}`;
            statusDot.title = data.status === 'online' ? '온라인' : '오프라인';
            this.partnerStatus.style.display = 'flex';
        }
    }
    
    updateConnectionStatus(connected) {
        const connectionStatus = document.getElementById('connection-status');
        if (connectionStatus) {
            const statusDot = connectionStatus.querySelector('.status-dot');
            const statusText = connectionStatus.querySelector('.status-text');
            
            if (connected) {
                statusDot.className = 'status-dot online';
                statusText.textContent = '연결됨';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = '연결 끊김';
            }
        }
    }
    
    toggleNotificationPanel() {
        if (this.notificationContainer) {
            const isVisible = this.notificationContainer.style.display !== 'none';
            this.notificationContainer.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                // 패널을 열 때 알림 목록 새로고침
                this.socket.emit('get_notifications');
            }
        }
    }
    
    closeNotificationPanel() {
        if (this.notificationContainer) {
            this.notificationContainer.style.display = 'none';
        }
    }
    
    markNotificationRead(notificationId) {
        this.socket.emit('mark_notification_read', {
            notification_id: parseInt(notificationId)
        });
    }
    
    markNotificationAsRead(notificationId) {
        const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
        if (notificationItem) {
            notificationItem.classList.remove('unread');
            notificationItem.classList.add('read');
            
            const unreadDot = notificationItem.querySelector('.unread-dot');
            if (unreadDot) {
                unreadDot.remove();
            }
        }
    }
}

// 페이지 로드 시 알림 매니저 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 로그인된 사용자만 알림 시스템 활성화
    if (document.body.dataset.userAuthenticated === 'true') {
        window.notificationManager = new NotificationManager();
    }
});