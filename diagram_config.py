#!/usr/bin/env python3
"""
다이어그램 생성을 위한 공통 설정 및 유틸리티
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

class DiagramType(Enum):
    """다이어그램 타입 열거형"""
    ARCHITECTURE = "architecture"
    NETWORK = "network"
    SIMPLE = "simple"
    COST = "cost"
    TIMELINE = "timeline"

@dataclass
class DiagramConfig:
    """다이어그램 설정 클래스"""
    width: int = 14
    height: int = 10
    dpi: int = 300
    title_fontsize: int = 18
    subtitle_fontsize: int = 12
    text_fontsize: int = 10
    
@dataclass
class ColorPalette:
    """색상 팔레트 클래스"""
    aws_orange: str = '#FF9900'
    aws_blue: str = '#232F3E'
    light_blue: str = '#E8F4FD'
    light_green: str = '#E8F5E8'
    light_orange: str = '#FFF4E6'
    light_gray: str = '#F5F5F5'
    red: str = '#FF6B6B'
    green: str = '#4ECDC4'
    purple: str = '#9B59B6'
    
    def to_dict(self) -> Dict[str, str]:
        """딕셔너리로 변환"""
        return {
            'aws_orange': self.aws_orange,
            'aws_blue': self.aws_blue,
            'light_blue': self.light_blue,
            'light_green': self.light_green,
            'light_orange': self.light_orange,
            'light_gray': self.light_gray,
            'red': self.red,
            'green': self.green,
            'purple': self.purple
        }

class DiagramUtils:
    """다이어그램 생성 유틸리티 클래스"""
    
    @staticmethod
    def setup_matplotlib_korean():
        """한글 폰트 설정"""
        plt.rcParams['font.family'] = [
            'Arial Unicode MS', 'AppleGothic', 'Malgun Gothic', 'DejaVu Sans'
        ]
        plt.rcParams['axes.unicode_minus'] = False
    
    @staticmethod
    def setup_matplotlib_english():
        """영문 폰트 설정"""
        plt.rcParams['font.family'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    @staticmethod
    def create_base_figure(config: DiagramConfig) -> Tuple[plt.Figure, plt.Axes]:
        """기본 figure와 axes 생성"""
        fig, ax = plt.subplots(1, 1, figsize=(config.width, config.height))
        ax.set_xlim(0, config.width)
        ax.set_ylim(0, config.height)
        ax.axis('off')
        return fig, ax
    
    @staticmethod
    def create_rounded_box(
        position: Tuple[float, float],
        size: Tuple[float, float],
        colors: ColorPalette,
        face_color_key: str,
        edge_color_key: str,
        linewidth: int = 2
    ) -> FancyBboxPatch:
        """둥근 모서리 박스 생성"""
        color_dict = colors.to_dict()
        return FancyBboxPatch(
            position, size[0], size[1],
            boxstyle="round,pad=0.1",
            facecolor=color_dict[face_color_key],
            edgecolor=color_dict[edge_color_key],
            linewidth=linewidth
        )
    
    @staticmethod
    def create_rectangle_box(
        position: Tuple[float, float],
        size: Tuple[float, float],
        colors: ColorPalette,
        face_color_key: str,
        edge_color_key: str,
        linewidth: int = 2
    ) -> Rectangle:
        """사각형 박스 생성"""
        color_dict = colors.to_dict()
        return Rectangle(
            position, size[0], size[1],
            facecolor=color_dict[face_color_key],
            edgecolor=color_dict[edge_color_key],
            linewidth=linewidth
        )
    
    @staticmethod
    def add_connection_arrow(
        ax: plt.Axes,
        start: Tuple[float, float],
        end: Tuple[float, float],
        colors: ColorPalette,
        color_key: str = 'aws_blue',
        linewidth: int = 2,
        arrow_style: str = "->"
    ):
        """연결 화살표 추가"""
        color_dict = colors.to_dict()
        arrow = ConnectionPatch(
            start, end, "data", "data",
            arrowstyle=arrow_style,
            shrinkA=5, shrinkB=5,
            mutation_scale=20,
            fc=color_dict[color_key],
            ec=color_dict[color_key],
            linewidth=linewidth
        )
        ax.add_patch(arrow)
    
    @staticmethod
    def save_figure(
        fig: plt.Figure,
        filename: str,
        config: DiagramConfig,
        message: Optional[str] = None
    ):
        """figure 저장"""
        fig.savefig(
            filename,
            dpi=config.dpi,
            bbox_inches='tight',
            facecolor='white',
            edgecolor='none'
        )
        if message:
            print(message)
        else:
            print(f"다이어그램이 '{filename}'로 저장되었습니다.")

# 상수 정의
DEFAULT_CONFIG = DiagramConfig()
DEFAULT_COLORS = ColorPalette()

# AWS 서비스별 아이콘 매핑
AWS_ICONS = {
    'users': '👥',
    'cloudfront': '🌐',
    'alb': '⚖️',
    'ecs': '🐳',
    'rds': '🗄️',
    'elasticache': '⚡',
    's3': '📦',
    'security': '🔒',
    'monitoring': '📊'
}