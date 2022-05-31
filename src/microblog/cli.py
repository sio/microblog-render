'''
Command line interface
'''

import argparse
import os
import toml
from dataclasses import dataclass, asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from . import logging
from .logging import log


def main(*a, **ka):
    '''CLI entrypoint'''
    logging.setup()
    args = parse_args(*a, **ka)
    cli = MicroblogCLI(args)
    cli.run()


@dataclass
class MicroblogCLI:
    repo: str = ''

    def __init__(self, args):
        self.args = args
        self._load()

    def __del__(self):
        self._dump()

    def _dump(self):
        '''Dump state to persistent storage'''
        statefile = self.args.state.resolve()
        log.debug(f'Dumping {self} to {statefile}')
        with NamedTemporaryFile(
                mode='w',
                prefix=__package__,
                dir=statefile.parent,
                delete=False,
        ) as temp:
            toml.dump(asdict(self), temp)
            temp.flush()
        os.replace(temp.name, statefile)  # atomic because we stay on the same filesystem

    def _load(self):
        '''Load state from persistent storage'''
        if not self.args.state.exists():
            return
        with self.args.state.open() as state:
            saved = toml.load(state)
        for key, value in saved.items():
            setattr(self, key, value)
        log.debug(f'Loaded {self} from {self.args.state}')

    def run(self):
        '''Execute action specified by args'''
        log.debug(f'Executing {self.args.action} on {self}')
        action = getattr(self, self.args.action)
        return action()

    def open(self):
        '''Remember which repo we will work with from now on'''
        self.repo = self.args.repo


def parse_args(*a, **ka):
    parser = argparse.ArgumentParser(
        description='Interact with microblogs stored in git commit messages',
        epilog='Licensed under Apache License, version 2.0'
    )
    parser.add_argument(
        '--state',
        metavar='PATH',
        type=Path,
        default=os.getenv('MICROBLOG_STATE', './microblog.state'),
        help=(
            'Path to file that stores persistent state between runs. '
            'Default: $MICROBLOG_STATE or "./microblog.state"'
        ),
    )
    subcommands = parser.add_subparsers(
        dest='action',
        required=True,
        metavar='SUBCOMMAND',
    )
    cmd = argparse.Namespace()
    cmd.open = subcommands.add_parser(
        'open',
        help='Open microblog from cloned git repository'
    )
    cmd.open.add_argument(
        'repo',
        metavar='PATH',
        type=Path,
        help='Path to git repository on local machine',
    )

    args = parser.parse_args(*a, **ka)

    if not (args.state.parent.exists() and args.state.parent.is_dir()):
        parser.error(f'not a directory: {args.state.parent}')
    if args.state.is_dir():
        parser.error(f'directory exists in place of state file: {args.state}')

    if args.action == 'open':
        git = args.repo / '.git'
        if not git.exists() or not git.is_dir():
            parser.error(f'not a git repository: {args.repo}')
    return args