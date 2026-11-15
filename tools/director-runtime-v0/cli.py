#!/usr/bin/env python3
"""Isolated WAR-90 text pilot entry point."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
from runtime import Pilot, PilotError, initialize


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init')
    init.add_argument('--workspace', required=True)
    init.add_argument('--source', required=True)
    init.add_argument('--skill', required=True, help='Seven-file directory or its SKILL.md')
    for name in ('run-stage', 'resume-pack', 'prepare-stage'):
        stage = commands.add_parser(name)
        stage.add_argument('--workspace', required=True)
        stage.add_argument('--stage', choices=('intent', 'beat', 'blocking', 'shot'), required=True)
        stage.add_argument('--mode', choices=('resume', 'continue', 'refresh'), default='resume')
        stage.add_argument('--scope', default='')
        stage.add_argument('--targets', nargs='*', default=[])
        if name == 'run-stage':
            stage.add_argument('--dry-run', action='store_true')
    submit = commands.add_parser('submit-stage')
    submit.add_argument('--workspace', required=True)
    submit.add_argument('--run-id', required=True)
    review = commands.add_parser('record-review')
    review.add_argument('--workspace', required=True)
    review.add_argument('--checkpoint', choices=('A', 'B'), required=True)
    review.add_argument('--decision', choices=('accept', 'reject', 'revise'), required=True)
    review.add_argument('--evidence-file', required=True)
    review.add_argument('--actor', choices=('human',), required=True)
    status = commands.add_parser('status')
    status.add_argument('--workspace', required=True)
    preview = commands.add_parser('review-pack', help='Read-only preview handoff, not WAR-35 schema')
    preview.add_argument('--workspace', required=True)
    review_shot = commands.add_parser('review-shot', help='Compact, pilot-only approved Shot read view')
    review_shot.add_argument('--workspace', required=True)
    review_shot.add_argument('--shot-id', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            result = initialize(args.workspace, args.source, args.skill)
        else:
            pilot = Pilot(args.workspace)
            if args.command == 'status':
                result = pilot.status()
            elif args.command == 'review-pack':
                result = pilot.review_packet()
            elif args.command == 'review-shot':
                result = pilot.review_shot(args.shot_id)
            elif args.command == 'record-review':
                result = pilot.review(args.checkpoint, args.decision, args.evidence_file, args.actor)
            elif args.command == 'prepare-stage':
                result = pilot.prepare(args.stage, args.mode, args.scope, args.targets)
            elif args.command == 'submit-stage':
                result = pilot.submit(args.run_id)
            elif args.command == 'resume-pack' or args.dry_run:
                print(pilot.packet(pilot.load(), args.stage, args.mode, args.scope, args.targets), end='')
                return 0
            else:
                result = pilot.run(args.stage, args.mode, args.scope, args.targets)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (PilotError, OSError, ValueError, KeyError) as error:
        print(f'Blocked: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
