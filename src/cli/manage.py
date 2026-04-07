import asyncio
import secrets

import click

from src.core.database import AsyncSessionLocal
from src.models.analysis import SafeDomain, KnownPattern, ApiKey
from src.services.auth_service import hash_api_key, create_api_key
from src.services.seed_data import seed_safe_domains, seed_known_patterns
from sqlalchemy import select, delete


def run_async(coro):
    asyncio.run(coro)


@click.group()
def cli():
    """Smishing Detection Agent 관리 CLI"""
    pass


@cli.group()
def whitelist():
    """안전 도메인 화이트리스트 관리"""
    pass


@whitelist.command("add")
@click.argument("domain")
@click.option("--category", default="custom", help="도메인 카테고리")
def whitelist_add(domain: str, category: str):
    """화이트리스트에 도메인 추가"""
    async def _add():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SafeDomain).where(SafeDomain.domain == domain))
            if result.scalar_one_or_none():
                click.echo(f"이미 존재: {domain}")
                return
            db.add(SafeDomain(domain=domain, category=category))
            await db.commit()
            click.echo(f"추가 완료: {domain} ({category})")
    run_async(_add())


@whitelist.command("remove")
@click.argument("domain")
def whitelist_remove(domain: str):
    """화이트리스트에서 도메인 제거"""
    async def _remove():
        async with AsyncSessionLocal() as db:
            await db.execute(delete(SafeDomain).where(SafeDomain.domain == domain))
            await db.commit()
            click.echo(f"제거 완료: {domain}")
    run_async(_remove())


@whitelist.command("list")
def whitelist_list():
    """화이트리스트 목록 조회"""
    async def _list():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(SafeDomain).where(SafeDomain.is_active == True))
            domains = result.scalars().all()
            for d in domains:
                click.echo(f"  {d.domain} ({d.category})")
            click.echo(f"\n총 {len(domains)}개")
    run_async(_list())


@cli.group()
def blacklist():
    """블랙리스트 도메인 관리"""
    pass


@blacklist.command("add")
@click.argument("domain")
@click.option("--category", default="custom", help="카테고리")
@click.option("--risk", default="HIGH", type=click.Choice(["HIGH", "WARNING"]))
def blacklist_add(domain: str, category: str, risk: str):
    """블랙리스트에 도메인 추가"""
    async def _add():
        async with AsyncSessionLocal() as db:
            db.add(KnownPattern(
                pattern_type="DOMAIN",
                pattern_value=domain,
                risk_level=risk,
                category=category,
                description=f"CLI로 추가됨",
            ))
            await db.commit()
            click.echo(f"블랙리스트 추가: {domain} ({risk})")
    run_async(_add())


@blacklist.command("list")
def blacklist_list():
    """블랙리스트 목록 조회"""
    async def _list():
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(KnownPattern).where(
                    KnownPattern.pattern_type == "DOMAIN",
                    KnownPattern.is_active == True,
                )
            )
            patterns = result.scalars().all()
            for p in patterns:
                click.echo(f"  {p.pattern_value} [{p.risk_level}] ({p.category})")
            click.echo(f"\n총 {len(patterns)}개")
    run_async(_list())


@cli.group()
def apikey():
    """API Key 관리"""
    pass


@apikey.command("create")
@click.argument("name")
@click.option("--rate-limit", default=60, help="분당 요청 제한")
def apikey_create(name: str, rate_limit: int):
    """새 API Key 발급"""
    raw_key = f"sk-smish-{secrets.token_hex(24)}"

    async def _create():
        async with AsyncSessionLocal() as db:
            await create_api_key(db, name, raw_key, rate_limit)
            await db.commit()
            click.echo(f"API Key 생성 완료:")
            click.echo(f"  이름: {name}")
            click.echo(f"  키: {raw_key}")
            click.echo(f"  Rate Limit: {rate_limit}/min")
            click.echo(f"\n이 키를 안전한 곳에 저장하세요. 다시 조회할 수 없습니다.")
    run_async(_create())


@apikey.command("list")
def apikey_list():
    """API Key 목록 조회"""
    async def _list():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ApiKey))
            keys = result.scalars().all()
            for k in keys:
                status = "활성" if k.is_active else "비활성"
                click.echo(f"  {k.name} [{status}] 사용량:{k.total_usage} (id:{k.id[:8]}...)")
            click.echo(f"\n총 {len(keys)}개")
    run_async(_list())


@apikey.command("revoke")
@click.argument("key_id")
def apikey_revoke(key_id: str):
    """API Key 비활성화 (긴급 폐기)"""
    async def _revoke():
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ApiKey).where(ApiKey.id.startswith(key_id)))
            key = result.scalar_one_or_none()
            if key is None:
                click.echo(f"Key not found: {key_id}")
                return
            key.is_active = False
            await db.commit()
            click.echo(f"비활성화 완료: {key.name}")
    run_async(_revoke())


@cli.command("seed")
def seed():
    """화이트리스트/패턴 DB 시딩"""
    async def _seed():
        async with AsyncSessionLocal() as db:
            await seed_safe_domains(db)
            await seed_known_patterns(db)
            await db.commit()
            click.echo("시딩 완료")
    run_async(_seed())


if __name__ == "__main__":
    cli()
