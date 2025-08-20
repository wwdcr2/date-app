#!/usr/bin/env python3
"""
커플 웹 애플리케이션 AWS 아키텍처 간단 다이어그램
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import numpy as np

# 기본 폰트 설정
plt.rcParams['font.family'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_simple_aws_diagram():
    """간단한 AWS 아키텍처 다이어그램"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 색상 정의
    colors = {
        'orange': '#FF9900',
        'blue': '#232F3E', 
        'light_blue': '#E8F4FD',
        'light_green': '#E8F5E8',
        'light_orange': '#FFF4E6',
        'light_gray': '#F5F5F5',
        'red': '#FF6B6B',
        'green': '#4ECDC4'
    }
    
    # 제목
    ax.text(7, 9.5, 'Couple Web App - AWS Architecture', 
            fontsize=18, fontweight='bold', ha='center')
    
    # 사용자
    user_rect = Rectangle((6, 8.5), 2, 0.6, facecolor=colors['light_gray'], 
                         edgecolor='black', linewidth=2)
    ax.add_patch(user_rect)
    ax.text(7, 8.8, 'Users', fontsize=12, fontweight='bold', ha='center')
    
    # CloudFront
    cf_rect = Rectangle((5, 7.2), 4, 0.8, facecolor=colors['light_orange'], 
                       edgecolor=colors['orange'], linewidth=2)
    ax.add_patch(cf_rect)
    ax.text(7, 7.6, 'CloudFront CDN', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, 7.3, 'Global Content Delivery', fontsize=10, ha='center')
    
    # Application Load Balancer
    alb_rect = Rectangle((5, 6), 4, 0.8, facecolor=colors['light_blue'], 
                        edgecolor=colors['blue'], linewidth=2)
    ax.add_patch(alb_rect)
    ax.text(7, 6.4, 'Application Load Balancer', fontsize=12, fontweight='bold', ha='center')
    ax.text(7, 6.1, 'HTTPS, Health Checks', fontsize=10, ha='center')
    
    # ECS Fargate
    ecs_rect = Rectangle((1, 4), 12, 1.5, facecolor=colors['light_green'], 
                        edgecolor=colors['green'], linewidth=2)
    ax.add_patch(ecs_rect)
    ax.text(7, 5.2, 'ECS Fargate Cluster', fontsize=14, fontweight='bold', ha='center')
    
    # Flask 컨테이너들
    containers = [(2.5, 4.5), (5.5, 4.5), (8.5, 4.5), (11.5, 4.5)]
    for i, (x, y) in enumerate(containers):
        container_rect = Rectangle((x-0.6, y-0.2), 1.2, 0.4, 
                                 facecolor='white', edgecolor=colors['green'], linewidth=1)
        ax.add_patch(container_rect)
        ax.text(x, y, f'Flask {i+1}', fontsize=9, ha='center')
    
    # 데이터베이스 계층
    db_rect = Rectangle((1, 2), 5, 1.5, facecolor=colors['light_blue'], 
                       edgecolor=colors['blue'], linewidth=2)
    ax.add_patch(db_rect)
    ax.text(3.5, 3.2, 'Amazon RDS', fontsize=12, fontweight='bold', ha='center')
    ax.text(3.5, 2.9, 'PostgreSQL Multi-AZ', fontsize=11, ha='center')
    ax.text(3.5, 2.6, 'Auto Backup & Encryption', fontsize=10, ha='center')
    ax.text(3.5, 2.3, 'Performance Insights', fontsize=10, ha='center')
    
    # ElastiCache
    cache_rect = Rectangle((8, 2), 5, 1.5, facecolor=colors['light_orange'], 
                          edgecolor=colors['red'], linewidth=2)
    ax.add_patch(cache_rect)
    ax.text(10.5, 3.2, 'ElastiCache Redis', fontsize=12, fontweight='bold', ha='center')
    ax.text(10.5, 2.9, 'Session Store', fontsize=11, ha='center')
    ax.text(10.5, 2.6, 'Real-time Messaging', fontsize=10, ha='center')
    ax.text(10.5, 2.3, 'Application Cache', fontsize=10, ha='center')
    
    # S3 스토리지
    s3_rect = Rectangle((1, 0.2), 5, 1.2, facecolor='#E8F8E8', 
                       edgecolor=colors['green'], linewidth=2)
    ax.add_patch(s3_rect)
    ax.text(3.5, 1.1, 'Amazon S3', fontsize=12, fontweight='bold', ha='center')
    ax.text(3.5, 0.8, 'Image & File Storage', fontsize=11, ha='center')
    ax.text(3.5, 0.5, 'Versioning & Lifecycle', fontsize=10, ha='center')
    
    # 보안 & 모니터링
    security_rect = Rectangle((8, 0.2), 5, 1.2, facecolor='#FFE8E8', 
                             edgecolor=colors['red'], linewidth=2)
    ax.add_patch(security_rect)
    ax.text(10.5, 1.1, 'Security & Monitoring', fontsize=12, fontweight='bold', ha='center')
    ax.text(10.5, 0.8, 'WAF, Shield, CloudWatch', fontsize=11, ha='center')
    ax.text(10.5, 0.5, 'X-Ray, Secrets Manager', fontsize=10, ha='center')
    
    # 연결선 그리기
    connections = [
        # 사용자 -> CloudFront
        ((7, 8.5), (7, 8.0)),
        # CloudFront -> ALB
        ((7, 7.2), (7, 6.8)),
        # ALB -> ECS
        ((7, 6.0), (7, 5.5)),
        # ECS -> RDS
        ((5, 4.0), (3.5, 3.5)),
        # ECS -> ElastiCache
        ((9, 4.0), (10.5, 3.5)),
        # ECS -> S3
        ((4, 4.0), (3.5, 1.4)),
        # CloudFront -> S3 (정적 파일)
        ((6, 7.6), (3.5, 1.4)),
    ]
    
    for start, end in connections:
        arrow = ConnectionPatch(start, end, "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc=colors['blue'], 
                               ec=colors['blue'], linewidth=1.5)
        ax.add_patch(arrow)
    
    # 범례
    legend_elements = [
        patches.Patch(color=colors['light_orange'], label='CDN & Load Balancer'),
        patches.Patch(color=colors['light_green'], label='Container Services'),
        patches.Patch(color=colors['light_blue'], label='Database'),
        patches.Patch(color='#E8F8E8', label='Storage'),
        patches.Patch(color='#FFE8E8', label='Security & Monitoring')
    ]
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
    
    plt.tight_layout()
    return fig

def create_cost_breakdown_chart():
    """비용 분석 차트"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 소규모 구성 비용
    services_small = ['ECS Fargate', 'RDS PostgreSQL', 'ElastiCache', 'ALB', 'S3', 'CloudFront', 'Others']
    costs_small = [60, 15, 15, 20, 5, 10, 15]
    colors_small = ['#FF9900', '#232F3E', '#FF6B6B', '#4ECDC4', '#2ECC71', '#9B59B6', '#95A5A6']
    
    ax1.pie(costs_small, labels=services_small, colors=colors_small, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Small Scale Configuration\n(~$140/month)', fontsize=14, fontweight='bold')
    
    # 중간 규모 구성 비용
    services_medium = ['ECS Fargate', 'RDS PostgreSQL', 'ElastiCache', 'CloudFront', 'S3', 'ALB', 'Others']
    costs_medium = [240, 60, 60, 85, 25, 20, 30]
    colors_medium = ['#FF9900', '#232F3E', '#FF6B6B', '#9B59B6', '#2ECC71', '#4ECDC4', '#95A5A6']
    
    ax2.pie(costs_medium, labels=services_medium, colors=colors_medium, autopct='%1.1f%%', startangle=90)
    ax2.set_title('Medium Scale Configuration\n(~$520/month)', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_deployment_timeline():
    """배포 타임라인 차트"""
    
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    
    phases = [
        'Phase 1: Infrastructure Setup',
        'Phase 2: Application Containerization', 
        'Phase 3: ECS Service Deployment',
        'Phase 4: CDN & Domain Setup',
        'Phase 5: Monitoring & Optimization'
    ]
    
    tasks = [
        ['VPC & Subnets', 'RDS Setup', 'S3 Buckets', 'ElastiCache'],
        ['Dockerfile', 'Environment Config', 'DB Migration', 'ECR Push'],
        ['ECS Cluster', 'ALB Setup', 'Auto Scaling', 'Health Checks'],
        ['CloudFront', 'Route 53', 'SSL Certificate', 'WAF Rules'],
        ['CloudWatch', 'Alarms', 'Performance Tuning', 'Backup Plan']
    ]
    
    durations = [5, 7, 4, 3, 6]  # days
    colors = ['#FF9900', '#232F3E', '#4ECDC4', '#9B59B6', '#2ECC71']
    
    y_pos = np.arange(len(phases))
    
    # 가로 막대 그래프
    bars = ax.barh(y_pos, durations, color=colors, alpha=0.7)
    
    # 각 단계별 작업 내용 추가
    for i, (bar, task_list) in enumerate(zip(bars, tasks)):
        # 막대 안에 작업 내용 표시
        ax.text(bar.get_width()/2, bar.get_y() + bar.get_height()/2, 
                ' • '.join(task_list[:2]), ha='center', va='center', 
                fontsize=9, fontweight='bold')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(phases)
    ax.set_xlabel('Duration (Days)', fontsize=12)
    ax.set_title('AWS Migration Timeline (Total: ~25 Days)', fontsize=16, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # 누적 일수 표시
    cumulative = 0
    for i, duration in enumerate(durations):
        cumulative += duration
        ax.text(duration + 0.2, i, f'Day {cumulative}', va='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # 메인 아키텍처 다이어그램
    fig1 = create_simple_aws_diagram()
    fig1.savefig('aws_architecture_simple.png', dpi=300, bbox_inches='tight', 
                 facecolor='white', edgecolor='none')
    print("간단한 아키텍처 다이어그램이 'aws_architecture_simple.png'로 저장되었습니다.")
    
    # 비용 분석 차트
    fig2 = create_cost_breakdown_chart()
    fig2.savefig('aws_cost_breakdown.png', dpi=300, bbox_inches='tight', 
                 facecolor='white', edgecolor='none')
    print("비용 분석 차트가 'aws_cost_breakdown.png'로 저장되었습니다.")
    
    # 배포 타임라인
    fig3 = create_deployment_timeline()
    fig3.savefig('aws_deployment_timeline.png', dpi=300, bbox_inches='tight', 
                 facecolor='white', edgecolor='none')
    print("배포 타임라인이 'aws_deployment_timeline.png'로 저장되었습니다.")
    
    plt.show()