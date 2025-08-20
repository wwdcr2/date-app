"""데이터베이스 관리 스크립트"""

import click
from app.create_app import create_app
from app.utils.db_init import init_database, reset_database, seed_database
from app.extensions import db

app = create_app()

@click.group()
def cli():
    """데이터베이스 관리 명령어"""
    pass

@cli.command()
def init_db():
    """데이터베이스 초기화"""
    with app.app_context():
        if init_database():
            click.echo("데이터베이스가 성공적으로 초기화되었습니다.")
        else:
            click.echo("데이터베이스 초기화에 실패했습니다.")

@cli.command()
def reset_db():
    """데이터베이스 리셋"""
    if click.confirm('모든 데이터가 삭제됩니다. 계속하시겠습니까?'):
        with app.app_context():
            if reset_database():
                click.echo("데이터베이스가 성공적으로 리셋되었습니다.")
            else:
                click.echo("데이터베이스 리셋에 실패했습니다.")

@cli.command()
def seed_db():
    """초기 데이터 삽입"""
    with app.app_context():
        if seed_database():
            click.echo("초기 데이터가 성공적으로 삽입되었습니다.")
        else:
            click.echo("초기 데이터 삽입에 실패했습니다.")

@cli.command()
def setup_db():
    """데이터베이스 전체 설정 (초기화 + 시드 데이터)"""
    with app.app_context():
        click.echo("데이터베이스를 설정합니다...")
        if init_database() and seed_database():
            click.echo("✅ 데이터베이스 설정이 완료되었습니다!")
        else:
            click.echo("❌ 데이터베이스 설정에 실패했습니다.")

if __name__ == '__main__':
    cli()