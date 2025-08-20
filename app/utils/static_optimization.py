"""정적 파일 최적화 유틸리티"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from flask import current_app, request, make_response
from functools import wraps

class StaticFileOptimizer:
    """정적 파일 최적화 클래스"""
    
    @staticmethod
    def compress_static_files():
        """정적 파일들을 gzip으로 압축"""
        static_folder = current_app.static_folder
        
        # 압축할 파일 확장자
        compressible_extensions = ['.css', '.js', '.html', '.svg', '.json']
        
        compressed_count = 0
        
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                if file_ext in compressible_extensions:
                    gzip_path = file_path + '.gz'
                    
                    # 원본 파일이 더 최신이거나 gzip 파일이 없는 경우에만 압축
                    if (not os.path.exists(gzip_path) or 
                        os.path.getmtime(file_path) > os.path.getmtime(gzip_path)):
                        
                        try:
                            with open(file_path, 'rb') as f_in:
                                with gzip.open(gzip_path, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                            
                            compressed_count += 1
                            print(f"압축 완료: {file_path}")
                            
                        except Exception as e:
                            print(f"압축 실패 {file_path}: {e}")
        
        print(f"총 {compressed_count}개 파일이 압축되었습니다.")
        return compressed_count
    
    @staticmethod
    def add_cache_headers(response, max_age=3600):
        """응답에 캐시 헤더 추가"""
        response.headers['Cache-Control'] = f'public, max-age={max_age}'
        response.headers['Expires'] = (datetime.utcnow() + timedelta(seconds=max_age)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
    
    @staticmethod
    def add_compression_headers(response):
        """응답에 압축 관련 헤더 추가"""
        accept_encoding = request.headers.get('Accept-Encoding', '')
        
        if 'gzip' in accept_encoding:
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
        
        return response

def cache_control(max_age=3600):
    """캐시 제어 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            return StaticFileOptimizer.add_cache_headers(response, max_age)
        return decorated_function
    return decorator

def gzip_response(f):
    """gzip 압축 응답 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        
        # 이미 압축된 응답이거나 작은 응답은 건너뛰기
        if (response.headers.get('Content-Encoding') or 
            len(response.get_data()) < 1000):
            return response
        
        accept_encoding = request.headers.get('Accept-Encoding', '')
        
        if 'gzip' in accept_encoding:
            response.data = gzip.compress(response.get_data())
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)
        
        return response
    return decorated_function

class AssetVersioning:
    """정적 자산 버전 관리 클래스"""
    
    def __init__(self):
        self.version_map = {}
        self.load_version_map()
    
    def load_version_map(self):
        """버전 맵 로드 (파일 수정 시간 기반)"""
        static_folder = current_app.static_folder
        
        for root, dirs, files in os.walk(static_folder):
            for file in files:
                if file.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, static_folder)
                    
                    # 파일 수정 시간을 버전으로 사용
                    mtime = os.path.getmtime(file_path)
                    version = str(int(mtime))
                    
                    self.version_map[relative_path] = version
    
    def get_versioned_url(self, filename):
        """버전이 포함된 URL 반환"""
        version = self.version_map.get(filename, '1')
        return f"/static/{filename}?v={version}"
    
    def refresh_version(self, filename):
        """특정 파일의 버전 갱신"""
        static_folder = current_app.static_folder
        file_path = os.path.join(static_folder, filename)
        
        if os.path.exists(file_path):
            mtime = os.path.getmtime(file_path)
            version = str(int(mtime))
            self.version_map[filename] = version
            return version
        
        return None

# 전역 자산 버전 관리자
asset_versioning = None

def init_asset_versioning(app):
    """자산 버전 관리 초기화"""
    global asset_versioning
    
    with app.app_context():
        asset_versioning = AssetVersioning()
        
        # Jinja2 템플릿에서 사용할 수 있도록 함수 등록
        app.jinja_env.globals['versioned_url'] = asset_versioning.get_versioned_url

def optimize_images():
    """이미지 최적화 (기본적인 처리)"""
    from PIL import Image
    import os
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    optimized_count = 0
    
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                
                try:
                    with Image.open(file_path) as img:
                        # 이미지가 너무 큰 경우 리사이즈
                        max_size = (1920, 1080)
                        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                            img.thumbnail(max_size, Image.Resampling.LANCZOS)
                            
                            # 품질을 조정하여 저장
                            if file.lower().endswith('.jpg') or file.lower().endswith('.jpeg'):
                                img.save(file_path, 'JPEG', quality=85, optimize=True)
                            else:
                                img.save(file_path, 'PNG', optimize=True)
                            
                            optimized_count += 1
                            print(f"이미지 최적화 완료: {file_path}")
                
                except Exception as e:
                    print(f"이미지 최적화 실패 {file_path}: {e}")
    
    print(f"총 {optimized_count}개 이미지가 최적화되었습니다.")
    return optimized_count

def create_webp_versions():
    """업로드된 이미지의 WebP 버전 생성"""
    from PIL import Image
    import os
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    webp_count = 0
    
    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                webp_path = os.path.splitext(file_path)[0] + '.webp'
                
                # WebP 파일이 없거나 원본이 더 최신인 경우
                if (not os.path.exists(webp_path) or 
                    os.path.getmtime(file_path) > os.path.getmtime(webp_path)):
                    
                    try:
                        with Image.open(file_path) as img:
                            # RGB 모드로 변환 (WebP는 RGBA를 지원하지만 호환성을 위해)
                            if img.mode in ('RGBA', 'LA'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                                img = background
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # WebP로 저장 (품질 80)
                            img.save(webp_path, 'WebP', quality=80, optimize=True)
                            webp_count += 1
                            print(f"WebP 생성 완료: {webp_path}")
                    
                    except Exception as e:
                        print(f"WebP 생성 실패 {file_path}: {e}")
    
    print(f"총 {webp_count}개 WebP 이미지가 생성되었습니다.")
    return webp_count