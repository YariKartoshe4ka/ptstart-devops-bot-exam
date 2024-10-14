from os import getenv
import re
import logging
from tempfile import mkstemp

from aiogram import Router, html
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile
import paramiko
from html import escape

from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

ANSI_ESCAPE_REGEX = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
PACKAGE_NAME_REGEX = re.compile(r'[\w\d\-\.]+')


router = Router()


def get_ssh_shell(host, username, password, port):
    cl = paramiko.client.SSHClient()
    cl.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    cl.connect(host, username=username, password=password, port=port)
    return cl

def chunkify(data):
    res = ''
    for line in data.split('\n'):
        line = line.rstrip() + '\n'

        if len(res + line) > 3072:
            yield res
            res = ''

        res += line

    yield res

async def send_command(cmd, host=None, username=None, password=None, port=None):
    host = host or getenv("RM_HOST")
    username = username or getenv("RM_USER")
    password = password or getenv("RM_PASSWORD")
    port = port or getenv("RM_PORT")

    logging.info(f"Command executed: '{cmd}'")

    cl = get_ssh_shell(host, username, password, port)
    stdin, stdout, stderr = cl.exec_command(cmd)
    stdout.channel.set_combine_stderr(True)

    output = stdout.read().decode()
    return escape(ANSI_ESCAPE_REGEX.sub('', output))


@router.message(Command('get_release'))
async def command_get_release(message: Message) -> None:
    for block in chunkify(await send_command('cat /etc/os-release')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_uname'))
async def command_get_uname(message: Message) -> None:
    for block in chunkify(await send_command('uname -a')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_uptime'))
async def command_get_uptime(message: Message) -> None:
    for block in chunkify(await send_command('uptime')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_df'))
async def command_get_df(message: Message) -> None:
    for block in chunkify(await send_command('df -h')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_free'))
async def command_get_free(message: Message) -> None:
    for block in chunkify(await send_command('free')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_mpstat'))
async def command_get_mpstat(message: Message) -> None:
    for block in chunkify(await send_command('mpstat')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_w'))
async def command_get_w(message: Message) -> None:
    for block in chunkify(await send_command('w')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_auths'))
async def command_get_ss(message: Message) -> None:
    res = await send_command('last')
    res = '\n'.join(res.split('\n')[:10])
    for block in chunkify(res):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_critical'))
async def command_get_critical(message: Message) -> None:
    for block in chunkify(await send_command('journalctl -p crit -n 5')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_ps'))
async def command_get_ps(message: Message) -> None:
    for block in chunkify(await send_command('ps auxf')):
        await message.answer(html.pre_language(block, language='plain'))

@router.message(Command('get_ss'))
async def command_get_ss(message: Message) -> None:
    for block in chunkify(await send_command('ss -ntulp')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_apt_list'))
async def command_get_apt_list(message: Message, command: CommandObject) -> None:
    arg = command.args
    if (arg is None or PACKAGE_NAME_REGEX.search(arg) is None):
        _, tmp_file = mkstemp()
        with open(tmp_file, 'w') as file:
            file.write(await send_command('apt list --installed 2>/dev/null'))

        await message.answer_document(FSInputFile(tmp_file, 'packages.txt'), caption='Список установленных пакетов')
    
    else:
        await message.answer(html.pre_language(await send_command(f'apt show {arg} 2>/dev/null'), 'plain'))

@router.message(Command('get_services'))
async def command_get_services(message: Message) -> None:
    for block in chunkify(await send_command('service --status-all')):
        await message.answer(html.pre_language(block, 'plain'))

@router.message(Command('get_repl_logs'))
async def command_get_repl_logs(message: Message) -> None:
    engine = create_async_engine(
        url=URL.create(
            'postgresql+asyncpg',
            username='postgres',
            password='LVnnQfM3YmXB',
            host=getenv('DB_HOST'),
            port=getenv('DB_PORT'),
        ),
        echo=True
    )

    async with engine.begin() as conn:
        query = text("SELECT pg_read_file('/var/log/postgresql/postgresql.log')")
        res, = (await conn.execute(query)).first()

    for block in chunkify('\n'.join(res.split('\n')[-10:])):
        await message.answer(html.pre_language(block, 'plain'))
